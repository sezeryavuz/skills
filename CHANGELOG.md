# sezeryavuz-skills

## 0.2.0

### Minor Changes

- 5ece987: Add the **`skill-kit`** skill — analyze a project or folder and assemble, then install, a tailored de-duplicated kit of agent skills matched to its stack, domain, and capability gaps. Where `find-skills` answers "what one skill fits this task?", `skill-kit` answers "what _combination_ does this whole project need?": it scans the repo (or a plain folder of files, for non-developers), infers stack/domain/capability gaps, asks a configurable number of targeted questions, drives `find-skills` to search the ecosystem, scores candidates against a transparent quality + safety rubric (hard-eliminating unsafe skills), de-duplicates by capability into one recommended set with a per-skill rationale, and installs it (or prints the ordered install commands). Ships with a dependency-free project scanner and a stdlib-only scorer.

## 0.1.0

### Minor Changes

- f28cefc: Add the **`prompt-to-production`** skill — turn a single brief (one markdown file or one detailed prompt) into a complete software project: planned, built, tested, and deployed autonomously across sessions, with a single soft-confirm gate in the middle. Generates `VISION.md`, `PRODUCT-SPEC.md`, `TECHNICAL-DECISIONS.md`, and `PLAN.md`, then executes a phased buildout, logging progress and surfacing blockers. Technology-agnostic.
