"""FastAPI app with /ask endpoint and static frontend."""
import os
import time
from collections import defaultdict
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from app.graph import build_graph

app = FastAPI(title="medinfo-multilingual-rag")
graph = build_graph()

# simple rate limit: 10 req/min per IP
_buckets = defaultdict(list)
LIMIT = 10
WINDOW = 60


def rate_limit(ip: str):
    now = time.time()
    b = [t for t in _buckets[ip] if now - t < WINDOW]
    if len(b) >= LIMIT:
        raise HTTPException(429, "rate limit exceeded")
    b.append(now)
    _buckets[ip] = b


class AskReq(BaseModel):
    question: str
    language: str | None = None


@app.post("/ask")
def ask(req: AskReq, request: Request):
    rate_limit(request.client.host)
    q = req.question.strip()
    if not q or len(q) > 500:
        raise HTTPException(400, "invalid question")
    state = {"question": q}
    if req.language:
        state["language"] = req.language
    res = graph.invoke(state)
    return {"answer": res.get("answer", ""), "language": res.get("language"), "citations": res.get("docs", [])}


@app.get("/", response_class=HTMLResponse)
def index():
    return FileResponse(os.path.join("static", "index.html"))


os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")
