# Founder Readiness Rubric

How to score, what "ready enough" means at each stage, and when to stop iterating. Used in
Phases 3, 4, 8.

## Contents

- [What this measures](#what-this-measures)
- [The scale](#the-scale)
- [Scoring format](#scoring-format)
- [Stage-aware reading](#stage-aware-reading)
- [The readiness gate](#the-readiness-gate)
- [Convergence](#convergence)
- [Detecting a plateau](#detecting-a-plateau)

## What this measures

Founder readiness: how truthfully and clearly the startup is currently understood and
expressed. It is not an investment score, an acceptance probability, or a judgment of the
founder.

Never present a total as a probability of success, funding, acceptance, or founder quality.
The number exists to make movement between iterations visible — nothing more. If reporting it
would invite a founder to read it as a verdict, report the dimension movements instead.

## The scale

| Score | Meaning |
|---|---|
| 0 | Missing |
| 1 | Asserted but vague |
| 2 | Specific but unverified |
| 3 | Evidence-backed or operationally testable |
| 4 | Strong, consistent, and demonstrated |

The 1 → 2 step is a *writing* improvement. The 2 → 3 step is almost never a writing improvement —
it requires evidence from outside the document. Knowing which step a gap needs is what tells a
founder whether an afternoon of editing will help.

## Scoring format

Score all ten dimensions, always with the evidence behind the score:

```markdown
| Dimension | Score | Evidence |
|---|---|---|
| Demand reality | 1 | "Everyone loves it" — no behavioral or commercial evidence cited |
| Status quo clarity | 3 | Named workflow: 4 analysts, ~6 hrs/week in a shared spreadsheet |
| Target-user specificity | 2 | "Ops leads at mid-market logistics firms" — a role, not a person |
| Pain and consequence | 1 | Consequence of failure not stated |
| Narrowest wedge | 0 | Wedge and platform vision are the same paragraph |
| Observation quality | 0 | No unassisted usage observed |
| Future-fit thesis | 1 | "AI keeps improving" — rising-tide argument |
| Premise integrity | 2 | Premises implicit; no falsification tests |
| Distribution clarity | 1 | "We'll do content marketing" |
| Narrative integrity | 2 | Memo and landing page disagree on target user |
```

A score without evidence cannot be compared across iterations, which makes plateau detection
meaningless — and plateau detection is the only thing preventing an endless rewrite loop.

Validate a scoring file with `scripts/rubric.py check`.

## Stage-aware reading

The same score means different things at different stages. Read the row against what evidence
could reasonably exist yet.

| Dimension | Pre-product ceiling | Notes |
|---|---|---|
| Demand reality | 2 | 3+ requires behavior that has not happened yet |
| Observation quality | 2 | No product to observe; interviews and status-quo shadowing still count |
| Distribution clarity | 3 | A tested channel hypothesis is achievable pre-product |
| Status quo clarity | 4 | Fully achievable now — the workaround already exists |
| Target-user specificity | 4 | Fully achievable now |
| Premise integrity | 4 | Fully achievable now |
| Narrative integrity | 4 | Fully achievable now |

**A pre-product startup scoring 2 on demand reality is not failing.** It is correctly reporting
its stage. What would be failing is scoring 1 on status-quo clarity or target-user specificity,
because those are fully within reach today and cost nothing but rigor.

For pre-product work a strong validation plan may substitute for evidence that cannot exist
yet — but it is never counted *as* evidence. Record it as a plan, and score the dimension on
what is actually known.

For startups with users or revenue, require the stronger behavioral and commercial evidence;
a paying-customer startup scoring 1 on demand reality has a real problem, because the evidence
is available and was not gathered.

## The readiness gate

"Ready enough for the current stage" requires all of:

- No material contradiction remains hidden
- The user and the pain are specific
- The status quo is concrete
- The wedge is distinguishable from the long-term platform vision
- Known facts and hypotheses are clearly separated
- Unsupported demand claims have been removed or relabeled
- Distribution is at least operationally plausible
- The next evidence-gathering action is concrete
- The latest `office-hours` pass has no unresolved critical concern fixable through the
  current artifact
- **The founder explicitly approves the result**

The last item is not a formality. This skill produces the founder's own words about their own
company; shipping it without their approval would defeat the purpose.

## Convergence

Default ceiling: **three `office-hours` passes per invocation.**

Stop when the gate is met, the founder approves, only real-world evidence gaps remain, two
consecutive passes produce materially identical findings, the process is blocked on a founder
decision, the dependency is unavailable, or continuing would only polish wording without
improving truth or clarity.

That last condition is the one that fires most often and is easiest to miss. Once every
remaining gap has repair type *collect evidence*, *observe users*, *validate willingness to
pay*, or *test distribution*, no further iteration can help — the work has moved outside the
document. Say so plainly and hand over the assignments.

When the ceiling is reached, stop with an unresolved-gaps report and a resumable checkpoint.
Never run an unbounded rewrite loop.

## Detecting a plateau

A plateau is **the same gaps recurring with the same repair types and evidence status** — not
merely a flat score. Score can stay flat while real repairs happen, and it can rise from added
prose while nothing improves.

Compare iterations with `scripts/rubric.py compare`. Then read the result honestly:

- **Same gaps, same repair types** → plateau. Stop.
- **Same score, different gaps** → progress. Continue.
- **Higher score, same gaps** → the artifact got more persuasive without getting more true.
  This is the failure mode this whole skill exists to prevent. Investigate before continuing;
  a rewrite may have upgraded a hypothesis.

When stopping, always name the triggering condition and what would justify resuming. "Stopped
after pass 2: demand reality and observation quality unchanged, both blocked on the same
missing evidence — resume after watching three users complete the workflow unassisted" gives
the founder something to do. "Converged" does not.
