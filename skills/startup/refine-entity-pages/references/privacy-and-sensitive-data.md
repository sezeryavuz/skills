# Privacy and Sensitive Data

This skill writes durable records about real people. Used in Phase 4 (research plan) and as a
standing check in Phases 6 and 8.

## Contents

- [The standard](#the-standard)
- [Never do these](#never-do-these)
- [Proportionality](#proportionality)
- [Inference safety](#inference-safety)
- [Sensitive-content review in Phase 8](#sensitive-content-review-in-phase-8)
- [When to stop and ask](#when-to-stop-and-ask)

## The standard

The operative question is not "can this be found?" but "does this belong in a durable personal
record about someone?"

**"Available on the internet" does not mean "appropriate to preserve in a personal brain."**
Public availability establishes only that a fact is knowable. A brain page aggregates scattered
facts into a single retrievable profile, and that aggregation is itself the privacy event —
each fact may be public while the compiled dossier is something that did not previously exist.

The people described here have not consented to it and will not review it. That asymmetry is
the reason for the constraints below.

## Never do these

**Identity and inference**

- Create a page for an unresolved or ambiguous identity
- Merge two people because they share a name
- Present inferred beliefs as hard facts, or predicted trajectory as verified fact
- Treat social-media tone as proof of private motivation
- Turn jokes, sarcasm, or isolated posts into permanent personality claims
- Infer health status, religion, sexual orientation, political affiliation, ethnicity,
  disability, or other highly sensitive traits — *inference* is the operative word; recording a
  fact the entity has stated publicly about itself is a different act from deducing one

**Collection scope**

- Store exact home addresses
- Collect unnecessary private phone numbers
- Collect private family information without a legitimate, user-authorized need
- Create dossiers for private individuals with no substantive relationship signal
- Enrich bots, spam accounts, joke profiles, or unverified identities
- Save secrets, authentication tokens, credentials, or unrelated confidential information

**Record integrity**

- Use a lower-quality source to overwrite a higher-quality first-party source
- Copy API boilerplate over user-authored relationship context
- Hide contradictory evidence
- Remove historical timeline entries because they no longer fit the current narrative

## Proportionality

Depth of research is depth of intrusion. Match it to the actual relationship, not to what is
technically retrievable:

- **Public figures and key business contacts** may justify broader public-source research —
  their public role is genuinely the subject.
- **Private individuals** require narrower scope and a stronger relevance test. What does the
  user actually need to remember about this person?
- **Tier 3 entities do not receive Tier 1 research.** This is the most common proportionality
  failure, because Tier 1 research is easy to run and looks thorough. Running a full people-API
  lookup on someone the user met once at a conference produces a surveillance record of a
  stranger.

Before paid, invasive, or credentialed external research, ask for authorization. State plainly
which calls cost money and which could expose private data — the user is deciding about a real
person, and needs to know that is what they are deciding.

## Inference safety

The single highest-risk content on a person page is a confident claim about their inner state.

A claim like *"They are motivated by status and secretly want to leave the company"* fails on
several counts at once: it asserts a private motivation as fact, it is unfalsifiable from
available evidence, it would damage the person if surfaced, and it will be read later as
established context.

The repair is not always deletion. Three options, in order of preference:

1. **Reformulate as an observation with a source.** "Their public writing returns repeatedly to
   competitive ranking [Source: …]" is defensible, useful, and lets the reader draw their own
   conclusion.
2. **Isolate and label it** as the user's own assessment, if that is what it is — user-authored
   judgment is legitimate content and is preserved, but it should be attributed rather than
   floating as page-voice fact.
3. **Remove it**, with user approval, if no evidence supports any version of it.

Explain what evidence *would* support a safer formulation. That turns a removal into a research
question rather than a loss.

Do not allow a subsequent `enrich` pass to reintroduce a claim that was removed for lack of
evidence — pass the constraint along as an explicit privacy boundary in Phase 7.

## Sensitive-content review in Phase 8

After `enrich` runs, check specifically for **privacy regression**: did the pass widen the
collected scope beyond what was authorized? New contact details, family information, location
precision, or inferred sensitive traits that were not in the baseline and were not approved are
regressions even when accurate, and they should be reported rather than quietly kept.

## When to stop and ask

Stop and ask for clarification when a requested action risks privacy harm, misidentification,
defamation, or harmful unsupported inference.

Refusing to guess is not unhelpfulness here. The cost of asking is one question; the cost of a
wrong or invasive permanent record about a real person is borne by someone who is not in the
conversation.
