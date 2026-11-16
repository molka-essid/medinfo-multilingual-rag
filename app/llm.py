"""LLM provider abstraction with fallback."""
import os
from groq import Groq
import google.generativeai as genai


def _groq(prompt: str) -> str:
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    r = client.chat.completions.create(model="openai/gpt-oss-20b", messages=[{"role": "user", "content": prompt}])
    return r.choices[0].message.content


def _gemini(prompt: str) -> str:
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    m = genai.GenerativeModel("gemini-1.5-flash")
    return m.generate_content(prompt).text


def generate(prompt: str) -> str:
    order = os.getenv("LLM_PROVIDER_ORDER", "groq,gemini").split(",")
    last = None
    for p in order:
        try:
            if p.strip() == "groq":
                return _groq(prompt)
            if p.strip() == "gemini":
                return _gemini(prompt)
        except Exception as e:
            last = e
            continue
    raise RuntimeError(f"All providers failed: {last}")
