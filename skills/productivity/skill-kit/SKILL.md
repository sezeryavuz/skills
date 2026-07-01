---
name: skill-kit
description: >
  Analyze the current project or folder and assemble a tailored KIT of agent skills for it —
  a curated, de-duplicated combination — then install them. Use whenever the user is inside a
  repository or a plain folder of files and wants the right skills set up for it: "what skills
  does this project need?", "set up the right skills for this repo", "analyze my project and
  install the skills it needs", "recommend a skill combination for this codebase", or any wish
  to equip a project with the right tooling — even if they never say the word "skill". It scans
  to infer stack, domain, and capability gaps, asks a configurable number of targeted questions,
  drives the find-skills skill to search the ecosystem, scores candidates for quality and safety,
  and de-duplicates them into one recommended set with a rationale each, then installs it. Reach
  for this instead of find-skills whenever the user wants a whole combination for a project
  rather than a single skill for one task.
---

# Skill Kit

`skill-kit` turns "here's my project" into "here's the exact set of skills it needs, and here's
how to install them." A person opens a repo — or even just a folder of files, if they aren't a
developer — runs one skill, and gets back a tailored, de-duplicated **kit**: the right combination
of agent skills for *this* project, each with a reason, ready to install.

It is a **finder that assembles a kit**, not a single-result search. It stands on the installed
**`find-skills`** skill: `skill-kit` owns project discovery and combination planning, and delegates
the actual ecosystem search / vetting / install to `find-skills`. Reuse `find-skills`'s heuristics
rather than reinventing them.

## What it needs to run

- A **real filesystem** (to scan the project) and the **Skills CLI** (`npx skills`) on PATH —
  i.e. Claude Code or a terminal-backed environment. If neither install path is available,
  `skill-kit` still runs the analysis and prints the exact commands for the user to run.
- The **`find-skills`** skill installed (either the `vercel-labs` or the multi-registry
  `agentspace-so` variant works). If it isn't installed, `skill-kit` falls back to calling
  `npx skills find [query]` directly and offers to install `find-skills` first.

## The pipeline at a glance

| Phase | What happens | Interaction |
|---|---|---|
| **0. Interaction mode** | Ask *one* question that sets the question budget for the whole run | Always asks |
| **1. Discover** | Scan the folder → a structured **project profile** (stack, domain, capability gaps) | Silent |
| **2. Pre-inference Qs** | Surface the coarse choices that steer the recommendation | Mode-gated |
| **3. Extract needs** | Turn the profile into concrete `find-skills` search queries | Silent |
| **4. Search** | Run each query through `find-skills`; pool candidates | Silent |
| **5. Score & vet** | Apply the quality + safety rubric; hard-eliminate unsafe skills | Silent |
| **6. Assemble kit** | De-duplicate by capability into one recommended set + rationale each | Mode-gated |
| **7. Install** | Install the set, or print the ordered install commands | Confirmed |

Run the phases in order. The two mode-gated phases (2 and 6) are where the questioning system
lives; everything else is inference the skill does on its own.

## Interaction rules (a first-class feature)

The questioning system is the point, not an afterthought — a good kit comes from a few
high-leverage questions, not an interrogation. Two rules govern every run:

**Rule 1 — Set the question budget first (Phase 0), every single run.** Before touching the
project, ask exactly one question:

> "I can ask you a few questions while I build this so the result fits your project better. How
> much should I ask?"
> - **Yes, ask me** — fully interactive.
> - **Only for critical things** — ask only when the answer would *change which skills get
>   recommended*; otherwise decide and move on.
> - **No, just run** — ask nothing; proceed on best inference.

Store that choice and honor it for the rest of the run. On tap-based clients, present the three
options as tappable buttons, not free text.

The middle mode needs a precise threshold so it's predictable: **a question is "critical" only if
the user's answer would change the recommended skill set.** "There's a checkout flow but no
payment provider chosen — which one?" changes which skill gets picked, so it's critical. A cosmetic
preference that leaves the set unchanged is *not* critical — skip it and default to the skill's own
recommendation.

**Rule 2 — Every question you ever ask carries three escape hatches,** in addition to its real
options, so the user is never cornered:

- **Recommend / apply your suggestion** — you make the best call.
- **Pass / skip** — leave this topic out entirely.
- **Your choice** — you decide, but briefly state your reasoning.

Keep questions minimal and one-at-a-time where possible. In "Only critical" mode, ask a Phase 2/6
question only when it clears the threshold above; in "No, just run" mode, ask nothing and infer
throughout.

---

## Phase 1 — Discover the project

Scan the current directory and build a **project profile**. This must work for developers *and*
non-developers, so read more than just code. Use the bundled scanner:

```bash
bash scripts/scan_project.sh . --json
```

It looks at, and you should reason over:

- **Dependency / manifest files** — `package.json`, `requirements.txt`, `pyproject.toml`,
  `Cargo.toml`, `go.mod`, `Gemfile`, `composer.json`, `pom.xml` → language, framework, libraries.
- **Config / infra signals** — `next.config.js`, `vite.config.*`, `tailwind.config.*`,
  `Dockerfile`, `.github/workflows`, `vercel.json`, `.env.example` → stack, deploy target, CI, env needs.
- **Repo metadata** — `.git/config`, `README`, folder structure, file-extension distribution.
- **Non-code folders (for non-developers)** — a folder dominated by `.docx`, `.xlsx`, images,
  PDFs, or design files → infer "accounting folder", "design project", "content archive",
  "research notes", and so on.

Fold the scanner's output into a structured profile: **detected stack**, **likely domain**
(e-commerce, fintech, blog, marketing site, data pipeline, document archive…), the **apparent
purpose**, and — the part that drives everything downstream — the **capability gaps / need
signals**, e.g.:

- No analytics/tracking code? → candidate need.
- A payment/checkout integration but no provider chosen? → need (and a likely *critical* question).
- Low or missing test coverage? No CI/CD? No linting/formatting config? → needs.
- Gaps in auth, i18n, accessibility, SEO, error monitoring, or documentation? → needs.

The scanner is a fast first pass, not the last word — read its findings and apply judgement. If it
misclassifies a folder, trust what you can see over the heuristic.

## Phase 2 — Pre-inference questions (mode-gated)

Surface the coarse decisions that steer the whole recommendation, honoring the interaction mode.
These are examples of the *style*, not a fixed script:

> "I don't see any analytics in this project. Want to add a tracking layer?"
> Yes → "Which one?" → PostHog / GA4 / Mixpanel / **Your choice** · No, skip · **Recommend for me**

Every such question carries the three escape hatches (Rule 2). In **"Only critical"** mode, ask
only the ones that would change the recommended set; otherwise default silently. In **"No, just
run"** mode, ask nothing.

## Phase 3 — Extract needs into search queries

Turn the (now question-refined) profile into a concrete list of `find-skills` queries — one or more
per need. Prefer **specific, multi-word** queries over vague single words, because the registries
index by a skill's *name*, not its meaning: `next.js performance`, `playwright e2e testing`,
`posthog analytics`, `stripe payments`, `accessibility audit`, `github actions ci`. For each need,
line up 2–3 adjacent-term queries (e.g. testing → `e2e`, `playwright`, `test automation`) — one
query routinely misses a great skill filed under a sibling term.

## Phase 4 — Search via find-skills

Run each query through `find-skills`'s search workflow (whatever variant is installed). Pool all
candidates. Two signals to capture as you go:

- **Cross-query hits.** If the same skill surfaces from several different queries, that's a stronger
  relevance signal — record how many queries it matched (it feeds the score in Phase 5).
- **Leaderboard staples.** Consult the skills.sh leaderboard for the battle-tested option in each
  domain; a well-known skill with 100K+ installs is a strong default even if a query didn't surface it.

`skill-kit` orchestrates `find-skills` here rather than duplicating its registry mechanics — if the
installed `find-skills` already emits install counts, stars, and security badges, consume those.

## Phase 5 — Score & vet

Score every candidate against the quality + safety rubric and drop the unsafe ones. The full rubric
— weights, install-count bands, the star threshold, and the three-indicator security model — lives
in **`references/scoring-rubric.md`**; read it when you reach this phase. The deterministic scorer:

```bash
python3 scripts/score_skill.py candidates.json     # or pipe JSON on stdin
```

The headline rules (full detail in the reference):

- **Official source** (anthropics, vercel-labs, microsoft, …) is a strong positive.
- **Install count**: 1K+ trusted · 100–1K okay · <100 risky.
- **GitHub stars**: under 100 → treat with skepticism.
- **Relevance**: matching multiple queries boosts the score.
- **Security** is one weighted factor with a hard floor: a skill whose **remote-execution indicator is
  red** — it runs fetched or obfuscated code, e.g. `curl | sh` — is eliminated automatically (any red
  indicator disqualifies; all three red is the worst case); **yellow** notes are surfaced and flagged
  but do *not* auto-reject — an official, popular, clearly-best-fit skill can still win with minor
  yellow warnings.

Security is a weighted factor with an any-red hard-eliminate, **not** a blunt gate — that's what lets
the best real skill win while still refusing the genuinely dangerous ones.

## Phase 6 — Assemble the kit (mode-gated)

- **De-duplicate by capability.** If two candidates do essentially the same job (say, three testing
  skills), keep only the best-scoring one. This is where a **post-inference question** may fire
  (mode permitting): *"I found 3 testing skills but you only need one — which style do you prefer?"*
  — again with the three escape hatches.
- **Produce the final recommended set** — "here are the N skills your project needs" — each with a
  **one-line rationale tied to a specific finding** from the profile ("added because there's a
  checkout flow but no analytics"). A rationale that just restates what the skill does has failed;
  tie it back to *this project's* gap.

## Phase 7 — Install

- If the environment allows and the user approves, install the set in order:
  ```bash
  npx skills add <owner/repo@skill> -g -y
  ```
  `-g` installs globally (user-level); `-y` skips the per-skill confirmation prompt.
- **Respect any auto-approve / bypass setting.** If the user has granted it, don't re-prompt per
  skill; otherwise get **one confirmation for the batch** (or per-skill if they asked for that).
- **If direct install isn't possible**, print the exact **ordered list of commands** in copy-paste
  form so the user can run them back-to-back themselves. Never leave them to reconstruct the list.

---

## Principles carried from find-skills

`skill-kit` triages many candidates with a score so a whole kit can be assembled systematically —
but the score is a *ranking aid*, never a verdict on its own. Keep these from `find-skills`:

- **Read before you trust.** Never recommend from metadata alone. For the top candidate of each
  need, skim its actual `SKILL.md` — does it do this project's specific task, or just share keywords?
- **Fit dominates popularity.** A 200-install skill that nails the need beats a 10K-install one that
  merely shares terms. Popularity is social proof *among* genuinely-fitting skills, not a substitute
  for fit.
- **Deliver a verdict, not a menu.** Don't dump the candidate table and make the user choose. Present
  the assembled kit with reasons; offer alternatives framed by need ("swap in X if you prefer Y").
- **State real signals, not a mystical number.** When you cite a score, back it with the concrete
  facts underneath it (installs, source, security status) — the rubric is transparent by design.

## Defaults you can change

The research brief left a few decisions open. `skill-kit` ships sensible defaults; treat any of them
as a (potentially critical) question when the interaction mode allows, and override on request.

| Decision | Default | Note |
|---|---|---|
| **Environment** | Claude Code / terminal (`npx skills` + filesystem) | If install isn't possible, print the commands instead. |
| **Scan depth** | 3 levels; skip `.git`, `node_modules`, build/vendor dirs | `scan_project.sh --depth N` to change. |
| **Install scope** | Global (`-g`) | Offer project-scoped install if the user prefers; ask when it's critical. |
| **Confirmation** | One batch confirmation when no bypass is set | Per-skill on request. |
| **How many** | Show all that clear the bar; if it's a long list, group by capability | No hard cap, but keep the kit focused. |

## Files in this skill

- `scripts/scan_project.sh` — Phase 1: detect stack / domain / capability gaps from a folder.
- `scripts/score_skill.py` — Phase 5: apply the quality + safety rubric and rank candidates.
- `references/scoring-rubric.md` — the full scoring criteria and the three-indicator security model.
- `evals/evals.json` — starter test prompts for verifying the skill (see `skill-creator`'s eval loop).
