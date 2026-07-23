---
name: refine-entity-pages
description: Audit, repair, and verify GBrain person and company entity pages against the enrichment quality bar, then drive the official enrich skill and check what it actually wrote. Use whenever someone wants to review a person page, improve a company page, make a GBrain entity page useful, fix missing citations or timeline gaps, prepare a page before running enrich, run enrich and inspect the result, find unsupported claims in a profile, repair person/company cross-links, check whether a page is a stub, update an entity without overwriting their own assessment, audit a GBrain enrichment, or decide whether an entity deserves Tier 1, Tier 2, or Tier 3 research. Reach for this even when the request sounds like a plain "just enrich this person" — identity resolution, privacy proportionality, and a recoverable snapshot run first, and the page is re-read from GBrain before any claim that it improved.
---

# Refine Entity Pages

Quality-guided refinement for GBrain person and company pages. This skill inspects a page,
explains what is weak, repairs what evidence supports, hands the actual research and mutation
to the official `enrich` skill, then re-reads the result and decides whether another pass is
worth it.

The goal is never a longer page. It is a page that is more accurate, better sourced, better
connected, more current, and more explicit about what remains uncertain — one that resists
identity mistakes and respects private information.

## The responsibility split

Keeping this boundary clean is what makes the skill safe. `enrich` is a mutating skill with its
own protocol; wrapping it means auditing it, not reimplementing it.

| This skill owns | `enrich` owns |
|---|---|
| Target resolution, identity confidence | Brain-first lookup, tier-aware external research |
| Baseline snapshot and rollback | Source extraction, raw external-data preservation |
| Page-quality audit, gap classification | CREATE / UPDATE execution, page mutations |
| Source and claim ledger | Compiled-truth updates, timeline writes |
| Privacy and proportionality review | Cross-reference updates, auto-linking |
| Candidate refinement (drafts only) | Its own validation rules |
| Pre/post comparison, convergence, reporting | |

Never reimplement `enrich`'s protocol here and call that integration, and never edit `enrich`
to make this skill's checks pass. When invoking it, supply the entity, existing context, source
material, and intended tier — never a desired verdict. Instructions like "confirm this page is
high quality" or "preserve all my conclusions" corrupt the one independent check in the loop.

## Non-negotiables

Five rules carry most of the safety. Everything else is elaboration.

1. **Resolve identity before any mutation.** A page written about the wrong person is worse
   than no page, and it is expensive to detect later. When multiple candidates share a name,
   produce an identity-resolution brief and stop.
2. **Snapshot before every material write.** `enrich` mutates. Recovery is only possible if the
   prior version and a content hash exist first.
3. **Re-read the page from GBrain after every write.** Judging a result from cached pre-write
   content is how "validation passed" becomes a false claim. If you did not re-read it, you do
   not know what it says.
4. **Never present inference as fact.** Belief, motivation, and trajectory are interpretations.
   Label them as such, or leave them out.
5. **Scale intrusion to the relationship.** "Available on the internet" does not mean
   "appropriate to preserve in someone's personal brain."

## Phase map

Work through these in order. Read the reference for a phase when you reach it, not up front —
the whole point of the split is to keep this router in context and the depth out of it.

| Phase | What happens | Read first | Writes? |
|---|---|---|---|
| 0 | Environment and dependency preflight | `references/enrich-integration.md` | session state only |
| 1 | Target resolution | `references/identity-and-notability.md` | no |
| 2 | Baseline snapshot | `references/output-contracts.md` | session artifacts only |
| 3 | Page-quality audit | `references/entity-quality-model.md` | no |
| 4 | Tier and research plan | `references/privacy-and-sensitive-data.md` | no |
| 5 | Claim and source ledger | `references/claim-and-citation-rules.md` | no |
| 6 | Candidate refinement | `references/entity-quality-model.md` | drafts only |
| 7 | Invoke `enrich` | `references/enrich-integration.md` | **yes, via enrich** |
| 8 | Post-enrich verification | `references/enrich-integration.md` | no |
| 9 | Controlled refinement loop | `references/quality-rubric.md` | via 6–7 |
| 10 | Final handoff | `references/output-contracts.md` | no |

Phases 0–6 never touch the brain. That is deliberate: everything reversible happens before
anything irreversible does.

### Phase 0 — Preflight

Run `scripts/preflight.py` to discover the environment, then confirm what it could not:

- Is `enrich` installed and discoverable? If not, install it once with
  `npx skills add https://github.com/garrytan/gbrain --skill enrich`. Never reinstall on every
  invocation, and do not invent non-interactive flags — inspect the command's help instead.
- Is the GBrain runtime reachable (CLI or MCP)? Installing a skill definition does not make the
  underlying tools available; verify separately.
- Which brain and source are active? **If routing is ambiguous, refuse to mutate.** Defaulting
  to a random brain when several are configured writes real content into the wrong place.
- Do read *and* write permissions exist? Are raw-data, timeline, and auto-link operations
  available? Their absence changes what you can promise, not just what you can do.
- Read the active brain's filing rules and quality conventions if present (`enrich` expects
  them at `skills/_brain-filing-rules.md` and `skills/conventions/quality.md` within the brain
  repo — they are the brain's files, not this skill's).
- Look for a previous refinement session to resume.

Record host limitations now. A limitation discovered at phase 7 has already cost the user a
pass.

### Phase 1 — Target resolution

Brain-first, always: search the brain before any external lookup. It is free, it is the richest
source of relationship context, and it is what prevents duplicate pages.

Establish canonical identity, existing page path and type, aliases, duplicate candidates, the
user's relationship, freshness, last enrichment date, and whether a **material new signal**
actually exists. Where the retrieval surface offers confidence hints (`exists` / `probable` /
`unknown`), use them — and do not read one weak semantic match as proof a page exists.

If identity confidence is insufficient, stop before any write. See
`references/identity-and-notability.md`.

### Phase 2 — Baseline snapshot

Run `scripts/snapshot.py` to capture the complete current page, a content hash, backlinks,
typed links, timeline, citations, user-authored sections, and unresolved contradictions.

Never overwrite the baseline on later passes — each pass gets its own record, or the audit
trail is worthless.

### Phase 3 — Page-quality audit

Score the baseline against the rubric and produce a gap map. Run `scripts/audit_page.py` for
the mechanical checks (citation coverage, timeline dates and ordering, duplicate entries,
stub detection, empty-section ratio); judge the rest by reading.

Every gap gets: dimension, current content, the problem, why it matters, evidence status,
proposed correction, mutation risk, whether `enrich` should handle it, whether the user must
approve, and severity. Gap taxonomy and the 20 quality dimensions are in
`references/entity-quality-model.md`; the 0–4 scale and gates are in
`references/quality-rubric.md`.

### Phase 4 — Tier and research plan

Recommend Tier 1, 2, or 3 and justify the *proportionality*, not just the importance. Tier 1
depth on a peripheral contact is a privacy problem even when the data is easy to get. Do not
choose Tier 1 merely because an API would return something.

State which sources to use, which to avoid, what is already known, what delta is needed, which
calls cost money, and which research could expose private data. Ask for authorization before
paid, invasive, or credentialed research. See `references/privacy-and-sensitive-data.md`.

### Phase 5 — Claim and source ledger

Build the ledger before drafting anything. Its purpose is structural: an unsupported claim
cannot become compiled truth if every claim must first carry a source, a date, a tier, a
confidence, and a contradiction status.

Format, claim types, source precedence, and citation-validity rules are in
`references/claim-and-citation-rules.md`.

### Phase 6 — Candidate refinement

Draft the improved page or patch *without* destroying the current one. Repairs that need no new
evidence — separating fact from interpretation, labeling uncertainty, deduplicating, reordering
the timeline, removing API boilerplate, adding contradiction notes — belong here. Gaps that need
new external evidence belong to `enrich`.

Show a concise change summary before any material write.

### Phase 7 — Invoke enrich

Invoke the real installed skill through the host's native mechanism. Reading `enrich`'s file is
not invoking it, and summarizing its protocol yourself is not running it.

Provide identity, page path, CREATE/UPDATE status, tier, the material new signal, source
material, routing, identity constraints, and privacy boundaries. Then record what it did:
sources queried, raw data saved, page writes, timeline entries, compiled-truth and
cross-reference changes, `auto_links` results, skipped sources, validation flags, failures,
and the final page path.

If skill-to-skill invocation is unavailable, do not fake it — save state and return a resumable
handoff telling the user exactly what to run. `references/enrich-integration.md` has both paths.

### Phase 8 — Post-enrich verification

Re-read the page fresh from GBrain, then compare baseline → candidate → actual result. Look
specifically for the failure modes an enrichment pass produces: unexpected overwrites, missing
user-authored text, unsupported additions, duplicated or misordered timeline entries, identity
drift, auto-link errors, privacy regressions, and boilerplate padding.

Produce a structured delta report.

### Phase 9 — Controlled refinement loop

Another pass is justified only by new evidence or a concrete correction — never by a wish for a
better score. Default ceiling is **three `enrich` passes per entity per invocation**.

Stop when the quality gate is met, the user accepts the result, only external evidence is
missing, identity is unresolved, two passes produce materially identical findings, no new
signal exists, further work would only add prose length, the page was enriched inside the
freshness window, privacy or authorization blocks research, or the next change risks
overwriting the user's own judgment.

Never add duplicate timeline entries to make a page look more complete.

### Phase 10 — Final handoff

Report per the contract in `references/output-contracts.md`: final path, identity and
confidence, CREATE/UPDATE result, tier, baseline and final quality summaries, sources used and
skipped, provenance status, citations repaired, timeline entries added, contradictions
preserved, cross-links verified, privacy decisions, remaining unknowns, iteration count, **why
the loop stopped**, and the recommended next action.

## Approval gates

Pause and ask before: creating a new person page, merging duplicate identities, changing a
user-written assessment, removing substantial historical content, adding sensitive relationship
information, escalating an entity to Tier 1, bulk mutation, resolving an identity conflict, or
syncing private brain content anywhere external.

When the user says "just enrich it," you still owe them target resolution, brain-first lookup,
the CREATE/UPDATE decision, a privacy check, and a minimal snapshot. Those five are fast, and
they are exactly what prevents the expensive mistakes.

## A no-mutation run is a valid result

If the evidence does not support a page, the correct outcomes include: no mutation, save raw
evidence only, ask the user, record an unresolved candidate, or defer enrichment. Do not force
every run to end in a write — a fabricated knowledge artifact costs more than an absent one,
because it will later be trusted.

## When things break

Report the exact blocker, the current target, active routing, work completed, preserved
artifacts, any mutations already made, the recovery action, and a precise resume instruction.

Two failure modes deserve naming because they are silent: claiming validation passed without
re-reading the page, and re-invoking `enrich` with no material delta. Both produce output that
looks like progress. Error handling in depth is in `references/enrich-integration.md`.

## Bulk mode

Bulk work amplifies every error, so it earns extra gates: resolve and deduplicate the list,
sample 3–5 entities through the full workflow, show the sample output, and require approval
before proceeding. Then bound the batches, respect rate limits, checkpoint every 5–10 entities,
pause on identity ambiguity or schema mismatch, and never push automatically. Full procedure and
the audit report shape are in `references/enrich-integration.md`.

## Scripts

Deterministic checks only — they exist so each pass measures the page the same way, not to hide
prose. Run them; do not reason about what they would have said.

| Script | Use |
|---|---|
| `scripts/preflight.py` | Phase 0 — locate `enrich`, probe GBrain runtime and permissions, find resumable sessions |
| `scripts/snapshot.py` | Phase 2 and before every write — snapshot, content hash, diff against a prior snapshot |
| `scripts/audit_page.py` | Phase 3 and 8 — citation coverage, timeline integrity, stub detection, section inventory |

## References

| File | Contents |
|---|---|
| `references/entity-quality-model.md` | The 20 quality dimensions, gap taxonomy, compiled truth, State, texture, timeline |
| `references/identity-and-notability.md` | Identity resolution, notability gate, CREATE vs UPDATE, tier selection |
| `references/claim-and-citation-rules.md` | Source precedence, claim ledger, citation validity, contradictions, raw provenance |
| `references/privacy-and-sensitive-data.md` | Safety model, proportionality, prohibited inferences |
| `references/enrich-integration.md` | `enrich`'s interface, invocation and handoff, verification, bulk mode, error recovery |
| `references/quality-rubric.md` | 0–4 scale, per-dimension evidence, readiness gates |
| `references/output-contracts.md` | Session artifacts, resumability, final report shape |
| `references/enrich-source/` | Vendored copy of the `enrich` skill, reference-only |

Source material: the `enrich` skill by Garry Tan (https://github.com/garrytan/gbrain), vendored
under `references/enrich-source/`.
