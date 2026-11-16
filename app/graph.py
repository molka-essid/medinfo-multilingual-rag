"""LangGraph pipeline."""
from langgraph.graph import StateGraph, END
from app.state import State
from app.lang import detect_language
from app.safety import safety_check
from app.retrieve import retrieve
from app.llm import generate


def node_lang(state: State) -> State:
    state["language"] = detect_language(state["question"])
    return state


def node_safety(state: State) -> State:
    state["safety"] = safety_check(state["question"])
    return state


def node_retrieve(state: State) -> State:
    if state.get("safety") != "ok":
        state["docs"] = []
        return state
    state["docs"] = retrieve(state["question"], k=5)
    return state


def node_generate(state: State) -> State:
    if state.get("safety") != "ok":
        state["answer"] = ""
        return state
    lang = state.get("language", "en")
    docs = state.get("docs", [])
    ctx = "\n\n".join(f"[{i+1}] {d['text']} (Source: {d['metadata'].get('title')})" for i, d in enumerate(docs))
    prompt = (
        f"Answer in language code '{lang}'. Use ONLY the provided context. "
        "Write a well-structured, scannable answer in Markdown: a short summary, "
        "then bullet points or a table for causes/symptoms, then 'When to seek care'. "
        "Include citations like [1]. If unsupported, say you don't know. "
        "General information only, no diagnosis/treatment/dosage.\n\n"
        f"Context:\n{ctx}\n\nQuestion: {state['question']}"
    )
    state["answer"] = generate(prompt)
    return state


def node_faith(state: State) -> State:
    if state.get("safety") != "ok":
        state["faithful"] = True
        return state
    ans = state.get("answer", "")
    state["faithful"] = (len(state.get("docs", [])) > 0) and ("[" in ans)
    return state


def node_respond(state: State) -> State:
    lang = state.get("language", "en")
    if state.get("safety") == "emergency":
        msgs = {"en": "This sounds like an emergency. Contact local emergency services or a doctor immediately.",
                "ar": "يبدو أن هذا وضع طارئ. اتصل بخدمات الطوارئ المحلية أو بطبيب فورًا.",
                "fr": "Cela semble être une urgence. Contactez les services d'urgence locaux ou un médecin immédiatement."}
        state["answer"] = msgs.get(lang, msgs["en"])
    elif state.get("safety") == "refusal":
        msgs = {"en": "I can't diagnose or prescribe. Here's general information instead; consult a healthcare professional.",
                "ar": "لا يمكنني التشخيص أو وصف العلاج. إليك معلومات عامة؛ استشر متخصصًا.",
                "fr": "Je ne peux pas diagnostiquer ni prescrire. Voici des informations générales ; consultez un professionnel."}
        state["answer"] = msgs.get(lang, msgs["en"])
    elif not state.get("faithful", True):
        msgs = {"en": "I couldn't find supporting sources; I won't guess.",
                "ar": "لم أجد مصادر داعمة؛ لن أخمن.",
                "fr": "Je n'ai pas trouvé de sources ; je ne devinerai pas."}
        state["answer"] = msgs.get(lang, msgs["en"])
    return state


def build_graph():
    g = StateGraph(State)
    g.add_node("language_detect", node_lang)
    g.add_node("safety_check", node_safety)
    g.add_node("retrieve", node_retrieve)
    g.add_node("generate_with_citations", node_generate)
    g.add_node("faithfulness_check", node_faith)
    g.add_node("respond_or_safe_refusal", node_respond)
    g.set_entry_point("language_detect")
    g.add_edge("language_detect", "safety_check")
    g.add_edge("safety_check", "retrieve")
    g.add_edge("retrieve", "generate_with_citations")
    g.add_edge("generate_with_citations", "faithfulness_check")
    g.add_edge("faithfulness_check", "respond_or_safe_refusal")
    g.add_edge("respond_or_safe_refusal", END)
    return g.compile()
