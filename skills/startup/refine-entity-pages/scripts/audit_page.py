#!/usr/bin/env python3
"""Mechanical quality checks on a brain page. Phases 3 and 8.

Deterministic checks only -- citation coverage, timeline integrity, section inventory,
stub classification. Judgment calls (does the source support the claim? is this inference
labeled honestly?) are not automatable and stay with the reader; this script exists so
that every pass measures the same things the same way, which is what makes plateau
detection meaningful.

Usage:
    python3 audit_page.py PAGE.md [--json]
    python3 audit_page.py PAGE.md --compare PREVIOUS-AUDIT.json

Exit codes: 0 = no blocking findings, 1 = blocking findings.
"""

import argparse
import json
import re
import sys
from pathlib import Path

# A timeline entry per the enrich template:  - **YYYY-MM-DD** | Event [Source: ...]
TIMELINE_ENTRY = re.compile(r"^\s*[-*]\s*\*\*(?P<date>\d{4}-\d{2}-\d{2})\*\*\s*\|?\s*(?P<body>.*)$")
LOOSE_BULLET = re.compile(r"^\s*[-*]\s+\S")
CITATION = re.compile(r"\[Source:[^\]]+\]|\[[^\]]+\]\(https?://[^)]+\)|https?://\S+")
EMPTY_MARKER = re.compile(r"\[No data yet\]", re.IGNORECASE)
HEADING = re.compile(r"^(?P<hashes>#{2,6})\s+(?P<title>.+?)\s*$")

# Sections that hold hard facts and therefore owe citations.
FACT_SECTIONS = {"state"}
# Person-page texture sections -- claims here must be labeled, not necessarily cited.
TEXTURE_SECTIONS = {
    "what they believe", "what they're building", "what they are building",
    "what motivates them", "hobby horses", "assessment", "trajectory",
}
BOILERPLATE_HINTS = [
    "is an ai company", "is a technology company", "is a leading provider",
    "innovative solutions", "cutting-edge", "world-class", "passionate about",
]


def split_frontmatter(text):
    """Return (frontmatter_dict, body). Minimal YAML -- top-level `key: value` only.

    Deliberately not using PyYAML: this must run anywhere without extra install, and the
    page frontmatter it needs to inspect is flat.
    """
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    raw = text[3:end]
    body = text[end + 4:]
    fm = {}
    for line in raw.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        k, _, v = line.partition(":")
        fm[k.strip().lower()] = v.strip()
    return fm, body


def parse_sections(body):
    """Split the body into sections keyed by heading, preserving order."""
    sections, current, buf = [], None, []
    for line in body.splitlines():
        m = HEADING.match(line)
        if m:
            if current is not None:
                sections.append({"title": current, "lines": buf})
            current, buf = m.group("title").strip(), []
        else:
            buf.append(line)
    if current is not None:
        sections.append({"title": current, "lines": buf})

    for s in sections:
        text = "\n".join(s["lines"])
        s["text"] = text
        s["key"] = s["title"].lower().strip()
        s["words"] = len(text.split())
        s["empty_marker"] = bool(EMPTY_MARKER.search(text))
        s["substantive"] = s["words"] >= 8 and not s["empty_marker"]
    return sections


def claim_lines(section_text):
    """Prose lines that assert something -- the unit citation coverage is measured over."""
    out = []
    for line in section_text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith(("#", ">", "|", "```")):
            continue
        if EMPTY_MARKER.search(stripped):
            continue
        if len(stripped.split()) < 4:
            continue
        out.append(stripped)
    return out


def check_citations(sections):
    stats = {"fact_claims": 0, "fact_cited": 0, "uncited_examples": [],
             "total_claims": 0, "total_cited": 0}
    for s in sections:
        claims = claim_lines(s["text"])
        cited = [c for c in claims if CITATION.search(c)]
        stats["total_claims"] += len(claims)
        stats["total_cited"] += len(cited)
        if s["key"] in FACT_SECTIONS:
            stats["fact_claims"] += len(claims)
            stats["fact_cited"] += len(cited)
            for c in claims:
                if not CITATION.search(c) and len(stats["uncited_examples"]) < 5:
                    stats["uncited_examples"].append({"section": s["title"], "claim": c[:120]})
    stats["fact_coverage"] = (
        round(stats["fact_cited"] / stats["fact_claims"], 3) if stats["fact_claims"] else None
    )
    return stats


def check_timeline(sections):
    tl = next((s for s in sections if s["key"] == "timeline"), None)
    if tl is None:
        return {"present": False, "entries": 0, "dated": 0, "sourced": 0,
                "duplicates": [], "undated_bullets": 0, "ordering_ok": None}

    dates, entries, undated = [], [], 0
    for line in tl["text"].splitlines():
        m = TIMELINE_ENTRY.match(line)
        if m:
            dates.append(m.group("date"))
            entries.append({"date": m.group("date"), "body": m.group("body").strip()})
        elif LOOSE_BULLET.match(line):
            undated += 1

    seen, dupes = {}, []
    for e in entries:
        # Same date + same event text = the classic repeated-pass duplicate.
        key = (e["date"], re.sub(r"\s+", " ", re.sub(CITATION, "", e["body"])).strip().lower())
        if key in seen:
            dupes.append(e)
        seen[key] = True

    return {
        "present": True,
        "entries": len(entries),
        "dated": len(dates),
        "sourced": sum(1 for e in entries if CITATION.search(e["body"])),
        "duplicates": [f"{d['date']} | {d['body'][:80]}" for d in dupes],
        "undated_bullets": undated,
        "ordering_ok": dates == sorted(dates, reverse=True) if dates else None,
    }


def check_boilerplate(sections):
    hits = []
    for s in sections:
        low = s["text"].lower()
        for phrase in BOILERPLATE_HINTS:
            if phrase in low:
                hits.append({"section": s["title"], "phrase": phrase})
    return hits


# ---------------------------------------------------------------------------
# TODO(contributor): implement stub classification.
#
# This is the one threshold in the audit that is a genuine judgment call, which is why
# it is not pre-decided here.
#
# The no-stub rule (references/entity-quality-model.md) says: reject a page carrying only
# a name, a title, empty headings, boilerplate, a copied bio, unverified API fields, or
# `[No data yet]` in nearly every section. But individual empty sections are legitimate --
# enrich deliberately leaves them as `[No data yet]` rather than padding them, and a Tier 3
# page is *supposed* to be small.
#
# So the trade-off runs in both directions:
#   - Too strict  -> you block legitimate minimal Tier 3 pages and push toward padding,
#                    which is the exact failure the no-stub rule exists to prevent.
#   - Too lax     -> fake knowledge artifacts enter the brain and are later read as
#                    established context by both the user and the next enrichment pass.
#
# Things worth weighing (all available in the arguments):
#   - ratio of substantive to empty sections, vs. absolute count of substantive ones
#   - whether a page can be rescued by one strong section (a real State + a dated,
#     sourced timeline entry is arguably a legitimate small page)
#   - whether an executive summary exists -- it is the "why does this matter to me" line
#   - whether the only content is boilerplate (see boilerplate_hits)
#   - whether any timeline entry exists at all; enrich requires one even on CREATE
#
# Return (is_stub, reason). The reason string is surfaced to the user and should say
# which condition decided it, e.g. "9 of 11 sections empty; no dated timeline entry".
# ---------------------------------------------------------------------------
def classify_stub(sections, has_summary, citation_stats, timeline_stats, boilerplate_hits):
    """Decide whether this page is a stub that should not exist in its current form.

    Args:
        sections: list of dicts with keys title, key, text, words, empty_marker, substantive
        has_summary: bool -- a blockquote executive summary is present
        citation_stats: dict from check_citations()
        timeline_stats: dict from check_timeline()
        boilerplate_hits: list from check_boilerplate()

    Returns:
        (is_stub: bool, reason: str)
    """
    raise NotImplementedError("classify_stub: see the TODO above")


def audit(path: Path):
    text = path.read_text(encoding="utf-8")
    fm, body = split_frontmatter(text)
    sections = parse_sections(body)
    has_summary = any(l.strip().startswith(">") for l in body.splitlines())

    citations = check_citations(sections)
    timeline = check_timeline(sections)
    boilerplate = check_boilerplate(sections)

    try:
        is_stub, stub_reason = classify_stub(sections, has_summary, citations, timeline,
                                             boilerplate)
    except NotImplementedError as exc:
        is_stub, stub_reason = None, f"not evaluated ({exc})"

    findings = []

    if not fm:
        findings.append(("blocking", "schema-conformance", "No frontmatter."))
    elif fm.get("type") not in {"person", "company"}:
        findings.append(("major", "schema-conformance",
                         f"frontmatter type is {fm.get('type')!r}; expected person or company."))

    if not has_summary:
        findings.append(("major", "state",
                         "No executive summary. The page never says why this entity matters."))

    if citations["fact_claims"] and citations["fact_coverage"] < 1.0:
        n = citations["fact_claims"] - citations["fact_cited"]
        findings.append(("blocking", "citation",
                         f"{n} of {citations['fact_claims']} State claims uncited."))

    if not timeline["present"]:
        findings.append(("blocking", "timeline", "No Timeline section."))
    else:
        if timeline["entries"] == 0:
            findings.append(("blocking", "timeline", "Timeline has no dated entries."))
        if timeline["duplicates"]:
            findings.append(("major", "timeline",
                             f"{len(timeline['duplicates'])} duplicate timeline entries."))
        if timeline["ordering_ok"] is False:
            findings.append(("major", "timeline", "Timeline is not reverse-chronological."))
        if timeline["undated_bullets"]:
            findings.append(("major", "timeline",
                             f"{timeline['undated_bullets']} undated timeline bullets."))
        unsourced = timeline["entries"] - timeline["sourced"]
        if unsourced > 0:
            findings.append(("major", "citation", f"{unsourced} timeline entries lack a source."))

    if boilerplate:
        findings.append(("minor", "duplicate-content",
                         f"Boilerplate phrasing in {len(boilerplate)} place(s)."))

    if is_stub:
        findings.append(("blocking", "stub-page", stub_reason))

    empty = [s["title"] for s in sections if not s["substantive"]]

    return {
        "page": str(path),
        "type": fm.get("type"),
        "sections": len(sections),
        "sections_substantive": sum(1 for s in sections if s["substantive"]),
        "sections_empty": empty,
        "has_summary": has_summary,
        "citations": citations,
        "timeline": timeline,
        "boilerplate": boilerplate,
        "stub": {"is_stub": is_stub, "reason": stub_reason},
        "findings": [{"severity": s, "taxonomy": t, "detail": d} for s, t, d in findings],
    }


def print_report(r):
    print(f"# Audit -- {r['page']}\n")
    print(f"type: {r['type']}   sections: {r['sections_substantive']}/{r['sections']} substantive")
    if r["sections_empty"]:
        print(f"empty: {', '.join(r['sections_empty'])}")

    c = r["citations"]
    cov = "n/a" if c["fact_coverage"] is None else f"{c['fact_coverage']:.0%}"
    print(f"\nState citation coverage: {cov} ({c['fact_cited']}/{c['fact_claims']})")
    for u in c["uncited_examples"]:
        print(f"  uncited: {u['claim']}")

    t = r["timeline"]
    if t["present"]:
        order = {True: "ok", False: "BROKEN", None: "n/a"}[t["ordering_ok"]]
        print(f"\nTimeline: {t['entries']} entries, {t['sourced']} sourced, "
              f"ordering {order}, duplicates {len(t['duplicates'])}")
        for d in t["duplicates"]:
            print(f"  dup: {d}")
    else:
        print("\nTimeline: MISSING")

    print(f"\nStub: {r['stub']['is_stub']} -- {r['stub']['reason']}")

    print("\n## Findings")
    if not r["findings"]:
        print("  none")
    for f in r["findings"]:
        print(f"  [{f['severity']}] {f['taxonomy']}: {f['detail']}")


def compare(current, previous_path):
    """Plateau check: are the same gaps recurring with the same status?"""
    prev = json.loads(Path(previous_path).read_text(encoding="utf-8"))
    now_keys = {(f["taxonomy"], f["detail"]) for f in current["findings"]}
    old_keys = {(f["taxonomy"], f["detail"]) for f in prev.get("findings", [])}
    print("\n## Versus previous audit")
    print(f"  resolved: {len(old_keys - now_keys)}")
    print(f"  new:      {len(now_keys - old_keys)}")
    print(f"  repeated: {len(now_keys & old_keys)}")
    if now_keys and now_keys == old_keys:
        print("  PLATEAU -- identical findings. Another enrich pass needs new evidence,")
        print("  not another attempt. See quality-rubric.md 'Detecting a plateau'.")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("page")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--compare", metavar="PREVIOUS_JSON")
    args = ap.parse_args()

    path = Path(args.page)
    if not path.is_file():
        print(f"error: no such page: {path}", file=sys.stderr)
        return 2

    result = audit(path)
    if args.json:
        json.dump(result, sys.stdout, indent=2)
        print()
    else:
        print_report(result)
        if args.compare:
            compare(result, args.compare)

    return 1 if any(f["severity"] == "blocking" for f in result["findings"]) else 0


if __name__ == "__main__":
    sys.exit(main())
