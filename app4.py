import os
from apikey import apikey
from langchain.llms import OpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import CharacterTextSplitter
from langchain.llms import OpenAI

from langchain.document_loaders import TextLoader
from langchain.chains import RetrievalQA


def get_response(prompt):
    os.environ["OPENAI_API_KEY"] = apikey

    loader = TextLoader("./train.txt")
    documents = loader.load()

    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    documents = text_splitter.split_documents(documents)

    embeddings = OpenAIEmbeddings()
    db = Chroma.from_documents(documents, embeddings)
    retriever = db.as_retriever(search_type="similarity", search_kwargs={"k":2})

    llm = OpenAI(temperature=0.9)

    # Create a RetrievalQA
    qa = RetrievalQA.from_chain_type(
        llm=llm, chain_type="stuff", retriever=retriever, return_source_documents=True)

    result = qa({"query": prompt})
    return result


