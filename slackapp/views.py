from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import logging
import json
import time
import os

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain.vectorstores import Pinecone as PineconeVectorStore

from langchain_openai import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings

from langchain.prompts import HumanMessagePromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableParallel, RunnableLambda
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from langchain_core.output_parsers import StrOutputParser
from pinecone import Pinecone, ServerlessSpec
from langchain.output_parsers import ResponseSchema, StructuredOutputParser
from langchain_core.prompts import PromptTemplate


logger = logging.getLogger(__name__)

@csrf_exempt
def products(request):
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
                llm = ChatOpenAI(temperature=0, model="gpt-4o")
                embeddings = OpenAIEmbeddings()
                index_name = 'slack-products'
                pinecone_api_key = os.environ.get("PINECONE_API_KEY")
                pc = Pinecone(api_key = pinecone_api_key)
                vectordb = PineconeVectorStore.from_existing_index(index_name, embeddings)
                general_system_template_withhistory = r""" 
                Assistant helps the people to query on the specific urls in slack channels from below context. Be brief in your answers.
                Answer ONLY from the facts listed in the list of sources below. If there isn't enough information below, say you don't know. Do not generate answers that don't use the sources below.
                Always return the Source url and sub_url of answer if present else return blank string.
                If there are multiple answers, answer in separate sections.
                Don't include the duplicate results.
                ALWAYS return 2-3 follow-up questions from the context after the response
                
                <context>
                {context}
                </context>
                
                Always use the below instructions to return the response in valid Json format:
                {format_instructions}
                
                Question: {question}
                """
                response_schemas = [
                    ResponseSchema(name="question", description="user's question"),
                    ResponseSchema(name="result",
                                description="answer to the user's question without source and don't remove the new line characters like \n for formatting etc."),
                    ResponseSchema(name="source", description="source url and sub_url if present else blank string"),
                    ResponseSchema(name="follow-up",
                                description="the follow up questions in a array or list if present else []", ),
                ]
                output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
                format_instructions = output_parser.get_format_instructions()

                qa_prompt_withhistory = PromptTemplate(
                                template=general_system_template_withhistory,
                                input_variables=["question", "context"],
                                partial_variables={"format_instructions": format_instructions},
                            )

                # qa_prompt_withhistory = ChatPromptTemplate.from_messages(
                #     [HumanMessagePromptTemplate.from_template(general_system_template_withhistory)])

                retriever = vectordb.as_retriever(search_type='similarity_score_threshold',
                                                search_kwargs={"k": 6, "score_threshold": 0.6})

                def format_docs(docs):
                    formatted = [
                        f"Source URL: {doc.metadata['sub_url']}\nContent: {doc.page_content}"
                        for i, doc in enumerate(docs)
                    ]
                    # print(formatted)
                    return "\n\n" + "\n\n".join(formatted)
                    # return "\n\n".join(doc.page_content for doc in docs)

                contextualize_q_system_prompt = """Given a chat history and the latest user question \
                which might reference context in the chat history, formulate a standalone question \
                which can be understood without the chat history. Do NOT answer the question, \
                just reformulate it if needed and otherwise return it as is."""

                contextualize_q_prompt = ChatPromptTemplate.from_messages(
                    [
                        ("system", contextualize_q_system_prompt),
                        MessagesPlaceholder(variable_name="chat_history"),
                        ("human", "{input}"),
                    ]
                )
                contextualize_q_chain = contextualize_q_prompt | llm | StrOutputParser()

                def contextualized_question(input: dict):
                    if input.get("chat_history"):
                        return contextualize_q_chain
                    else:
                        return input["question"]

                rag_chain_chat = (
                    RunnablePassthrough.assign(
                        context=contextualized_question | retriever | format_docs
                    )
                    .assign(result=qa_prompt_withhistory | llm | output_parser)
                    .pick(["result"])
                )

                output = rag_chain_chat.invoke({"question": query, "chat_history": []})
                # output['result'] = output['result'].replace("Answer: ","")
                
                logger.debug(output)
                return JsonResponse({"result": output["result"], "Status": "PASS", "response_time": time.time()-t0})
            else:
                logger.debug('Query can not be blank.')
                return JsonResponse({'result': 'Query can not be blank.', "status": "FAIL", "response_time": time.time()-t0})

    except Exception as e:
        logger.debug('Wrong API request ' + str(e))
        return JsonResponse({'result': 'Wrong API request ' + str(e), "status": "FAIL"})
