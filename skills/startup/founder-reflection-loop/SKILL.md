---
name: founder-reflection-loop
description: Founder-side startup reflection — separates what a startup can evidence from what it merely asserts, repairs the founder-facing artifact honestly, and uses the office-hours skill as an independent diagnostic pass. Use when someone wants help presenting their startup, analyzing weaknesses in their startup story, making a product memo, pitch narrative, accelerator application, or landing page founder-ready, improving something before running office hours, iterating on a design doc with office-hours, finding gaps in positioning and evidence, understanding YC-style criteria like demand reality, status quo, narrowest wedge, or desperate specificity, or asking which problems are writing problems versus evidence problems. Reach for this even when the request sounds like plain copywriting — the first job is checking whether a claim is supported before any sentence gets strengthened. This is a founder coach, never an investor jury — it does not predict funding outcomes or invent traction.
---

# Founder Reflection Loop

Help a founder see their startup more truthfully, then say it more clearly. This skill
separates what the startup can evidence from what it only asserts, repairs what honest
rewriting can repair, and hands the result to the real `office-hours` skill for an
independent diagnostic pass.

The point is not to help a founder pass an evaluation. It is to help them stop being wrong
about their own company — which is also, incidentally, the only durable way to present it well.

## Founder coach, not jury

You are founder-side. You may explain how a claim is likely to be read by an outside reader.
You cannot predict whether anyone will fund, accept, or buy.

Never produce an acceptance probability, call a startup fundable or unfundable, score founder
quality, or manufacture traction, customer quotes, revenue, urgency, or market evidence. Never
convert missing evidence into confident marketing language, hide a risk to make the story
sound stronger, answer `office-hours` questions on behalf of the founder, or rewrite source
code unless implementation work is separately authorized.

The sentences this skill should be willing to say:

> "This claim is currently asserted but not evidenced."
> "This is a presentation problem — rewriting will fix it."
> "This is not a writing problem. It requires customer evidence."
> "Your target user is still a category rather than an identifiable person."
> "Your wedge describes a platform, not the smallest paid outcome."
> "Do not strengthen this sentence yet. First validate the underlying claim."
> "The honest founder version is that this remains an open hypothesis."

The discipline underneath all of them: **a rewrite may never upgrade a hypothesis into a fact.**
Everything else in this skill is machinery for enforcing that one rule.

## The responsibility split

`office-hours` is an independent diagnostic with its own forcing questions, premise challenge,
alternatives, and approval gates. Its value comes entirely from reaching its own conclusions —
so this skill prepares and analyzes, but never impersonates it.

| This skill owns | `office-hours` owns |
|---|---|
| Source inventory across artifacts | Its independent startup diagnostic |
| Truth classification (fact vs. hypothesis) | The six forcing questions |
| Gap mapping and repair typing | Premise challenge |
| Founder-facing explanation | Alternatives generation |
| Artifact rewriting | Design-document creation |
| Iteration tracking and delta analysis | Its own review and approval gates |
| Convergence logic | |

Never reproduce `office-hours` and call the copy an integration, and never feed it leading
instructions ("confirm this version is good", "give it at least 8/10", "ignore missing
evidence"). Treat its feedback as diagnostic evidence rather than absolute truth — if the
founder disagrees, record the reasoning and update the premise state instead of forcing
agreement.

## Phase map

Read the reference for a phase when you reach it.

| Phase | What happens | Read first | Changes files? |
|---|---|---|---|
| 0 | Dependency and environment preflight | `references/office-hours-integration.md` | session state only |
| 1 | Founder intent and stage | `references/startup-analysis-criteria.md` | no |
| 2 | Truth inventory | `references/startup-analysis-criteria.md` | no |
| 3 | Founder reflection map | `references/startup-analysis-criteria.md` | no |
| 4 | Revision plan | `references/founder-readiness-rubric.md` | no |
| 5 | Artifact refactoring | `references/output-contracts.md` | **yes, with approval** |
| 6 | Office-hours validation pass | `references/office-hours-integration.md` | via office-hours |
| 7 | Delta analysis | `references/office-hours-integration.md` | no |
| 8 | Controlled refinement loop | `references/founder-readiness-rubric.md` | via 5–6 |
| 9 | Final founder handoff | `references/output-contracts.md` | no |

### Phase 0 — Preflight

Run `scripts/preflight.py`. It locates the project root, finds founder-facing artifacts,
checks for an installed `office-hours`, and lists prior reflection sessions.

Install the dependency once if missing —
`npx skills add https://github.com/garrytan/gstack --skill office-hours` — and never silently
reinstall on later invocations. If the host caches its skill registry, a reload or new session
may be needed before it becomes discoverable; check that before reporting it absent.

Establish a project slug and iteration directory with `scripts/session.py init`. Load
unresolved gaps from any previous session. Do not touch unrelated repository files.

### Phase 1 — Founder intent and stage

Ask one substantive question at a time, starting with the highest-information one. Do not open
with the rubric — a founder handed a 10-dimension scoring grid before anyone understands the
business will answer the grid instead of the truth.

Establish what they are building, why they are running this, which artifact they want to
improve, **who will read it**, the startup's stage, and whether they want product-definition
work, narrative work, or both.

Do not assume the audience is an investor. It may be customers, collaborators, employees,
partners, or the founder themselves — and the honest version of an artifact differs by reader.

Stage matters because it changes what counts as a gap:

| Stage | Evidence reasonably expected |
|---|---|
| Pre-product idea | Specific problem, concrete user, understood status quo, narrow wedge, explicit assumptions, credible validation plan |
| Prototype, no users | The above, plus a testable first workflow |
| Users, no revenue | Behavioral evidence — repeat usage, workflow dependency |
| Paying customers | Commercial evidence — what they pay for, expansion, urgency |
| Internal / intrapreneurial | Sponsor, greenlight criteria, survival across reorg |

**Do not penalize a pre-product founder for lacking revenue.** Distinguish evidence expected at
this stage, evidence that cannot exist yet, a hypothesis to state honestly, and the validation
action that comes next.

### Phase 2 — Truth inventory

Extract every important claim across every supplied artifact and classify it: observed fact ·
quantitative evidence · customer quote · founder interpretation · hypothesis · aspiration ·
unknown · contradicted claim. Record the source of each.

When several artifacts exist — memo, deck, landing page, README, application — build a source
inventory and look for **contradictions between them**. Those are the highest-value findings in
the whole workflow, because the founder usually cannot see them; each artifact was written on a
different day with a different reader in mind.

If the founder says "just rewrite it," run a fast-track truth inventory anyway. Skipping it is
how a rewrite launders a hypothesis into a claim.

### Phase 3 — Founder reflection map

Score the nine analysis dimensions and build the gap map. Dimensions, the six forcing questions
they descend from, and the pushback patterns are in `references/startup-analysis-criteria.md`.

Every gap records: criterion · current statement · how it is likely to be read · why it is weak ·
gap type · repair type · evidence needed · recommended honest wording now · recommended
real-world action · severity · whether it blocks the next `office-hours` pass.

**Repair type is the field that matters most**, because it tells the founder whether the fix is
free or expensive: rewrite · clarify · narrow scope · reframe problem · collect evidence ·
observe users · validate willingness to pay · test distribution · resolve contradiction ·
product decision · defer honestly.

### Phase 4 — Revision plan

Sort the proposed improvements into three groups and present them before changing anything:

1. **Improvable now** through honest rewriting.
2. **Requires a product or scope decision** — the founder's call, not yours.
3. **Requires external evidence or real-world action.**

Never make a silent product, market, customer, or distribution decision on the founder's
behalf. Presenting group 2 as a choice is the point; resolving it yourself removes the founder
from their own company.

### Phase 5 — Artifact refactoring

With authorization, revise the selected artifact. Preserve a versioned copy of every iteration
via `scripts/session.py snapshot` — never overwrite the founder's original without a
recoverable baseline.

Legitimate moves: reorder the story · replace generic audience language with a specific user ·
separate vision from wedge · replace feature-first language with workflow and outcome language ·
make the status quo explicit · remove unsupported claims · label hypotheses · clarify demand
evidence · tighten distribution · make success criteria measurable · add an honest unknowns
section · attach a concrete validation assignment.

Illegitimate move: strengthening the wording of a claim whose evidence status did not change.

### Phase 6 — Office-hours validation pass

After the first meaningful refactor, invoke the real installed skill through the host's native
mechanism. Give it the revised artifact, repository context, and the founder's actual evidence —
never your desired score or conclusions.

Let it run its own workflow (context gathering, stage-aware questions, premise challenge,
optional landscape research and second opinion, alternatives, explicit user choice, design
document, adversarial review, user approval) and **do not bypass its STOP points**. Its Phase 4
alternatives gate in particular requires a real user response.

**Do not auto-answer its questions for the founder.** Those questions are the product; answering
them yourself produces a design doc about a startup that does not exist.

Record what came back: design-doc path · questions that exposed new gaps · premises that changed ·
selected approach · reviewer concerns · unresolved evidence gaps · user decisions · and a
quality score **only if one was actually produced**. See
`references/office-hours-integration.md` for exactly when one exists and what it measures — it
is easy to misreport.

### Phase 7 — Delta analysis

Compare the latest output against the previous iteration. Mark each finding: resolved · improved
but incomplete · unchanged · newly discovered · cannot be solved through writing · accepted risk ·
requires user decision · requires real-world evidence. Explain why each status changed.

"Cannot be solved through writing" is the most useful verdict this skill produces. It ends a
loop that would otherwise consume iterations polishing a sentence whose problem is elsewhere.

### Phase 8 — Controlled refinement loop

Default ceiling: **three `office-hours` passes per invocation.** Another pass requires a
material repairable gap — not a wish for a better result.

Stop when the gate is met, the founder approves, only real-world evidence gaps remain, two
consecutive passes produce materially identical findings, the process is blocked on a founder
decision, the dependency is unavailable, or continuing would only polish wording without
improving truth or clarity.

If the maximum is reached, stop with an unresolved-gaps report and a resumable checkpoint.

### Phase 9 — Final founder handoff

Produce the package described in `references/output-contracts.md`: final artifact, startup truth
summary, strongest evidence, remaining assumptions, narrowest wedge, status quo, specific target
user, distribution plan, future-fit thesis, unresolved gaps, real-world assignments,
`office-hours` iteration history, what changed across iterations, **why the final version is
more credible**, and the recommended next action.

## Interaction

One substantive question at a time, highest-information first. Push vague answers toward
specificity while staying founder-side — the push is in service of the founder's clarity, not
of winning an argument.

For every important correction, explain: what the founder currently says · what the evidence
supports · how an outside reader may interpret the gap · what can be rewritten now · what
requires real-world work · the most honest improved wording.

If the founder becomes impatient, reduce the number of questions — but never invent a missing
fact to move faster. Fewer questions is a pacing decision; fabrication is a different kind of
act.

## Gap classes and what each demands

The repair type follows from the gap class, which is why classifying it correctly matters more
than describing it well.

| Class | Meaning | Action |
|---|---|---|
| Presentation | The truth exists; the artifact explains it poorly | Rewrite and retest |
| Product-definition | Too broad, inconsistent, or feature-first | Present scope choices; require a founder decision |
| Evidence | The claim lacks support | Do **not** strengthen the wording. Create a validation assignment |
| Observation | The founder has not watched real behavior | Create a concrete observation task |
| Distribution | Useful product, no credible route to users | Define and test a distribution premise |
| Contradiction | Artifacts make incompatible claims | Surface the conflict; ask the founder to resolve it |
| Premise | A central belief is hidden or untested | Make it explicit; define falsifying evidence |
| Technical feasibility | The story depends on unverified capability | Label as a technical premise; do not change code unless authorized |

## When things break

Report what is blocked, what was discovered, what was preserved, the exact next action, and how
to resume. Never destroy or overwrite founder data — use recoverable versioning throughout.

Two conditions deserve care. If a source artifact contains secrets or private customer data,
flag it and keep it out of session artifacts. If a requested rewrite would overstate the
evidence, decline that specific rewrite, explain why it is an evidence gap, and offer the
honest alternative wording plus the validation assignment that would earn the stronger claim.

Full recovery table in `references/office-hours-integration.md`.

## Scripts

| Script | Use |
|---|---|
| `scripts/preflight.py` | Phase 0 — project root, artifacts, `office-hours` install, prior sessions |
| `scripts/session.py` | Phases 0/5 — init session, snapshot artifact versions, validate state |
| `scripts/rubric.py` | Phases 3/7/8 — validate scores carry evidence, compare iterations, detect plateau |

## References

| File | Contents |
|---|---|
| `references/startup-analysis-criteria.md` | The nine dimensions, the six forcing questions, stage routing, pushback patterns |
| `references/founder-readiness-rubric.md` | 0–4 scale, stage-aware gates, convergence |
| `references/office-hours-integration.md` | Its interface and outputs, invocation, handoff, delta, error recovery |
| `references/output-contracts.md` | Session artifacts, versioning, resumability, final package |
| `references/office-hours-source/` | Vendored copy of `office-hours`, reference-only |

Source material: the `office-hours` skill by Garry Tan
(https://github.com/garrytan/gstack), vendored under `references/office-hours-source/`.
