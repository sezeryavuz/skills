# Output Contracts

Where session artifacts live, what they contain, and the shape of the final report. Used in
Phases 2 and 10, and whenever a run is interrupted.

## Contents

- [Where artifacts live](#where-artifacts-live)
- [Artifact set](#artifact-set)
- [session-state.json](#session-statejson)
- [Persistence rules](#persistence-rules)
- [Resuming an interrupted run](#resuming-an-interrupted-run)
- [The final handoff report](#the-final-handoff-report)
- [Reporting a no-mutation outcome](#reporting-a-no-mutation-outcome)

## Where artifacts live

Store refinement artifacts **outside the installed skill folder** — a skill directory is code,
not state, and writing session data into it makes the skill unclean to update or reinstall.

Prefer a path established by the active GBrain conventions, or:

```
~/.gbrain/refinement-sessions/{brain-id}/{entity-slug}/{session-id}/
```

Keying by `brain-id` matters when multiple brains exist: it keeps two sessions about
same-named entities in different brains from colliding.

## Artifact set

| File | Written in | Contents |
|---|---|---|
| `00-target-resolution.md` | Phase 1 | Canonical identity, candidates considered, confidence, page path |
| `01-baseline.md` | Phase 2 | Complete pre-change page, content hash, links, timeline, citations |
| `02-source-inventory.md` | Phase 4–5 | Every source available, its tier, what it can support |
| `03-claim-ledger.md` | Phase 5 | The claim ledger from `claim-and-citation-rules.md` |
| `04-quality-audit.md` | Phase 3 | Rubric scores with evidence, plus the gap map |
| `05-refinement-plan.md` | Phase 6 | Proposed changes, owner per gap, approval requirements |
| `candidate-page.md` | Phase 6 | The drafted page or patch, before any mutation |
| `enrich-pass-01.md` … `-03.md` | Phase 7–8 | Per pass: what was provided, what enrich did, the post-write page as re-read |
| `final-delta.md` | Phase 8 | Baseline → candidate → actual comparison |
| `final-quality-report.md` | Phase 10 | The handoff report below |
| `session-state.json` | Continuously | Machine-readable resume point |

Not every run produces all of these. A run that stops at an identity block produces
`00-target-resolution.md` and a `session-state.json` — which is the correct output for that run.

## session-state.json

```json
{
  "session_id": "…",
  "brain_id": "…",
  "source_routing": "…",
  "entity": { "canonical_name": "…", "type": "person|company", "slug": "…",
              "page_path": "…", "identity_confidence": "high|medium|low|unresolved" },
  "mode": "CREATE|UPDATE|TIMELINE_ONLY|RAW_ONLY|SKIP",
  "tier": 1,
  "phase": 7,
  "iteration": 2,
  "max_iterations": 3,
  "baseline_hash": "…",
  "current_hash": "…",
  "mutations_applied": [ { "pass": 1, "type": "put_page", "at": "…", "hash_after": "…" } ],
  "approvals": { "create_page": true, "tier_1_escalation": false },
  "privacy_boundaries": ["no family information", "removed: unsourced motivation claim"],
  "open_gaps": [ { "id": "G3", "taxonomy": "citation", "status": "blocked_on_external" } ],
  "blocked_on": null,
  "resume_instruction": "…"
}
```

`privacy_boundaries` and `mutations_applied` are the two fields that must never be dropped on
resume. The first prevents a later pass reintroducing a claim that was deliberately removed;
the second is the only record of what has already been written to the real brain.

## Persistence rules

- Preserve the original page and each actual post-enrich version. Never overwrite the baseline.
- Associate each pass with the sources it used.
- Make interrupted sessions resumable.
- Do not store API credentials. Redact tokens and secrets from diagnostics.
- Do not duplicate raw data GBrain already stores safely.
- Keep private data out of logs.
- Do not write telemetry unless the user or the active GBrain policy explicitly permits it.

## Resuming an interrupted run

1. Read `session-state.json`.
2. Re-read the live page from GBrain and compare its hash to `current_hash`. **If it differs,
   someone or something else has written since — re-snapshot and re-audit rather than resuming
   against a stale picture.**
3. Restore privacy boundaries and approvals. Approvals do not expire within a session, but they
   also do not widen: an approval to create a page is not an approval to escalate to Tier 1.
4. Resume at the recorded phase.

## The final handoff report

```markdown
# Refinement report — <canonical name>

**Final page:** <path>
**Identity:** <canonical name> · confidence <high|medium|low>
**Result:** <CREATE|UPDATE|TIMELINE_ONLY|RAW_ONLY|NO_MUTATION>
**Tier:** <1|2|3> — <why this was proportionate>

## Quality
| | Baseline | Final |
|---|---|---|
| Refinement readiness score | <n>/80 | <n>/80 |
| Blocking gaps | <n> | <n> |
<per-dimension movement for dimensions that changed>

## What changed
- **Citations:** <added/repaired n>
- **Timeline:** <n entries added; duplicates removed: n>
- **Contradictions preserved:** <list>
- **Cross-links verified:** <n; errors: n>
- **User-authored content:** <preserved / changed with approval — detail>

## Sources
**Used:** <source — what it supported>
**Skipped:** <source — why>
**Raw provenance:** <stored / unavailable — why>

## Privacy decisions
<what was collected, what was deliberately not, what was removed and why>

## What remains
**Unknowns:** <list>
**Evidence gaps:** <what would resolve each>
**Open threads:** <actionable items>

## Loop
**Passes:** <n> of <max>
**Stopped because:** <the specific condition from quality-rubric.md>
**Recommended next action:** <concrete, or "none — page is current">
```

Two fields carry most of the value. **Stopped because** tells the user whether they got a
finished page or a blocked one. **Recommended next action** turns a remaining gap into
something they can act on.

## Reporting a no-mutation outcome

A run that writes nothing still owes a full account. Report it as a result, not a failure:

```markdown
# No mutation — <entity as given>

**Reason:** <identity unresolved | notability gate not met | insufficient evidence |
             recently enriched, no new signal | write permission unavailable |
             authorization required for the research needed>

**What was checked:** <brain search performed, candidates found, sources reviewed>
**What was preserved:** <raw evidence saved, unresolved candidate recorded — with paths>
**What would unblock it:** <the specific signal or authorization required>
**Session state:** <path> — resumable
```

Padding a page to justify a run is worse than returning nothing, because the padding will later
be read as knowledge. "I looked, and here is precisely why there is nothing to write" is a
useful answer.
