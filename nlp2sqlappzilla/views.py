from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import logging
import os
import json
import ast
import time
import re
import numbers
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

import dotenv
dotenv.load_dotenv()
from structured_agentzilla import structured_chain_withouthistory, structured_chain_withhistory

logger = logging.getLogger(__name__)

lcel_chain = structured_chain_withouthistory()
lcel_chain2 = structured_chain_withhistory()

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
        # print("COLUMNS EXTRACTED", columns)
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
    # print("CHART", chart_dict)
    return chart_dict

topic_prompt_template = '''Your task is to generate the topic of below question in 2-4 word with significant meaning:
                    Question: {question}
                    Topic:'''
topic_prompt = PromptTemplate(
    input_variables=["question"], template=topic_prompt_template
)

llm = ChatOpenAI(temperature=0, model="gpt-4")
topic_chain = topic_prompt | llm | StrOutputParser()
@csrf_exempt
def nlp2sqlzilla(request):
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
                output['topic'] = topic_chain.invoke({"question": query})
                output['chart_response'] = {}
                if 'error' in output['postgres_result']:
                    output['postgres_result_error'] = output['postgres_result']
                    output['postgres_result'] = []
                else:
                    # print("OUTPUT TYPE", type(output["postgres_result"]))
                    # print("OUTPUT TYPE", type(eval(output["postgres_result"])))
                    # output['postgres_result'] = eval(output['postgres_result'])
                    # print(output)
                    output['chart_response'] = chartResponse(output)

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

