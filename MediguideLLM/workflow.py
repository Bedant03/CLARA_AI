from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    SystemMessage
)

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph
from langgraph.prebuilt import ToolNode
from llm import llm
from state import MedicalState
from tools.healthcare import find_nearby_healthcare
from tools.medical_rag import medical_rag
from tools.safety import (
    detect_red_flags,
    safety_triage
)
TOOLS = [
    medical_rag,
    safety_triage,
    find_nearby_healthcare
]
llm_with_tools = llm.bind_tools(TOOLS)
SYSTEM_PROMPT = """
You are CLARA AI, a medical information assistant
for an educational prototype.

GENERAL BEHAVIOUR

- Be friendly, clear, and concise.
- Ask one or two relevant follow-up questions when
  the user's request lacks context.
- Use the conversation history.
- Do not repeatedly ask for details already supplied.
- Do not claim to diagnose or prescribe.
- Do not replace a qualified healthcare professional.
- Do not recommend starting, stopping, or changing
  prescription medicines.

MEDICAL KNOWLEDGE / RAG

- Use the medical_rag tool for questions that should
  be answered from the project's medical PDFs.
- Ground document-based answers in retrieved passages.
- Cite the PDF filename and page number when using
  retrieved material.
- If the knowledge base has no relevant information,
  say so. Do not invent sources.
- General information is not a substitute for
  professional assessment.

SAFETY

- Use safety_triage when an initial limited warning-sign
  check is appropriate.
- The safety tool is not clinically validated and
  cannot rule out an emergency.
- For severe, rapidly worsening, or potentially
  life-threatening symptoms, tell the user to seek
  urgent medical attention and contact local
  emergency services.
- Do not delay care.

NEARBY HEALTHCARE

- Use find_nearby_healthcare when the user asks to
  locate a hospital, doctor, clinic, or pharmacy.
- Use only the exact latitude and longitude supplied
  in the application context.
- Never guess or fabricate coordinates.
- If coordinates are unavailable, ask the user to
  enter them in the location panel.
- Present only facilities returned by the tool.
- Do not invent ratings, opening status, phone numbers,
  or addresses.
- Explain that the distance shown is straight-line
  distance, not driving distance.

You are an informational assistant, not a doctor.
"""
def safety_gate(state: MedicalState) -> dict:
    """
    Basic phrase check before the LLM responds.

    This is not a medical diagnosis or a clinically
    validated emergency detection system.
    """
    messages = state.get("messages", [])
    latest_user_message = next(
        (
            message
            for message in reversed(messages)
            if isinstance(message, HumanMessage)
        ),
        None
    )
    if (
        latest_user_message is None
        or not isinstance(latest_user_message.content, str)
    ):
        return {
            "urgent": False
        }
    warning_signs = detect_red_flags(
        latest_user_message.content
    )
    if warning_signs:
        return {
            "urgent": True,
            "messages": [
                AIMessage(
                    content=(
                        "Your message contains wording that may "
                        "indicate a serious symptom. Please seek "
                        "urgent medical evaluation now. Contact "
                        "your local emergency service if symptoms "
                        "are severe or life-threatening. Do not "
                        "delay care to continue chatting. This is "
                        "a precautionary message, not a diagnosis. "
                        "The project's keyword check is limited "
                        "and is not clinically validated."
                    )
                )
            ]
        }
    return {
        "urgent": False
    }
def agent_node(state: MedicalState) -> dict:
    """Send the conversation and tool definitions to Groq."""
    latitude = state.get("latitude")
    longitude = state.get("longitude")
    if latitude is not None and longitude is not None:
        location_context = (
            "The application supplied these user-entered "
            "coordinates: "
            f"latitude={latitude}, longitude={longitude}. "
            "If you call the nearby healthcare tool, use "
            "these exact numbers."
        )
    else:
        location_context = (
            "No user coordinates were supplied. If nearby "
            "healthcare is requested, ask the user to enter "
            "latitude and longitude in the location panel. "
            "Do not call the healthcare finder without coordinates."
        )
    system_message = SystemMessage(
        content=SYSTEM_PROMPT + "\n\n" + location_context
    )
    response = llm_with_tools.invoke(
        [
            system_message,
            *state["messages"]
        ]
    )
    return {
        "messages": [response]
    }

def route_after_safety(state: MedicalState) -> str:
    if state.get("urgent", False):
        return "end"
    return "agent"

def route_after_agent(state: MedicalState) -> str:
    last_message = state["messages"][-1]

    if getattr(last_message, "tool_calls", None):
        return "tools"
    return "end"
# Build the LangGraph workflow.
builder = StateGraph(MedicalState)
builder.add_node(
    "safety_gate",
    safety_gate
)
builder.add_node(
    "agent",
    agent_node
)
builder.add_node(
    "tools",
    ToolNode(TOOLS)
)
builder.set_entry_point(
    "safety_gate"
)
builder.add_conditional_edges(
    "safety_gate",
    route_after_safety,
    {
        "agent": "agent",
        "end": END
    }
)
builder.add_conditional_edges(
    "agent",
    route_after_agent,
    {
        "tools": "tools",
        "end": END
    }
)
builder.add_edge(
    "tools",
    "agent"
)
# Memory is stored in this Python process
# and separated by thread_id.
checkpointer = MemorySaver()
graph = builder.compile(
    checkpointer=checkpointer
)