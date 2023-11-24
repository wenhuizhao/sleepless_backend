from langchain.embeddings import SentenceTransformerEmbeddings
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from utils import load_docs, split_docs

directory = "./data/content"
loaded_docs = load_docs(directory)
docs = split_docs(loaded_docs)
#embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
embeddings = OpenAIEmbeddings()
persist_directory="./data/chroma_db"
vectordb = Chroma.from_documents(
    documents=docs,
    embeddings=embeddings,
    persist_directory=persist_directory
)