# Sezer Yavuz's Skills

[![skills.sh](https://skills.sh/b/sezeryavuz/skills)](https://skills.sh/sezeryavuz/skills)

Agent skills I build and use for real work — small, composable, and model-agnostic. Hack around with them, adapt them, make them your own.

## Quickstart

```bash
npx skills@latest add sezeryavuz/skills
```

Pick the skills you want and which coding agents to install them on.

## Reference

Skills split on one axis — who can invoke them. **User-invoked** skills are reachable only when you type them (e.g. `/some-skill`); their job is to orchestrate. **Model-invoked** skills can be invoked by you _or_ reached for automatically by the agent when the task fits. See [docs/invocation.md](./docs/invocation.md) for the full convention.

### Engineering

Skills for code work.

**Model-invoked**

- **[prompt-to-production](./skills/engineering/prompt-to-production/SKILL.md)** — Turn a single brief (one markdown file or one detailed prompt) into a complete software project: planned, built, tested, and deployed autonomously across sessions, with one soft-confirm gate in the middle. Technology-agnostic.

### Productivity

_No skills yet._

### Misc

_No skills yet._

## Repo layout

```
skills/
├── engineering/   (promoted — listed here + in plugin.json)
├── productivity/  (promoted)
├── misc/          (promoted)
├── personal/      (hidden)
├── in-progress/   (hidden)
└── deprecated/    (hidden)
```

Each skill is a folder with a `SKILL.md`. Conventions, the promotion contract, and how to add a skill live in [CLAUDE.md](./CLAUDE.md).

## License

[MIT](./LICENSE).
