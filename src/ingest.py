import os
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma

def load_documents(folder_path):
    documents = []
    for file in os.listdir(folder_path):
        path = os.path.join(folder_path, file)
        if file.endswith(".pdf"):
            loader = PyPDFLoader(path)
        elif file.endswith(".txt"):
            loader = TextLoader(path, encoding="utf-8")
        else:
            continue
        documents.extend(loader.load())
        print(f"Loaded: {file}")
    return documents

def split_documents(documents):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    chunks = splitter.split_documents(documents)
    print(f"Total chunks: {len(chunks)}")
    return chunks

def create_vector_store(chunks):
    vectorstore = Chroma.from_documents(
        documents=chunks,
        persist_directory="./chroma_db"
    )
    print("Vector store created and saved.")
    return vectorstore

if __name__ == "__main__":
    print("Starting document ingestion...")
    docs = load_documents("./data/documents")
    chunks = split_documents(docs)
    create_vector_store(chunks)
    print("Ingestion complete.")