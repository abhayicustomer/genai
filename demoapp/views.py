"""
This module contains the views for the demo application.
"""

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import logging
import json
import time
import ast
import numbers

from langchain_openai import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings

from langchain_community.document_loaders import PDFMinerLoader, TextLoader

from langchain_community.vectorstores import FAISS, Chroma
from langchain_core.example_selectors import SemanticSimilarityExampleSelector

from langchain_core.prompts import (
    ChatPromptTemplate,
    FewShotPromptTemplate,
    MessagesPlaceholder,
    PromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate
)

from langchain.output_parsers import ResponseSchema, StructuredOutputParser

from langchain_core.runnables import RunnablePassthrough, RunnableParallel, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from operator import itemgetter

import os

import index
from langchain.chains import create_sql_query_chain
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from langchain_community.utilities import SQLDatabase

from prompt_config import *

import dotenv

dotenv.load_dotenv()

logger = logging.getLogger(__name__)

llm = ChatOpenAI(temperature=0, model="gpt-4")
embeddings = OpenAIEmbeddings()

host = os.getenv('POSTGRES_HOST')
port = os.getenv('POSTGRES_PORT')
user = os.getenv('POSTGRES_USER')
database = os.getenv('POSTGRES_DATABASE')
password = os.getenv('POSTGRES_PASSWORD')
session_schemaname = os.getenv('POSTGRES_CHATHISTORY_SCHEMANAME')
session_tablename = ast.literal_eval(os.getenv('POSTGRES_CHATHISTORY_TABLENAME'))
talkable_schemaname = os.getenv('POSTGRES_SCHEMANAME')
talkable_tablename = ast.literal_eval(os.getenv('POSTGRES_TABLENAME'))
zilla_schemaname = os.getenv('POSTGRES_SCHEMANAME_ZILLA')
zilla_tablename = ast.literal_eval(os.getenv('POSTGRES_TABLENAME_ZILLA'))

session_db = SQLDatabase.from_uri(f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}",
                                  schema=session_schemaname,
                                  sample_rows_in_table_info=1,
                                  include_tables=session_tablename)
talkable_db = SQLDatabase.from_uri(f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}",
                              schema=talkable_schemaname,
                              sample_rows_in_table_info=0,
                              include_tables=talkable_tablename)
zilla_db = SQLDatabase.from_uri(f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}",
                              schema=zilla_schemaname,
                              sample_rows_in_table_info=0,
                              include_tables=zilla_tablename)

def session_by_id(session_id, user_id=None):
    """
    Retrieve the chat history for a given session ID.

    Args:
        session_id (str): The session ID.
        user_id (str, optional): The user ID. Defaults to None.

    Returns:
        list: The chat history.
    """
    try:
        query = f"SELECT chat_array FROM dev.chat_v4 WHERE session_id='{session_id}';"
        query_result = session_db.run(query)
        res = []
        if query_result:
            res = ast.literal_eval(query_result)
        if res:
            res1 = [["Human: " + i['question'], "AI:"+'\nResult: ' + i['postgres_result']] for i in res[0][0]]
            # res1 = [["Human: " + i['question'], "AI: " + i['postgres_query'].replace('\n',' ') +'\n' + i['postgres_result']] for i in res[0][0]]
            res1 = [item for sublist in res1 for item in sublist][-4:]
            return res1
        else:
            return []
    except Exception as e:
        print(e)
        return []

def tables_by_id(session_id, session_db):
    """
    Retrieve the table information for a given session ID.

    Args:
        session_id (str): The session ID.
        session_db (SQLDatabase): The SQL database.

    Returns:
        list: The table information.
    """
    try:
        query = f"SELECT file_table_name, schema_name FROM dev.chat_v4 WHERE session_id='{session_id}';"
        res = ast.literal_eval(session_db.run(query))
        if res:
            return res
        else:
            return []
    except Exception as e:
        print(e)
        return []

topic_prompt = PromptTemplate(input_variables=["question"], template=topic_prompt_template)
topic_chain = topic_prompt | llm | StrOutputParser()

column_prompt = PromptTemplate(input_variables=["sql_query"], template=column_prompt_template)
column_chain = column_prompt | llm | StrOutputParser()

def chartResponse(res):
    """
    Generate a chart response based on the query result.

    Args:
        res (dict): The query result.

    Returns:
        dict: The chart response.
    """
    chart_dict = {}
    if 'postgres_query' in res:
        columns = column_chain.invoke({"sql_query": res['postgres_query']})
        columns = ast.literal_eval(columns)
        try:
            postgres_result = ast.literal_eval(res['postgres_result'])
        except:
            postgres_result = res['postgres_result']
        if len(columns) == 2 and type(postgres_result) == list:
            if isinstance(postgres_result[0][0], numbers.Number) or isinstance(postgres_result[-1][0], numbers.Number):
                chart_dict["metadata"] = {"labelX": columns[0], "labelY": columns[1], "rep": res["topic"]}
                data = [{"xValue": i[1], "yValue": i[0]} for i in postgres_result]
                chart_dict["data"] = data
            elif isinstance(postgres_result[0][1], numbers.Number) or isinstance(postgres_result[-1][1], numbers.Number):
                chart_dict["metadata"] = {"labelX": columns[0], "labelY": columns[1], "rep": res["topic"]}
                data = [{"xValue": i[0], "yValue": i[1]} for i in postgres_result]
                chart_dict["data"] = data
            else:
                pass
    return chart_dict

def contextualized_question(input: dict):
    """
    Generate a contextualized question.

    Args:
        input (dict): The input data.

    Returns:
        str: The contextualized question.
    """
    return input["question"]

def format_docs(docs):
    """
    Format the document content.

    Args:
        docs (list): The list of documents.

    Returns:
        str: The formatted document content.
    """
    formatted = [
        f"Source: {doc.metadata['source']}\nContent: {doc.page_content}"
        for i, doc in enumerate(docs)
    ]
    return "\n\n" + "\n\n".join(formatted)

def text_preprocessing(data):
    """
    Perform text preprocessing on the data.

    Args:
        data: The input data.

    Returns:
        str: The preprocessed data.
    """
    try:
        import re
        data.page_content = re.sub(r' +', ' ', data.page_content)
        data.page_content = re.sub(r'\n+', '\n', data.page_content)
        data.page_content = re.sub(r'\n\t\n', '\n', data.page_content)
        data.page_content = re.sub(r"’", "'", data.page_content)
        data.page_content = re.sub(r"‘", "'", data.page_content)
        return data
    except Exception as e:
        print(e)
        return ''
        pass

def pdf_data_fn(files):
    """
    Load and preprocess the data from PDF files.

    Args:
        files (list): The list of file paths.

    Returns:
        list: The preprocessed data.
    """
    try:
        data = []
        for file in files:
            loaders = PDFMinerLoader(file)
            data.extend([text_preprocessing(loaders.load()[0])])
        return data
    except Exception as e:
        print(e)
        pass

index_name = "serverless-index"

@csrf_exempt
def unstructured(request):
    """
    Fetch the necessary tables information using OpenAI.

    Args:
        request (POST): The query.

    Returns:
        JsonResponse: A dictionary containing the query result and the status of the operation.
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
            index_location = f'./media/{session_id}/faiss_index'
            if query:
                try:
                    vectordb = index.load_index(index_location)
                except Exception as e:
                    return JsonResponse({'result': 'Embeddings not created yet.\n' + str(e), "status": "FAIL"})
                response_schemas = [
                    ResponseSchema(name="question", description="user's question"),
                    ResponseSchema(name="result",
                                   description="answer to the user's question without source and don't remove the new line characters like \n for formatting etc."),
                    ResponseSchema(name="source", description="source fileneme if present else blank string"),
                    ResponseSchema(name="follow-up",
                                   description="the follow up questions in a array or list if present else []", ),
                ]
                output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
                format_instructions = output_parser.get_format_instructions()

                qa_prompt_withhistory = PromptTemplate(
                    template=unstructured_generic_qna,
                    input_variables=["question", "context"],
                    partial_variables={"format_instructions": format_instructions},
                )

                retriever = vectordb.as_retriever(search_type='similarity_score_threshold',
                                                  search_kwargs={"k": 10, "score_threshold": 0.1})

                rag_chain_chat = (
                    RunnablePassthrough.assign(
                        context=contextualized_question | retriever | format_docs
                    )
                    .assign(result=qa_prompt_withhistory | llm | output_parser)
                    .pick(["result"])
                )
                try:
                    output = rag_chain_chat.invoke({"question": query})
                except Exception as e:
                    try:
                        retry_count = 0
                        while retry_count < 2:
                            output = rag_chain_chat.invoke({"question": query})
                            retry_count += 1
                    except Exception as e:
                        return JsonResponse({'result': 'Wrong API request ' + str(e), "status": "FAIL"})
                # if questionId == 0:
                # chat_history = []
                # else:
                # chat_history = sessions.retrieve_chats_by_session(user_id, session_id, "Internal RSI", "Case Studies QnA V3")
                # if not chat_history:
                # chat_history = []
                logger.debug(output)
                return JsonResponse({"result": output["result"], "Status": "PASS", "response_time": time.time() - t0})
            else:
                logger.debug('Query can not be blank.')
                return JsonResponse(
                    {'result': 'Query can not be blank.', "status": "FAIL", "response_time": time.time() - t0})

    except Exception as e:
        logger.debug('Wrong API request ' + str(e))
        return JsonResponse({'result': 'Wrong API request ' + str(e), "status": "FAIL"})


@csrf_exempt
def structured(request):
    """
    This method will fetch the necessary tables information using openai.
    parameters: request (POST) - Query
    Output: A dictionary containing the query result and the status of the operation.
    """

    try:
        if request.method == 'POST':
            # print(request.body)
            query = json.loads(request.body.decode('utf-8')).get('query', '')
            user_id = json.loads(request.body.decode('utf-8')).get('user_id')
            session_id = json.loads(request.body.decode('utf-8')).get('session_id')
            schemaname = json.loads(request.body.decode('utf-8')).get('schemaname')
            tablename = json.loads(request.body.decode('utf-8')).get('tablename')

            print("Query", query)
            t0 = time.time()

            if query:
                tablename = tablename.split(',')
                tablename = [i.strip() for i in tablename]
                # res = tables_by_id(session_id, session_db)
                # if res:
                #     tablename = res[0][0].split(',')
                #     tablename = [i.strip() for i in tablename]
                #     schemaname = res[0][1]
                # tablename = ["master_account_hfsf_account_deals_oppo", "master_contact_hfsf_lead_contact"]
                # schemaname= "talkable_master"
                print("SCHEMA", schemaname)
                # print("TABLE", tablename)
                if schemaname == "talkable_master":
                    # tablename = talkable_tablename
                    db = talkable_db
                    example_selector = SemanticSimilarityExampleSelector.from_examples(
                        training_data_talkable,
                        OpenAIEmbeddings(),
                        FAISS,
                        k=5,
                        input_keys=["input"],
                    )
                    few_shot_prompt = FewShotPromptTemplate(
                        example_selector=example_selector,
                        example_prompt=PromptTemplate.from_template(
                            "Query: {input}\nPostgres SQL Query: {query}"
                        ),
                        input_variables=["input", "top_k"],
                        prefix=structured_system_qna_withfewshots,
                        suffix="Always ignore the NULL values while creating the query.\n{input}\nPostgres SQL Query: ",
                    )
                    #First draft: << FIRST Postgres SQL Query:>>\nPostgres SQL Query: << FINAL Postgres SQL Query:>>
                    # few_shot_prompt = PromptTemplate(
                    #     template=structured_system_qna_withfewshots_talkable,
                    #     input_variables=["input", "top_k"],
                    # )
                elif schemaname == "zillasecurity_master":
                    # tablename = zilla_tablename
                    db = zilla_db
                    example_selector = SemanticSimilarityExampleSelector.from_examples(
                        training_data_zilla,
                        OpenAIEmbeddings(),
                        FAISS,
                        k=5,
                        input_keys=["input"],
                    )
                    few_shot_prompt = FewShotPromptTemplate(
                        example_selector=example_selector,
                        example_prompt=PromptTemplate.from_template(
                            "Query: {input}\nPostgres SQL Query: {query}"
                        ),
                        input_variables=["input", "top_k"],
                        prefix=structured_system_qna_withfewshots,
                        suffix="Always ignore the NULL values while creating the query.\n{input}\nPostgres SQL Query:",
                    )
                    # few_shot_prompt = PromptTemplate(
                    #     template=structured_system_qna_withfewshots_zilla,
                    #     input_variables=["input", "top_k"],
                    # )
                else:
                    try:
                        db = SQLDatabase.from_uri(f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}",
                                                  schema=schemaname,
                                                  sample_rows_in_table_info=0,  # default 3
                                                  include_tables=tablename)
                    except Exception as e:
                        return JsonResponse({'result': 'Wrong Schema & Table name ' + str(e), "status": "FAIL"})
                    few_shot_prompt = PromptTemplate(
                        template=structured_system_qna_withoutfewshots,
                        input_variables=["input", "top_k"],
                    )

                write_query_chain = create_sql_query_chain(llm, db, prompt=few_shot_prompt, k=10)
                execute_query = QuerySQLDataBaseTool(db=db, handle_tool_error=False, handle_validation_error=False,
                                                     return_direct=False)

                prompt = ChatPromptTemplate.from_messages(
                    [("system", structured_response_prompt,),
                     ("human", "{question}"), ])

                contextualize_q_prompt = ChatPromptTemplate.from_messages(
                    [("system", contextualize_q_system_prompt), MessagesPlaceholder(variable_name="chat_history"),
                     ("human", "{question}"), ])
                contextualize_q_chain = contextualize_q_prompt | llm | StrOutputParser()

                def contextualized_question(input: dict):
                    if input.get("chat_history"):
                        return contextualize_q_chain
                    else:
                        return input["question"]

                # lcel_chain = (
                #     RunnablePassthrough.assign(postgres_query=write_query_chain)
                #     .assign(postgres_result=itemgetter("postgres_query") | execute_query)
                #     .assign(result=prompt | llm | StrOutputParser())
                #     .pick(["question", "postgres_query", "postgres_result", "result"])
                # )
                lcel_chain2 = (
                    RunnableParallel(question=contextualized_question)
                    .assign(
                        postgres_query=write_query_chain)  # , passed=RunnablePassthrough(), question = lambda x:x["question"])
                    .assign(postgres_result=itemgetter("postgres_query") | execute_query)
                    .assign(result=prompt | llm | StrOutputParser())
                    .pick(["question", "postgres_query", "postgres_result", "result"])
                )
                try:
                    chat_history = session_by_id(session_id, session_db)
                    print(chat_history)
                    output = lcel_chain2.invoke({"question": query, "chat_history": chat_history})
                    output['topic'] = topic_chain.invoke({"question": query})
                    output['chart_response'] = {}
                    output['chart_response'] = chartResponse(output)
                except Exception as e:
                    return JsonResponse({'result': 'Wrong API request ' + str(e), "status": "FAIL"})
                return JsonResponse({"result": output, "Status": "PASS", "response_time": time.time() - t0})
            else:
                return JsonResponse(
                    {'result': 'Query can not be blank.', "status": "FAIL", "response_time": time.time() - t0})

    except Exception as e:
        return JsonResponse({'result': 'Wrong API request ' + str(e), "status": "FAIL"})
#
# @csrf_exempt
# def structured_file(request):
#     """
#     This method will fetch the necessary tables information using openai.
#     parameters: request (POST) - Query
#     Output: A dictionary containing the query result and the status of the operation.
#     """
#
#     try:
#         if request.method == 'POST':
#             print(request.body)
#             logger.debug("API REQUEST --> %s", request)
#             query = json.loads(request.body.decode('utf-8')).get('query', '')
#             user_id = json.loads(request.body.decode('utf-8')).get('user_id')
#             session_id = json.loads(request.body.decode('utf-8')).get('session_id')
#
#             print("Query", query)
#             logger.debug("USER ID, SESSION ID --> %s, %s", user_id, session_id)
#             logger.debug("QUERY --> %s", query)
#             t0 = time.time()
#             file_location_path = f'./media/{session_id}/data'
#             if query:
#                 filename = [file for sublist in
#                             [[os.path.join(i[0], j) for j in i[2]] for i in os.walk(file_location_path)] for file in
#                             sublist if '.csv' in file]
#                 filename = filename[0]
#                 df = pd.read_csv(filename)
#                 # print(df.head(1))
#                 filename_name = filename.replace('.csv', '')
#                 print(filename_name)
#                 engine = create_engine(f"sqlite:///{filename_name}.db")
#                 temp_file = filename_name.split('\\')[-1].split('/')[-1]
#                 if not os.path.isfile(f'./media/{session_id}/data/{temp_file}.db'):
#                     print("FILE NOT EXISTS", temp_file)
#                     df.to_sql(f'{temp_file}', engine, index=False)
#
#                 db = SQLDatabase(engine=engine)
#                 system_prefix = """You are an agent designed to interact with a Postgres SQL database.
#                 Given an input question, create a syntactically correct Postgres SQL query to run, then look at the results of the query and return the answer.
#                 Unless the user specifies a specific number of examples they wish to obtain, always limit your query to at most {top_k} results.
#                 Always use the LIMIT 10 to limit the result.
#                 You can order the results by a relevant column to return the most interesting examples in the database.
#                 Never query for all the columns from a specific table, only ask for the relevant columns given the question.
#                 You have access to tools for interacting with the database.
#                 Only use the given tools. Only use the information returned by the tools to construct your final answer.
#                 You MUST double check your query before executing it. If you get an error while executing a query, rewrite the query and try again.
#                 DO NOT include the duplicate rows. Make sure whatever columns you will choose should return distinct rows values.
#
#                 DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the database.
#
#                 Only use the following tables:
#                 {table_info}
#
#                 Write an initial draft of the query.
#                 Then double check the Postgres SQL query for common mistakes, including:
#                 - Using NOT IN with NULL values
#                 - Using UNION when UNION ALL should have been used
#                 - Using BETWEEN for exclusive ranges
#                 - Data type mismatch in predicates
#                 - Properly quoting identifiers
#                 - Using the correct number of arguments for functions
#                 - Casting to the correct data type
#                 - Using the proper columns for joins
#                 - Always try to include the important column in Postgres SQL query based on user input
#
#                 If there are any of the above mistakes, rewrite the query. If there are no mistakes, just reproduce the original query.
#
#                 {input}
#                 Postgres SQL Query:
#                 """
#
#                 # few_shot_prompt = ChatPromptTemplate.from_messages(
#                 #         [HumanMessagePromptTemplate.from_template(system_prefix)])
#
#                 few_shot_prompt = PromptTemplate(
#                     template=system_prefix,
#                     input_variables=["input", "top_k"],
#                     # partial_variables = {"format_instructions": format_instructions},
#                 )
#
#                 write_query_chain = create_sql_query_chain(llm, db, prompt=few_shot_prompt, k=10)
#                 execute_query = QuerySQLDataBaseTool(db=db, handle_tool_error=True, handle_validation_error=True,
#                                                      return_direct=True)
#
#                 prompt = ChatPromptTemplate.from_messages(
#                     [
#                         (
#                             "system",
#                             '''You're a helpful AI assistant. You need to answer the question from the Postgres result.
#                             Given a user question and some result, answer the user question from this result ONLY.
#                             DO NOT generate query of irrelevant or out of context general questions.
#                             DO NOT try to generate the answer from own.\n\nHere are the result: POSTGRES QUERY: {postgres_query}\n{postgres_result}
#                             If postgres query is not generated then respond "I am sorry, currently i am not able to handle this request as it doesn't belongs to the database. Please try rephrasing".
#
#                             Answer:''',
#                         ),
#                         ("human", "{question}"),
#                     ]
#                 )
#
#                 lcel_chain = (
#                         RunnablePassthrough.assign(postgres_query=write_query_chain)
#                         .assign(postgres_result=itemgetter("postgres_query") | execute_query)
#                         .assign(result=prompt | llm | StrOutputParser())
#                         .pick(["question", "postgres_query", "postgres_result", "result"])
#                     )
#
#                 try:
#                     output = lcel_chain.invoke({"question": query, "chat_history": []})
#                 except Exception as e:
#                     try:
#                         retry_count = 0
#                         while retry_count < 2:
#                             output = lcel_chain.invoke({"question": query, "chat_history": []})
#                             retry_count += 1
#                     except Exception as e:
#                         return JsonResponse({'result': 'Wrong API request ' + str(e), "status": "FAIL"})
#                 # if questionId == 0:
#                 # chat_history = []
#                 # else:
#                 # chat_history = sessions.retrieve_chats_by_session(user_id, session_id, "Internal RSI", "Case Studies QnA V3")
#                 # if not chat_history:
#                 # chat_history = []
#                 logger.debug(output)
#                 return JsonResponse({"result": output, "Status": "PASS", "response_time": time.time() - t0})
#             else:
#                 logger.debug('Query can not be blank.')
#                 return JsonResponse(
#                     {'result': 'Query can not be blank.', "status": "FAIL", "response_time": time.time() - t0})
#
#     except Exception as e:
#         logger.debug('Wrong API request ' + str(e))
#         return JsonResponse({'result': 'Wrong API request ' + str(e), "status": "FAIL"})
