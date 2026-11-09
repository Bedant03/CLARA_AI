
from pathlib import Path

from langchain_chroma import Chroma
from rag.embeddings import get_embeddings
BASE_DIR = Path(__file__).resolve().parent.parent
CHROMA_DIR = BASE_DIR / "chroma_db"
COLLECTION_NAME = "medical_documents"

def get_vectorstore():
    database_file = CHROMA_DIR / "chroma.sqlite3"
    if not database_file.exists():
        raise RuntimeError(
            "Medical knowledge base not found. "
            "Upload and process medical PDFs first."
        )
    return Chroma(
        collection_name=COLLECTION_NAME,
        persist_directory=str(CHROMA_DIR),
        embedding_function=get_embeddings()
    )

def get_retriever():
    vectorstore = get_vectorstore()
    if vectorstore._collection.count() == 0:
        raise RuntimeError(
            "Medical knowledge base is empty. "
            "Upload and process medical PDFs first."
        )
    return vectorstore.as_retriever(
        search_kwargs={"k": 4}
    )