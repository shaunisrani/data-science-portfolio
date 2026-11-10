# AI App Scorecard

A reusable evaluation framework that scores how accurate a team's AI apps are — RAG apps, agents, or chatbots — on one shared test suite, with quality gates and regression checks.

Any app plugs in through a small adapter (`ask(question) → {answer, sources}`), or over HTTP.

## What it measures

| Metric | Meaning | Applies to |
|---|---|---|
| Retrieval hit@k | The expected source document was retrieved | Answerable questions |
| MRR | How high the right source ranked | Answerable |
| Answer correctness | Share of required facts in the answer | Answerable, calculation |
| Correct refusals | App says "I don't know" when the answer isn't in its knowledge | Unanswerable |
| False refusals | App refuses a question it should answer | Answerable |
| Citation rate | App returned sources | Answerable |
| Latency | p50 and max seconds per question | All |

The overall score (0–100, grade A–F) is a weighted average. **Quality gates**: retrieval ≥ 85%, correctness ≥ 75%, correct refusals ≥ 75%. A run fails if any gate fails or any metric regresses vs. a baseline.

## Results on FabLens

The scorecard caught a real bug on its first run: FabLens answered every off-topic question instead of saying "I don't know."

| Run | Overall | Retrieval | Correctness | Correct refusals | Result |
|---|---|---|---|---|---|
| Baseline | 78 (C) | 100% | 94% | **0%** | FAIL |
| After relevance gate | 98 (A) | 100% | 94% | **100%** | PASS |

The fix: FabLens now checks that a question's key terms exist in its knowledge base before answering, and refuses otherwise. False refusals stayed at 0%.

Reports: `reports/baseline/` and `reports/fablens-rag/` (Markdown, HTML, and JSON). Scores above are for BM25 retrieval in extractive mode (no LLM); the agent adds 2 calculation cases.

## Usage

```
python scorecard.py --app fablens-rag   --cases cases/fablens.json --out reports/fablens-rag
python scorecard.py --app fablens-agent --cases cases/fablens.json --out reports/fablens-agent   # needs an LLM key
python scorecard.py --app http --url http://localhost:8000/ask --cases cases/my_app.json --out reports/my_app
python scorecard.py ... --baseline reports/fablens-rag/results.json   # exit 1 on any regression
```

## Adding a team's app

1. Write a test suite JSON like `cases/fablens.json` (answerable, unanswerable, and calculation cases).
2. Either expose the app as `POST {"question"} → {"answer", "sources"}` and use `--app http`, or add a small adapter class in `adapters.py`.
3. Run it in CI with `--baseline` so accuracy can't silently drop.

## Tests

```
python -m pytest -q tests
```

## Roadmap
- LLM-as-judge faithfulness score (does every claim trace to a cited source?)
- Cost per query tracking
- One dashboard comparing all team apps side by side

## Tech
Python · pytest · JSON test suites · self-contained HTML reports · GitHub Actions
