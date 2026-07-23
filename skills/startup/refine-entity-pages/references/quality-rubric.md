# Quality Rubric and Readiness Gates

How to score a page and decide whether it is done. Used in Phase 3 (baseline), Phase 8 (result),
and Phase 9 (convergence).

## Contents

- [What this rubric is not](#what-this-rubric-is-not)
- [The scale](#the-scale)
- [Scoring the 20 dimensions](#scoring-the-20-dimensions)
- [Naming the aggregate](#naming-the-aggregate)
- [Readiness gates](#readiness-gates)
- [Convergence and stopping](#convergence-and-stopping)

## What this rubric is not

This scores an **entity page**, not an entity. It measures whether a document is accurate, well
sourced, and operationally useful — never a person's importance, credibility, or worth.

The distinction matters because the artifact is a durable record about a real person, and a
number attached to their name reads as a judgment of them no matter what the column header
says. Score the document.

## The scale

| Score | Meaning |
|---|---|
| 0 | Missing or unsafe |
| 1 | Present but weak, vague, or unsupported |
| 2 | Partially useful |
| 3 | Solid and traceable |
| 4 | Strong, current, well-supported, and operationally useful |

**Every score carries evidence.** A score without a quoted line or a named absence is an
opinion, and it cannot be compared across passes — which makes plateau detection meaningless.

## Scoring the 20 dimensions

The dimensions are defined in `entity-quality-model.md`. Record them like this:

```markdown
| # | Dimension | Score | Evidence |
|---|---|---|---|
| 1 | Identity certainty | 4 | Employer, handle, and meeting date all match the brain record |
| 5 | Citation coverage | 1 | 7 of 11 State claims uncited; funding figure has no source |
| 11 | Fact/inference separation | 0 | "secretly wants to leave" stated as fact in State |
```

Two dimensions act as gates rather than contributors:

- **Identity certainty below 3 blocks everything.** Do not mutate, do not score the rest as
  though they mean something — facts about the wrong entity score zero regardless of how well
  sourced they are.
- **Privacy and proportionality below 2 blocks further research.** Resolve the scope question
  before collecting more.

## Naming the aggregate

If you compute an aggregate, call it exactly:

> **Refinement readiness score**

Do not call it an enrich score, trust score, person score, reputation score, importance score,
investment score, or relationship value score. Those names describe the entity rather than the
document, and they invite the page to be used as a verdict on a person.

**Never attribute a score to `enrich`.** It does not produce one. Claiming otherwise
manufactures external authority for your own judgment.

## Readiness gates

Scores guide the work; these gates decide whether it is finished.

### A new person page is ready when

- Identity is unambiguous
- Notability is established
- Filing is correct
- The executive summary explains how the user knows them and why they matter
- `State` contains hard facts only
- Material factual claims are cited
- At least one dated timeline entry exists
- Empty sections do not dominate the page
- Texture claims are evidence-backed or clearly labeled as interpretation
- User-authored assessment is preserved
- Relevant relationship context exists
- Open threads are actionable or explicitly absent
- Person/company links are valid
- No sensitive unsupported inference exists
- No major contradiction is hidden

### A new company page is ready when

- Identity and canonical company are unambiguous
- `State` explains what it does, stage, key people, and the user's connection
- Material facts and metrics are sourced
- At least one dated timeline entry exists
- Open threads are useful
- Person/company cross-references are valid
- Unsupported marketing claims are excluded
- No major contradiction is hidden

### An updated page is ready when

- The new signal is material
- Existing history is preserved
- Timeline entries are not duplicated
- Compiled-truth changes are justified
- User-written content was not silently replaced
- Citations support the new claims
- Freshness metadata is correct
- Auto-link errors are resolved or reported
- Privacy scope has not expanded without authorization

### When the gate cannot be met

Insufficient evidence is a legitimate ending. Valid outcomes: no mutation · save raw evidence
only · ask the user · record an unresolved candidate · defer enrichment.

Do not force a run to end in a page write. A page that meets the gate by padding does not meet
the gate — it defeats the measurement.

## Convergence and stopping

Default ceiling: **three `enrich` passes per entity per invocation.**

Another pass requires a *reason*, and only two reasons qualify: new evidence has become
available, or a specific identified correction has not yet been applied. Wanting a better score
is not a reason — it is what produces padded pages.

Stop when any of these holds:

- The quality gate is met
- The user accepts the current result
- Only missing external evidence remains
- Identity remains unresolved
- Two passes produce materially identical findings
- No new source or material signal exists
- Further work would only add prose length
- The page was enriched inside the freshness window with no new signal
- Privacy or authorization blocks additional research
- External APIs are unavailable
- The remaining gap requires direct user knowledge
- The next change risks overwriting user-authored judgment

### Detecting a plateau

Compare the current pass's gap map against the previous one by taxonomy label and dimension. A
plateau is not "the score stopped rising" — it is **the same gaps recurring with the same
evidence status**. Score can stay flat while real repairs happen, and score can rise from added
prose while nothing improves.

When you stop, always report *which* condition triggered it and what would justify resuming.
"Stopped at pass 2: citation and provenance gaps unchanged, both blocked on the same missing
first-party source; resume if the company publishes the funding announcement" tells the user
what to do. "Converged" does not.
