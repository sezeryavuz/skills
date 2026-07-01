# Skill Kit

> `skill-kit` — Analyze a project or folder and assemble, then install, a tailored de-duplicated kit of agent skills matched to its stack, domain, and capability gaps.

## Install

Install it into your agent with the [`skills`](https://skills.sh) CLI:

```bash
# just this skill, by name — recommended (resolves by SKILL.md `name`, so it
# survives the skill being moved to another folder in the repo)
npx skills@latest add sezeryavuz/skills@skill-kit

# ...or grab the whole collection and pick from the list
npx skills@latest add sezeryavuz/skills
```

Add **`-g`** to install globally (user-level, available in every project) instead of into the
current folder, and **`-y`** to skip the per-skill confirmation. The explicit in-repo path works
too if you prefer it: `sezeryavuz/skills/skills/productivity/skill-kit`.

## How to run it

`skill-kit` is **model-invoked** — so there are two ways to run it. Pick whichever is faster:

| Way | What you do | Example |
|---|---|---|
| **Just describe it** *(automatic)* | Say what you want in plain language while inside the project — Claude reaches for the skill on its own. | *"analyze this repo and set up the skills it's missing"* |
| **Call it directly** *(slash command)* | Type the command, optionally with a hint. | `/skill-kit` — or — `/skill-kit analyze this folder` |

Either way it opens with **one** question — *how many questions should I ask while I build this?* (**Ask me** · **Only critical** · **Just run**) — then scans the project, recommends a de-duplicated kit with a reason per skill, and installs it (or prints the exact commands).

> **Needs:** a terminal-backed agent (Claude Code) with `npx skills` on PATH. Best with the `find-skills` skill installed; otherwise it falls back to `npx skills find` and offers to install it first.

## What it does

Analyze a project or folder and assemble, then install, a tailored de-duplicated kit of agent skills matched to its stack, domain, and capability gaps. This is an [Agent Skill](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview):
a self-contained bundle of instructions and resources that Claude loads on demand when a task
matches its description.

Where `find-skills` answers "what one skill fits this task?", `skill-kit` answers "what *combination*
of skills does this whole project need?" — it scans the repo (or a plain folder of files, for
non-developers), infers stack/domain/capability gaps, asks a configurable number of well-targeted
questions, drives `find-skills` to search the ecosystem, scores candidates for quality and safety,
de-duplicates them into one recommended set with a reason per skill, and installs the set (or prints
the exact ordered install commands).

## When it triggers

Claude reaches for this skill when you:

- Are inside a repository or folder and ask "what skills does this project need?", "set up the right
  skills for this repo", or "analyze my project and install the skills it needs".
- Want a whole **combination** of skills equipped for a project, not one skill for one task.
- Have a non-code folder (spreadsheets, documents, designs) and want the right tools set up for it.
- Express a wish to equip a project with the right tooling — even without saying the word "skill".

## What's inside

```
skill-kit/
├── SKILL.md                     # the 7-phase workflow + interaction rules (the router)
├── README.md                    # this file
├── references/
│   └── scoring-rubric.md        # full quality + safety rubric; three-indicator security model
├── scripts/
│   ├── scan_project.sh          # Phase 1: detect stack / domain / capability gaps (dependency-free)
│   └── score_skill.py           # Phase 5: apply the rubric, hard-eliminate unsafe skills, rank
└── evals/
    └── evals.json               # starter test prompts for the skill-creator eval loop
```

- **`SKILL.md`** — the lean orchestration body: the interaction-mode/question-budget system, the
  seven phases (discover → question → extract → search → score → assemble → install), and the
  principles carried from `find-skills` (read before you trust, fit over popularity, verdict not menu).
- **`references/scoring-rubric.md`** — loaded at Phase 5: the transparent scoring weights, the
  install-count and star bands, and the three-indicator (red/yellow/green) security model with its
  all-red hard-eliminate.
- **`scripts/scan_project.sh`** — a POSIX-only scanner that turns a folder into a structured profile
  (JSON or report); it powers Phase 1 without any external dependencies or network access.
- **`scripts/score_skill.py`** — a stdlib-only implementation of the rubric that ranks the candidate
  pool into a kit, listing superseded duplicates and safety-eliminated skills so nothing vanishes silently.

The skill uses **progressive disclosure**: the lightweight `SKILL.md` is loaded when the skill
triggers, and the heavier bundled resources are read only when a task needs them — so the skill
stays cheap until its depth is actually required.

## How this skill was built

Built with Anthropic's [`skill-creator`](https://github.com/anthropics/skills), standing on two
existing finders:

- **`agentspace-so/find-skills`** — the multi-registry finder that supplied the security-scan
  taxonomy, the "read before you judge / deliver a verdict, not a menu" decision rubric, and the
  install-quality heuristics.
- **`vercel-labs/find-skills`** — the simpler single-registry finder that supplied the canonical
  `npx skills` command set (`find` / `add -g -y`) and the leaderboard-first search habit.

`skill-kit` owns project discovery and combination planning and delegates the actual ecosystem
search / vetting / install to whichever `find-skills` variant is installed, reusing its heuristics
rather than reinventing them. See the repo's `CLAUDE.md` for the skill conventions this follows.

## Credits

- **Maintainer:** [@sezeryavuz](https://github.com/sezeryavuz)
- **Built with:** Anthropic [`skill-creator`](https://github.com/anthropics/skills)

## License

See the repository for license terms.
