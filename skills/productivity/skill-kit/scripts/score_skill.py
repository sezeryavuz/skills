#!/usr/bin/env python3
"""score_skill.py — Phase 5 quality + safety scoring for the skill-kit skill.

Applies the transparent rubric in references/scoring-rubric.md to a pool of
candidate skills, hard-eliminates the unsafe ones, de-duplicates by capability,
and ranks the survivors into a KIT. Every component of the score is a real,
inspectable signal — the number is a ranking aid, not an oracle. The final call
still means reading the top candidate (see SKILL.md).

Stdlib only; no network. Reads candidate JSON from a file arg or stdin.

Input: a JSON array (or {"candidates": [...]}) of objects like:
  {
    "name": "playwright-e2e", "owner": "microsoft",
    "installs": 12000, "stars": 3400, "relevance_count": 3,
    "capability": "e2e-testing",
    "security": {"remote_exec": "green", "tool_scope": "yellow", "secrets": "green"},
    "summary": "End-to-end browser testing with Playwright.",
    "rationale": "(optional) tie back to a project finding"
  }
`security` may also be a shorthand string: "green"/"clean", "yellow"/"caution",
"red"/"risky" (applied to all three indicators).

Usage:
  python3 scripts/score_skill.py candidates.json
  cat candidates.json | python3 scripts/score_skill.py --json
"""
import json
import sys

# Tunable weights — keep in sync with references/scoring-rubric.md.
OFFICIAL = {"anthropics", "vercel-labs", "microsoft", "google", "openai", "meta", "aws", "amazon"}
REPUTABLE = {"composiohq", "langchain-ai", "huggingface", "stripe", "supabase"}
INDICATORS = ("remote_exec", "tool_scope", "secrets")


def norm_owner(o):
    return (o or "").strip().lower().lstrip("@")


def source_points(owner):
    o = norm_owner(owner)
    if o in OFFICIAL:
        return 30, "official source"
    if o in REPUTABLE:
        return 15, "reputable source"
    return 0, "unknown source"


def install_points(n):
    n = n or 0
    if n >= 1000:
        return 25, f"{n} installs (1K+ trusted)"
    if n >= 100:
        return 12, f"{n} installs (100-1K okay)"
    return 0, f"{n} installs (<100 — risky by obscurity)"


def star_points(n):
    n = n or 0
    if n >= 100:
        return 15, f"{n} stars"
    return 0, f"{n} stars (<100 — treat with skepticism)"


def relevance_points(count):
    count = count or 1
    pts = max(0, (count - 1) * 10)
    pts = min(pts, 20)
    return pts, f"matched {count} query/queries"


def read_indicators(security):
    """Return {indicator: color} for the three indicators."""
    if security is None:
        return {k: "green" for k in INDICATORS}
    if isinstance(security, str):
        s = security.strip().lower()
        color = {"clean": "green", "green": "green",
                 "caution": "yellow", "yellow": "yellow",
                 "risky": "red", "red": "red"}.get(s, "green")
        return {k: color for k in INDICATORS}
    if isinstance(security, dict):
        out = {}
        for k in INDICATORS:
            v = str(security.get(k, "green")).strip().lower()
            out[k] = v if v in ("green", "yellow", "red") else "green"
        return out
    return {k: "green" for k in INDICATORS}


def security_assessment(security):
    """Return (bonus, status, note, eliminated:bool)."""
    ind = read_indicators(security)
    colors = list(ind.values())
    reds = [k for k, c in ind.items() if c == "red"]
    yellows = [k for k, c in ind.items() if c == "yellow"]

    if len(reds) == len(INDICATORS):  # all three red — hard eliminate
        return 0, "risky", "all security indicators red", True
    if reds:  # any red (in practice the remote-exec / curl|sh case) — disqualify by default
        return 0, "risky", f"red: {', '.join(reds)} (include only with explicit user acceptance)", True
    if yellows:  # allowed but flagged — never auto-reject on yellow
        return 0, "caution", f"yellow: {', '.join(yellows)}", False
    return 10, "clean", "clean", False


def score_candidate(c):
    name = c.get("name", "unnamed")
    parts = []
    total = 0
    for pts, label in (
        source_points(c.get("owner")),
        install_points(c.get("installs")),
        star_points(c.get("stars")),
        relevance_points(c.get("relevance_count")),
    ):
        parts.append((pts, label))
        total += pts
    sec_bonus, sec_status, sec_note, eliminated = security_assessment(c.get("security"))
    parts.append((sec_bonus, f"security {sec_status}: {sec_note}"))
    total += sec_bonus
    return {
        "name": name,
        "owner": norm_owner(c.get("owner")) or "unknown",
        "capability": c.get("capability") or name,
        "score": total,
        "security_status": sec_status,
        "eliminated": eliminated,
        "elimination_reason": sec_note if eliminated else None,
        "components": [{"points": p, "label": l} for p, l in parts],
        "summary": c.get("summary", ""),
        "rationale": c.get("rationale", ""),
    }


def build_kit(scored):
    """De-duplicate by capability: highest score wins each slot."""
    survivors = [s for s in scored if not s["eliminated"]]
    eliminated = [s for s in scored if s["eliminated"]]
    groups = {}
    for s in survivors:
        groups.setdefault(s["capability"], []).append(s)
    kit, also_ran = [], []
    for cap, members in groups.items():
        members.sort(key=lambda x: -x["score"])
        winner = members[0]
        kit.append(winner)
        for loser in members[1:]:
            loser["superseded_by"] = winner["name"]
            also_ran.append(loser)
    kit.sort(key=lambda x: -x["score"])
    also_ran.sort(key=lambda x: -x["score"])
    return kit, also_ran, eliminated


def load(argv):
    src = None
    for a in argv:
        if a != "--json":
            src = a
    raw = open(src).read() if src else sys.stdin.read()
    data = json.loads(raw)
    if isinstance(data, dict):
        data = data.get("candidates", [])
    if not isinstance(data, list):
        raise SystemExit("error: expected a JSON array of candidates")
    return data


def main():
    argv = sys.argv[1:]
    as_json = "--json" in argv
    candidates = load(argv)
    scored = [score_candidate(c) for c in candidates]
    kit, also_ran, eliminated = build_kit(scored)

    if as_json:
        print(json.dumps({"kit": kit, "also_ran": also_ran, "eliminated": eliminated}, indent=2))
        return

    def comp_line(s):
        return "  ·  ".join(f"{p:+d} {l}" for p, l in
                            [(c["points"], c["label"]) for c in s["components"]])

    print("KIT — recommended skills (one per capability, ranked)")
    print("=" * 60)
    if not kit:
        print("  (nothing cleared the bar — read the top candidates by hand)")
    for s in kit:
        flag = "" if s["security_status"] == "clean" else f"  [{s['security_status']}]"
        print(f"\n  {s['score']:>3}  {s['name']}  ({s['owner']}) · {s['capability']}{flag}")
        print(f"       {comp_line(s)}")
        if s["rationale"]:
            print(f"       why: {s['rationale']}")
        elif s["summary"]:
            print(f"       {s['summary'][:110]}")

    if also_ran:
        print("\n" + "-" * 60)
        print("ALSO CONSIDERED — superseded duplicates (kept the best per capability)")
        for s in also_ran:
            print(f"  · {s['name']} ({s['owner']}), score {s['score']} — superseded by {s['superseded_by']}")

    if eliminated:
        print("\n" + "-" * 60)
        print("ELIMINATED — safety hard-floor (do not recommend without explicit acceptance)")
        for s in eliminated:
            print(f"  · {s['name']} ({s['owner']}) — {s['elimination_reason']}")

    print("\nNOTE: the score ranks; you still read the top pick before recommending it.")


if __name__ == "__main__":
    main()
