# Scoring & Safety Rubric

The full rubric for Phase 5. Load this when scoring candidates; keep the SKILL.md body lean.

The score exists to **triage a whole kit** — dozens of candidates across many capability gaps —
into a ranked, de-duplicated set. It is a transparent ranking aid, not an oracle: every component is
a real, inspectable signal, and the final call still requires reading the top candidate (see
"Principles carried from find-skills" in `SKILL.md`). `score_skill.py` implements exactly this rubric;
if you change a weight here, change it there too.

## Contents

- [Inputs the scorer expects](#inputs-the-scorer-expects)
- [Quality components](#quality-components)
- [The three-indicator security model](#the-three-indicator-security-model)
- [Combining into a score](#combining-into-a-score)
- [De-duplication by capability](#de-duplication-by-capability)
- [What the scorer outputs](#what-the-scorer-outputs)
- [Worked example](#worked-example)

---

## Inputs the scorer expects

Each candidate is one JSON object. Populate it from `find-skills`'s output where you can — if the
installed `find-skills` already emits install counts, stars, and a security badge, consume those
rather than re-deriving them.

```json
{
  "name": "playwright-e2e",
  "owner": "microsoft",
  "installs": 12000,
  "stars": 3400,
  "relevance_count": 3,
  "capability": "e2e-testing",
  "security": {"remote_exec": "green", "tool_scope": "yellow", "secrets": "green"},
  "summary": "End-to-end browser testing with Playwright."
}
```

- `owner` — the source repo owner; drives the official-source signal.
- `installs`, `stars` — popularity signals (board-native numbers, not invented).
- `relevance_count` — how many distinct Phase 3 queries surfaced this skill (≥1).
- `capability` — the coarse job it does; the de-dup key (two skills with the same `capability`
  compete for one slot).
- `security` — the three indicators (see below). A plain string (`"green"` / `"yellow"` / `"red"`)
  is accepted as shorthand for "all three the same".

## Quality components

All weights are **tunable defaults**, chosen to match the bands the research brief specifies. They
are additive and transparent — no hidden composite.

| Component | Rule | Points |
|---|---|---|
| **Official source** | owner ∈ {anthropics, vercel-labs, microsoft, google, openai, …} | +30 |
| | other known-reputable owner | +15 |
| | unknown owner | 0 |
| **Install count** | 1K+ | +25 |
| | 100–1K | +12 |
| | under 100 | 0 *(and flag as risky-by-obscurity)* |
| **GitHub stars** | 100+ | +15 |
| | under 100 | 0 *(treat with skepticism)* |
| **Relevance** | +10 per query matched beyond the first, capped at +20 | 0…+20 |
| **Security** | see the three-indicator model below | −∞…+10 |

The install-count bands (1K+ / 100–1K / <100) and the <100-star skepticism threshold come straight
from `find-skills`'s quality heuristics — `skill-kit` reuses them rather than inventing new ones.

## The three-indicator security model

Model **three security checks** per skill, each **red / yellow / green**. The three indicators, and
the concrete patterns that trip them (mapped from `find-skills`'s security scan), are:

| Indicator | What it checks | Red (risky) | Yellow (caution) | Green |
|---|---|---|---|---|
| **remote_exec** | Runs fetched/obfuscated code | `curl \| sh`, `eval $(curl …)`, `base64 -d \| sh` | — | none found |
| **tool_scope** | Permission breadth | — | `allowed-tools` grants `Bash(*)` / unrestricted | scoped tools |
| **secrets** | Credential handling | — | reads `~/.ssh` `~/.aws` `.env` / asks you to paste an API key | none found |

The rollup rule from the research brief:

- **Any red → eliminate automatically.** Do not recommend, regardless of how good the quality score
  is. In practice only the remote-exec indicator can go red, and a single red remote-exec indicator is
  on its own disqualifying unless the user knowingly accepts the risk — never surface a `curl | sh`
  skill without spelling out what it does. "All three red" is just the worst case of the same rule.
  (This is deliberately stricter than the research brief's literal "all three red" wording: the concrete
  taxonomy makes a red remote-exec = a `curl | sh` skill, which `find-skills` treats as disqualifying,
  so `skill-kit` eliminates on any red to stay on the safe side.)
- **One or more yellow (and no red) → allowed, but flagged.** A skill can be high-quality *and* carry
  a medium/yellow note. Surface the warning in the rationale and let the score carry it; do not
  auto-reject. This is the whole point of a weighted factor over a blunt gate.
- **All green → clean.** No security note needed.

Security contributes at most **+10** to the score (all green), **0** for any yellow, and triggers
**hard elimination** on any red indicator — so safety shapes the ranking without ever letting a
dangerous skill outrank a safe one on popularity alone.

If `find-skills` already produced a badge (`✓ clean` / `⚠ caution` / `⛔ risky`), map it onto the
indicators: `clean → all green`, `caution → the relevant indicator yellow`, `risky → the relevant
indicator red`. A badge is a heuristic prompt to read the skill yourself, not a guarantee.

## Combining into a score

```
score = source + installs + stars + relevance + security_bonus
```

with the security **hard-eliminate** applied first: if any indicator is red, the candidate is dropped
from the ranking entirely (it never gets a numeric score). Everything else is the additive
sum above, so a reader can always reconstruct *why* one skill outranks another from its component
line. Ties break toward the skill you have actually read and can vouch for, with the narrowest clear
scope and the fewest surprising dependencies.

## De-duplication by capability

A kit should contain **one** skill per job. Group the surviving candidates by `capability`; within
each group, keep the highest-scoring skill and mark the rest as *"also considered — superseded by
X."* When a group has two strong, genuinely different options (e.g. two testing *styles*), that is a
legitimate **Phase 6 post-inference question** — ask which the user prefers (mode permitting, with
the three escape hatches) instead of silently picking.

## What the scorer outputs

`score_skill.py` prints (and, with `--json`, emits) two things:

1. **The kit** — the de-duplicated winners, ranked, each with its component breakdown, security flag,
   and a slot for the one-line rationale you'll tie back to a project finding in Phase 6.
2. **Also-ran / eliminated** — superseded duplicates and any hard-eliminated skills, with the reason,
   so nothing disappears silently.

## Worked example

Two testing candidates surface for the same `e2e-testing` capability:

- `microsoft/playwright-e2e` — official (+30), 12K installs (+25), 3.4K stars (+15), matched 3
  queries (+20), all-green security (+10) → **100**.
- `randomdev/quick-e2e` — unknown owner (0), 60 installs (0, obscure), 12 stars (0), matched 1 query
  (0), tool_scope yellow (`Bash(*)`, 0 + flag) → **0**, flagged.

The kit keeps `playwright-e2e` with rationale *"added because there's a web app but no e2e tests"*;
`quick-e2e` is listed under also-ran as *superseded by playwright-e2e, and grants broad Bash access.*
The numbers are all real signals — the recommendation reads as a defensible verdict, not a black box.
