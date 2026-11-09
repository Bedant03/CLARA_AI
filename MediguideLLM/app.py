import uuid
from pathlib import Path
import streamlit as st
from langchain_core.messages import HumanMessage
from workflow import graph
from rag.ingest import ingest_documents, PDF_DIR

# PAGE CONFIGURATION
st.set_page_config(
    page_title="CLARA AI",
    page_icon="🩺",
    layout="centered"
)

# HEADER
st.title("🩺 CLARA AI")
st.caption(
    "Your AI-powered medical information assistant"
)
st.warning(
    "CLARA AI provides general health information. "
    "It cannot diagnose conditions or rule out emergencies. "
    "For severe or rapidly worsening symptoms, seek urgent care."
)

# MEDICAL DOCUMENT UPLOAD
with st.expander("📚 Upload Medical Documents"):
    st.write(
        "Upload medical PDF documents to add information "
        "to the MediGuide AI knowledge base."
    )
    with st.form("document_upload_form"):
        uploaded_files = st.file_uploader(
            "Choose medical PDF documents",
            type=["pdf"],
            accept_multiple_files=True
        )
        process_documents = st.form_submit_button(
            "Upload and Process Documents"
        )
    if process_documents:
        if not uploaded_files:
            st.warning("Please upload at least one PDF.")
        else:
            try:
                PDF_DIR.mkdir(
                    parents=True,
                    exist_ok=True
                )
                saved_files = []
                for uploaded_file in uploaded_files:
                    filename = Path(uploaded_file.name).name
                    file_path = PDF_DIR / filename
                    file_path.write_bytes(
                        uploaded_file.getvalue()
                    )
                    saved_files.append(filename)
                with st.spinner(
                    "Processing documents and generating embeddings..."
                ):
                    ingest_documents()
                st.success(
                    f"Successfully processed {len(saved_files)} PDF file(s)!"
                )
                for filename in saved_files:
                    st.write(f"📄 {filename}")
            except Exception as error:
                st.error("Document processing failed.")
                with st.expander("Technical Error Details"):
                    st.code(str(error))

# SESSION STATE
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# SIDEBAR
with st.sidebar:
    st.header("📍 Healthcare Finder")
    st.write(
        "Enter your coordinates to find nearby "
        "hospitals, doctors, clinics or pharmacies."
    )
    latitude_text = st.text_input(
        "Latitude",
        placeholder="Example: 20.3537"
    )
    longitude_text = st.text_input(
        "Longitude",
        placeholder="Example: 85.8187"
    )

    latitude = None
    longitude = None
    coordinates_valid = True
    if latitude_text.strip() or longitude_text.strip():
        try:
            if not latitude_text.strip() or not longitude_text.strip():
                raise ValueError(
                    "Please enter both latitude and longitude."
                )
            latitude = float(latitude_text)
            longitude = float(longitude_text)
            if not -90 <= latitude <= 90:
                raise ValueError(
                    "Latitude must be between -90 and 90."
                )
            if not -180 <= longitude <= 180:
                raise ValueError(
                    "Longitude must be between -180 and 180."
                )
        except ValueError as error:
            st.error(str(error))
            latitude = None
            longitude = None
            coordinates_valid = False
    st.caption(
        "Coordinates are optional. You can use the medical "
        "chatbot without entering them."
    )
    st.divider()
    if st.button(
        "🗑️ Clear Conversation",
        use_container_width=True
    ):
        st.session_state.thread_id = str(uuid.uuid4())
        st.session_state.chat_history = []
        st.rerun()

# DISPLAY CHAT HISTORY
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# CHAT INPUT
user_input = st.chat_input(
    "Describe your symptoms or ask a health question..."
)

# PROCESS USER MESSAGE
if user_input:
    if not coordinates_valid:
        st.error(
            "Please correct the latitude and longitude before sending your message."
        )
    else:
        with st.chat_message("user"):
            st.markdown(user_input)
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_input
        })
        with st.chat_message("assistant"):
            with st.spinner("MediGuide AI is thinking..."):
                try:
                    result = graph.invoke(
                        {
                            "messages": [
                                HumanMessage(content=user_input)
                            ],
                            "latitude": latitude,
                            "longitude": longitude,
                            "urgent": False
                        },
                        config={
                            "configurable": {
                                "thread_id": st.session_state.thread_id

                            }
                        }
                    )
                    final_message = result["messages"][-1]
                    content = final_message.content
                    if isinstance(content, str):
                        answer = content
                    elif isinstance(content, list):
                        text_parts = [
                            item.get("text", "")
                            for item in content
                            if (
                                isinstance(item, dict)
                                and item.get("type") == "text"
                            )
                        ]
                        answer = "\n".join(text_parts)
                        if not answer:
                            answer = str(content)
                    else:
                        answer = str(content)
                    st.markdown(answer)
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": answer
                    })
                except Exception as error:
                    answer = (
                        "Sorry, something went wrong while "
                        "processing your request. Please check "
                        "your API configuration and application setup."
                    )
                    st.error(answer)
                    with st.expander("Technical Error Details"):
                        st.code(str(error))
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": answer
                    })
