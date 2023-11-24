import os
from dotenv import load_dotenv
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import SentenceTransformerEmbeddings
from langchain.memory import ConversationBufferMemory
from langchain.vectorstores import Chroma

api_key = os.getenv("OPENAI_API_KEY")
os.environ["OPENAI_API_KEY"] = api_key
GPT_MODEL="gpt-3.5-turbo"

def get_vectordb():    
    persist_directory = "./data/chroma_db"
    embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    vectordb = Chroma(persist_directory=persist_directory, embedding_function=embeddings)
    #retriever = vectordb.as_retriever()
    return vectordb

def get_qa_chain():
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    vectordb = get_vectordb()
    qa_chain = ConversationalRetrievalChain.from_llm(
        ChatOpenAI(temperature=0.8, model=GPT_MODEL),
        vectordb.as_retriever(search_kwargs={"k": 3}),
        condense_question_llm=ChatOpenAI(temperature=0, model=GPT_MODEL),
        memory=memory
    )
    return qa_chain