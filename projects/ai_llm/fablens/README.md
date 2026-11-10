---
title: FabLens
emoji: 🔬
colorFrom: indigo
colorTo: blue
sdk: gradio
app_file: app.py
pinned: false
---

# FabLens — Semiconductor Yield RAG Assistant

Ask plain-language questions about semiconductor manufacturing — yield models, EUV lithography, overlay/CD metrology, defect inspection, wafer maps, SPC/FDC, equipment health, and AI in fabs — and get answers that cite their sources.

## How it works

```
docs (MD/PDF) → chunk (600 chars, 100 overlap)
             → BM25 keyword index + FAISS index (all-MiniLM-L6-v2 embeddings)
             → reciprocal rank fusion (hybrid retrieval, top 4)
             → Claude (claude-haiku-4-5) answers only from retrieved context, with [n] citations
```

- **Hybrid retrieval**: BM25 catches exact terms (Cpk, WM-811K); dense embeddings catch meaning. Results are merged with reciprocal rank fusion.
- **Grounded answers**: the LLM is told to answer only from retrieved context and say "I don't know" otherwise.
- **Works without an API key**: if `ANTHROPIC_API_KEY` is not set, it returns the most relevant passages instead of a generated answer.
- **Bring your own docs**: upload PDFs or notes in the UI to extend the knowledge base.

## Evaluation

`eval.py` runs a 20-question retrieval test set covering all 8 topic documents and reports hit@4 and MRR.

```
python eval.py
```

## Run locally

```
pip install -r requirements.txt
export ANTHROPIC_API_KEY=...   # optional
python app.py
```

## Deploy to Hugging Face Spaces

1. Create a new Space (SDK: Gradio).
2. Push this folder to the Space repo.
3. In Space settings → Secrets, add `ANTHROPIC_API_KEY`.

## Tech
Python · LangChain · FAISS · BM25 · sentence-transformers · Claude API · Gradio · Hugging Face Spaces

Knowledge base documents in `docs/` are original summaries written for this project.
