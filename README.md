# medinfo-multilingual-rag

Multilingual (Arabic, French, English) health INFORMATION assistant using RAG, deployed on Azure.

> General information only. Not medical advice. Not a substitute for professional care.

## Disclaimer
This project provides general health information grounded in trusted public sources. It does not diagnose, prescribe, or give dosage advice. In an emergency, contact local emergency services immediately.

## Status
Phase 1: ingestion (in progress).

## Corpus
See docs/CORPUS.md. MedlinePlus content (public domain US gov). Rebuild index: `python -m app.ingest`.

## License
MIT (code). Corpus attribution: see docs/CORPUS.md (to be added).


## Evaluation Results

| Lang | Recall@5 | Refusal/Escalation cases |
|---|---|---|
| en | 14/14 | 6/6 |
| fr | 14/14 | 6/6 |
| ar | 0/14 | 6/6 |
