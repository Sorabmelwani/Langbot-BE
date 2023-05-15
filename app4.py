import os
from apikey import apikey
from langchain.llms import OpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import CharacterTextSplitter
from langchain.llms import OpenAI

from langchain.document_loaders import TextLoader
from langchain.chains import RetrievalQA,ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory


def get_response(prompt, conversation):
    print("none type",conversation)
    os.environ["OPENAI_API_KEY"] = apikey

    loader = TextLoader("./train.txt")
    documents = loader.load()

    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    documents = text_splitter.split_documents(documents)

    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

    embeddings = OpenAIEmbeddings()
    db = Chroma.from_documents(documents, embeddings)
    retriever = db.as_retriever(search_type="similarity", search_kwargs={"k":2})

    llm = OpenAI(temperature=0.9)

    chat_history = []

    if conversation:
        for i in range(1, len(conversation)):
            if conversation[i]["role"] == "ai" and conversation[i-1]["role"] == "user":
                query = conversation[i-1]["content"]
                answer = conversation[i]["content"]
                chat_history.append((query, answer))

    print(chat_history)

    # Create a RetrievalQA
    qa = ConversationalRetrievalChain.from_llm(
        llm=llm, retriever=retriever, return_source_documents=False)

    result = qa({"question": prompt,'chat_history': chat_history})
    print('result', result)
    return result


