#!/usr/bin/env python3
"""Phase 0 preflight: locate the project, its founder-facing artifacts, and office-hours.

Read-only. It never installs, edits, or initialises anything -- discovery only, so that a
founder can run it against a repo without it touching their working tree.

Usage:
    python3 preflight.py [PROJECT_DIR] [--json]

Exit codes: 0 = ready, 1 = blockers found.
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

SKILL_SEARCH_DIRS = [
    "~/.claude/skills", "~/.config/skills", "~/.skills", "~/.agents/skills",
    ".claude/skills", ".agents/skills", "skills",
]

# Founder-facing artifacts worth analysing, by conventional filename.
ARTIFACT_PATTERNS = [
    "README.md", "README.rst",
    "*memo*.md", "*pitch*.md", "*one-pager*.md", "*onepager*.md",
    "*narrative*.md", "*positioning*.md", "*application*.md",
    "*landing*.md", "*demo-script*.md", "*vision*.md",
    "docs/*memo*.md", "docs/*pitch*.md", "docs/*vision*.md",
]

GSTACK_PROJECTS = "~/.gstack/projects"


def find_office_hours():
    found = []
    for d in SKILL_SEARCH_DIRS:
        base = Path(d).expanduser()
        if not base.is_dir():
            continue
        for candidate in (base / "office-hours", base / "gstack" / "office-hours"):
            skill_md = candidate / "SKILL.md"
            if skill_md.is_file():
                try:
                    readable = bool(skill_md.read_text(encoding="utf-8").strip())
                except OSError as exc:
                    readable = False
                    print(f"  ! could not read {skill_md}: {exc}", file=sys.stderr)
                found.append({"path": str(candidate), "skill_md_readable": readable})
    return found


def find_artifacts(root: Path):
    seen, out = set(), []
    for pattern in ARTIFACT_PATTERNS:
        for p in root.glob(pattern):
            if p.is_file() and p not in seen:
                seen.add(p)
                out.append({"path": str(p.relative_to(root)),
                            "lines": p.read_text(encoding="utf-8", errors="replace").count("\n") + 1})
    return sorted(out, key=lambda a: a["path"])


def git_context(root: Path):
    """Git is useful context but its absence is not a blocker."""
    def run(*args):
        try:
            r = subprocess.run(["git", "-C", str(root), *args],
                               capture_output=True, text=True, timeout=10)
            return r.stdout.strip() if r.returncode == 0 else None
        except (OSError, subprocess.SubprocessError):
            return None

    if run("rev-parse", "--is-inside-work-tree") != "true":
        return {"is_repo": False}
    dirty = run("status", "--porcelain") or ""
    return {
        "is_repo": True,
        "branch": run("rev-parse", "--abbrev-ref", "HEAD"),
        "uncommitted_changes": bool(dirty.strip()),
        "changed_files": len([l for l in dirty.splitlines() if l.strip()]),
    }


def project_slug(root: Path, git):
    return root.resolve().name


def find_prior_sessions(slug: str):
    base = Path(GSTACK_PROJECTS).expanduser() / slug / "founder-reflection"
    if not base.is_dir():
        return []
    out = []
    for state in base.glob("*/session-state.json"):
        entry = {"state_file": str(state), "iteration": None,
                 "passes_completed": None, "blocked_on": None}
        try:
            data = json.loads(state.read_text(encoding="utf-8"))
            entry.update({k: data.get(k) for k in
                          ("iteration", "passes_completed", "blocked_on")})
        except (OSError, json.JSONDecodeError) as exc:
            entry["error"] = str(exc)
        entry["mtime"] = state.stat().st_mtime
        out.append(entry)
    return sorted(out, key=lambda s: s["mtime"], reverse=True)


def find_design_docs(slug: str):
    base = Path(GSTACK_PROJECTS).expanduser() / slug
    if not base.is_dir():
        return []
    docs = sorted(base.glob("*-design-*.md"), key=lambda p: p.stat().st_mtime, reverse=True)
    return [str(p) for p in docs[:5]]


def build_report(root: Path):
    oh = find_office_hours()
    git = git_context(root)
    slug = project_slug(root, git)
    artifacts = find_artifacts(root)

    blockers = []
    if not oh:
        blockers.append(
            "office-hours not found. Install once: "
            "npx skills add https://github.com/garrytan/gstack --skill office-hours  "
            "(if the host caches its skill registry, a reload or new session may be needed "
            "before it becomes discoverable -- check before reporting it absent)"
        )

    notes = []
    if not artifacts:
        notes.append("No founder-facing artifact files found. Not a blocker -- the founder can "
                     "describe the startup in chat and the truth inventory is built from that.")
    if git.get("is_repo") and git.get("uncommitted_changes"):
        notes.append(f"{git['changed_files']} uncommitted change(s) in the working tree. "
                     "Snapshot before editing any artifact, and confirm before overwriting.")
    if not git.get("is_repo"):
        notes.append("Not a git repository. Fine -- skip git context; do not initialise one.")

    return {
        "project_root": str(root.resolve()),
        "project_slug": slug,
        "git": git,
        "artifacts": artifacts,
        "office_hours_installations": oh,
        "prior_sessions": find_prior_sessions(slug),
        "prior_design_docs": find_design_docs(slug),
        "blockers": blockers,
        "notes": notes,
    }


def print_report(r):
    print("# Preflight\n")
    print(f"project: {r['project_root']}")
    print(f"slug:    {r['project_slug']}")
    g = r["git"]
    print(f"git:     {'branch ' + str(g.get('branch')) if g.get('is_repo') else 'not a repo'}"
          + (f", {g['changed_files']} uncommitted" if g.get("uncommitted_changes") else ""))

    print("\n## office-hours")
    if r["office_hours_installations"]:
        for i in r["office_hours_installations"]:
            print(f"  found: {i['path']} (SKILL.md "
                  f"{'readable' if i['skill_md_readable'] else 'NOT READABLE'})")
        if len(r["office_hours_installations"]) > 1:
            print("  ! multiple installations -- confirm which the host invokes")
    else:
        print("  not found")

    print("\n## Founder-facing artifacts")
    for a in r["artifacts"] or []:
        print(f"  {a['path']} ({a['lines']} lines)")
    if not r["artifacts"]:
        print("  none found")

    print("\n## Prior work")
    for s in r["prior_sessions"][:5]:
        blocked = f"  BLOCKED: {s['blocked_on']}" if s.get("blocked_on") else ""
        print(f"  session: iteration {s['iteration']}, "
              f"{s['passes_completed']} pass(es){blocked}")
        print(f"    {s['state_file']}")
    for d in r["prior_design_docs"]:
        print(f"  design doc: {d}")
    if not r["prior_sessions"] and not r["prior_design_docs"]:
        print("  none")

    if r["notes"]:
        print("\n## Notes")
        for n in r["notes"]:
            print(f"  - {n}")

    if r["blockers"]:
        print("\n## BLOCKERS")
        for b in r["blockers"]:
            print(f"  - {b}")
    else:
        print("\nNo blockers detected.")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("project_dir", nargs="?", default=".")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    root = Path(args.project_dir)
    if not root.is_dir():
        print(f"error: not a directory: {root}", file=sys.stderr)
        return 2

    report = build_report(root)
    if args.json:
        json.dump(report, sys.stdout, indent=2)
        print()
    else:
        print_report(report)
    return 1 if report["blockers"] else 0


if __name__ == "__main__":
    sys.exit(main())
