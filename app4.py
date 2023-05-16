import os
from apikey import apikey
from langchain.llms import OpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import CharacterTextSplitter
from langchain.llms import OpenAI

from langchain.document_loaders import TextLoader,CSVLoader
from langchain.chains import RetrievalQA,ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory


def get_response(prompt, conversation):
    os.environ["OPENAI_API_KEY"] = apikey

    loader = TextLoader("./train.txt")
    documents = loader.load()

    product_loader = CSVLoader("./products.csv")
    product_documents = product_loader.load()

    documentsCollection = documents + product_documents

    text_splitter = CharacterTextSplitter(chunk_size=512, chunk_overlap=0)
    documents = text_splitter.split_documents(documentsCollection)


    embeddings = OpenAIEmbeddings()
    db = Chroma.from_documents(documents, embeddings)
    retriever = db.as_retriever(search_type="similarity", search_kwargs={"k":2})

    llm = OpenAI(temperature=0.4)

    chat_history = []

    if conversation:
        for i in range(1, len(conversation)):
            if conversation[i]["role"] == "ai" and conversation[i-1]["role"] == "user":
                query = conversation[i-1]["content"]
                answer = conversation[i]["content"]
                chat_history.append((query, answer))


    # Create a RetrievalQA
    qa = ConversationalRetrievalChain.from_llm(
        llm=llm, retriever=retriever, return_source_documents=False)

    result = qa({"question": prompt,'chat_history': chat_history})
    return result


