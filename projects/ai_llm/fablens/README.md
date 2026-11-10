---
title: FabLens
emoji: 🔬
colorFrom: indigo
colorTo: blue
sdk: gradio
app_file: app.py
pinned: false
---

# FabLens — Semiconductor Yield RAG Assistant + Agent

Ask plain-language questions about semiconductor manufacturing — yield models, EUV lithography, overlay/CD metrology, defect inspection, wafer maps, SPC/FDC, equipment health, and AI in fabs — and get answers that cite their sources. An agent mode adds calculators for yield, dies per wafer, and Cpk.

## How it works

```
docs (MD/PDF) → chunk (600 chars, 100 overlap)
             → BM25 keyword index + FAISS index (all-MiniLM-L6-v2 embeddings)
             → reciprocal rank fusion (hybrid retrieval, top 4)
             → LLM (Claude claude-haiku-4-5 or Mistral mistral-small-latest) answers only from retrieved context, with citations
```

**Agent mode** (LangChain tool-calling agent) picks between four tools:

| Tool | What it does |
|---|---|
| `search_docs` | Hybrid search over the knowledge base |
| `yield_calculator` | Die yield with Poisson, Murphy, or negative binomial (Stapper) models |
| `dies_per_wafer` | Gross dies per wafer from wafer diameter and die area |
| `cpk_calculator` | Process capability vs. the 1.33 target |

The agent is told never to do the math itself — numbers always come from a tested tool.

## Design choices

- **Hybrid retrieval**: BM25 catches exact terms (Cpk, WM-811K); embeddings catch meaning; merged with reciprocal rank fusion.
- **Grounded answers**: the LLM answers only from retrieved context and says "I don't know" otherwise.
- **Swappable LLM provider**: set `MISTRAL_API_KEY` or `ANTHROPIC_API_KEY` (or force one with `LLM_PROVIDER=mistral|anthropic`).
- **Works without an API key**: RAG mode falls back to showing the most relevant passages.
- **Bring your own docs**: upload PDFs or notes in the UI.

## Governance: query logging

Every RAG and agent query is appended to `logs/queries.jsonl`: timestamp, mode, provider, model, retrieval mode, sources, tools used, answer length, latency.

- `FABLENS_LOG=/path/file.jsonl` changes the location; `FABLENS_LOG=off` disables it.
- `FABLENS_LOG_REDACT=1` stores a hash instead of the question text, for sensitive data.

## Testing and CI

```
python -m pytest -q tests        # tool math, agent wiring (scripted fake LLM), retrieval gate
python eval.py --min-hit 0.85    # 20-question retrieval eval; exits 1 below the threshold
```

GitHub Actions (`.github/workflows/fablens-ci.yml` at the repo root) runs both on every change to this folder, so a change that hurts retrieval accuracy fails the build.

## Run locally

```
pip install -r requirements.txt
export MISTRAL_API_KEY=...     # or ANTHROPIC_API_KEY (optional for RAG, required for the agent)
python app.py
```

## Roadmap: deploy to Hugging Face Spaces

Next step is a public demo on Hugging Face Spaces. The YAML header at the top of this README is already the Space config.

1. Create a new Space (SDK: Gradio).
2. Push this folder to the Space repo.
3. In Space settings → Secrets, add `MISTRAL_API_KEY` or `ANTHROPIC_API_KEY`.

Other planned work: score FabLens with the [AI App Scorecard](../ai-app-scorecard/) on every release, and add an LLM-as-judge faithfulness check.

## Tech
Python · LangChain (RAG + agents) · FAISS · BM25 · sentence-transformers · Claude API · Mistral AI · Gradio · pytest · GitHub Actions

Knowledge base documents in `docs/` are original summaries written for this project.
