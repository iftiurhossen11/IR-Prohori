from langchain_chroma import Chroma

def get_vectorstore():
    return Chroma(
        persist_directory="./chroma_db",
        embedding_function=None
    )

def retrieve(query, k=3):
    vectorstore = get_vectorstore()
    results = vectorstore.similarity_search(query, k=k)
    return results