import os
from langchain_community.document_loaders import PDFMinerLoader, TextLoader

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS, Chroma
import re
from langchain.embeddings import OpenAIEmbeddings

import dotenv
dotenv.load_dotenv()


embeddings = OpenAIEmbeddings()
def text_preprocessing(data):
    try:
        data.page_content = re.sub(r' +',' ', data.page_content)
        data.page_content = re.sub(r'\n+','\n', data.page_content)
        data.page_content = re.sub(r'\n\t\n','\n', data.page_content)
        data.page_content = re.sub(r"’","'", data.page_content)
        data.page_content = re.sub(r"‘","'", data.page_content)
        return data
    except Exception as e:
        print(e)
        return ''
        pass

def pdf_data_fn(files):
    try:
        data = []
        for file in files:
            loaders = PDFMinerLoader(file)
            data.extend([text_preprocessing(loaders.load()[0])])
        return data
    except Exception as e:
        print(e)
        pass

def create_index(fileLoc):
    print("PATH", fileLoc)
    pdfs = [file for sublist in [[os.path.join(i[0], j) for j in i[2]] for i in os.walk(fileLoc)] for file in sublist if '.pdf' in file]
    data = pdf_data_fn(pdfs)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=20)
    docs = text_splitter.split_documents(data)
    vectordb = FAISS.from_documents(docs, embeddings)
    index_loc = fileLoc.replace(r'/data', r'/faiss_index').replace(r'\data', r'\faiss_index')
    print("INDEX PATH", index_loc)
    vectordb.save_local(index_loc)

    # vectordb = FAISS.load_local("faiss_index", embeddings)

    # vectordb = Chroma.from_documents(docs, embeddings, persist_directory="./chroma_db")
    # vectordb = Chroma(persist_directory="./chroma_db", embedding_function=embeddings)

def load_index(fileLoc):
    index_loc = fileLoc.replace(r'/data', r'/faiss_index').replace(r'\data', r'\faiss_index')
    vectordb = FAISS.load_local(index_loc, embeddings)
    return vectordb
