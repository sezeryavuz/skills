# Claims, Citations, and Provenance

How evidence becomes compiled truth — and what stops it when it shouldn't. Used in Phase 5,
and again in Phase 8 when checking what `enrich` added.

## Contents

- [Source precedence](#source-precedence)
- [The claim ledger](#the-claim-ledger)
- [Claim types](#claim-types)
- [Citation validity](#citation-validity)
- [Handling contradictions](#handling-contradictions)
- [Raw provenance](#raw-provenance)

## Source precedence

Not all sources are equal, and collapsing them into uniform-confidence facts is how a scraped
aggregator profile ends up outranking something the user personally witnessed.

| Rank | Source | Notes |
|---|---|---|
| 1 | User's direct interactions and explicit notes | Highest context, irreplaceable, cannot be re-derived |
| 2 | Meeting transcripts | First-hand, dated, verifiable |
| 3 | Email threads | First-hand, dated |
| 4 | First-party statements and official pages | Authoritative on the entity's own facts |
| 5 | Direct public posts or talks | The entity speaking for itself |
| 6 | Reputable secondary reporting | Good for events; interpret claims about intent carefully |
| 7 | Company or people enrichment APIs | Good for hard facts, poor for texture, prone to same-name errors |
| 8 | Aggregators and scraped profiles | Often stale; treat as leads, not conclusions |
| 9 | Unverified mentions | Leads only |

**A lower-precedence source never overwrites a higher-precedence one.** If an API contradicts
what the user wrote from a direct conversation, that is a contradiction to surface — not a
correction to apply.

Note that precedence is per-claim, not global: an enrichment API may be the best source for a
funding round and a terrible source for what someone believes.

## The claim ledger

Build this before drafting page content. Its function is structural — if every claim must carry
a source before it can enter compiled truth, unsupported claims cannot silently arrive.

| Field | Notes |
|---|---|
| Claim ID | Stable within the session, so later passes can reference it |
| Claim text | As it would appear on the page |
| Page section | Where it is destined |
| Claim type | See below |
| Source | Specific — a URL, transcript, or note, not "web research" |
| Source date | The date the source is *about*, distinct from retrieval date |
| Source tier | 1–9 from the precedence table |
| Direct or inferred | Does the source state this, or did you conclude it? |
| Confidence | And on what basis |
| Freshness | Is this still current? |
| Contradiction status | Consistent / contradicted by claim N / unresolved |
| Privacy sensitivity | See `privacy-and-sensitive-data.md` |
| Proposed action | Add / keep / revise / soften / remove / hold for evidence |

The **Direct or inferred** column does the most work. Most unsupported page content is not
fabricated — it is an inference that lost its qualifier somewhere between the source and the
draft.

## Claim types

Hard fact · First-party statement · User observation · Relationship fact · Public position ·
Repeated theme · Assessment · Trajectory hypothesis · Open thread · Unknown · Contradicted

The type determines where a claim may land. Hard facts and first-party statements can enter
`State`. Assessments and trajectory hypotheses belong in labeled texture sections, never in
`State`. Anything typed Unknown or Contradicted stays out of compiled truth entirely until it
is resolved.

## Citation validity

A citation is not valid merely because a URL is present. Check:

- **Presence** — does the material claim have one at all?
- **Correctness** — does the reference resolve, and is it well-formed?
- **Accessibility** — can the source actually be reached?
- **Claim-to-source alignment** — this is the one that gets skipped. Does the cited source
  support *the specific nearby claim*, or merely discuss the entity? A profile page cited for
  "they believe X" proves only that the person exists.
- **Date freshness** — a correct 2019 citation does not support a claim about the present.
- **Precedence** — is this the best available source for this kind of claim?
- **Entity match** — does the citation point at the right person or company? Same-name
  citations are the identity error's second entry point.

Dead links, malformed references, and citations attached to the wrong claim are all repairable
without new research — they belong to Phase 6, not to `enrich`.

## Handling contradictions

When sources conflict, the instinct is to pick a winner. Resist it unless the evidence actually
justifies one.

- **Preserve both sources.** Deleting the losing citation destroys the reader's ability to
  re-evaluate.
- **Describe the contradiction** in the page, so it is visible rather than silently resolved.
- **Use dates.** Many apparent contradictions are sequential facts: someone was CEO and later
  became chair. That is not a conflict, it is a timeline — record the transition and let
  `State` carry the current role once the newer claim is sufficiently supported.
- **Record what evidence would resolve it**, so a future pass knows what to look for.

Hiding contradictory evidence is a correctness failure even when the chosen answer is right,
because the page then asserts more certainty than the evidence supports.

## Raw provenance

For external API or structured lookup results, preserve the raw response before distillation
where the active GBrain surface supports it. The reference `enrich` skill stores these via a
raw-data operation with the shape:

```json
{
  "source": "<provider>",
  "fetched_at": "<ISO 8601 timestamp>",
  "query": "<the query issued>",
  "data": { }
}
```

Record the provider, the query, the fetch timestamp, the target entity, the match confidence,
and which subset was used in compiled truth. Provenance is what makes compiled truth auditable
later — if a claim is ever questioned, the raw record shows exactly what the source returned.

Three constraints:

- **Raw data is not verified truth.** It is a record of what a provider said. The match may be
  the wrong person entirely.
- **Never store secrets.** Strip authentication tokens, credentials, and unrelated confidential
  material from anything preserved or logged.
- **Do not duplicate** raw data that GBrain already stores safely.
