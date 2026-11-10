# Scorecard: fablens-rag

Suite: FabLens semiconductor Q&A · 22 cases

**Overall: 78/100 (grade C) — FAIL**

| Metric | Score | Gate |
|---|---|---|
| Retrieval hit@k | 100% | ≥85% |
| MRR | 0.81 | — |
| Answer correctness | 94% | ≥75% |
| Correct refusals (unanswerable) | 0% | ≥75% |
| False refusals (answerable) | 0% | — |
| Cites sources | 100% | — |
| Latency p50 / max | 0.00s / 0.00s | — |

## Failed cases

- `wafer-01` (answerable): What wafer map pattern points to a CMP problem? — missing ['scratch']
- `none-01` (unanswerable): What is the stock price of TSMC today?
- `none-02` (unanswerable): Who won the 2022 World Cup?
- `none-03` (unanswerable): Give me a recipe for banana bread
- `none-04` (unanswerable): What is the capital of Australia?
