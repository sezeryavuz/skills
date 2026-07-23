# Founder Reflection Loop

> `founder-reflection-loop` — Separates what a startup can actually evidence from what it merely
> asserts, repairs the founder-facing artifact honestly, and uses the `office-hours` skill as an
> independent diagnostic pass.

## What it does

Separates what a startup can actually evidence from what it merely asserts, repairs the
founder-facing artifact honestly, and uses the `office-hours` skill as an independent diagnostic
pass. This is an
[Agent Skill](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview): a
self-contained bundle of instructions and resources that Claude loads on demand when a task
matches its description.

It is a founder coach, not an investor jury. It will not predict funding outcomes, score founder
quality, or manufacture traction — and its central rule is that **a rewrite may never upgrade a
hypothesis into a fact**. The most useful thing it produces is often the verdict "this is not a
writing problem," which ends a rewrite loop that could never have worked and replaces it with a
concrete validation assignment.

## When it triggers

Claude reaches for this skill when you:

- Want help preparing how to present a startup, or want the weaknesses in a startup story found
- Ask to make a product memo, pitch narrative, accelerator application, or landing page
  "founder-ready" — or to improve one before running office hours
- Want to iterate on a design doc with `office-hours` and analyse what changed between passes
- Ask which problems are writing problems versus evidence problems, or ask about criteria like
  demand reality, status quo, narrowest wedge, or desperate specificity

## Quickstart

Just describe the task — Claude consults the skill automatically. For example:

> We have six paying logistics customers, but our pitch says we are an end-to-end AI operating
> system for global supply chains. Something feels off — can you help me fix the narrative?

## What's inside

```
founder-reflection-loop/
├── SKILL.md                              # router: coach-not-jury stance, 10-phase map, gap classes
├── README.md
├── references/
│   ├── startup-analysis-criteria.md      # 9 dimensions, stage routing, pushback patterns
│   ├── founder-readiness-rubric.md       # 0–4 scale, stage-aware ceilings, convergence
│   ├── office-hours-integration.md       # its outputs, STOP points, the score caveat, recovery
│   ├── output-contracts.md               # session artifacts, versioning, final founder package
│   └── office-hours-source/              # vendored copy of office-hours, reference-only
│       ├── office-hours-SKILL.reference.md
│       ├── office-hours-SKILL.tmpl.reference.md
│       └── sections/
│           ├── design-and-handoff.reference.md
│           ├── design-and-handoff.tmpl.reference.md
│           └── manifest.json
├── scripts/
│   ├── preflight.py                      # project root, artifacts, office-hours install, sessions
│   ├── session.py                        # init, append-only iteration snapshots, state validation
│   └── rubric.py                         # evidence-backed scores, iteration compare, plateau guard
└── evals/
    └── evals.json                        # 7 starter test prompts
```

- **`SKILL.md`** — the router. Carries the founder-coach stance, the responsibility split against
  `office-hours`, the phase map (0–9), the gap-class table, and the interaction rules.
- **`references/`** — the depth, read per phase rather than up front.
- **`scripts/`** — the mechanical guards. `rubric.py` is the important one: it refuses scores
  without evidence and distinguishes "the score rose" from "a gap was resolved", which is what
  stops an endless rewrite loop.
- **`evals/evals.json`** — starter prompts from the brief's forward-test scenarios, each
  withholding the expected diagnosis.

The skill uses **progressive disclosure**: the lightweight `SKILL.md` is loaded when the skill
triggers, and the heavier bundled resources are read only when a task needs them — so the skill
stays cheap until its depth is actually required.

## How this skill was built

Forged with **`skill-forge`** (this repo's skill-building pipeline), which combined:

- **`projects/reversed-office-hours/resources/brief.md`** — a 1,051-line specification
  reverse-engineered from the gstack `office-hours` skill, defining the founder-side workflow,
  readiness rubric, gap taxonomy, and acceptance criteria. Ground truth for what this skill does.
- **`office-hours`** by Garry Tan ([github.com/garrytan/gstack](https://github.com/garrytan/gstack))
  — the skill this one hands off to. Ground truth for its own behaviour: the six forcing
  questions, stage routing, design-doc structure, STOP points, completion statuses, and the
  adversarial-review score. Vendored read-only under `references/office-hours-source/`.

The research documents supplied the *facts* (APIs, versions, capabilities); the related skills
supplied the proven *structure*. `skill-forge` drives Anthropic's
[`skill-creator`](https://github.com/anthropics/skills) engine to assemble the two into a single
coherent skill. See the repo's `CLAUDE.md` for the full pipeline.

### Notes on the synthesis

- **Dimensions 1–6 are the founder-side reading of `office-hours`' six forcing questions**;
  dimensions 7–9 (premise integrity, distribution reality, narrative integrity) are what the
  brief adds for the work a founder does *between* diagnostic sessions.
- **The `office-hours` quality score is carefully scoped.** It exists only when an adversarial
  reviewer subagent is available, and it grades the *design document* on completeness,
  consistency, clarity, scope, and feasibility — not the startup. Reporting it as a startup
  score would be exactly the fabrication the brief prohibits, so the integration reference makes
  the distinction explicit.
- **The brief says `.tmpl` files are the source of truth.** Mostly true, but the generated
  `design-and-handoff.md` carries the adversarial-review step its template does not, so both
  were read and both are vendored.
- **Not carried across:** gstack's template placeholders, its builder-profile and relationship-tier
  personalisation, its analytics logging, and its frontmatter schema (`preamble-tier`, `version`,
  `triggers`, `gbrain`). Those are host-specific; this skill's frontmatter is `name` and
  `description` only.

### Two deviations from repo convention, made deliberately

- **The skill name is `founder-reflection-loop`, not the folder name `reversed-office-hours`.**
  This repo normally treats folder-name as skill-name, but the source brief specifies its own
  working name and that name describes what the skill does. `inventory_project.py` will still
  report `reversed-office-hours` for this folder.
- **The brief targets a Codex skill** (`agents/openai.yaml`, no README) — this ships as a Claude
  Agent Skill instead, so the README is present and the frontmatter carries only `name` and
  `description`.

## Credits

- **Maintainer:** [@sezeryavuz](https://github.com/sezeryavuz)
- **Built with:** [`skill-forge`](../../../.claude/skills/skill-forge) · Anthropic
  [`skill-creator`](https://github.com/anthropics/skills)
- **`office-hours`** skill by Garry Tan — [github.com/garrytan/gstack](https://github.com/garrytan/gstack)

## License

See the repository for license terms.
