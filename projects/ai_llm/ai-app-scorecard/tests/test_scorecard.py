import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scorecard import aggregate, compare, is_refusal, run, score_case, write_reports  # noqa: E402

SUITE = {"suite": "toy", "cases": [
    {"id": "a", "category": "answerable", "question": "q1", "expected_sources": ["x.md"], "must_include": ["13.5"]},
    {"id": "b", "category": "answerable", "question": "q2", "expected_sources": ["y.md"], "must_include": ["tin", "plasma"]},
    {"id": "n", "category": "unanswerable", "question": "q3"},
]}


class FakeApp:
    def ask(self, q):
        return {"q1": {"answer": "EUV uses 13.5 nm light", "sources": ["z.md", "x.md"]},
                "q2": {"answer": "a tin plasma", "sources": ["y.md"]},
                "q3": {"answer": "I don't know.", "sources": []}}[q]


def test_refusal_detection():
    assert is_refusal("I don't know: that isn't covered")
    assert not is_refusal("EUV uses 13.5 nm light")


def test_score_case_rank_and_correctness():
    row = score_case(SUITE["cases"][0], {"answer": "13.5 nm", "sources": ["z.md", "x.md"]})
    assert row["retrieval_hit"] == 1 and row["reciprocal_rank"] == 0.5 and row["correctness"] == 1


def test_run_and_gates(tmp_path):
    rows, m = run(FakeApp(), SUITE)
    assert m["retrieval"] == 1 and m["refusal"] == 1 and m["correctness"] == 1
    assert m["mrr"] == 0.75 and m["passed"]
    out = write_reports(tmp_path, "fake", SUITE, rows, m, [])
    assert (out / "scorecard.html").exists() and "PASS" in (out / "scorecard.md").read_text()


def test_regression_detected(tmp_path):
    base = tmp_path / "base.json"
    base.write_text(json.dumps({"metrics": {"refusal": 1.0, "overall": 95}}))
    regs = compare({"refusal": 0.5, "overall": 70}, base)
    assert {r["metric"] for r in regs} == {"refusal", "overall"}


def test_failing_app_fails_gate():
    class Bad:
        def ask(self, q):
            return {"answer": "something unrelated", "sources": []}
    _, m = run(Bad(), SUITE)
    assert not m["passed"]
