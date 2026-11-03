# MediGuide AI 🩺

MediGuide AI is an educational medical-information chatbot built with Groq, LangGraph, Hugging Face embeddings, ChromaDB, and Geoapify. It answers general health questions, retrieves information from uploaded medical PDFs, checks a limited set of warning phrases, and searches for nearby healthcare facilities.

> **Disclaimer:** This is a student prototype, not a medical device or clinically validated triage system. It cannot diagnose, prescribe treatment, or rule out an emergency. For severe or rapidly worsening symptoms, seek urgent medical care.

## Features

- Chat with a hosted LLM through the Groq API.
- Ask questions about medical PDFs using retrieval-augmented generation (RAG).
- Create local embeddings with Hugging Face `sentence-transformers/all-MiniLM-L6-v2`.
- Store and search document chunks with ChromaDB.
- Use LangGraph to route requests to the available tools.
- Search for nearby hospitals, clinics/practices, and pharmacies with Geoapify.
- Use a basic warning-phrase check for precautionary safety guidance.

## Tech stack

- **Frontend:** Streamlit
- **LLM:** Groq API (`GROQ_MODEL`)
- **Embeddings:** Hugging Face `all-MiniLM-L6-v2`
- **RAG and tools:** LangChain
- **Agent workflow:** LangGraph
- **Vector database:** ChromaDB
- **Healthcare search:** Geoapify Places API

## Project structure

```text
MediguideLLM/
├── app.py
├── llm.py
├── state.py
├── workflow.py
├── requirements.txt
├── .env.example
├── tools/
│   ├── healthcare.py
│   ├── medical_rag.py
│   └── safety.py
├── rag/
│   ├── embeddings.py
│   ├── ingest.py
│   └── retriever.py
└── data/
    └── medical_documents/
```

## Setup

Use Python and run these commands from the project root (`MediguideLLM`).

### 1. Create and activate a virtual environment (Windows PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 3. Configure API keys

Create a `.env` file in the same folder as `app.py`:

```env
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=openai/gpt-oss-120b
GEOAPIFY_API_KEY=your_geoapify_api_key
```

The Groq key is required for chat. The Geoapify key is required only for nearby healthcare search. Keep `.env` private and do not commit it to GitHub.

## Add medical PDFs

Place trusted, text-searchable PDF files in:

```text
data/medical_documents/
```

Build or rebuild the ChromaDB index:

```powershell
python -m rag.ingest
```

The first run downloads the Hugging Face embedding model. Re-running ingestion rebuilds the local vector database, so keep your source PDFs.

## Run the app

```powershell
streamlit run app.py
```

Enter latitude and longitude in the sidebar when using the nearby healthcare finder. The app does not automatically detect the user's location. Geoapify results depend on available map data, and the displayed distance is straight-line distance, not driving distance.

## Deploy on Streamlit Community Cloud

1. Push the project to GitHub. Do not commit `.env`, `.venv/`, or private API keys.
2. Create an app at [Streamlit Community Cloud](https://share.streamlit.io/) and select the repository and `app.py`.
3. Add the following under **Advanced settings → Secrets**, using your real keys:

```toml
GROQ_API_KEY = "your_groq_api_key"
GROQ_MODEL = "openai/gpt-oss-120b"
GEOAPIFY_API_KEY = "your_geoapify_api_key"
```

**RAG deployment note:** The generated `chroma_db/` folder is excluded from Git. The cloud app therefore needs its ChromaDB index created or provisioned separately before PDF question-answering will work. The current app does not automatically ingest PDFs on cloud startup.

## Limitations

- The warning-phrase checker is incomplete and not clinically validated; it can miss emergencies.
- LLM responses and retrieved passages may be inaccurate or incomplete. Verify medical information with a qualified professional and the original source documents.
- Nearby facility information depends on Geoapify/OpenStreetMap data and may be incomplete or outdated.
- Do not enter identifiable patient records or other sensitive medical information into this prototype.
