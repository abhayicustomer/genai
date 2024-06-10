from django.http import JsonResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
import logging
import json
import time
import ast
import re
import numbers
import dotenv
dotenv.load_dotenv()

import structured_agent, unstructured_agent

logger = logging.getLogger(__name__)

llm = ChatOpenAI(temperature=0, model="gpt-4")

structured_llm = structured_agent.structured_chain_withhistory()
unstructured_llm = unstructured_agent.unstructured_chain_withhistory()

topic_prompt_template = '''Your task is to generate the topic of below question in 2-4 word with significant meaning:
                    Question: {question}
                    Topic:'''
topic_prompt = PromptTemplate(
    input_variables=["question"], template=topic_prompt_template
)

topic_chain = topic_prompt | llm | StrOutputParser()

def result_processing(text):
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
        columns = columnNames(res['postgres_query'])
        if len(columns) == 2:
            postgres_result = ast.literal_eval(res['postgres_result'])
            if isinstance(postgres_result[0][0], numbers.Number):
                chart_dict["metadata"] = {"labelX": columns[0], "labelY": columns[1], "rep": res["topic"]}
                data = [{"xValue": i[1], "yValue": i[0]} for i in postgres_result]
                chart_dict["data"] = data

            elif isinstance(postgres_result[0][1], numbers.Number):
                chart_dict["metadata"] = {"labelX": columns[0], "labelY": columns[1], "rep": res["topic"]}
                data = [{"xValue": i[0], "yValue": i[1]} for i in postgres_result]
                chart_dict["data"] = data

            else:
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
                result_unstructured = unstructured_llm.invoke({"input": query, "chat_history": chat_history})
                result_unstructured['result'] = result_unstructured['result'].replace("Answer: ", "")

                if ('sorry' in result_structured['result']) and ('sorry' in result_unstructured['result']):
                    result['result'] = result_structured['result']

                elif ('sorry' in result_structured['result']) and ('sorry' not in result_unstructured['result']):
                    result['result'] = result_unstructured['result']

                elif ('sorry' not in result_structured['result']) and ('sorry' in result_unstructured['result']):
                    result['result'] = result_structured['result'] + '\nSources: Customer Knowledge Graph'
                    result['postgres_query'] = result_structured['postgres_query']
                    result['postgres_result'] = result_structured['postgres_result']
                    result['chart_response'] = chartResponse(result)
                else:
                    result['result'] = result_structured['result'] + '\nSources: Customer Knowledge Graph' + '\n\n' + result_unstructured['result']
                    result['postgres_query'] = result_structured['postgres_query']
                    result['postgres_result'] = result_structured['postgres_result']
                    result['chart_response'] = chartResponse(result)
                logger.debug(result)
                # result['result'] = result['result'].replace('./data', 'http://localhost:8001/hybridapp/pdf_view/?filename=./data')
                result['result'] = "\n".join([result_processing(i) for i in result['result'].split("\n")])
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
