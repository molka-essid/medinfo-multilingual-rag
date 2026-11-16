"""Shared state for the LangGraph pipeline."""
from typing import TypedDict, List, Optional


class State(TypedDict, total=False):
    question: str
    language: str  # en/ar/fr
    safety: str  # ok/emergency/refusal
    docs: List[dict]
    answer: str
    citations: List[str]
    faithful: bool
