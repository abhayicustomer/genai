from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import logging
import os
import json
import ast
import time

import dotenv
dotenv.load_dotenv()

from langchain.chains import create_sql_query_chain #to create sql query
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool #to execute the query
from langchain_community.utilities import SQLDatabase

from langchain_community.vectorstores import FAISS
from langchain_core.example_selectors import SemanticSimilarityExampleSelector
from langchain.embeddings import OpenAIEmbeddings

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

host = os.getenv('POSTGRES_HOST')
port = os.getenv('POSTGRES_PORT')
user = os.getenv('POSTGRES_USER')
database = os.getenv('POSTGRES_DATABASE')
password = os.getenv('POSTGRES_PASSWORD')
schemaname = os.getenv('POSTGRES_SCHEMANAME')
tablename = ast.literal_eval(os.getenv('POSTGRES_TABLENAME'))


logger = logging.getLogger(__name__)

# Create your views here.
# csrf_exempt is used to avoid csrf token error

db = SQLDatabase.from_uri(f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}",
                          schema=schemaname,
                         sample_rows_in_table_info=0, # default 3
                         include_tables=tablename)

llm = ChatOpenAI(temperature=0, model="gpt-4")

training_data = [
    {
        "input": "list all the companies",
        "query": "SELECT DISTINCT hb_account_properties_name FROM talkable_test.master_account_hfsf_account_deals_oppo LIMIT 10;"
    },
    {
        "input": "Retrieve all companies in the technology industry",
        "query": "SELECT DISTINCT hb_account_properties_name FROM talkable_test.master_account_hfsf_account_deals_oppo WHERE hb_account_properties_industry = 'Technology' LIMIT 10;"
    },
    {
        "input": "Filter companies founded in the last five years",
        "query": "SELECT DISTINCT hb_account_properties_name,hb_account_properties_founded_year FROM talkable_test.master_account_hfsf_account_deals_oppo WHERE hb_account_properties_founded_year >= (EXTRACT(YEAR FROM CURRENT_DATE) - 5) LIMIT 10;"
    },
    {
        "input": "Group companies by location and revenue range", 
        "query": "SELECT DISTINCT hb_account_properties_name, hb_account_properties_address, hb_account_properties_annual_revenue_range__c FROM talkable_test.master_account_hfsf_account_deals_oppo GROUP BY hb_account_properties_name, hb_account_properties_address, hb_account_properties_annual_revenue_range__c LIMIT 10;"
    },
    {
        "input": "Group companies by location and employee count range", 
        "query": "SELECT DISTINCT hb_account_properties_name, hb_account_properties_address, hb_account_properties_numberofemployees FROM talkable_test.master_account_hfsf_account_deals_oppo GROUP BY hb_account_properties_name, hb_account_properties_address, hb_account_properties_numberofemployees LIMIT 10;"
    },
    {
        "input": "How many leads converted to opportunity in this month", 
        "query": "SELECT COUNT(DISTINCT sf_leads_id) FROM talkable_test.master_contact_hfsf_lead_contact WHERE sf_leads_status = 'Converted' AND DATE_TRUNC('month', sf_leads_converteddate::date) = DATE_TRUNC('month', CURRENT_DATE) LIMIT 10;"
    },
    {
        "input": "Show companies in the automotive industry with revenue between $10 million and $50 million",
        "query": "SELECT DISTINCT hb_account_properties_name, hb_account_properties_annualrevenue FROM talkable_test.master_account_hfsf_account_deals_oppo WHERE hb_account_properties_industry = 'Automotive' AND hb_account_properties_annualrevenue BETWEEN 100000000 AND 50000000 LIMIT 10;"
    }
]

example_selector = SemanticSimilarityExampleSelector.from_examples(
    training_data,
    OpenAIEmbeddings(),
    FAISS,
    k=3,
    input_keys=["input"],
)

system_prefix = """You are an agent designed to interact with a Postgres SQL database.
Given an input question, create a syntactically correct Postgres SQL query to run, then look at the results of the query and return the answer.
Unless the user specifies a specific number of examples they wish to obtain, always limit your query to at most {top_k} results.
Always use the LIMIT 10 to limit the result.
You can order the results by a relevant column to return the most interesting examples in the database.
Never query for all the columns from a specific table, only ask for the relevant columns given the question.
You have access to tools for interacting with the database.
Only use the given tools. Only use the information returned by the tools to construct your final answer.
You MUST double check your query before executing it. If you get an error while executing a query, rewrite the query and try again.
DO NOT include the duplicate rows. Make sure whatever columns you will choose should return distinct rows values.

DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the database.

Only use the following tables:
{table_info}

Write an initial draft of the query. 
Then double check the Postgres SQL query for common mistakes, including:
- Using NOT IN with NULL values
- Using UNION when UNION ALL should have been used
- Using BETWEEN for exclusive ranges
- Data type mismatch in predicates
- Properly quoting identifiers
- Using the correct number of arguments for functions
- Casting to the correct data type
- Using the proper columns for joins
- Always try to include the important column in Postgres SQL query based on user input

If there are any of the above mistakes, rewrite the query. If there are no mistakes, just reproduce the original query.

Below are some examples of user inputs and their corresponding Postgres SQL queries. These queries are added just to provide you the sample examples. Don't use the below queries If they are not relevant to use input query:
"""

few_shot_prompt = FewShotPromptTemplate(
    example_selector=example_selector,
    example_prompt=PromptTemplate.from_template(
        "Query: {input}\nPostgres SQL Query: {query}"
    ),
    input_variables=["input", "top_k"],
    prefix=system_prefix,
    suffix="{input}\nPostgres SQL Query:",
)

# few_shot_prompt.pretty_print()

write_query_chain = create_sql_query_chain(llm, db, prompt=few_shot_prompt, k=10)
execute_query = QuerySQLDataBaseTool(db=db, handle_tool_error=True, handle_validation_error=True, return_direct=True)

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            '''You're a helpful AI assistant. You need to answer the question from the Postgres result.
            Given a user question and some result, answer the user question from this result ONLY.
            DO NOT generate query of irrelevant or out of context general questions.
            DO NOT try to generate the answer from own.\n\nHere are the result: POSTGRES QUERY: {postgres_query}\n{postgres_result}
            If postgres query is not generated then respond "I am sorry, currently i am not able to handle this request as it doesn't belongs to the database. Please try rephrasing". 
            
            Answer:''',
        ),
        ("human", "{question}"),
    ]
)

lcel_chain = (
    RunnablePassthrough.assign(postgres_query=write_query_chain)
    .assign(postgres_result=itemgetter("postgres_query") | execute_query)
    .assign(result = prompt| llm| StrOutputParser())
    .pick(["question", "postgres_query", "postgres_result", "result"])
)

@csrf_exempt
def nlp2sql(request):
    """
    This method will fetch the necessary tables information using openai.
    parameters: request (POST) - Query
    Output: A dictionary containing the query result and the status of the operation.
    """

    try:
        if request.method == 'POST':
            print(request.body)
            logger.debug("API REQUEST --> %s", request)
            query = json.loads(request.body.decode('utf-8')).get('query', '')
            user_id = json.loads(request.body.decode('utf-8')).get('user_id')
            session_id = json.loads(request.body.decode('utf-8')).get('session_id')

            print("Query", query)
            logger.debug("USER ID, SESSION ID --> %s, %s", user_id, session_id)
            logger.debug("QUERY --> %s", query)
            t0 = time.time()
            if query:
                output = lcel_chain.invoke({"question": query})
                if 'error' in output['postgres_result']:
                    output['postgres_result_error'] = output['postgres_result']
                    output['postgres_result'] = []
                else:
                    output['postgres_result'] = ast.literal_eval(output['postgres_result'])
                # if questionId == 0:
                    # chat_history = []
                # else:
                    # chat_history = sessions.retrieve_chats_by_session(user_id, session_id, "Internal RSI", "Case Studies QnA V3")
                    # if not chat_history:
                        # chat_history = []
                logger.debug(output)
                return JsonResponse({"result": output, "Status": "PASS", "response_time": time.time()-t0})
            else:
                logger.debug('Query can not be blank.')
                return JsonResponse({'result': 'Query can not be blank.', "status": "FAIL", "response_time": time.time()-t0})

    except Exception as e:
        logger.debug('Wrong API request ' + str(e))
        return JsonResponse({'result': 'Wrong API request ' + str(e), "status": "FAIL"})

