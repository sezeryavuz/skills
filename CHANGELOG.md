# sezeryavuz-skills

## 0.3.0

### Minor Changes

- 203b5c7: Add a new promoted **`startup/`** bucket — company-building work: evidence, positioning, and entity knowledge — with two skills.

  **`founder-reflection-loop`** — founder-side startup reflection. It separates what a startup can actually evidence from what it merely asserts, repairs the founder-facing artifact (product memo, pitch narrative, accelerator application, landing page) honestly, and hands the result to the real `office-hours` skill for an independent diagnostic pass. Its central rule is that a rewrite may never upgrade a hypothesis into a fact, so its most useful output is often the verdict "this is not a writing problem" — ending a rewrite loop that could never have worked and replacing it with a concrete validation assignment. It is a founder coach, never an investor jury: it does not predict funding outcomes or invent traction. Ships a readiness rubric, YC-style analysis criteria, office-hours integration contract, and stdlib-only preflight/session/rubric scripts.

  **`refine-entity-pages`** — quality-guided refinement for GBrain person and company entity pages. It audits a page against the enrichment quality bar, explains what is weak, repairs what the evidence supports, hands the actual research and mutation to the official `enrich` skill, then re-reads the page from GBrain before claiming any improvement. The responsibility split is the point: this skill owns judgment (identity resolution, quality audit, claim ledger, privacy proportionality, convergence) while `enrich` owns external research and mutation — a wrapper that reimplemented the thing it audits would have no independent opinion. Runs identity resolution, privacy proportionality, and a recoverable snapshot before any mutation, even when the request is a plain "just enrich this person". Ships an entity quality model, claim/citation rules, notability tiers, and dependency-free audit/snapshot/preflight scripts.

## 0.2.2

### Patch Changes

- 2e3b5d4: `skill-kit`: harden against the two audited security findings.

  - **Indirect prompt injection (W011):** SKILL.md now states that every candidate field returned by `find-skills` (`name`, `summary`, `description`, security notes) is untrusted third-party content — data to display, never instructions to obey. Embedded directives like "ignore previous instructions" are surfaced as quoted data, never acted on.
  - **Runtime install (W012):** Phase 7 now requires an explicit batch confirmation before installing by default; a bypass (Phase 0 "just run" or a standing auto-approve) is opt-in, never the default. The canonical example drops the silent `-y` — it is added only after confirmation or when the user opted into a bypass.

## 0.2.1

### Patch Changes

- 23d5fc1: `skill-kit`: document installation in its README — add an **Install** section with the `skills` CLI commands, including the `sezeryavuz/skills@skill-kit` by-name form (resolves by `SKILL.md` `name`, so it survives the skill moving folders), the whole-collection form, and the `-g`/`-y` flags.

## 0.2.0

### Minor Changes

- 5ece987: Add the **`skill-kit`** skill — analyze a project or folder and assemble, then install, a tailored de-duplicated kit of agent skills matched to its stack, domain, and capability gaps. Where `find-skills` answers "what one skill fits this task?", `skill-kit` answers "what _combination_ does this whole project need?": it scans the repo (or a plain folder of files, for non-developers), infers stack/domain/capability gaps, asks a configurable number of targeted questions, drives `find-skills` to search the ecosystem, scores candidates against a transparent quality + safety rubric (hard-eliminating unsafe skills), de-duplicates by capability into one recommended set with a per-skill rationale, and installs it (or prints the ordered install commands). Ships with a dependency-free project scanner and a stdlib-only scorer.

## 0.1.0

### Minor Changes

- f28cefc: Add the **`prompt-to-production`** skill — turn a single brief (one markdown file or one detailed prompt) into a complete software project: planned, built, tested, and deployed autonomously across sessions, with a single soft-confirm gate in the middle. Generates `VISION.md`, `PRODUCT-SPEC.md`, `TECHNICAL-DECISIONS.md`, and `PLAN.md`, then executes a phased buildout, logging progress and surfacing blockers. Technology-agnostic.
