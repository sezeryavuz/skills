#!/usr/bin/env python3
"""Session lifecycle: init, snapshot artifact versions, validate resumable state.

The founder's original artifact must survive every iteration, and a resumed session must
not re-open decisions the founder already made. Both are mechanical, so they live here
rather than depending on being remembered.

Usage:
    python3 session.py init  --slug SLUG --artifact PATH [--stage STAGE] [--root DIR]
    python3 session.py snapshot --session DIR --artifact PATH --iteration N
    python3 session.py validate --session DIR

Sessions default to ~/.gstack/projects/{slug}/founder-reflection/{session-id}/ -- outside
the skill directory and outside the founder's repo.
"""

import argparse
import datetime
import hashlib
import json
import sys
from pathlib import Path

DEFAULT_ROOT = "~/.gstack/projects"
STAGES = ["pre-product", "prototype", "users", "paying", "internal"]

REQUIRED_STATE_KEYS = ["session_id", "project_slug", "stage", "artifact", "iteration",
                       "max_office_hours_passes", "passes_completed", "open_gaps",
                       "founder_decisions", "premises"]


def now_iso():
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")


def content_hash(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def session_dir(root, slug, session_id):
    return Path(root).expanduser() / slug / "founder-reflection" / session_id


def cmd_init(args):
    artifact = Path(args.artifact)
    if not artifact.is_file():
        print(f"error: no such artifact: {artifact}", file=sys.stderr)
        return 2

    session_id = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d-%H%M%S")
    sdir = session_dir(args.root, args.slug, session_id)
    sdir.mkdir(parents=True, exist_ok=True)

    text = artifact.read_text(encoding="utf-8")
    (sdir / "01-baseline.md").write_text(text, encoding="utf-8")

    state = {
        "session_id": session_id,
        "created_at": now_iso(),
        "project_slug": args.slug,
        "stage": args.stage,
        "audience": None,
        "artifact": {
            "original_path": str(artifact.resolve()),
            "baseline": "01-baseline.md",
            "baseline_hash": content_hash(text),
            "current_iteration": 0,
            "current_path": "01-baseline.md",
        },
        "iteration": 0,
        "max_office_hours_passes": 3,
        "passes_completed": 0,
        "readiness": {},
        "open_gaps": [],
        "founder_decisions": [],
        "premises": [],
        "blocked_on": None,
        "resume_instruction": None,
    }
    (sdir / "session-state.json").write_text(json.dumps(state, indent=2), encoding="utf-8")

    print(f"session   {sdir}")
    print(f"baseline  {sdir / '01-baseline.md'}")
    print(f"hash      {state['artifact']['baseline_hash']}")
    return 0


def cmd_snapshot(args):
    sdir = Path(args.session).expanduser()
    state_path = sdir / "session-state.json"
    if not state_path.is_file():
        print(f"error: no session-state.json in {sdir}", file=sys.stderr)
        return 2

    artifact = Path(args.artifact)
    if not artifact.is_file():
        print(f"error: no such artifact: {artifact}", file=sys.stderr)
        return 2

    state = json.loads(state_path.read_text(encoding="utf-8"))
    text = artifact.read_text(encoding="utf-8")
    h = content_hash(text)

    dest = sdir / f"iteration-{args.iteration:02d}.md"
    if dest.exists():
        print(f"error: {dest.name} already exists -- iterations are append-only.",
              file=sys.stderr)
        print("       use the next iteration number rather than overwriting history.",
              file=sys.stderr)
        return 3

    dest.write_text(text, encoding="utf-8")

    if h == state["artifact"].get("baseline_hash"):
        print("note: identical to the baseline -- nothing was actually revised.")

    state["artifact"]["current_iteration"] = args.iteration
    state["artifact"]["current_path"] = dest.name
    state["artifact"][f"iteration_{args.iteration:02d}_hash"] = h
    state["iteration"] = args.iteration
    state["updated_at"] = now_iso()
    state_path.write_text(json.dumps(state, indent=2), encoding="utf-8")

    print(f"saved  {dest}")
    print(f"hash   {h}")
    return 0


def cmd_validate(args):
    sdir = Path(args.session).expanduser()
    state_path = sdir / "session-state.json"
    if not state_path.is_file():
        print(f"error: no session-state.json in {sdir}", file=sys.stderr)
        return 2

    try:
        state = json.loads(state_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"error: malformed session-state.json: {exc}", file=sys.stderr)
        return 2

    problems, warnings = [], []

    for key in REQUIRED_STATE_KEYS:
        if key not in state:
            problems.append(f"missing key: {key}")

    if state.get("stage") not in STAGES:
        problems.append(f"stage {state.get('stage')!r} not one of {STAGES}")

    art = state.get("artifact", {})
    baseline = sdir / art.get("baseline", "01-baseline.md")
    if not baseline.is_file():
        problems.append(f"baseline missing: {baseline}")
    elif art.get("baseline_hash") and content_hash(
            baseline.read_text(encoding="utf-8")) != art["baseline_hash"]:
        problems.append("baseline file no longer matches its recorded hash -- it was modified. "
                        "The original input must be preserved.")

    # The founder may have edited their own file since the last snapshot; their edits win.
    original = Path(art.get("original_path", ""))
    if original.is_file() and art.get("current_iteration", 0) > 0:
        cur = sdir / art.get("current_path", "")
        if cur.is_file():
            if content_hash(original.read_text(encoding="utf-8")) != content_hash(
                    cur.read_text(encoding="utf-8")):
                warnings.append(
                    "the founder's artifact differs from the last snapshot -- they have edited "
                    "it since. Re-baseline rather than overwriting their changes.")

    passes = state.get("passes_completed", 0)
    max_passes = state.get("max_office_hours_passes", 3)
    if passes > max_passes:
        problems.append(f"passes_completed ({passes}) exceeds max ({max_passes})")
    elif passes == max_passes:
        warnings.append(f"pass ceiling reached ({passes}/{max_passes}) -- stop with an "
                        "unresolved-gaps report rather than iterating further.")

    if state.get("open_gaps"):
        actionable = [g for g in state["open_gaps"]
                      if g.get("status") not in ("requires_real_world_evidence",)]
        if not actionable:
            warnings.append("every open gap requires real-world evidence -- further rewriting "
                            "cannot help. Deliver the validation assignments and stop.")

    if not state.get("founder_decisions") and state.get("iteration", 0) > 1:
        warnings.append("no founder decisions recorded past iteration 1 -- confirm that scope "
                        "choices were actually put to the founder rather than assumed.")

    print(f"# Session {state.get('session_id')}  ({sdir})")
    print(f"stage {state.get('stage')} | iteration {state.get('iteration')} | "
          f"passes {passes}/{max_passes}")
    print(f"open gaps {len(state.get('open_gaps', []))} | "
          f"decisions {len(state.get('founder_decisions', []))} | "
          f"premises {len(state.get('premises', []))}")

    if problems:
        print("\n## PROBLEMS")
        for p in problems:
            print(f"  - {p}")
    if warnings:
        print("\n## Warnings")
        for w in warnings:
            print(f"  - {w}")
    if not problems and not warnings:
        print("\nState is valid and resumable.")

    return 1 if problems else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    i = sub.add_parser("init")
    i.add_argument("--slug", required=True)
    i.add_argument("--artifact", required=True)
    i.add_argument("--stage", default="pre-product", choices=STAGES)
    i.add_argument("--root", default=DEFAULT_ROOT)
    i.set_defaults(func=cmd_init)

    s = sub.add_parser("snapshot")
    s.add_argument("--session", required=True)
    s.add_argument("--artifact", required=True)
    s.add_argument("--iteration", type=int, required=True)
    s.set_defaults(func=cmd_snapshot)

    v = sub.add_parser("validate")
    v.add_argument("--session", required=True)
    v.set_defaults(func=cmd_validate)

    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
