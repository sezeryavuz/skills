#!/usr/bin/env python3
"""Phase 0 preflight: what is actually available before anything is written.

Discovers the `enrich` skill installation, probes for a GBrain runtime, and finds
resumable refinement sessions. Read-only -- it never installs, configures, or mutates.

The point of running this rather than assuming: installing a skill definition does not
make the underlying GBrain tools available, and a limitation discovered at Phase 7 has
already cost the user an enrichment pass.

Usage:
    python3 preflight.py [--json]

Exit codes: 0 = ready to proceed, 1 = blockers found (see the report).
"""

import argparse
import json
import os
import shutil
import sys
from pathlib import Path

SKILL_SEARCH_DIRS = [
    "~/.claude/skills",
    "~/.config/skills",
    "~/.skills",
    "~/.agents/skills",
    ".claude/skills",
    ".agents/skills",
    "skills",
]

MCP_CONFIG_CANDIDATES = [
    "~/.claude/settings.json",
    "~/.claude/settings.local.json",
    ".mcp.json",
    ".claude/settings.json",
    ".claude/settings.local.json",
]

SESSION_ROOT = "~/.gbrain/refinement-sessions"


def find_enrich():
    """Locate an installed `enrich` skill and confirm its SKILL.md is readable."""
    found = []
    for d in SKILL_SEARCH_DIRS:
        base = Path(d).expanduser()
        if not base.is_dir():
            continue
        for candidate in (base / "enrich", base / "gbrain" / "enrich"):
            skill_md = candidate / "SKILL.md"
            if skill_md.is_file():
                try:
                    readable = bool(skill_md.read_text(encoding="utf-8").strip())
                except OSError as exc:
                    readable = False
                    print(f"  ! could not read {skill_md}: {exc}", file=sys.stderr)
                found.append({"path": str(candidate), "skill_md_readable": readable})
    return found


def find_gbrain_cli():
    path = shutil.which("gbrain")
    return {"available": path is not None, "path": path}


def find_gbrain_mcp():
    """Look for a gbrain MCP server declared in host config.

    A config mention proves declaration, not a live connection -- the caller still has to
    confirm the tools respond.
    """
    hits = []
    for cfg in MCP_CONFIG_CANDIDATES:
        p = Path(cfg).expanduser()
        if not p.is_file():
            continue
        try:
            raw = p.read_text(encoding="utf-8")
        except OSError:
            continue
        if "gbrain" in raw.lower():
            hits.append(str(p))
    return {"declared_in": hits}


def find_sessions():
    """Find resumable refinement sessions, newest first."""
    root = Path(SESSION_ROOT).expanduser()
    if not root.is_dir():
        return []
    sessions = []
    for state in root.glob("*/*/*/session-state.json"):
        entry = {"state_file": str(state), "entity": None, "phase": None,
                 "iteration": None, "blocked_on": None}
        try:
            data = json.loads(state.read_text(encoding="utf-8"))
            entry["entity"] = (data.get("entity") or {}).get("canonical_name")
            entry["phase"] = data.get("phase")
            entry["iteration"] = data.get("iteration")
            entry["blocked_on"] = data.get("blocked_on")
        except (OSError, json.JSONDecodeError) as exc:
            entry["error"] = str(exc)
        entry["mtime"] = state.stat().st_mtime
        sessions.append(entry)
    return sorted(sessions, key=lambda s: s["mtime"], reverse=True)


def build_report():
    enrich = find_enrich()
    cli = find_gbrain_cli()
    mcp = find_gbrain_mcp()
    sessions = find_sessions()

    blockers = []
    if not enrich:
        blockers.append(
            "enrich not found. Install once: "
            "npx skills add https://github.com/garrytan/gbrain --skill enrich  "
            "(if the host caches its skill registry, a reload or new session may be "
            "required before it becomes discoverable -- check before reporting it absent)"
        )
    if not cli["available"] and not mcp["declared_in"]:
        blockers.append(
            "No GBrain runtime detected (neither a `gbrain` CLI on PATH nor an MCP server "
            "declared in host config). Installing the skill definition does not provide the "
            "tools; without a runtime no page can be read or written."
        )

    return {
        "enrich_installations": enrich,
        "gbrain_cli": cli,
        "gbrain_mcp": mcp,
        "resumable_sessions": sessions,
        "blockers": blockers,
        "unverifiable_here": [
            "active brain / source routing (ask; never default when several exist)",
            "read permission",
            "write permission",
            "timeline operations",
            "raw-data operations",
            "auto-link behavior",
        ],
    }


def print_report(r):
    print("# Preflight\n")

    print("## enrich")
    if r["enrich_installations"]:
        for inst in r["enrich_installations"]:
            ok = "readable" if inst["skill_md_readable"] else "NOT READABLE"
            print(f"  found: {inst['path']}  (SKILL.md {ok})")
        if len(r["enrich_installations"]) > 1:
            print("  ! multiple installations -- confirm which the host actually invokes")
    else:
        print("  not found")

    print("\n## GBrain runtime")
    print(f"  CLI: {r['gbrain_cli']['path'] or 'not on PATH'}")
    mcp = r["gbrain_mcp"]["declared_in"]
    print(f"  MCP: {'declared in ' + ', '.join(mcp) if mcp else 'not declared in known config'}")
    print("  (declaration is not a live connection -- confirm the tools respond)")

    print("\n## Resumable sessions")
    if r["resumable_sessions"]:
        for s in r["resumable_sessions"][:10]:
            blocked = f"  BLOCKED: {s['blocked_on']}" if s.get("blocked_on") else ""
            print(f"  {s['entity'] or '?'}  phase {s['phase']} iter {s['iteration']}{blocked}")
            print(f"    {s['state_file']}")
    else:
        print("  none")

    print("\n## Still to verify by hand")
    for item in r["unverifiable_here"]:
        print(f"  - {item}")

    if r["blockers"]:
        print("\n## BLOCKERS")
        for b in r["blockers"]:
            print(f"  - {b}")
    else:
        print("\nNo blockers detected.")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json", action="store_true", help="emit JSON instead of a report")
    args = ap.parse_args()

    report = build_report()
    if args.json:
        json.dump(report, sys.stdout, indent=2)
        print()
    else:
        print_report(report)
    return 1 if report["blockers"] else 0


if __name__ == "__main__":
    sys.exit(main())
