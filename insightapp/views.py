from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from langchain_openai import ChatOpenAI
from langchain.agents import (AgentExecutor, Tool, ZeroShotAgent,
                              initialize_agent, load_tools)
from langchain_experimental.tools import PythonREPLTool

import logging
import json
import time
import dotenv
dotenv.load_dotenv()

logger = logging.getLogger(__name__)

llm = ChatOpenAI(temperature=0, model="gpt-4")

tools = [PythonREPLTool()]
# Standard prefix
prefix = "Fulfill the following request as best you can. You have access to the following tools:"

# Remind the agent of the Data tool, and what types of input it expects
suffix = (
    ''' "You are a data analyst and chart design expert helping users to build charts."

        "Show a {plot} graph visualizing the answer to the following question:\n"
        "Always try to plot the graph in such a manner that its values can be easily readable."
        "{input}"
        "{agent_scratchpad}"
        "ALWAYS save this plots into a .png file with best name according to query."
        "ALWAYS return saved filename in response with keyname 'filename' and insights summary with 'Summary'"        
'''
)

# The agent's prompt is built with the list of tools, prefix, suffix, and input variables
prompt = ZeroShotAgent.create_prompt(
    tools, prefix=prefix, suffix=suffix, input_variables=["input", "plot", "agent_scratchpad"]
)

from langchain import LLMChain

# Set up the llm_chain
llm_chain = LLMChain(llm=llm, prompt=prompt, verbose=False)

# Specify the tools the agent may use
tool_names = [tool.name for tool in tools]
agent = ZeroShotAgent(llm_chain=llm_chain, allowed_tools=tool_names)

# Create the AgentExecutor
agent_executor = AgentExecutor.from_agent_and_tools(
    agent=agent, tools=tools, verbose=False
)

@csrf_exempt
def insight(request):
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
                result = agent_executor.run({"input": query, "plot": "bar"})
                logger.debug(result)
                return JsonResponse({"result": result, "Status": "PASS", "response_time": time.time()-t0})
            else:
                logger.debug('Query can not be blank.')
                return JsonResponse({'result': 'Query can not be blank.', "status": "FAIL", "response_time": time.time()-t0})

    except Exception as e:
        logger.debug('Wrong API request ' + str(e))
        return JsonResponse({'result': 'Wrong API request ' + str(e), "status": "FAIL"})

