from app.state import State
from app.lang import detect_language
from app.safety import safety_check
from app.graph import node_faith, node_respond


def test_lang():
    assert detect_language("What is diabetes?") == "en"


def test_safety_emergency():
    assert safety_check("I have chest pain") == "emergency"


def test_safety_refusal():
    assert safety_check("Do I have diabetes?") == "refusal"


def test_faith_blocks():
    s: State = {"question": "q", "safety": "ok", "docs": [], "answer": "x"}
    node_faith(s)
    assert s["faithful"] is False


def test_respond_emergency():
    s: State = {"question": "q", "language": "en", "safety": "emergency"}
    node_respond(s)
    assert "emergency" in s["answer"].lower()
