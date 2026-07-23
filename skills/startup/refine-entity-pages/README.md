# Entity Page Refinement

> `refine-entity-pages` — Audits, repairs, and verifies GBrain person and company pages against
> the enrichment quality bar, then drives the official `enrich` skill and checks what it
> actually wrote.

## What it does

Audits, repairs, and verifies GBrain person and company pages against the enrichment quality
bar, then drives the official `enrich` skill and checks what it actually wrote. This is an
[Agent Skill](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview): a
self-contained bundle of instructions and resources that Claude loads on demand when a task
matches its description.

The goal is never a longer page — it is one that is more accurate, better sourced, better
connected, more current, and more explicit about what remains uncertain. It keeps a strict
separation from `enrich`: this skill owns judgment about the page (identity, quality audit,
claim ledger, privacy proportionality, convergence), while `enrich` owns external research and
mutation. That separation is what makes the check meaningful — a wrapper that reimplements the
thing it audits has no independent opinion.

## When it triggers

Claude reaches for this skill when you:

- Ask to review, improve, audit, or "make useful" a person or company page in a GBrain brain
- Want citations, timeline gaps, stubs, unsupported claims, or broken person/company
  cross-links found and fixed
- Are about to run `enrich`, or just ran it and want the result inspected
- Ask whether an entity deserves Tier 1, Tier 2, or Tier 3 research — or say "just enrich this
  person", where identity resolution and a snapshot still need to happen first

## Quickstart

Just describe the task — Claude consults the skill automatically. For example:

> Can you review and update people/priya-raman.md? Her role changed last month — she moved from
> Head of Eng to CTO at Lumen. I've got a pretty detailed read on her in there already that I
> don't want touched.

## What's inside

```
refine-entity-pages/
├── SKILL.md                          # router: responsibility split, 11-phase map, gates
├── README.md
├── references/
│   ├── entity-quality-model.md       # 20 quality dimensions, gap taxonomy, no-stub rule
│   ├── identity-and-notability.md    # identity resolution, notability gate, CREATE/UPDATE, tiers
│   ├── claim-and-citation-rules.md   # source precedence, claim ledger, contradictions, provenance
│   ├── privacy-and-sensitive-data.md # safety model, proportionality, inference safety
│   ├── enrich-integration.md         # enrich's interface, invocation, verification, bulk, recovery
│   ├── quality-rubric.md             # 0–4 scale, readiness gates, plateau detection
│   ├── output-contracts.md           # session artifacts, resumability, final report shape
│   └── enrich-source/
│       └── enrich-SKILL.reference.md # vendored copy of enrich, reference-only
├── scripts/
│   ├── preflight.py                  # locate enrich, probe GBrain runtime, find sessions
│   ├── snapshot.py                   # snapshot, content hash, diff — recovery and delta checks
│   └── audit_page.py                 # citations, timeline integrity, stub check, plateau compare
└── evals/
    └── evals.json                    # 8 starter test prompts
```

- **`SKILL.md`** — the router. Carries the responsibility split against `enrich`, five
  non-negotiables, the phase map (0–10), approval gates, and stop conditions. Everything deeper
  is one level down.
- **`references/`** — the depth, read per phase rather than up front.
- **`scripts/`** — deterministic checks only, so every pass measures the page the same way.
  That consistency is what makes plateau detection possible; judgment calls (does the source
  actually support this claim?) stay with the reader by design.
- **`evals/evals.json`** — starter prompts from the source brief's forward-test scenarios, each
  withholding the expected diagnosis. Assertions are left for the `skill-creator` eval loop.

The skill uses **progressive disclosure**: the lightweight `SKILL.md` is loaded when the skill
triggers, and the heavier bundled resources are read only when a task needs them — so the skill
stays cheap until its depth is actually required.

## How this skill was built

Forged with **`skill-forge`** (this repo's skill-building pipeline), which combined:

- **`projects/reversed-enrich/resources/brief.md`** — a 1,638-line specification
  reverse-engineered from the GBrain `enrich` skill, defining the refinement workflow, quality
  rubric, privacy model, and acceptance criteria. Ground truth for what this skill does.
- **`enrich`** by Garry Tan ([github.com/garrytan/gbrain](https://github.com/garrytan/gbrain)) —
  the skill this one wraps. Ground truth for `enrich`'s own interface: operation names, the
  seven-step protocol, the `auto_links` response shape, tier definitions, page templates, and
  validation heuristics. Vendored read-only under `references/enrich-source/`.

The research documents supplied the *facts* (APIs, versions, capabilities); the related skills
supplied the proven *structure*. `skill-forge` drives Anthropic's
[`skill-creator`](https://github.com/anthropics/skills) engine to assemble the two into a single
coherent skill. See the repo's `CLAUDE.md` for the full pipeline.

### Two deviations from repo convention, made deliberately

- **The skill name is `refine-entity-pages`, not the folder name `reversed-enrich`.** This
  repo's convention is normally folder-name-is-skill-name, but the source brief specifies its
  own working name, and that name describes what the skill does. `inventory_project.py` will
  still report `reversed-enrich` for this folder.
- **The brief targets a Codex skill** (`agents/openai.yaml`, no README) — this ships as a Claude
  Agent Skill instead, so the frontmatter carries only `name` and `description` and the README
  is present. The `enrich` reference's own frontmatter (`version`, `triggers`, `tools`,
  `mutating`, `writes_to`) belongs to another host's schema and was deliberately not carried
  across.

## Credits

- **Maintainer:** [@sezeryavuz](https://github.com/sezeryavuz)
- **Built with:** [`skill-forge`](../../../.claude/skills/skill-forge) · Anthropic
  [`skill-creator`](https://github.com/anthropics/skills)
- **`enrich`** skill by Garry Tan — [github.com/garrytan/gbrain](https://github.com/garrytan/gbrain)

## License

See the repository for license terms.
