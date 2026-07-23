#!/usr/bin/env python3
"""Validate readiness scores and compare iterations to detect a plateau.

Two things this enforces that are easy to skip by hand: every score carries evidence, and
"the score went up" is not the same as "the startup got clearer". The second check is the
convergence guard -- without it the refinement loop has no principled stopping point.

Scores live in a JSON file:

    {
      "iteration": 2,
      "stage": "pre-product",
      "scores": {
        "demand_reality": {"score": 1, "evidence": "'everyone loves it' - no behaviour cited"},
        ...
      },
      "gaps": [
        {"id": "G1", "dimension": "demand_reality", "repair_type": "collect_evidence"}
      ]
    }

Usage:
    python3 rubric.py check   SCORES.json
    python3 rubric.py compare PREVIOUS.json CURRENT.json
"""

import argparse
import json
import sys
from pathlib import Path

DIMENSIONS = [
    "demand_reality", "status_quo_clarity", "target_user_specificity",
    "pain_and_consequence", "narrowest_wedge", "observation_quality",
    "future_fit_thesis", "premise_integrity", "distribution_clarity",
    "narrative_integrity",
]

# What a dimension can honestly reach before a product exists. See
# references/founder-readiness-rubric.md -- scoring a pre-product startup down for
# evidence that cannot exist yet is the failure mode this guards against.
PRE_PRODUCT_CEILING = {
    "demand_reality": 2,
    "observation_quality": 2,
    "distribution_clarity": 3,
}

# Repair types that no amount of rewriting can close.
REAL_WORLD_REPAIRS = {
    "collect_evidence", "observe_users", "validate_willingness_to_pay", "test_distribution",
}


def load(path):
    p = Path(path)
    if not p.is_file():
        print(f"error: no such file: {p}", file=sys.stderr)
        sys.exit(2)
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"error: malformed JSON in {p}: {exc}", file=sys.stderr)
        sys.exit(2)


def cmd_check(args):
    data = load(args.scores)
    scores = data.get("scores", {})
    stage = data.get("stage")
    problems, warnings = [], []

    missing = [d for d in DIMENSIONS if d not in scores]
    if missing:
        problems.append(f"missing dimensions: {', '.join(missing)}")

    for name, entry in scores.items():
        if name not in DIMENSIONS:
            warnings.append(f"unknown dimension: {name}")
            continue
        if not isinstance(entry, dict):
            problems.append(f"{name}: expected an object with score and evidence")
            continue
        score = entry.get("score")
        if not isinstance(score, int) or not 0 <= score <= 4:
            problems.append(f"{name}: score {score!r} is not an integer 0-4")
        evidence = (entry.get("evidence") or "").strip()
        if not evidence:
            problems.append(f"{name}: no evidence. A score without evidence cannot be "
                            f"compared across iterations.")
        elif len(evidence.split()) < 4:
            warnings.append(f"{name}: evidence is very thin ({evidence!r})")

        if stage == "pre-product" and name in PRE_PRODUCT_CEILING and isinstance(score, int):
            ceiling = PRE_PRODUCT_CEILING[name]
            if score > ceiling:
                warnings.append(
                    f"{name}: {score} exceeds the pre-product ceiling of {ceiling}. Confirm "
                    f"this reflects real evidence rather than a validation plan counted as one.")

    valid = [e["score"] for e in scores.values()
             if isinstance(e, dict) and isinstance(e.get("score"), int)]
    total = sum(valid)

    print(f"# Rubric check -- iteration {data.get('iteration', '?')}, stage {stage}")
    print(f"total {total}/40 across {len(valid)} scored dimension(s)")

    gaps = data.get("gaps", [])
    if gaps:
        real_world = [g for g in gaps if g.get("repair_type") in REAL_WORLD_REPAIRS]
        print(f"gaps {len(gaps)} ({len(real_world)} need real-world evidence)")
        if gaps and len(real_world) == len(gaps):
            warnings.append("every open gap needs real-world evidence -- further rewriting "
                            "cannot help. Deliver the assignments and stop.")

    if problems:
        print("\n## PROBLEMS")
        for p in problems:
            print(f"  - {p}")
    if warnings:
        print("\n## Warnings")
        for w in warnings:
            print(f"  - {w}")
    if not problems and not warnings:
        print("\nScores are well-formed and evidenced.")

    return 1 if problems else 0


def cmd_compare(args):
    prev, cur = load(args.previous), load(args.current)
    ps, cs = prev.get("scores", {}), cur.get("scores", {})

    moved, flat = [], []
    for d in DIMENSIONS:
        a = (ps.get(d) or {}).get("score")
        b = (cs.get(d) or {}).get("score")
        if a is None or b is None:
            continue
        (moved if a != b else flat).append((d, a, b))

    def gap_key(g):
        return (g.get("dimension"), g.get("repair_type"))

    pg = {gap_key(g) for g in prev.get("gaps", [])}
    cg = {gap_key(g) for g in cur.get("gaps", [])}

    resolved, new, repeated = pg - cg, cg - pg, pg & cg

    print(f"# Iteration {prev.get('iteration', '?')} -> {cur.get('iteration', '?')}\n")
    print(f"scores moved: {len(moved)}   unchanged: {len(flat)}")
    for d, a, b in moved:
        print(f"  {d}: {a} -> {b}")
    print(f"\ngaps resolved: {len(resolved)}   new: {len(new)}   repeated: {len(repeated)}")
    for d, r in sorted(repeated):
        print(f"  repeated: {d} ({r})")

    print()
    total_prev = sum(v for _, v, _ in moved) + sum(v for _, v, _ in flat)
    total_cur = sum(v for _, _, v in moved) + sum(v for _, v, _ in flat)

    if cg and cg == pg:
        print("PLATEAU -- identical gaps with identical repair types.")
        print("Another pass needs new evidence, not another attempt. Stop and report.")
        return 0

    if total_cur > total_prev and not resolved:
        print("WARNING -- the score rose but no gap was resolved.")
        print("The artifact may have become more persuasive without becoming more true.")
        print("Check whether a rewrite upgraded a hypothesis into a claim.")
        return 0

    if not moved and not resolved and not new:
        print("No measurable change. Treat as a plateau unless a founder decision is pending.")
        return 0

    print("Progress: gaps resolved or newly surfaced. Continuing is justified.")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("check")
    c.add_argument("scores")
    c.set_defaults(func=cmd_check)

    m = sub.add_parser("compare")
    m.add_argument("previous")
    m.add_argument("current")
    m.set_defaults(func=cmd_compare)

    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
