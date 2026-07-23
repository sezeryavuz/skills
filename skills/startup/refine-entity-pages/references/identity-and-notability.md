# Identity, Notability, and Tier Selection

The three decisions made before anything is written: *is this the right entity*, *does it
belong in the brain*, and *how much effort is proportionate*. Used in Phases 1 and 4.

## Contents

- [Why identity comes first](#why-identity-comes-first)
- [Identity resolution](#identity-resolution)
- [The identity-resolution brief](#the-identity-resolution-brief)
- [Identity validation signals](#identity-validation-signals)
- [The notability gate](#the-notability-gate)
- [CREATE versus UPDATE](#create-versus-update)
- [Tier selection](#tier-selection)

## Why identity comes first

Every other error is recoverable by editing a page. An identity error writes true facts about
one person onto another person's page, and it is self-concealing: the page looks well-sourced,
because the sources are real — they are just about someone else. Later passes will read that
page as established context and build on it.

So identity is not the first step because it is convenient. It is first because it is the only
error the rest of the pipeline cannot detect.

## Identity resolution

Determine, before any external lookup:

- Exact canonical name, and whether the entity is a person or a company
- Existing slug and page path, if any
- Known aliases
- Employer or associated company
- Location, when legitimately relevant
- The user's relationship to the entity
- The source context the entity arrived from
- Whether multiple candidates share the name
- Identity confidence
- Evidence that any external profile belongs to the intended entity

**Search the brain before creating anything.** This is free, it is often the richest source of
relationship context, and it is what prevents duplicate pages for one entity.

Where the retrieval surface offers safety hints — `exists`, `probable`, `unknown` — use them as
intended. A single weak semantic match is not proof a page exists; acting on one produces
either a duplicate page or an update written to the wrong record.

When identity confidence is insufficient, stop before any mutation and produce the brief below.

## The identity-resolution brief

```markdown
## Identity resolution required: <name as given>

**Signal source:** <where this entity came from>
**Candidates found in brain:** <n>

| # | Candidate | Page | Distinguishing evidence | Last activity |
|---|---|---|---|---|
| 1 | <name, role, company> | <path> | <what separates this one> | <date> |
| 2 | … | | | |

**Not in brain:** <any external candidate under consideration, and why it is a candidate>

**What would disambiguate:** <the specific signal needed — an employer, a handle, a meeting
date, an email domain>

**Blocked:** no mutation until resolved.
```

Ask for one disambiguating signal, not a full interview. The user usually knows immediately
which one they meant.

## Identity validation signals

Concrete checks that catch a wrong match before it is written:

- **Name mismatch between brain and an external source** — skip and flag for review rather than
  reconciling silently.
- **Implausibly thin professional profile** for a claimed senior figure. The reference `enrich`
  skill uses a connection count below 20 on LinkedIn as a likely-wrong-person signal.
- **Employer mismatch** between the source context and the returned profile — the single most
  common failure of same-name enrichment APIs.
- **Joke, bot, or spam profiles**, and obviously wrong data — save to raw evidence if useful,
  but do not update the page.

When in doubt, the safe move is asymmetric: save raw data, leave the page alone. Raw evidence
costs storage. A wrong compiled fact costs trust in the whole brain.

## The notability gate

Not every mentioned entity deserves a page. Apply the gate before CREATE, and check the active
brain's filing rules — the reference `enrich` skill defers to `skills/_brain-filing-rules.md`
within the brain repo for both notability and filing location.

Do not create a page for:

- Random mentions carrying no relationship signal
- Bots, spam accounts, obvious joke profiles, unverified identities
- Entities with no substantive connection to the user's work
- Anyone for whom the available evidence would produce only a stub

Creating dossiers for private individuals with no meaningful relationship to the user is a
privacy problem, not just a clutter problem. See `privacy-and-sensitive-data.md`.

## CREATE versus UPDATE

The decision is not binary — there are more outcomes than "new page" and "rewrite page":

| Outcome | When |
|---|---|
| Create a new page | Notable, identity resolved, meaningful sourced content available |
| Update an existing page | Material new signal about a known entity |
| Add only a timeline entry | A dated event occurred; the current picture is unchanged |
| Update compiled truth | New evidence materially changes what is currently true |
| Update relationship context | The user's connection changed |
| Add an open thread | Something now needs follow-up |
| Add cross-references | A connection surfaced; the entity's own facts are unchanged |
| Save raw evidence only | Evidence exists but is unverified, conflicting, or off-target |
| Skip entirely | No material signal, or recently enriched with nothing new |

### CREATE requirements

Apply the notability gate; confirm filing location; require meaningful content, at least one
reliable source or substantive brain signal, and an initial dated timeline entry. Reject
empty or boilerplate-only pages — leave genuinely unknown sections as `[No data yet]` rather
than padding them.

### UPDATE requirements

- Preserve existing history; timeline entries are append-only.
- Change compiled truth only when new evidence materially changes the picture.
- **Preserve user-written assessments** unless the user explicitly revises them. The user's own
  read on someone is the highest-context content on the page and the least reproducible; an API
  career summary is the lowest-context content and infinitely reproducible. Never let the
  second overwrite the first.
- Flag contradictions rather than silently resolving them.
- Avoid refreshing the same page within a week unless a material new signal exists.

## Tier selection

Scale effort to importance — both to avoid wasting research budget and because depth is
intrusion. The three tiers mirror the reference `enrich` skill's protocol.

| Tier | Who | Expected depth |
|---|---|---|
| **1 — Key** | Inner circle, close collaborator, key customer, critical partner, important candidate, high-value company, entity central to current work | Full brain cross-reference, deep first-party context review, web research, social research where appropriate, people/company APIs when authorized, relationship history, network context, contradiction review, raw data preservation, detailed timeline |
| **2 — Notable** | Occasional collaborator, relevant industry figure, potential partner, company worth monitoring, meaningful but limited connection | Brain cross-reference, moderate web research, relevant social research, basic relationship context, material timeline, selective external APIs only where useful |
| **3 — Minor but trackable** | Limited but meaningful mention, peripheral participant, early contact, worth remembering but not researching | Brain cross-reference, source-signal extraction, minimal public lookup when identity is clear and a handle is known, no deep profile, a small but meaningful page or update |

Two rules on top of the table:

- **Do not choose Tier 1 because data is available.** Availability is not justification. Tier
  is a statement about the relationship, not about the API surface.
- **Document the decision and why the cost and privacy level are proportionate.** Escalating an
  entity to Tier 1 requires user approval precisely because it expands both spend and intrusion.

Applying Tier 1 research to a Tier 3 private individual is the specific mistake to avoid. It is
easy, it looks thorough, and it produces a surveillance record of someone the user met once.
