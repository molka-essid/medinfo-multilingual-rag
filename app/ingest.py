"""Offline ingestion: download MedlinePlus English health topics, chunk, embed, persist ChromaDB."""
import argparse
import json
import os
from datetime import date, timedelta

import httpx
from bs4 import BeautifulSoup
import chromadb
from chromadb.utils import embedding_functions
from tqdm import tqdm

CHROMA_DIR = os.getenv("CHROMA_DIR", "./data/chroma")
RAW_DIR = os.path.join(os.path.dirname(CHROMA_DIR.rstrip("/\\")), "raw") if False else "./data/raw"
RAW_DIR = os.getenv("RAW_DIR", "./data/raw")
EMBED_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
COLLECTION = "medlineplus"
BASE = "https://medlineplus.gov/xml/mplus_topics_{}.xml"


def candidate_urls() -> list[str]:
    pinned = os.getenv("MEDLINEPLUS_XML_URL", "").strip()
    if pinned:
        return [pinned]
    urls = []
    for i in range(8):
        d = (date.today() - timedelta(days=i)).isoformat()
        urls.append(BASE.format(d))
    return urls


def download(refresh: bool = False) -> tuple[str, str]:
    os.makedirs(RAW_DIR, exist_ok=True)
    for url in candidate_urls():
        fname = url.split("/")[-1]
        path = os.path.join(RAW_DIR, fname)
        if (not refresh) and os.path.exists(path):
            return path, fname
        try:
            r = httpx.get(url, timeout=120, follow_redirects=True)
            r.raise_for_status()
            with open(path, "w", encoding="utf-8") as f:
                f.write(r.text)
            print(f"Downloaded: {fname}")
            return path, fname
        except httpx.HTTPError:
            continue
    raise RuntimeError("Could not download MedlinePlus XML (tried 8 days)")


def clean_text(html: str) -> str:
    soup = BeautifulSoup(html, "lxml")
    return " ".join(soup.get_text(" ").split())


def chunk(text: str, size: int = 800, overlap: int = 100) -> list[str]:
    words = text.split()
    out = []
    i = 0
    while i < len(words):
        out.append(" ".join(words[i:i + size]))
        i += size - overlap
    return [c for c in out if c.strip()]


def build_index(refresh: bool = False) -> dict:
    path, fname = download(refresh=refresh)
    with open(path, encoding="utf-8") as f:
        xml_text = f.read()
    soup = BeautifulSoup(xml_text, "xml")
    topics = [t for t in soup.find_all("health-topic") if t.get("language", "English") == "English"]
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=EMBED_MODEL)
    try:
        client.delete_collection(COLLECTION)
    except Exception:
        pass
    col = client.create_collection(COLLECTION, embedding_function=ef)
    docs, ids, metas = [], [], []
    n = 0
    for t in tqdm(topics, desc="topics"):
        title = t.get("title", "")
        url = t.get("url", "")
        summary = t.find("full-summary") or t.find("short-summary")
        text = clean_text(str(summary)) if summary else ""
        if not text:
            continue
        for c in chunk(text):
            docs.append(c)
            ids.append(f"{title}-{n}")
            metas.append({"title": title, "url": url, "lang": "en"})
            n += 1
    bs = 256
    for i in range(0, len(docs), bs):
        col.add(documents=docs[i:i + bs], ids=ids[i:i + bs], metadatas=metas[i:i + bs])
    # version date from filename
    version = fname.replace("mplus_topics_", "").replace(".xml", "")
    meta = {"source": "MedlinePlus.gov", "version": version, "file": fname, "topics": len(topics), "chunks": len(docs)}
    os.makedirs(CHROMA_DIR, exist_ok=True)
    with open(os.path.join(CHROMA_DIR, "source_meta.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)
    print(f"Indexed {len(docs)} chunks from {len(topics)} topics. Version {version}.")
    return meta


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--refresh", action="store_true")
    args = ap.parse_args()
    build_index(refresh=args.refresh)
