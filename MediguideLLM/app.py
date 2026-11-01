import uuid
import streamlit as st
from langchain_core.messages import HumanMessage
from workflow import graph
# 1. PAGE CONFIGURATION
st.set_page_config(
    page_title="CLARA AI",
    page_icon="🩺",
    layout="centered"
)
# 2. APPLICATION HEADER
st.title("🩺 CLARA AI")
st.caption(
    "Your AI-powered medical information assistant"
)
st.warning(
    """
    CLARA AI provides general health information.
    It is not a substitute for a doctor or emergency service.
    It cannot diagnose conditions or rule out emergencies.
    For severe or rapidly worsening symptoms, seek urgent care.
    """
)
# 3. INITIALIZE SESSION STATE
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
# 4. SIDEBAR
with st.sidebar:
    st.header("📍 Healthcare Finder")
    st.write(
        "Enter your coordinates to find nearby "
        "hospitals, clinics, doctors or pharmacies."
    )
    latitude_text = st.text_input(
        "Latitude",
        placeholder="Example: 20.2961"
    )
    longitude_text = st.text_input(
        "Longitude",
        placeholder="Example: 85.8245"
    )
    latitude = None
    longitude = None
    # Validate coordinates
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
    st.divider()
    st.caption(
        "Coordinates are optional. You can use the "
        "medical information chatbot without them."
    )
    # Clear conversation
    if st.button(
        "🗑️ Clear Conversation",
        use_container_width=True
    ):
        st.session_state.thread_id = str(uuid.uuid4())
        st.session_state.chat_history = []
        st.rerun()
# 5. DISPLAY CHAT HISTORY
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
# 6. CHAT INPUT

user_input = st.chat_input(
    "Describe your symptoms or ask a health question..."
)
# 7. PROCESS USER MESSAGE

if user_input:
    # Display user message
    with st.chat_message("user"):
        st.markdown(user_input)
    # Save user message
    st.session_state.chat_history.append({
        "role": "user",
        "content": user_input
    })
    with st.chat_message("assistant"):
        with st.spinner("MediGuide AI is thinking..."):
            try:
                # Invoke LangGraph workflow
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
                # Get the final assistant message
                final_message = result["messages"][-1]
                content = final_message.content
                # Handle different response formats
                if isinstance(content, str):
                    answer = content
                elif isinstance(content, list):
                    text_parts = []
                    for item in content:
                        if (
                            isinstance(item, dict)
                            and item.get("type") == "text"
                        ):
                            text_parts.append(item.get("text", ""))
                    answer = "\n".join(text_parts)
                    if not answer:
                        answer = str(content)
                else:
                    answer = str(content)
                # Display response
                st.markdown(answer)
                # Save assistant response
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
                # Show technical error during development
                with st.expander("Technical Error Details"):
                    st.code(str(error))
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": answer
                })