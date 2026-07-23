# Entity Quality Model

What makes a brain page good, and how to name what is wrong with one. Used in Phase 3 (audit)
and Phase 6 (candidate refinement).

## Contents

- [The premise: compiled truth, not collected facts](#the-premise-compiled-truth-not-collected-facts)
- [The State section](#the-state-section)
- [Texture sections](#texture-sections)
- [Company pages are not person pages](#company-pages-are-not-person-pages)
- [Timeline integrity](#timeline-integrity)
- [Cross-reference integrity](#cross-reference-integrity)
- [The no-stub rule](#the-no-stub-rule)
- [The 20 quality dimensions](#the-20-quality-dimensions)
- [Gap taxonomy](#gap-taxonomy)
- [Gap map format](#gap-map-format)

## The premise: compiled truth, not collected facts

A page that accumulates facts is an archive. A page that synthesizes them is useful. The
distinction matters because the user reads this page before a meeting, not during research —
it has to answer questions, not store material.

Compiled truth should answer: who or what is this entity, why does it matter to the user, what
is currently true, what has materially changed, what remains uncertain, what relationship
context is actionable, and which open threads need attention.

Synthesis has been replaced by accumulation when the page contains copied profile text, lists
of search snippets, API field dumps, generic career summaries, the same fact repeated across
sections, or personality claims with nothing behind them.

The reference `enrich` skill frames the target as an intelligence dossier rather than a
profile scrape: facts are table stakes, texture is the value.

## The State section

`State` holds hard current facts only — current role, current company, current product, company
stage, confirmed funding, confirmed key people, confirmed relationship context, and where
legitimately relevant, location and metrics.

Two rules govern it:

- **Every factual claim carries a citation or traceable source.** A claim in `State` without one
  is either an uncited fact (repairable) or an inference that has drifted into the facts
  section (a correctness problem).
- **Speculation does not live here.** Motivation, belief, and trajectory claims belong in
  texture sections where they can be labeled. Uncertain claims move to an uncertainty or
  contradiction note rather than being stated flatly.

## Texture sections

For person pages: What They Believe, What They're Building, What Motivates Them, Hobby Horses,
Assessment, Trajectory, Relationship, Contact, Network, Open Threads.

Texture is the highest-value and highest-risk content on the page. It is what makes the page
worth reading, and it is where unsupported claims about a real person do damage. The
discipline is not to avoid texture — it is to label its epistemic status.

Distinguish these, and let the wording carry the distinction:

| Status | Phrasing that fits |
|---|---|
| Directly stated belief | "They have repeatedly stated…" |
| Repeated observed theme | "Recent public posts focus on…" |
| User-authored assessment | "The user's current assessment is…" |
| Agent interpretation | "Available evidence suggests…" |
| Unknown | "This remains uncertain." |

Never write an inferred inner state as a fact. "They are motivated by status" is a claim about
a real person's mind; "their public writing returns repeatedly to competitive ranking" is an
observation with a source. The second is useful and defensible. The first is neither.

## Company pages are not person pages

Company pages carry State, key people, stage, metrics, user connection, open threads, and
timeline. Do not force psychological texture sections onto a company — "What Motivates Them"
applied to an organization produces confident nonsense, because there is no single mind to
attribute a motivation to.

## Timeline integrity

Every entry needs a date, an event description, and a source. Beyond that:

- Reverse-chronological ordering, append-only, prior history preserved.
- No duplicates — the most common corruption from repeated refinement passes is the same event
  re-added each time, which makes a page look richer while making it less trustworthy.
- Distinguish the **event date** from the **retrieval date**. They are different facts and
  conflating them silently backdates or postdates real events.
- No undated evergreen facts. If it has no date, it belongs in State or texture, not here.
- When an event date is uncertain, label the uncertainty rather than inventing precision.

Removing historical entries because they no longer fit the current narrative is a form of
falsification, even when the current narrative is correct. A role someone no longer holds is
still something they held.

## Cross-reference integrity

Check person-to-company and company-to-person connections, related meetings, projects, deals,
source pages, open-thread references, existing typed links, and backlinks.

Where the write path performs automatic link creation, do not also create the links manually —
inspect the result instead. The reference `enrich` skill notes that links between brain pages
are auto-created on every `put_page` call, reporting through an `auto_links` field shaped
`{ created, removed, errors }`; timeline entries still require explicit timeline-add calls.
Record created, removed, and failed links.

An auto-created graph edge is not relationship context. The edge says two pages are connected;
only prose says how or why. Verify both.

## The no-stub rule

Reject a page that contains only a name, a title, empty headings, boilerplate description, a
copied social bio, a generic company sentence, unverified API fields, or `[No data yet]` in
nearly every section.

Individual empty sections may legitimately read `[No data yet]` — that is honest. The test is
whether the page **as a whole** carries meaningful, sourced value.

If evidence is insufficient, do not create the page. Save the unresolved signal or candidate
state instead. An empty page is a gap; a fake page is a gap that will be trusted.

## The 20 quality dimensions

Score each on the 0–4 scale in `quality-rubric.md`. Every score cites evidence.

| # | Dimension | The question it answers |
|---|---|---|
| 1 | Identity certainty | Is this unambiguously the right entity? |
| 2 | Notability and relationship relevance | Does this entity belong in the brain at all? |
| 3 | Filing and schema correctness | Right location, right type, right structure? |
| 4 | State accuracy | Are the hard facts correct and current? |
| 5 | Citation coverage | Do material claims have sources? |
| 6 | Citation-to-claim alignment | Do those sources actually support the claims? |
| 7 | Source quality | Are the sources high-precedence for what they support? |
| 8 | Raw provenance | Is the underlying evidence preserved? |
| 9 | Timeline integrity | Dated, ordered, sourced, non-duplicated? |
| 10 | Texture depth | Is there value beyond hard facts? |
| 11 | Fact-versus-inference separation | Is interpretation labeled as interpretation? |
| 12 | Contradiction handling | Are conflicts surfaced rather than resolved silently? |
| 13 | Relationship usefulness | Does it capture how the user actually knows them? |
| 14 | Open-thread usefulness | Are next actions real and current? |
| 15 | Cross-reference integrity | Do links and backlinks resolve and mean something? |
| 16 | Freshness | Is the current picture actually current? |
| 17 | Preservation of user-authored judgment | Has the user's own knowledge survived? |
| 18 | Privacy and proportionality | Is the depth appropriate to the relationship? |
| 19 | No-stub compliance | Does the page carry real value? |
| 20 | Overall operational usefulness | Would this help before a meeting? |

## Gap taxonomy

Classify every finding as exactly one of these. Consistent naming is what lets successive
passes tell whether the same problem persists.

Identity · Notability · Filing · State · Citation · Source-quality · Provenance · Timeline ·
Texture · Contradiction · Relationship-context · Open-thread · Cross-reference · Freshness ·
Privacy · Unsupported-inference · Duplicate-content · Stub-page · Schema-conformance

## Gap map format

```markdown
### Gap N — <Taxonomy label>

- **Dimension:** <one of the 20>
- **Current content:** "<what the page says now>"
- **Problem:** <what is wrong>
- **Why it matters:** <consequence for the user>
- **Evidence status:** <supported / uncited / contradicted / absent>
- **Source required:** <what evidence would resolve it, or "none — repairable now">
- **Proposed correction:** <exact change>
- **Mutation risk:** <none / low / high — what could be lost>
- **Owner:** <this skill (repairable without new evidence) | enrich (needs research)>
- **User approval required:** <yes/no — see the approval gates in SKILL.md>
- **Severity:** <blocking / major / minor>
```

The **Owner** field is the one that drives the workflow: it partitions the gap list into what
Phase 6 can fix on its own and what Phase 7 must hand to `enrich`. A gap map where everything
is owned by `enrich` usually means the audit stopped at "needs more data" instead of examining
what is already on the page.
