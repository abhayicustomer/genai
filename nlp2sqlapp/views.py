from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import logging
import os
import json
import ast
import time

import dotenv
dotenv.load_dotenv()
from structured_agent import structured_chain_withouthistory, structured_chain_withhistory


host = os.getenv('POSTGRES_HOST')
port = os.getenv('POSTGRES_PORT')
user = os.getenv('POSTGRES_USER')
database = os.getenv('POSTGRES_DATABASE')
password = os.getenv('POSTGRES_PASSWORD')
schemaname = os.getenv('POSTGRES_SCHEMANAME')
tablename = ast.literal_eval(os.getenv('POSTGRES_TABLENAME'))


logger = logging.getLogger(__name__)

lcel_chain = structured_chain_withouthistory()
lcel_chain2 = structured_chain_withhistory()
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

