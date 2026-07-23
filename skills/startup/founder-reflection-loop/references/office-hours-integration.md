# Office-Hours Integration

How to verify, invoke, and read the output of the `office-hours` skill. Used in Phases 0, 6, 7,
and for error recovery.

## Contents

- [What office-hours is](#what-office-hours-is)
- [What it produces](#what-it-produces)
- [The quality score — read this before reporting one](#the-quality-score--read-this-before-reporting-one)
- [Dependency preflight](#dependency-preflight)
- [Invoking it](#invoking-it)
- [Its STOP points](#its-stop-points)
- [The handoff fallback](#the-handoff-fallback)
- [Delta analysis](#delta-analysis)
- [Error and recovery behavior](#error-and-recovery-behavior)

## What office-hours is

An independent startup diagnostic that runs a founder through forcing questions, challenges
premises, generates alternatives, and writes a design document. It has two modes: **startup
mode** (the rigorous product diagnostic) and **builder mode** (an enthusiastic design partner
for side projects, hackathons, learning, and open source).

This skill's work sits alongside **startup mode**. If a founder's goal is genuinely a side
project or a hackathon, `office-hours` will route to builder mode — and much of the analysis
here (demand evidence, willingness to pay, distribution) simply does not apply. Notice that
early rather than pushing commercial rigor onto someone building for fun.

Its hard gate: it produces design documents, never code. It will not scaffold, implement, or
invoke an implementation skill.

A vendored copy lives in `office-hours-source/` — reference only, renamed so it cannot be
discovered as an active skill. Never edit the installed copy to make this skill's checks pass.

## What it produces

A design doc at `~/.gstack/projects/{slug}/{user}-{branch}-design-{datetime}.md`. The
startup-mode template maps almost one-to-one onto the dimensions in
`startup-analysis-criteria.md`, which is what makes delta analysis tractable:

| Design-doc section | Dimension it evidences |
|---|---|
| Problem Statement | 3 Desperate specificity |
| Demand Evidence | 1 Demand reality |
| Status Quo | 2 Status quo |
| Target User & Narrowest Wedge | 3, 4 |
| Premises | 7 Premise integrity |
| Approaches Considered / Recommended Approach | product-definition decisions |
| Open Questions | unresolved gaps |
| Success Criteria | measurability |
| Distribution Plan | 8 Distribution reality |
| The Assignment | the concrete next real-world action |
| Reviewer Concerns | unresolved issues from adversarial review |
| What I noticed about how you think | founder-signal observations |

Completion statuses it reports: **DONE** (design doc approved) · **DONE_WITH_CONCERNS**
(approved with open questions listed) · **NEEDS_CONTEXT** (questions unanswered, design
incomplete). A `NEEDS_CONTEXT` result means the pass did not really happen — do not treat it as
a validation pass or count it against the three-pass ceiling.

## The quality score — read this before reporting one

`office-hours` can produce a **1–10 quality score**, and misreporting it is the easiest way for
this skill to violate its own rules. Three facts govern it:

1. **It scores the document, not the startup.** It comes from an adversarial reviewer subagent
   that grades five *document* dimensions — completeness, consistency, clarity, scope,
   feasibility. It says nothing about demand, wedge, or whether the business works.
   Reporting "your startup scored 7/10" would be a fabrication.
2. **It often does not exist.** The reviewer runs as a subagent; if that subagent fails, times
   out, or is unavailable, `office-hours` skips the review entirely and presents an unreviewed
   doc — the review is a quality bonus, not a gate. **Never invent a score when none was
   produced.** Record "no score — review step skipped" and move on.
3. **The reviewer has its own loop.** Up to three review iterations, with a convergence guard
   that persists unresolved issues as a `## Reviewer Concerns` section rather than looping
   further. Nested inside this skill's own three-pass ceiling, a worst case is nine reviewer
   dispatches — a reason to stop at genuine convergence rather than burning the ceiling.

When a score does exist, report it as what it is: "the design document scored 8/10 on
completeness, consistency, clarity, scope, and feasibility." Then report the founder-readiness
dimensions separately, because those are the ones about the startup.

## Dependency preflight

Run `scripts/preflight.py`, then confirm what it cannot.

1. Check whether `office-hours` is installed and discoverable.
2. If not, install once:
   `npx skills add https://github.com/garrytan/gstack --skill office-hours`
3. Do not install duplicates when an equivalent current installation exists.
4. Do not invent undocumented non-interactive flags — inspect the installer's help if it
   requires interaction.
5. Confirm the installed location and that its `SKILL.md` is readable.
6. If the host needs a registry reload or a new session before newly installed skills become
   available, handle that explicitly rather than reporting a false absence.
7. **Never silently reinstall or update on every invocation.**
8. At runtime, re-check availability. If it is gone, give an exact recovery instruction and
   preserve the current iteration state.

## Invoking it

Use the host's native skill-invocation mechanism. Reading its file is not invoking it.

Provide: the revised artifact · relevant repository context · the founder's actual evidence ·
the startup stage.

Never provide a desired score, expected answer, or your own conclusions. Leading instructions
like "confirm this version is good", "give it at least 8/10", "focus only on resolved issues",
or "ignore missing evidence" destroy the independence that makes the pass worth running. If the
result is steered, it confirms your analysis instead of testing it — which is worse than not
running it at all, because it produces false confidence.

**Do not auto-answer its questions on the founder's behalf.** Its user-approval gates must stay
real. A design doc built from your guesses describes a startup nobody is running.

## Its STOP points

`office-hours` deliberately stops and waits at several points. Do not bypass any of them:

- **Phase 1** — the goal question that selects startup versus builder mode
- **Phase 2** — each forcing question, asked one at a time
- **Phase 2.75** — a privacy gate before any web search, which sends generalized category terms
  rather than the founder's specific idea. If the founder declines, that phase is skipped
- **Phase 3** — premise agreement, stated as explicit agree/disagree items
- **Phase 4** — the alternatives gate. Even a clearly winning approach requires explicit
  approval before it lands in the design doc
- **Phase 5** — design-doc approval

If the founder disagrees with something `office-hours` concludes, that is legitimate. Record
the reasoning, update the premise state, and carry the disagreement forward as an open premise —
do not force agreement, and do not quietly adopt its view over the founder's.

## The handoff fallback

If direct skill-to-skill invocation is unavailable, do not simulate the pass.

1. Save the current iteration artifact.
2. Tell the founder exactly how to invoke `office-hours`.
3. Tell them which artifact and context to provide.
4. Stop at a resumable checkpoint.
5. Resume when the resulting design document or findings are available.

```markdown
## Handoff — office-hours pass required

**Artifact:** <path to the current iteration>
**Stage:** <pre-product | prototype | users | paying | internal>
**Run:** <exact invocation for this host>
**Provide:** the artifact above, plus <the specific evidence to bring>
**Do not tell it:** your expectations of the outcome — the pass is only useful if independent.

**Session state:** <path> — resumable
**Not yet validated:** no office-hours pass has run; no validation claim is being made.
```

Never describe an un-run pass as validation.

## Delta analysis

Compare the latest output against the previous iteration and mark each finding:

resolved · improved but incomplete · unchanged · newly discovered · **cannot be solved through
writing** · accepted risk · requires user decision · requires real-world evidence

Explain why each status changed — a status that moved for no articulable reason usually means
the artifact got more persuasive rather than more true.

```markdown
## Delta — pass <n>

**Design doc:** <path>   **Status:** <DONE | DONE_WITH_CONCERNS | NEEDS_CONTEXT>
**Document score:** <n/10 on completeness, consistency, clarity, scope, feasibility — or
                     "not produced; review step skipped">

| Finding | Status | Why it changed |
|---|---|---|
| … | resolved | … |

**Premises that changed:** <which, and on what evidence>
**New gaps exposed by its questions:** <list>
**Reviewer concerns:** <unresolved issues from the adversarial review>
**Founder decisions recorded:** <list>
**Readiness movement:** <dimension: before → after, for those that moved>
```

## Error and recovery behavior

| Condition | Response |
|---|---|
| `office-hours` not installed | Give the exact install command; preserve the iteration; do not claim validation |
| Installed but not discoverable this session | Check whether the host needs a reload or new session; report that requirement |
| Copied reference files missing | Proceed using the installed skill; note the missing references |
| Founder provides no artifact | Work from the chat description; build the truth inventory from it before anything else |
| Not a git repository | Fine — skip git context, use the filesystem; do not initialise a repo uninvited |
| Previous session interrupted | Resume from `session-state.json`; reload unresolved gaps |
| An office-hours pass is incomplete | Treat as `NEEDS_CONTEXT`; do not count it as a pass |
| Its approval gate was not completed | Not a validated pass. Say so; do not proceed as if approved |
| Design doc cannot be located | Ask for the path; check `~/.gstack/projects/{slug}/`; do not reconstruct it from memory |
| The latest iteration regresses | Restore the prior version from the session directory and report what regressed |
| Two iterations produce the same findings | Plateau — stop, report, hand over the assignments |
| Only real-world evidence gaps remain | Stop. Further writing cannot help. Deliver the validation assignments |
| Source artifact contains secrets or private customer data | Flag it; keep it out of session artifacts; do not copy it forward |
| A requested rewrite would overstate the evidence | Decline that rewrite specifically; explain the evidence gap; offer honest wording plus the validation assignment that would earn the stronger claim |
| Existing user file has uncommitted changes | Do not overwrite. Snapshot first, and confirm before editing |

Never destroy or overwrite founder data; use recoverable versioning throughout. Do not commit
project artifacts and do not push unless the founder explicitly asks.

When blocked, state: what is blocked · what was discovered · what was preserved · the exact next
action · how to resume.
