from pathlib import Path
import shutil
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from rag.embeddings import get_embeddings
from rag.retriever import BASE_DIR, CHROMA_DIR, COLLECTION_NAME
# Directory containing medical PDF documents
PDF_DIR = BASE_DIR / "data" / "medical_documents"
def ingest_documents():
    print("\nStarting MediGuide AI document ingestion...\n")
    # Load PDF files

    PDF_DIR.mkdir(parents=True, exist_ok=True)
    pdf_files = sorted(
        file for file in PDF_DIR.iterdir()
        if file.is_file() and file.suffix.lower() == ".pdf"
    )
    if not pdf_files:
        print("No PDF files found!")
        print(f"Please add PDFs to: {PDF_DIR}")
        return
    documents = []

    for pdf_file in pdf_files:
        try:
            print(f"Loading: {pdf_file.name}")
            loader = PyPDFLoader(str(pdf_file))
            pages = loader.load()
            pages = [
                page for page in pages
                if page.page_content.strip()
            ]
            documents.extend(pages)
            print(f"Successfully loaded {len(pages)} pages.")
        except Exception as error:
            print(f"Error loading {pdf_file.name}: {error}")
    if not documents:
        print("No readable PDF content found.")
        return
    # Split documents into smaller chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=120,
        add_start_index=True
    )
    chunks = text_splitter.split_documents(documents)
    if not chunks:
        print("No text chunks generated.")
        return
    print(f"\nTotal pages loaded: {len(documents)}")
    print(f"Total chunks generated: {len(chunks)}")

    # Remove old vector database before rebuilding
    if CHROMA_DIR.exists():
        shutil.rmtree(CHROMA_DIR)

    # Load Hugging Face embedding model
    print("\nLoading Hugging Face embedding model...")
    embeddings = get_embeddings()

    # Initialize ChromaDB
    vectorstore = Chroma(
        collection_name=COLLECTION_NAME,
        persist_directory=str(CHROMA_DIR),
        embedding_function=embeddings
    )
    # Generate unique IDs for chunks
    ids = [
        f"medical-chunk-{index}"
        for index in range(len(chunks))
    ]
    # Store documents and embeddings
    print("Generating embeddings and storing in ChromaDB...")

    vectorstore.add_documents(
        documents=chunks,
        ids=ids
    )
    print("\nDocument ingestion completed successfully!")
    print(f"PDF files processed: {len(pdf_files)}")
    print(f"Pages processed: {len(documents)}")
    print(f"Chunks stored: {len(chunks)}")
    print(f"Database location: {CHROMA_DIR}")
if __name__ == "__main__":
    ingest_documents()