from functools import lru_cache
from pathlib import Path

from langchain_chroma import Chroma

from rag.embeddings import get_embeddings


BASE_DIR = Path(__file__).resolve().parent.parent

CHROMA_DIR = BASE_DIR / "chroma_db"

COLLECTION_NAME = "medical_documents"


@lru_cache(maxsize=1)
def get_vectorstore() -> Chroma:
    """Open the persistent Chroma collection."""

    database_file = CHROMA_DIR / "chroma.sqlite3"

    if not database_file.exists():

        raise RuntimeError(
            "ChromaDB has not been created. Add PDF files "
            "to data/medical_documents/ and run "
            "`python -m rag.ingest`."
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
            "The medical knowledge base is empty. "
            "Run `python -m rag.ingest`."
        )

    return vectorstore.as_retriever(
        search_kwargs={
            "k": 4
        }
    )