from langchain_core.tools import tool


EMERGENCY_PATTERNS = [
    "severe chest pain",
    "chest pain and difficulty breathing",
    "difficulty breathing",
    "severe difficulty breathing",
    "cannot breathe",
    "can't breathe",
    "not breathing",
    "unconscious",
    "loss of consciousness",
    "severe bleeding",
    "vomiting blood",
    "face drooping",
    "sudden weakness on one side",
    "stroke symptoms",
]


def detect_red_flags(text: str) -> list[str]:
    """Find listed warning phrases in the supplied text."""

    lowered_text = text.lower()

    return [
        phrase
        for phrase in EMERGENCY_PATTERNS
        if phrase in lowered_text
    ]


@tool
def safety_triage(symptoms: list[str]) -> dict:
    """
    Check symptoms against a limited list of emergency
    warning phrases.

    This prototype cannot diagnose, determine that symptoms
    are safe, or rule out an emergency.
    """

    warning_signs = detect_red_flags(
        " ".join(symptoms)
    )

    if warning_signs:

        return {
            "status": "urgent_evaluation",

            "warning_signs": warning_signs,

            "recommendation": (
                "Seek emergency medical evaluation now. "
                "Contact your local emergency service if "
                "symptoms are severe. Do not delay care."
            ),
        }

    return {
        "status": "no_listed_warning_phrase_detected",

        "warning_signs": [],

        "recommendation": (
            "This limited keyword check cannot determine "
            "whether symptoms are safe and cannot rule out "
            "an emergency."
        ),
    }