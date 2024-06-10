import logging
import os
import ast

import dotenv
dotenv.load_dotenv()

from langchain.chains import create_sql_query_chain  # to create sql query
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool  # to execute the query
from langchain_community.utilities import SQLDatabase

from langchain_community.vectorstores import FAISS
from langchain_core.example_selectors import SemanticSimilarityExampleSelector
from langchain.embeddings import OpenAIEmbeddings

from langchain_core.runnables import RunnableParallel
from langchain_core.runnables import RunnablePassthrough
from operator import itemgetter
from langchain_core.output_parsers import StrOutputParser

from langchain.globals import set_debug, set_verbose

set_debug(False)
set_verbose(True)

from langchain_core.prompts import (
    ChatPromptTemplate,
    FewShotPromptTemplate,
    MessagesPlaceholder,
    PromptTemplate,
    SystemMessagePromptTemplate,
)

from langchain_openai import ChatOpenAI
from prompt_config import *

host = os.getenv('POSTGRES_HOST')
port = os.getenv('POSTGRES_PORT')
user = os.getenv('POSTGRES_USER')
database = os.getenv('POSTGRES_DATABASE')
password = os.getenv('POSTGRES_PASSWORD')
schemaname = os.getenv('POSTGRES_SCHEMANAME_ZILLA')
tablename = ast.literal_eval(os.getenv('POSTGRES_TABLENAME_ZILLA'))

logger = logging.getLogger(__name__)

db = SQLDatabase.from_uri(f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}",
                          schema=schemaname,
                          sample_rows_in_table_info=0,  # default 3
                          include_tables=tablename)

llm = ChatOpenAI(temperature=0, model="gpt-4")

example_selector = SemanticSimilarityExampleSelector.from_examples(
    training_data_zilla,
    OpenAIEmbeddings(),
    FAISS,
    k=3,
    input_keys=["input"],
)

few_shot_prompt = FewShotPromptTemplate(
    example_selector=example_selector,
    example_prompt=PromptTemplate.from_template(
        "Query: {input}\nPostgres SQL Query: {query}"
    ),
    input_variables=["input", "top_k"],
    prefix=structured_system_qna_withfewshots,
    suffix="{input}\nPostgres SQL Query:",
)

# few_shot_prompt.pretty_print()

write_query_chain = create_sql_query_chain(llm, db, prompt=few_shot_prompt, k=10)
execute_query = QuerySQLDataBaseTool(db=db, handle_tool_error=True, handle_validation_error=True, return_direct=True)

prompt = ChatPromptTemplate.from_messages([("system",structured_response_prompt,),("human", "{question}"),])

def structured_chain_withouthistory():
    lcel_chain = (
        RunnablePassthrough.assign(postgres_query=write_query_chain)
        .assign(postgres_result=itemgetter("postgres_query") | execute_query)
        .assign(result=prompt | llm | StrOutputParser())
        .pick(["question", "postgres_query", "postgres_result", "result"])
    )

    return lcel_chain

contextualize_q_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", contextualize_q_system_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{question}"),
    ]
)
#Ignore the null values:\n
contextualize_q_chain = contextualize_q_prompt | llm | StrOutputParser()

def contextualized_question(input: dict):
    if input.get("chat_history"):
        return contextualize_q_chain
    else:
        return input["question"]
        
#"Ignore the null values:\n"+

def structured_chain_withhistory():
    lcel_chain2 = (
        RunnableParallel(question=contextualized_question)
        .assign(postgres_query=write_query_chain)  # , passed=RunnablePassthrough(), question = lambda x:x["question"])
        .assign(postgres_result=itemgetter("postgres_query") | execute_query)
        .assign(result=prompt | llm | StrOutputParser())
        .pick(["question", "postgres_query", "postgres_result", "result"])
    )

    return lcel_chain2
