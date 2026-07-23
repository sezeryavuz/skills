#!/usr/bin/env python3
"""Snapshot a brain page before mutation, and diff snapshots afterwards.

`enrich` mutates. Recovery is only possible if the prior version and a content hash exist
first, and Phase 8 can only detect a silent overwrite by comparing against what was there
before. This script is the mechanical half of both.

Usage:
    # Phase 2, and again before every material write
    python3 snapshot.py save PAGE.md --session DIR [--label baseline]

    # Phase 8 -- what actually changed
    python3 snapshot.py diff DIR/01-baseline.md PAGE.md

    # Cheap staleness check on resume
    python3 snapshot.py hash PAGE.md

Snapshots are written with a `label`, so successive passes never overwrite the baseline.
"""

import argparse
import datetime
import difflib
import hashlib
import json
import sys
from pathlib import Path


def content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def now_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")


def cmd_save(args) -> int:
    page = Path(args.page)
    if not page.is_file():
        print(f"error: no such page: {page}", file=sys.stderr)
        return 2

    text = page.read_text(encoding="utf-8")
    session = Path(args.session).expanduser()
    session.mkdir(parents=True, exist_ok=True)

    label = args.label
    dest = session / (f"01-baseline.md" if label == "baseline" else f"snapshot-{label}.md")

    # Refuse to clobber an existing baseline: the audit trail depends on it surviving.
    if dest.exists() and label == "baseline" and not args.force:
        print(f"error: baseline already exists at {dest}", file=sys.stderr)
        print("       later passes must use --label pass-N, not overwrite the baseline.",
              file=sys.stderr)
        return 3

    dest.write_text(text, encoding="utf-8")

    meta = {
        "label": label,
        "source_page": str(page),
        "captured_at": now_iso(),
        "content_hash": content_hash(text),
        "bytes": len(text.encode("utf-8")),
        "lines": text.count("\n") + 1,
        "snapshot_path": str(dest),
    }
    meta_path = session / f"snapshot-{label}.json"
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")

    print(f"saved   {dest}")
    print(f"hash    {meta['content_hash']}")
    print(f"meta    {meta_path}")
    return 0


def cmd_diff(args) -> int:
    before_p, after_p = Path(args.before), Path(args.after)
    for p in (before_p, after_p):
        if not p.is_file():
            print(f"error: no such file: {p}", file=sys.stderr)
            return 2

    before = before_p.read_text(encoding="utf-8")
    after = after_p.read_text(encoding="utf-8")

    hb, ha = content_hash(before), content_hash(after)
    if hb == ha:
        print("identical -- no change written")
        print(f"hash {hb}")
        return 0

    b_lines, a_lines = before.splitlines(), after.splitlines()
    added = sum(1 for l in difflib.ndiff(b_lines, a_lines) if l.startswith("+ "))
    removed = sum(1 for l in difflib.ndiff(b_lines, a_lines) if l.startswith("- "))

    print(f"hash  {hb}\n   -> {ha}")
    print(f"lines +{added} -{removed}\n")

    if removed:
        print("NOTE: lines were removed. Check them against user-authored sections and the")
        print("      timeline before accepting -- append-only is the expectation.\n")

    print("\n".join(
        difflib.unified_diff(b_lines, a_lines,
                             fromfile=str(before_p), tofile=str(after_p),
                             lineterm="", n=2)
    ))
    return 0


def cmd_hash(args) -> int:
    p = Path(args.page)
    if not p.is_file():
        print(f"error: no such page: {p}", file=sys.stderr)
        return 2
    print(content_hash(p.read_text(encoding="utf-8")))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("save", help="snapshot a page into a session directory")
    s.add_argument("page")
    s.add_argument("--session", required=True, help="session directory")
    s.add_argument("--label", default="baseline", help="baseline (default) or e.g. pass-1")
    s.add_argument("--force", action="store_true", help="allow overwriting a baseline")
    s.set_defaults(func=cmd_save)

    d = sub.add_parser("diff", help="compare two versions")
    d.add_argument("before")
    d.add_argument("after")
    d.set_defaults(func=cmd_diff)

    h = sub.add_parser("hash", help="print a page's content hash")
    h.add_argument("page")
    h.set_defaults(func=cmd_hash)

    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
