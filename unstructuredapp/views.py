from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import logging
import os
import json
import ast
import time

from unstructured_agent import unstructured_chain_withhistory

logger = logging.getLogger(__name__)

rag_chain_chat = unstructured_chain_withhistory()
@csrf_exempt
def rag(request):
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
                output = rag_chain_chat.invoke({"input": query, "chat_history": []})
                output['result'] = output['result'].replace("Final Answer: ","")
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

