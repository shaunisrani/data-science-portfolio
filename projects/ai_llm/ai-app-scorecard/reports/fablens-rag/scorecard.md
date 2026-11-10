# Scorecard: fablens-rag

Suite: FabLens semiconductor Q&A · 22 cases

**Overall: 98/100 (grade A) — PASS**

| Metric | Score | Gate |
|---|---|---|
| Retrieval hit@k | 100% | ≥85% |
| MRR | 0.83 | — |
| Answer correctness | 94% | ≥75% |
| Correct refusals (unanswerable) | 100% | ≥75% |
| False refusals (answerable) | 0% | — |
| Cites sources | 100% | — |
| Latency p50 / max | 0.00s / 0.00s | — |

## Failed cases

- `wafer-01` (answerable): What wafer map pattern points to a CMP problem? — missing ['scratch']
