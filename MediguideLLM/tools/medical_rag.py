from pathlib import Path
from langchain_core.tools import tool
from rag.retriever import get_retriever

@tool
def medical_rag(query: str) -> str:
    """
    Search the project's medical PDF knowledge base
    for general health information.
    Use this tool for medical knowledge questions
    that should be grounded in the uploaded PDFs.
    """
    try:
        documents = get_retriever().invoke(query)
    except Exception as exc:
        return (
            f"Medical knowledge-base search is unavailable: {exc}"
        )
    if not documents:
        return (
            "No relevant information was found in the "
            "medical knowledge base. Do not invent an answer "
            "from missing documents."
        )
    passages = []
    for index, document in enumerate(documents, start=1):
        source = Path(
            document.metadata.get("source", "Unknown source")
        ).name
        page_index = document.metadata.get("page")
        page_number = (
            page_index + 1
            if isinstance(page_index, int)
            else "unknown"
        )
        passages.append(
            f"Source {index}: {source}, PDF page {page_number}\n"
            f"{document.page_content}"
        )

    return "\n\n---\n\n".join(passages)