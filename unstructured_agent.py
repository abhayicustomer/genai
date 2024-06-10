from langchain_openai import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings

from langchain.prompts import HumanMessagePromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableParallel, RunnableLambda
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from langchain.vectorstores import Pinecone as PineconeVectorStore
from langchain_core.output_parsers import StrOutputParser

import dotenv
dotenv.load_dotenv()

def unstructured_chain_withhistory():
    llm = ChatOpenAI(temperature=0, model="gpt-4")
    embeddings = OpenAIEmbeddings()
    vectordb = PineconeVectorStore.from_existing_index("talkable-index", embeddings)
    general_system_template_withhistory = r""" 
    Assistant helps the company employees with their company/feedback/reviews/social media related questions, and questions about the company. Be brief in your answers.
    Answer only if the answer is present in the SOURCES below. If answer is not present in the sources don't answer that question.
    Answer ONLY from the facts listed in the list of sources below. If there isn't enough information below, say you don't know. Do not generate answers that don't use the sources below.
    If there are multiple answers, answer in separate sections.
    Customers can be from Glassdoor, g2, linkedin, facebook, twitter, instagram, google, website, press etc.
    online forums, community and social media means data from Facebook, Twitter, Linkedin, glassdoor, g2, google, website, press etc.
    Don't include the duplicate results.
    If the answer can not be generated from the context then respond "I am sorry, currently i am not able to handle this request as it doesn't belongs to the provided data. Please try rephrasing".
    
    Given a chat history and the latest user question which might reference context in the chat history.
    
    Chat History:
    {chat_history}
    
    Use the following format:
    Answer: the final answer to the original input question
    Sources: Use the context and Provide the top 5 sources as well from docs metadata source from where it is able to generate the final answer without sorry for Unstructured dataset in a list format else return []. Do not make any changes in sources, provide the exact source if it is there.  
    Always return the sources in the form of list or array only.
    
    Question: {input}
    
    <context>
    {context}
    </context>
    """

    qa_prompt_withhistory = ChatPromptTemplate.from_messages(
        [HumanMessagePromptTemplate.from_template(general_system_template_withhistory)])

    retriever = vectordb.as_retriever(search_type='similarity_score_threshold',
                                      search_kwargs={"k": 6, "score_threshold": 0.75})

    def source_processing(text):
        if ('contacts unstructured data' in text.lower()) or ('linkedin' in text.lower()):
            link = 'https://www.linkedin.com/company/talkable/'
        elif 'facebook' in text.lower():
            link = 'https://www.facebook.com/talkable/'
        elif '@talkable' in text.lower():
            link = 'https://twitter.com/talkable?lang=en'
        elif 'g2' in text.lower():
            link = 'https://www.g2.com/products/talkable/reviews'
        elif 'glassdoor' in text.lower():
            link = 'https://www.glassdoor.co.in/Overview/Working-at-Talkable-EI_IE998303.11,19.htm'
        elif 'press' in text.lower():
            link = 'https://www.talkable.com/'
        elif 'website' in text.lower():
            link = 'https://www.talkable.com/'
        else:
            link = text
        return link

    def format_docs(docs):
        formatted = [
            f"Source: {source_processing(doc.metadata['source'])}\nContent: {doc.page_content}"
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
            return input["input"]

    rag_chain_chat = (
        RunnablePassthrough.assign(
            context=contextualized_question | retriever | format_docs
        )
        # RunnableParallel({"docs": retriever, "question": RunnablePassthrough()})
        # .assign(context=itemgetter("docs") | RunnableLambda(format_docs))
        .assign(result=qa_prompt_withhistory | llm | StrOutputParser())
        .pick(["question", "result", "docs"])
    )

    return rag_chain_chat
