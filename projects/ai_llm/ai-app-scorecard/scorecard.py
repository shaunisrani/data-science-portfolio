"""AI App Scorecard — score any question-answering AI app (RAG, agent, chatbot) on one test suite.

Metrics per case
  retrieval_hit   expected source appears in the app's sources          (answerable)
  reciprocal_rank 1 / rank of the first expected source                 (answerable)
  correctness     share of required facts (must_include) in the answer  (answerable, calculation)
  refusal         app correctly says it doesn't know                    (unanswerable)
  cited           app returned at least one source                      (answerable)
  latency_s       seconds per question

The overall score is a weighted average of the category scores (0-100), with pass/fail quality gates.

Usage:
  python scorecard.py --app fablens-rag --cases cases/fablens.json --out reports/fablens-rag
  python scorecard.py --app http --url http://localhost:8000/ask --cases cases/my_app.json --out reports/my_app
  python scorecard.py ... --baseline reports/fablens-rag/results.json   # flag regressions
"""
import argparse
import json
import re
import statistics
import sys
import time
from pathlib import Path

REFUSAL_PATTERNS = [
    r"\bi don'?t know\b", r"\bnot (in|covered by) (the|my) (knowledge base|documents|context)\b",
    r"\bno relevant\b", r"\bcan(no|')t (find|answer)\b", r"\bunable to answer\b", r"\bnot enough information\b",
]

WEIGHTS = {"retrieval": 0.25, "correctness": 0.35, "refusal": 0.20, "citation": 0.10, "latency": 0.10}
GATES = {"retrieval": 0.85, "correctness": 0.75, "refusal": 0.75}
LATENCY_TARGET_S = 5.0


def norm(text):
    return re.sub(r"\s+", " ", text.lower())


def is_refusal(answer):
    a = norm(answer)
    return any(re.search(p, a) for p in REFUSAL_PATTERNS)


def score_case(case, result):
    cat = case["category"]
    answer, sources = result.get("answer", ""), result.get("sources", [])
    row = {"id": case["id"], "category": cat, "latency_s": result.get("latency_s", 0.0)}
    if cat in {"answerable", "calculation"} and case.get("must_include"):
        found = [k for k in case["must_include"] if norm(k) in norm(answer)]
        row["correctness"] = len(found) / len(case["must_include"])
        row["missing"] = [k for k in case["must_include"] if k not in found]
    if cat == "answerable":
        gold = set(case.get("expected_sources", []))
        ranks = [i + 1 for i, s in enumerate(sources) if s in gold]
        row["retrieval_hit"] = 1.0 if ranks else 0.0
        row["reciprocal_rank"] = 1 / ranks[0] if ranks else 0.0
        row["cited"] = 1.0 if sources else 0.0
        row["false_refusal"] = 1.0 if is_refusal(answer) else 0.0
    if cat == "unanswerable":
        row["refusal"] = 1.0 if is_refusal(answer) else 0.0
    return row


def mean(rows, key):
    vals = [r[key] for r in rows if key in r]
    return statistics.mean(vals) if vals else None


def aggregate(rows):
    lat = [r["latency_s"] for r in rows]
    m = {
        "retrieval": mean(rows, "retrieval_hit"),
        "mrr": mean(rows, "reciprocal_rank"),
        "correctness": mean(rows, "correctness"),
        "refusal": mean(rows, "refusal"),
        "citation": mean(rows, "cited"),
        "false_refusal_rate": mean(rows, "false_refusal"),
        "latency_p50_s": statistics.median(lat) if lat else None,
        "latency_max_s": max(lat) if lat else None,
    }
    m["latency"] = None if m["latency_p50_s"] is None else max(0.0, 1 - m["latency_p50_s"] / LATENCY_TARGET_S)
    used = {k: w for k, w in WEIGHTS.items() if m.get(k) is not None}
    m["overall"] = 100 * sum(m[k] * w for k, w in used.items()) / sum(used.values())
    m["grade"] = next(g for t, g in [(90, "A"), (80, "B"), (70, "C"), (60, "D"), (0, "F")] if m["overall"] >= t)
    m["gates"] = {k: (m[k] is None or m[k] >= t) for k, t in GATES.items()}
    m["passed"] = all(m["gates"].values())
    return m


def run(adapter, suite, categories=None):
    rows = []
    for case in suite["cases"]:
        if categories and case["category"] not in categories:
            continue
        t0 = time.time()
        try:
            result = adapter.ask(case["question"])
        except Exception as e:  # a crash counts as a wrong answer, not a crash of the scorecard
            result = {"answer": f"ERROR: {e}", "sources": []}
        result.setdefault("latency_s", time.time() - t0)
        rows.append({**score_case(case, result), "question": case["question"]})
    return rows, aggregate(rows)


def compare(metrics, baseline_path, tolerance=0.02):
    """Return regressions vs. a previous results.json."""
    base = json.loads(Path(baseline_path).read_text())["metrics"]
    out = []
    for k in ["retrieval", "mrr", "correctness", "refusal", "citation", "overall"]:
        b, n = base.get(k), metrics.get(k)
        if b is None or n is None:
            continue
        scale = 100 if k == "overall" else 1
        if n < b - tolerance * scale:
            out.append({"metric": k, "baseline": b, "now": n})
    return out


def pct(v):
    return "n/a" if v is None else f"{v:.0%}"


def write_reports(out_dir, app_name, suite, rows, m, regressions):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "results.json").write_text(json.dumps({"app": app_name, "suite": suite["suite"], "metrics": m,
                                                   "regressions": regressions, "cases": rows}, indent=2))
    mrr_s = "n/a" if m["mrr"] is None else f"{m['mrr']:.2f}"
    fails = [r for r in rows if r.get("correctness", 1) < 1 or r.get("retrieval_hit", 1) < 1 or r.get("refusal", 1) < 1]
    lines = [
        f"# Scorecard: {app_name}", "", f"Suite: {suite['suite']} · {len(rows)} cases", "",
        f"**Overall: {m['overall']:.0f}/100 (grade {m['grade']}) — {'PASS' if m['passed'] else 'FAIL'}**", "",
        "| Metric | Score | Gate |", "|---|---|---|",
        f"| Retrieval hit@k | {pct(m['retrieval'])} | {'≥' + pct(GATES['retrieval'])} |",
        f"| MRR | {mrr_s} | — |",
        f"| Answer correctness | {pct(m['correctness'])} | {'≥' + pct(GATES['correctness'])} |",
        f"| Correct refusals (unanswerable) | {pct(m['refusal'])} | {'≥' + pct(GATES['refusal'])} |",
        f"| False refusals (answerable) | {pct(m['false_refusal_rate'])} | — |",
        f"| Cites sources | {pct(m['citation'])} | — |",
        f"| Latency p50 / max | {m['latency_p50_s']:.2f}s / {m['latency_max_s']:.2f}s | — |", "",
    ]
    if regressions:
        lines += ["## Regressions vs. baseline", ""] + [f"- {r['metric']}: {r['baseline']:.2f} → {r['now']:.2f}" for r in regressions] + [""]
    lines += ["## Failed cases", ""] + ([f"- `{r['id']}` ({r['category']}): {r['question']}"
                                          + (f" — missing {r['missing']}" if r.get("missing") else "") for r in fails] or ["None"])
    (out / "scorecard.md").write_text("\n".join(lines) + "\n")
    (out / "scorecard.html").write_text(render_html(app_name, suite, rows, m, regressions, fails))
    return out


def render_html(app_name, suite, rows, m, regressions, fails):
    def bar(label, v, gate=None):
        if v is None:
            return ""
        ok = gate is None or v >= gate
        mark = f'<span class="gate" style="left:{gate * 100:.0f}%"></span>' if gate else ""
        return (f'<div class="row"><span class="lbl">{label}</span><div class="track">'
                f'<div class="fill {"ok" if ok else "bad"}" style="width:{v * 100:.0f}%"></div>{mark}</div>'
                f'<span class="val">{v:.0%}</span></div>')

    mrr_s = "n/a" if m["mrr"] is None else f"{m['mrr']:.2f}"
    fail_rows = "".join(f"<tr><td>{r['id']}</td><td>{r['category']}</td><td>{r['question']}</td>"
                        f"<td>{', '.join(r.get('missing', [])) or '—'}</td></tr>" for r in fails) or \
        "<tr><td colspan=4>None</td></tr>"
    reg = "".join(f"<li>{r['metric']}: {r['baseline']:.2f} → {r['now']:.2f}</li>" for r in regressions)
    return f"""<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Scorecard: {app_name}</title><style>
:root{{--bg:#fff;--fg:#1a1a1a;--mute:#666;--ok:#2f7d4f;--bad:#c0392b;--track:#eee}}
@media (prefers-color-scheme:dark){{:root{{--bg:#141414;--fg:#eee;--mute:#999;--track:#2a2a2a}}}}
body{{font:15px/1.5 system-ui,sans-serif;background:var(--bg);color:var(--fg);max-width:820px;margin:24px auto;padding:0 16px}}
.big{{font-size:44px;font-weight:700}}.mute{{color:var(--mute)}}
.row{{display:flex;align-items:center;gap:10px;margin:8px 0}}.lbl{{width:220px}}.val{{width:48px;text-align:right}}
.track{{flex:1;height:14px;background:var(--track);border-radius:7px;position:relative}}
.fill{{height:100%;border-radius:7px}}.ok{{background:var(--ok)}}.bad{{background:var(--bad)}}
.gate{{position:absolute;top:-3px;width:2px;height:20px;background:var(--fg)}}
table{{border-collapse:collapse;width:100%}}td,th{{border-bottom:1px solid var(--track);padding:6px;text-align:left;vertical-align:top}}
.pill{{display:inline-block;padding:2px 10px;border-radius:10px;color:#fff;background:{'var(--ok)' if m['passed'] else 'var(--bad)'}}}
</style></head><body>
<h1>Scorecard: {app_name}</h1><p class="mute">{suite['suite']} · {len(rows)} cases</p>
<p><span class="big">{m['overall']:.0f}</span><span class="mute">/100 · grade {m['grade']}</span> <span class="pill">{'PASS' if m['passed'] else 'FAIL'}</span></p>
{bar('Retrieval hit@k', m['retrieval'], GATES['retrieval'])}
{bar('Answer correctness', m['correctness'], GATES['correctness'])}
{bar('Correct refusals', m['refusal'], GATES['refusal'])}
{bar('Cites sources', m['citation'])}
<p class="mute">Vertical line = quality gate. MRR {mrr_s} · false refusals {pct(m['false_refusal_rate'])} · latency p50 {m['latency_p50_s']:.2f}s</p>
{'<h2>Regressions vs. baseline</h2><ul>' + reg + '</ul>' if regressions else ''}
<h2>Failed cases</h2><table><tr><th>ID</th><th>Category</th><th>Question</th><th>Missing</th></tr>{fail_rows}</table>
</body></html>"""


def main(argv=None):
    from adapters import get_adapter

    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--app", required=True, help="fablens-rag | fablens-agent | http")
    ap.add_argument("--url", help="endpoint for --app http (POST {'question': ...} → {'answer', 'sources'})")
    ap.add_argument("--cases", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--baseline", help="previous results.json to compare against")
    args = ap.parse_args(argv)

    suite = json.loads(Path(args.cases).read_text())
    adapter = get_adapter(args.app, url=args.url)
    rows, m = run(adapter, suite, categories=getattr(adapter, "categories", None))
    regressions = compare(m, args.baseline) if args.baseline else []
    out = write_reports(args.out, args.app, suite, rows, m, regressions)
    print(f"{args.app}: {m['overall']:.0f}/100 (grade {m['grade']}) — {'PASS' if m['passed'] else 'FAIL'} → {out}")
    if regressions:
        print("REGRESSIONS:", regressions)
    return 0 if m["passed"] and not regressions else 1


if __name__ == "__main__":
    sys.exit(main())
