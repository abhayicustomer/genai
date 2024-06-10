import zipfile
from django.http import JsonResponse, FileResponse, HttpResponse
from io import BytesIO
from django.views.decorators.csrf import csrf_exempt
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
import logging
import json
import time
import ast
import re
import os
import numbers
from prompt_config import *
import dotenv
dotenv.load_dotenv()

import structured_agent#, unstructured_agent

llm = ChatOpenAI(temperature=0, model="gpt-4")
structured_llm = structured_agent.structured_chain_withhistory()
# unstructured_llm = unstructured_agent.unstructured_chain_withhistory()

topic_prompt = PromptTemplate(input_variables=["question"], template=topic_prompt_template)
topic_chain = topic_prompt | llm | StrOutputParser()

column_prompt = PromptTemplate(input_variables=["sql_query"], template=column_prompt_template)
column_chain = column_prompt | llm | StrOutputParser()

def result_processing(text):
    # used to remove duplicate sources from unstructured dataset
    new_text = ''
    if 'Sources:' in text:
        try:
            split_text = ast.literal_eval(text.split('Sources:')[1])
            if isinstance(split_text, list):
                split_text = list(set(split_text))
                new_text = 'Sources: ' + str(split_text)
        except:
            new_text = text
    else:
        new_text = text
    return new_text


def columnNames(query):
    column_names_match = re.search(r'SELECT\s+DISTINCT\s+(.+?)\s+FROM', query, re.IGNORECASE | re.MULTILINE)
    if column_names_match:
        column_names_string = column_names_match.group(1)
        # Split column names by comma
        column_names = [col.strip() for col in column_names_string.split(',')]
    else:
        column_names = []
    return column_names


def chartResponse(res):
    chart_dict = {}
    if 'postgres_query' in res:
        # columns = columnNames(res['postgres_query'])
        columns = column_chain.invoke({"sql_query": res['postgres_query']})
        # print("COLUMNS", columns)
        columns = ast.literal_eval(columns)
        # print("PROCESSED COLUMNS", columns)
        try:
            postgres_result = ast.literal_eval(res['postgres_result'])
        except:
            postgres_result = res['postgres_result']
        if len(columns) == 2 and type(postgres_result)==list:
            # postgres_result = ast.literal_eval(res['postgres_result'])
            # print("POSTGRES RESULT", postgres_result)
            if isinstance(postgres_result[0][0], numbers.Number) or isinstance(postgres_result[-1][0], numbers.Number):
                print("COLUMNS HERE IF")
                chart_dict["metadata"] = {"labelX": columns[0], "labelY": columns[1], "rep": res["topic"]}
                data = [{"xValue": i[1], "yValue": i[0]} for i in postgres_result]
                chart_dict["data"] = data

            elif isinstance(postgres_result[0][1], numbers.Number) or isinstance(postgres_result[-1][1], numbers.Number):
                print("COLUMNS HERE ELIF")
                chart_dict["metadata"] = {"labelX": columns[0], "labelY": columns[1], "rep": res["topic"]}
                data = [{"xValue": i[0], "yValue": i[1]} for i in postgres_result]
                chart_dict["data"] = data

            else:
                print("COLUMNS HERE ELSE")
                pass
    return chart_dict


@csrf_exempt
def hybrid(request):
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
                result = dict()
                chat_history= []
                result['question'] = query
                result['topic'] = topic_chain.invoke({"question": query})
                result['chart_response'] = {}
                result_structured = structured_llm.invoke({"question": query, "chat_history": chat_history})
                # print("RESULT", result_structured)
                # result_unstructured = unstructured_llm.invoke({"input": query, "chat_history": chat_history})
                # result_unstructured['result'] = result_unstructured['result'].replace("Answer: ", "")

                # if ('sorry' in result_structured['result']) and ('sorry' in result_unstructured['result']):
                #     result['result'] = result_structured['result']
                #
                # elif ('sorry' in result_structured['result']) and ('sorry' not in result_unstructured['result']):
                #     result['result'] = result_unstructured['result']

                # elif ('sorry' not in result_structured['result']) and ('sorry' in result_unstructured['result']):
                #     result['result'] = result_structured['result'] + '\nSources: Customer Knowledge Graph'
                #     result['postgres_query'] = result_structured['postgres_query']
                #     result['postgres_result'] = result_structured['postgres_result']
                #     result['chart_response'] = chartResponse(result)
                # else:
                result['result'] = result_structured['result'] #+ '\nSources: Customer Knowledge Graph' + '\n\n' + result_unstructured['result']
                result['postgres_query'] = result_structured['postgres_query']
                result['postgres_result'] = result_structured['postgres_result']
                # print("RESULT 1", result)
                result['chart_response'] = chartResponse(result)
                # print("RESULT 2", result)
                logger.debug(result)
                # result['result'] = result['result'].replace('./data', 'http://localhost:8001/hybridapp/pdf_view/?filename=./data')
                # result['result'] = "\n".join([result_processing(i) for i in result['result'].split("\n")])
                return JsonResponse({"result": result, "Status": "PASS", "response_time": time.time()-t0})
            else:
                logger.debug('Query can not be blank.')
                return JsonResponse({'result': 'Query can not be blank.', "status": "FAIL", "response_time": time.time()-t0})

    except Exception as e:
        logger.debug('Wrong API request ' + str(e))
        return JsonResponse({'result': 'Wrong API request ' + str(e), "status": "FAIL"})

def pdf_view(request):
    try:
        if request.method == 'GET':
            path = ''
            pdf_path = request.GET['filename']
            final_path = path+pdf_path
            print(f'{final_path}')
            pdf_file = open(f'{final_path}', 'rb')
            return FileResponse(pdf_file)
    except Exception as e:
        return JsonResponse({'result': 'Wrong API request '+str(e), "status": "FAIL"})

def csv_view(request):
    try:
        if request.method == 'GET':
            # Define the base path for CSV files
            session_id = request.GET['session_id']
            base_path = f"C:\\Users\\Abhay\\Downloads\\iCustomer\\{session_id}\\data"

            # List all files in the directory
            files = os.listdir(base_path)

            # Filter out non-CSV files
            csv_files = [file for file in files if file.endswith('.csv')]
            # Create a zip file in memory
            # zip_buffer = BytesIO()
            # with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
            #     for csv_file in csv_files:
            #         file_path = os.path.join(base_path, csv_file)
            #         zip_file.write(file_path, csv_file)
            #
            # zip_buffer.seek(0)
            #
            # # Create a response with the zip file
            # response = HttpResponse(zip_buffer, content_type='application/zip')
            # response['Content-Disposition'] = 'attachment; filename=all_csv_files.zip'
            # response['status'] = 'SUCCESS'
            # return response
            # Filter out non-CSV files

            if len(csv_files) == 0:
                return JsonResponse({'result': 'No CSV files found', 'status': 'FAIL'})
            elif len(csv_files) > 1:
                return JsonResponse({'result': 'Multiple CSV files found', 'status': 'FAIL'})

            # Only one CSV file is present
            csv_file_path = os.path.join(base_path, csv_files[0])

            # Open and serve the CSV file
            # Open and serve the CSV file
            csv_file = open(csv_file_path, 'rb')
            response = FileResponse(csv_file, content_type='text/csv')
            response['Content-Disposition'] = f'inline; filename="{csv_files[0]}"'

            return response

    except Exception as e:
        return JsonResponse({'result': 'Wrong API request ' + str(e), "status": "FAIL"})
