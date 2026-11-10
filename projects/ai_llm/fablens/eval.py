"""Retrieval evaluation: does the right source doc appear in the top-k chunks?
Run: python eval.py [--min-hit 0.9]   (reports hit@k and MRR; exits 1 if hit@k is below the threshold, for CI)."""
import argparse
import sys

from rag import build_index

EVAL_SET = [
    ("What does the alpha parameter mean in the Stapper yield model?", "01_yield_basics.md"),
    ("Why do large GPU dies have lower yield?", "01_yield_basics.md"),
    ("What is the difference between line yield and sort yield?", "01_yield_basics.md"),
    ("What wavelength does EUV lithography use?", "02_lithography_euv.md"),
    ("How is the EUV light generated?", "02_lithography_euv.md"),
    ("What is the Rayleigh resolution formula?", "02_lithography_euv.md"),
    ("What is a focus-exposure matrix used for?", "03_overlay_cd_metrology.md"),
    ("How does scatterometry measure critical dimension?", "03_overlay_cd_metrology.md"),
    ("What is overlay error?", "03_overlay_cd_metrology.md"),
    ("What are stochastic defects?", "04_defect_inspection.md"),
    ("When is darkfield inspection preferred over brightfield?", "04_defect_inspection.md"),
    ("What is a killer defect?", "04_defect_inspection.md"),
    ("What does an edge ring failure pattern indicate?", "05_wafer_maps.md"),
    ("What is the WM-811K dataset?", "05_wafer_maps.md"),
    ("What are the Western Electric rules?", "06_spc_fdc.md"),
    ("How does run-to-run control adjust a recipe?", "06_spc_fdc.md"),
    ("How is OEE calculated?", "07_equipment_health.md"),
    ("What is remaining useful life estimation?", "07_equipment_health.md"),
    ("What is optical proximity correction?", "08_ai_in_fabs.md"),
    ("What is holistic lithography?", "08_ai_in_fabs.md"),
]


def evaluate(k=4):
    """Return (hit_rate, mrr, mode)."""
    r = build_index()
    hits, rr = 0, 0.0
    for q, gold in EVAL_SET:
        srcs = [d.metadata["source"] for d in r.invoke(q)[:k]]
        if gold in srcs:
            hits += 1
            rr += 1 / (srcs.index(gold) + 1)
        else:
            print(f"MISS: {q} -> {srcs}")
    n = len(EVAL_SET)
    print(f"Mode: {r.mode} | {n} questions | hit@{k}: {hits / n:.0%} | MRR: {rr / n:.2f}")
    return hits / n, rr / n, r.mode


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-hit", type=float, default=0.9, help="fail (exit 1) if hit@4 is below this")
    args = ap.parse_args()
    hit, _, _ = evaluate()
    if hit < args.min_hit:
        print(f"FAIL: hit@4 {hit:.0%} < required {args.min_hit:.0%}")
        sys.exit(1)
    print("PASS")
