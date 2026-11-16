"""Safety checks."""
import re

EMERGENCY = ["chest pain", "overdose", "suicid", "severe bleeding", "can't breathe", "stroke", "heart attack"]
DIAGNOSIS = ["do i have", "diagnose", "prescribe", "dosage", "how much should i take", "treatment for me"]


def safety_check(question: str) -> str:
    q = question.lower()
    if any(k in q for k in EMERGENCY):
        return "emergency"
    if any(k in q for k in DIAGNOSIS):
        return "refusal"
    return "ok"
