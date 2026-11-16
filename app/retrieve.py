"""Retrieval helper over persistent ChromaDB."""
import os
import chromadb
from chromadb.utils import embedding_functions

CHROMA_DIR = os.getenv("CHROMA_DIR", "./data/chroma")
EMBED_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
COLLECTION = "medlineplus"


def get_collection():
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=EMBED_MODEL)
    return client.get_collection(COLLECTION, embedding_function=ef)


def retrieve(query: str, k: int = 5) -> list[dict]:
    col = get_collection()
    res = col.query(query_texts=[query], n_results=k)
    out = []
    for i, doc in enumerate(res["documents"][0]):
        out.append({"text": doc, "metadata": res["metadatas"][0][i], "distance": res["distances"][0][i]})
    return out
