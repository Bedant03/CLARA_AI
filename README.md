MediGuide AI 🩺
MediGuide AI is an educational medical-information chatbot built as a college project. It combines a hosted large language model, retrieval-augmented generation (RAG), a basic warning-sign check, and a nearby healthcare finder.
Medical safety notice: MediGuide AI is a student prototype, not a medical device or a clinically validated triage system. It cannot diagnose, prescribe treatment, or rule out an emergency. Its keyword-based warning check is incomplete and can miss serious conditions. For severe, rapidly worsening, or potentially life-threatening symptoms, seek urgent medical care and contact local emergency services. Do not delay care to use this application.

Features
- Conversational health information: Chat with a hosted LLM through the Groq API.
- Medical document Q&A (RAG): Search text extracted from medical PDF documents and use retrieved passages to ground responses.
- Hugging Face embeddings: Generate document and query embeddings locally with sentence-transformers/all-MiniLM-L6-v2.
- Vector search: Store and retrieve document chunks using ChromaDB.
- LangGraph workflow: Manage the conversation and route requests to the available tools.
- Basic safety check: Detect a small set of emergency-related phrases and display precautionary guidance.
- Nearby healthcare search: Use Geoapify Places API to search mapped hospitals, clinics/practices, and pharmacies near coordinates entered by the user.
- Streamlit interface: Provide a browser-based chat interface.
Technology stack
Component	Technology
Frontend	Streamlit
LLM	Groq API (model configured with GROQ_MODEL)
Embedding model	Hugging Face sentence-transformers/all-MiniLM-L6-v2
Embedding integration	langchain-huggingface
RAG orchestration	LangChain
Agent workflow	LangGraph
Vector database	ChromaDB
PDF loading	PyPDF / PyPDFLoader
Nearby healthcare data	Geoapify Places API


The LLM runs through Groq's hosted API. The Hugging Face embedding model runs locally on the machine/container and is downloaded to its model cache on first use. No Ollama installation is required by this architecture.
Project structure
MediguideLLM/
│
├── app.py                         # Streamlit user interface
├── llm.py                         # Groq LLM configuration
├── state.py                       # LangGraph state definition
├── workflow.py                    # Agent, safety gate, and tool routing
├── requirements.txt               # Python dependencies
├── .env.example                   # Example local environment variables
├── .gitignore                     # Files excluded from Git
│
├── tools/
│   ├── __init__.py
│   ├── medical_rag.py              # Medical document retrieval tool
│   ├── safety.py                   # Basic warning-phrase tool
│   └── healthcare.py               # Geoapify nearby healthcare tool
│
├── rag/
│   ├── __init__.py
│   ├── embeddings.py               # Hugging Face embedding model
│   ├── ingest.py                   # PDF ingestion and ChromaDB creation
│   └── retriever.py                # ChromaDB retriever
│
├── data/
│   └── medical_documents/          # Add trusted medical PDFs here
│
└── chroma_db/                      # Generated vector database (not committed)
Requirements
- Python 3.12 or a Python version supported by the installed packages. Use the same Python version locally and on the deployment platform where possible.
- A Groq API key.
- A Geoapify API key for nearby healthcare search.
- Internet access for Groq requests, Geoapify requests, and the first Hugging Face model download.
- Enough disk space and memory to install and run the Python dependencies and embedding model.
Geoapify is optional for the rest of the chatbot. Without its API key, the LLM and document RAG features can still be used, but nearby healthcare lookup will be unavailable.
Installation (Windows / VS Code)
Open the MediguideLLM project folder in VS Code. Open a terminal in that folder and run:
# Create a virtual environment
python -m venv .venv

# Activate it in PowerShell
.\.venv\Scripts\Activate.ps1

# Upgrade pip and install dependencies
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
If PowerShell blocks environment activation, use Command Prompt:
.venv\Scripts\activate.bat
Check the environment and dependencies:
python --version
python -m pip check
If VS Code does not automatically detect the environment, select this interpreter:
<project-folder>\.venv\Scripts\python.exe
Configure API keys
Local development
1. Copy .env.example and name the copy .env.
2. Add your actual API keys to .env:
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=openai/gpt-oss-120b
GEOAPIFY_API_KEY=your_geoapify_api_key
3. Save the file in the same directory as app.py.
The model name above is an example default. Model availability can change; check the models enabled for your Groq account and update GROQ_MODEL if necessary.
API key safety
- Never commit .env, API keys, access tokens, or passwords to GitHub.
- Keep .env in .gitignore.
- If a key is accidentally exposed in a screenshot, message, or repository, revoke it and create a replacement.
- Restrict API keys in each provider's dashboard when those restrictions are available.
Add medical PDF documents
Place trusted, legally usable, text-searchable PDF files in:
data/medical_documents/
Use reliable sources such as government public-health agencies, recognised health organisations, or documents for which you have permission to use the content. Avoid uploading identifiable patient records or other private health information.

Build the vector database from the project root:
python -m rag.ingest
The ingestion script:
1. Loads PDF files from data/medical_documents/.
2. Splits the extracted text into overlapping chunks.
3. Generates embeddings with all-MiniLM-L6-v2.
4. Rebuilds and writes the ChromaDB collection to chroma_db/.
The first ingestion downloads the Hugging Face model. A Hugging Face access token is not normally required for this public model.

Important: Running python -m rag.ingest rebuilds the local ChromaDB directory. It removes the previous local index before writing a new one. Keep the original PDFs so you can recreate the index.

Scanned PDFs without an embedded text layer may not produce usable text with the current PDF loader. OCR support is not included in this starter implementation.
Run the application
From the project root, with the virtual environment activated:
streamlit run app.py
Streamlit will print a local URL, commonly http://localhost:8501. Open that URL in a browser.
Using MediGuide AI
1. Ask a general health-information question
Ask a question in the chat interface. The model may answer directly or use the medical RAG tool when relevant.
2. Ask a question about your PDFs
After adding PDFs and running ingestion, ask a question that relates to the uploaded documents. The RAG tool retrieves relevant passages from ChromaDB. Answers should be checked against the original PDF and its cited page because retrieval can omit context or return imperfect matches.
3. Find nearby healthcare facilities
Enter latitude and longitude in the Streamlit sidebar, then ask for a nearby hospital, clinic, doctor, or pharmacy. The app uses the coordinates entered by the user; it does not automatically detect device location and must not invent coordinates.

Geoapify results depend on the coverage and accuracy of mapped data. A doctor search is mapped to the Geoapify clinic/practice category and may return practices rather than named individual clinicians. The distance calculated by the project is straight-line distance, not road or driving distance. Verify the facility's details and availability directly before travelling.
4. Test the basic warning check
You can test the prototype with a phrase such as severe chest pain and difficulty breathing. The current pre-LLM gate checks only a small list of exact phrases. It is not comprehensive, and a response that does not trigger the gate does not mean symptoms are safe.
Deploy on Streamlit Community Cloud
1. Push the project source code to a GitHub repository.
2. Confirm that requirements.txt is in the repository root and that the Streamlit entry point is app.py.
3. Do not commit .env or .streamlit/secrets.toml.
4. Create or deploy the app in Streamlit Community Cloud.
5. Select the repository, branch, and app.py as the main file.
6. In the deployment's Advanced settings → Secrets, add valid TOML values:
GROQ_API_KEY = "your_groq_api_key"
GROQ_MODEL = "openai/gpt-oss-120b"
GEOAPIFY_API_KEY = "your_geoapify_api_key"
7. Save and deploy. If you edit secrets later, save the changes and reboot/redeploy the app as needed.
Streamlit Community Cloud exposes root-level secrets as environment variables, so the project's os.getenv() configuration can read these root-level entries. See the Streamlit secrets documentation.
RAG deployment note
The .gitignore excludes chroma_db/, so the generated local vector database is not pushed to GitHub. The current app.py does not automatically run PDF ingestion when a cloud app starts. Therefore, a deployed app will need its ChromaDB collection provisioned separately before the medical RAG feature can work. For a small demonstration, one option is to add the permitted PDF files to the repository and implement a controlled first-run ingestion step in the app; another is to use a separately hosted persistent vector database. Do not assume that the local chroma_db/ folder is available in the cloud deployment.

The Hugging Face model is downloaded on the deployment machine at first use, which may increase initial startup time and memory/disk use.
Troubleshooting
Problem	What to check
GROQ_API_KEY is missing	Confirm .env is in the project root or the root-level Streamlit secret is configured. Restart the app after changing local environment settings.
Groq authentication or model error	Check that the key is valid, the account can access the configured model, and GROQ_MODEL is spelled correctly.
ModuleNotFoundError	Activate .venv, then run python -m pip install -r requirements.txt using that environment's Python.
No module named pip	Run python -m ensurepip --upgrade, then python -m pip install --upgrade pip.
Hugging Face model download fails	Check internet access, disk space, package compatibility, and whether the model is available from Hugging Face.
Medical knowledge base is missing or empty	Add PDFs to data/medical_documents/ and run python -m rag.ingest from the project root.
Geoapify authentication error	Check GEOAPIFY_API_KEY, account status, and API key restrictions.
Geoapify returns no facilities	Try a larger radius or another test location. Coverage varies by area and by map data.
Streamlit Cloud deployment fails	Review the app logs, confirm requirements.txt is correct, and verify Secrets TOML syntax.


For dependency problems, capture the complete terminal error and the output of:
python --version
python -m pip check
Do not share API keys when posting logs or screenshots.
Project limitations and responsible use
- This is an educational prototype, not a clinical decision-support system.
- The safety checker is a small keyword-based demonstration and is not clinically validated.
- The chatbot can produce inaccurate or incomplete information. LLM output must not be treated as a diagnosis or treatment plan.
- RAG answers depend on the quality, currency, and coverage of the PDFs supplied by the project owner.
- Nearby facility data may be incomplete, outdated, or incorrectly categorised.
- The app does not automatically locate users, contact emergency services, book appointments, or verify real-time facility availability.
- Do not submit sensitive personal or identifiable medical information to this demonstration app.
Useful links
- Groq Console
- Groq API documentation
- Hugging Face model: all-MiniLM-L6-v2
- Geoapify Places API documentation
- LangChain documentation
- LangGraph documentation
- Streamlit documentation
License
Add the license that applies to your own source code before publishing the repository. The use of third-party models, APIs, datasets, PDF documents, and map data is also subject to their respective licenses and terms. Do not imply that all project components share one license unless you have verified that.
MediGuide AI — Built as an educational project to demonstrate LLMs, RAG, tool calling, and healthcare information discovery.
