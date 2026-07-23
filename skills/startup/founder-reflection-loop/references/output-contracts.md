# Output Contracts

Where iteration artifacts live, how versioning works, and the shape of the final founder
package. Used in Phases 0, 5, 9, and when resuming.

## Contents

- [Where artifacts live](#where-artifacts-live)
- [Artifact set](#artifact-set)
- [session-state.json](#session-statejson)
- [Versioning rules](#versioning-rules)
- [Resuming](#resuming)
- [The final founder package](#the-final-founder-package)
- [Validation assignments](#validation-assignments)
- [Reporting a blocked run](#reporting-a-blocked-run)

## Where artifacts live

**Outside the installed skill folder, and outside the founder's repository** unless they ask
otherwise. A skill directory is code, not state; and writing session files into a founder's
repo pollutes a working tree they may be about to commit.

Use a gstack-compatible location:

```
~/.gstack/projects/{project-slug}/founder-reflection/{session-id}/
```

This sits alongside where `office-hours` writes its design docs
(`~/.gstack/projects/{slug}/*-design-*.md`), which keeps a session's inputs and its diagnostic
outputs discoverable together.

## Artifact set

| File | Written in | Contents |
|---|---|---|
| `00-source-inventory.md` | Phase 2 | Every artifact supplied, what it claims, contradictions between them |
| `01-baseline.md` | Phase 0/2 | The founder's original artifact, unmodified |
| `02-truth-inventory.md` | Phase 2 | Every important claim, its classification, its source |
| `03-gap-map.md` | Phase 3 | The gap map with repair types and severities |
| `iteration-01.md` … `-03.md` | Phase 5 | Each revised version of the artifact |
| `office-hours-pass-01.md` … `-03.md` | Phase 6 | Per pass: what was provided, design-doc path, findings, decisions |
| `final-founder-narrative.md` | Phase 9 | The final artifact |
| `final-readiness-report.md` | Phase 9 | The package below |
| `session-state.json` | Continuously | Machine-readable resume point |

Not every run produces all of these. A run that stops because only evidence gaps remain
produces the inventories, the gap map, and a validation-assignment list — which is the correct
and useful output for that situation.

## session-state.json

```json
{
  "session_id": "…",
  "project_slug": "…",
  "stage": "pre-product|prototype|users|paying|internal",
  "audience": "who will read the artifact",
  "artifact": { "original_path": "…", "baseline": "01-baseline.md",
                "current_iteration": 2, "current_path": "iteration-02.md" },
  "iteration": 2,
  "max_office_hours_passes": 3,
  "passes_completed": 1,
  "readiness": { "demand_reality": 1, "status_quo_clarity": 3, "…": 0 },
  "open_gaps": [
    { "id": "G4", "dimension": "observation_quality", "repair_type": "observe_users",
      "status": "requires_real_world_evidence" }
  ],
  "founder_decisions": [
    { "question": "wedge vs platform positioning", "decision": "lead with wedge",
      "at": "iteration-02" }
  ],
  "premises": [
    { "claim": "ops leads will pay to remove the spreadsheet",
      "state": "unresolved", "falsified_by": "three ops leads decline at $200/mo" }
  ],
  "blocked_on": null,
  "resume_instruction": "…"
}
```

`founder_decisions` and `premises` are the fields that must survive a resume. Without them a
later pass re-opens a scope question the founder already settled — which reads as the skill not
listening, and wastes the one resource a founder cannot replace.

Validate with `scripts/session.py validate`.

## Versioning rules

- **Preserve the original input.** Never overwrite the founder's artifact without a recoverable
  baseline. `scripts/session.py snapshot` handles this.
- Make every iteration traceable, and record which `office-hours` output belongs to which
  revision. Without that mapping, delta analysis compares the wrong pair.
- Make interrupted sessions resumable.
- Do not commit project artifacts unless explicitly requested; do not push.
- Do not write telemetry unless the founder or existing gstack policy permits it.
- Avoid storing secrets, private customer data, or unnecessary personal information. If a
  supplied artifact contains them, flag it and keep them out of session files.

## Resuming

1. Read `session-state.json`.
2. Check whether the founder's artifact changed since the last snapshot — if it did, they have
   been editing, and their changes take precedence. Re-baseline rather than overwriting.
3. Reload open gaps, founder decisions, and premise states.
4. Resume at the recorded phase.

Decisions do not expire within a session, and they do not widen: approval to rewrite a landing
page is not approval to restructure the product memo.

## The final founder package

```markdown
# Founder reflection — {project}

**Artifact:** {path}   **Stage:** {stage}   **Audience:** {who this is written for}
**Office-hours passes:** {n} of {max}

## Startup truth summary
{What is known, in plain language, separated from what is believed.}

**Strongest evidence:** {the single best-supported claim, and what supports it}
**Remaining assumptions:** {each, with what would falsify it}

## The current answer to each question
- **Specific target user:** …
- **Status quo:** …
- **Narrowest wedge:** … (distinct from the platform vision: …)
- **Distribution plan:** …
- **Future-fit thesis:** …

## Readiness
| Dimension | Baseline | Final | Moved by |
|---|---|---|---|
| … | 1 | 3 | evidence added / rewriting / unchanged |

## Unresolved gaps
| Gap | Repair type | Why it is still open |
|---|---|---|

## Real-world assignments
{Concrete actions — see below}

## Iteration history
{Per pass: what changed, what office-hours found, what the founder decided}

## Why the final version is more credible
{The honest answer. If it is more credible only because claims were softened to match the
evidence, say exactly that — it is a real improvement and worth naming.}

## Recommended next action
{One thing.}
```

The "why it is more credible" section is the one that keeps this skill honest. If the only
change was that overstated claims became accurate, that is a genuine and valuable outcome — and
saying so plainly prevents the package from reading as though the startup itself got stronger.

## Validation assignments

Every gap whose repair type is `collect evidence`, `observe users`, `validate willingness to
pay`, or `test distribution` becomes a concrete assignment. Vague ones do not get done.

```markdown
### Assignment {n}: {short title}
**Closes gap:** {gap id — dimension}
**Do:** {a specific action — who to contact, what to watch, what to ask}
**Success looks like:** {the observation or behavior that would resolve the gap}
**Failure looks like:** {what would falsify the premise — equally informative}
**Then:** {what this unblocks in the artifact}
```

Naming what failure looks like matters as much as naming success. An assignment that can only
confirm the founder's belief is not a test, and running it teaches nothing.

## Reporting a blocked run

```markdown
# Blocked — {project}

**What is blocked:** {specific}
**What was discovered:** {the analysis that did complete}
**What was preserved:** {paths — baseline, inventories, gap map, iterations}
**Exact next action:** {what the founder or the environment must do}
**How to resume:** {command or instruction}
```

A blocked run that hands over a truth inventory and a gap map has delivered most of this
skill's value. Say what was learned rather than only what failed.
