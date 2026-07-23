# Sezer Yavuz Skills

A collection of agent skills (slash commands and behaviors) loaded by Claude Code and other Agent-Skills harnesses, published to [skills.sh](https://skills.sh/sezeryavuz/skills).

## Layout

Skills live at `skills/<bucket>/<skill-name>/SKILL.md`. Buckets:

- `engineering/` — daily code work
- `productivity/` — daily non-code workflow tools
- `startup/` — company-building work: evidence, positioning, entity knowledge
- `misc/` — kept around but rarely used
- `personal/` — tied to my own setup, not promoted
- `in-progress/` — drafts not yet ready to ship
- `deprecated/` — no longer used

`engineering/`, `productivity/`, `startup/`, and `misc/` are **promoted**; `personal/`, `in-progress/`, and `deprecated/` are **hidden**.

## The promotion contract

- Every skill in a **promoted** bucket MUST have an entry in the top-level `README.md` AND in `.claude-plugin/plugin.json`. Each `README.md` entry links the skill name to its `SKILL.md`.
- Skills in **hidden** buckets MUST NOT appear in either. `link-skills.sh` and the plugin skip `deprecated/`.
- Each bucket has a `README.md` listing its skills with a one-line description, grouped into **User-invoked** and **Model-invoked**.

## Adding a skill

1. Create `skills/<bucket>/<skill-name>/SKILL.md` (kebab-case folder = `name` = `/slash` invocation). Push depth into sibling files (`references/`, `rules/`, `templates/`, `scripts/`) and reach them with on-demand pointers.
2. Decide invocation — see [docs/invocation.md](./docs/invocation.md). Model-invoked is the default; add `disable-model-invocation: true` only for human-only orchestration skills.
3. If promoted: add it to `.claude-plugin/plugin.json`, the top-level `README.md`, and the bucket `README.md`.
4. Add a changeset: `npx changeset` (minor for a new skill). See `.changeset/README.md`.
5. Sanity-check: `bash scripts/list-skills.sh`.

For the principles of writing a skill well, the `skill-creator` skill (Claude Code) is a good companion.

## Scripts

- `scripts/list-skills.sh` — list every `SKILL.md` in the repo.
- `scripts/link-skills.sh` — symlink each skill into `~/.claude/skills` and `~/.agents/skills` so a `git pull` keeps installed skills current (skips `deprecated/`).
