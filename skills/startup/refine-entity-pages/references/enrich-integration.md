# Enrich Integration

How to verify, invoke, and audit the official `enrich` skill. Used in Phases 0, 7, 8, and for
bulk runs and error recovery.

## Contents

- [What enrich is](#what-enrich-is)
- [Dependency preflight](#dependency-preflight)
- [Runtime verification is separate from installation](#runtime-verification-is-separate-from-installation)
- [Invoking enrich](#invoking-enrich)
- [The handoff fallback](#the-handoff-fallback)
- [Post-enrich verification](#post-enrich-verification)
- [Bulk enrichment](#bulk-enrichment)
- [Error and recovery behavior](#error-and-recovery-behavior)

## What enrich is

`enrich` is a mutating skill that creates and updates person and company pages from external
sources, scaling effort to importance through a three-tier protocol. Its contract: every
enriched page carries compiled truth with inline citations and a dated timeline, back-links are
bidirectional, and no page is created as a stub.

A vendored copy is at `enrich-source/enrich-SKILL.reference.md` — reference only. Never edit the
installed skill to make this skill's checks pass, and never place a second active `SKILL.md`
where it could be discovered as this skill's root definition.

### Its operations

| Operation | Purpose |
|---|---|
| `get_page` / `put_page` | Read and write a brain page |
| `search` / `query` | Brain-first lookup |
| `add_link` / `get_backlinks` | Graph edges and backlink inspection |
| `add_timeline_entry` | Timeline writes — required explicitly, not automatic |
| `put_raw_data` / `get_raw_data` | Raw provenance preservation |
| `list_pages` | Enumerate by type |

CLI forms appear as `gbrain search "name"`, `gbrain query "what do we know about name"`, and
`gbrain timeline-add`.

### Its seven-step protocol

1. Identify entities in the incoming signal
2. Check brain state — search decides CREATE vs UPDATE
3. Extract signal from source, capturing texture and not only facts
4. External lookups in priority order: brain cross-reference (all tiers) → web research
   (Tier 1–2) → social lookup (all tiers when a handle is known) → people APIs (Tier 1) →
   company APIs (Tier 1)
5. Save raw data, preserving provenance
6. Write to brain via the CREATE or UPDATE path
7. Cross-reference related pages

Knowing the protocol is what lets Phase 8 check whether it was actually followed. It is not a
license to perform the steps yourself — see the responsibility split in `SKILL.md`.

### Behavior worth knowing before auditing a result

- **Links auto-create on every `put_page`.** The response carries an `auto_links` field shaped
  `{ created, removed, errors }`. Do not also create those links manually; inspect the field.
  Timeline entries are *not* covered by this and still need explicit calls.
- **Empty sections are left as `[No data yet]`** rather than filled with boilerplate — so an
  empty section is expected behavior, not a defect. Judge the page as a whole.
- **A page enriched within the past week is normally skipped** unless new signal warrants it.

## Dependency preflight

Run `scripts/preflight.py` first, then confirm what it cannot determine.

1. Check whether `enrich` is already installed and discoverable.
2. If not, install it once:
   `npx skills add https://github.com/garrytan/gbrain --skill enrich`
3. Do not install duplicates when a compatible installation exists.
4. Do not invent undocumented installer flags. If the installer is interactive, inspect its
   help output rather than guessing at a non-interactive form.
5. Confirm the installed location and that its `SKILL.md` is readable.
6. Read it completely — the installed version is authoritative over the vendored copy, which
   may lag.
7. Determine whether the host needs a registry reload or a new session before newly installed
   skills become discoverable, and handle that explicitly rather than reporting a false absence.
8. Record host-specific limitations.

**Never silently reinstall or update `enrich` on every invocation.** That turns a dependency
check into an unpredictable upgrade in the middle of the user's workflow.

## Runtime verification is separate from installation

Installing the skill definition does not make the underlying GBrain tools available. Verify
independently:

- GBrain CLI availability
- GBrain MCP availability
- Active brain and source routing
- Read permissions
- Write permissions
- Timeline operations
- Raw-data operations
- Search and query operations
- Page write operations
- Auto-link behavior

**If routing is ambiguous, refuse to mutate.** When multiple brains or sources are configured,
never default to one — a write to the wrong brain is a real mutation in a real place, and the
user has no reason to look for it there.

Where an operation is missing, say so and adjust what you promise. If raw-data storage is
unavailable, provenance cannot be preserved that way; report the limitation instead of
proceeding as if it were.

## Invoking enrich

Use the host's native skill-invocation mechanism. **Reading `enrich`'s file is not invoking
it**, and neither is following its protocol yourself.

Provide:

- Exact entity identity
- Existing page path
- CREATE or UPDATE status
- Selected tier
- The material new signal
- Relevant source material
- Active brain and source routing
- Known identity constraints
- Existing page context
- Privacy boundaries (including any claim removed for lack of evidence, so it is not
  reintroduced)

### Never lead the witness

Do not supply a desired verdict. These corrupt the only independent check in the loop:

- "Confirm that this page is high quality."
- "Ignore unresolved citation problems."
- "Do not challenge the existing assessment."
- "Produce a passing result."
- "Preserve all of my proposed conclusions."
- "Add information even if no source supports it."

The value of invoking a separate skill comes entirely from it reaching its own conclusion. An
`enrich` run steered toward agreement tells you nothing you did not already believe.

### Record what it did

Sources queried · raw data saved · page writes · timeline entries · compiled-truth changes ·
cross-reference changes · `auto_links` results · skipped sources · validation flags · API
failures · identity warnings · contradictions · final page path

Never claim `enrich` assigned a quality score. It does not. Any aggregate is yours, and is
labeled accordingly — see `quality-rubric.md`.

## The handoff fallback

If direct skill-to-skill invocation is unavailable, do not simulate it. Produce a resumable
handoff:

1. Save the current page snapshot and refinement state.
2. Save the candidate changes.
3. Tell the user exactly how to invoke `enrich`.
4. Identify the entity and target page.
5. Identify which source material to provide.
6. **Stop before claiming validation.**
7. Resume when the enriched page or `enrich` output is available.

```markdown
## Handoff — enrich invocation required

**Entity:** <canonical name>  **Page:** <path>  **Mode:** <CREATE|UPDATE>  **Tier:** <1|2|3>
**Brain / source:** <active routing>

**Run:** <exact invocation for this host>
**Provide:** <the specific source material>
**Constraints:** <identity constraints and privacy boundaries to pass along>

**State saved at:** <session path>
**To resume:** <exact instruction>
**Not yet verified:** the page has not been re-read; no quality claim is being made.
```

## Post-enrich verification

Read the resulting page **fresh from GBrain**. Judging from cached pre-write content is how a
false validation claim gets made — and it is indistinguishable from a real one in the output.

Compare three versions: baseline → candidate refinement → actual enriched result. The candidate
matters here because the gap between what you proposed and what landed is where silent
overwrites show up.

Inspect for: unexpected overwrites · missing user-authored text · unsupported additions ·
citation coverage · source quality · timeline duplication · timeline ordering · identity
consistency · cross-reference integrity · auto-link errors · contradictions · privacy
regressions · boilerplate · empty sections · material usefulness.

### Delta report

```markdown
## Delta — pass <n>

**Page:** <path>   **Read back at:** <timestamp>   **Content hash:** <before> → <after>

| Change | Section | Before | After | Sourced? | Verdict |
|---|---|---|---|---|---|
| <added/changed/removed> | <section> | … | … | <citation or none> | <keep / flag / revert> |

**User-authored content:** <preserved / MODIFIED — detail>
**Timeline:** +<n> entries, duplicates: <n>, ordering: <ok/broken>
**auto_links:** created <n>, removed <n>, errors <n> — <detail on any error>
**Privacy scope:** <unchanged / widened — detail>
**Unsupported additions:** <list, or none>
**Rubric movement:** <dimension: before → after, for dimensions that moved>
```

Reverting is a legitimate outcome. If a pass overwrote user-authored judgment or added
unsupported claims, restore from the snapshot and report it.

## Bulk enrichment

Bulk work multiplies every error and removes the human read that would catch it, so the gates
come before the volume.

**Before mutating:** resolve the source list · deduplicate entities · sample 3–5 · run the
complete workflow on the sample · show the sample outputs · require user approval · define rate
limits, API budget, privacy scope, failure and retry behavior, and resume checkpoints.

The sample is the point. Reading actual output for a few entities is what reveals a systematic
problem while it still costs five pages instead of a hundred.

**During:** process in bounded batches · respect rate limits · avoid repeat research for
duplicates · save raw provenance · record per-entity status · pause on identity ambiguity or
schema mismatch · do not let one failure corrupt the batch · check load before spawning
parallel work · checkpoint every 5–10 entities where the active repository policy allows ·
never push automatically.

**After — audit report:** total entities · created · updated · skipped · ambiguous identities ·
no-notability results · sources used · API failures · citation failures · privacy flags ·
auto-link errors · remaining gaps.

## Error and recovery behavior

| Condition | Response |
|---|---|
| `enrich` not installed | Install once via the documented command; if that fails, report a precise blocker |
| Installed but not discoverable | Check whether the host needs a reload or new session; report that requirement |
| GBrain CLI or MCP unavailable | Report which surface is missing; no mutation |
| Available but write permission missing | Audit and report only — this is a valid no-mutation run |
| Multiple brains configured / routing ambiguous | Stop. Ask which brain. Never default |
| Target entity ambiguous | Identity-resolution brief; no mutation |
| Duplicate person or company pages | Surface both; merging requires explicit user approval |
| Page changed after baseline snapshot | Re-snapshot and re-audit; someone else wrote to it |
| Page enriched recently | Skip unless a material new signal exists; say which |
| Source conflicts with compiled truth | Preserve both, surface the contradiction |
| External API returns the wrong person | Save raw only, do not update compiled truth, flag the identity error |
| Source contains stale data | Date it; do not let it overwrite fresher first-party material |
| Page contains unsupported sensitive claims | Flag; repair per `privacy-and-sensitive-data.md` |
| Raw-data or timeline operations unavailable | Report the limitation and what it means for provenance |
| Auto-linking reports errors | Record created/removed/errors; verify content cross-references separately |
| `enrich` partially succeeds | Record what landed; re-read; do not assume the rest |
| A pass adds boilerplate or overwrites user content | Revert from snapshot; report; do not re-run blindly |
| Two passes produce no improvement | Plateau — stop and report what would justify resuming |
| APIs rate-limited | Back off; checkpoint; resume |
| Paid research requires authorization | Ask before spending |
| Bulk run interrupted | Resume from the last checkpoint; do not restart the batch |

When blocked, report: the exact blocker · current target · active brain and source · work
completed · preserved artifacts · mutations already made · recovery action · exact resume
instruction.

### Repository safety

Do not use destructive repository commands, force-push, or delete pages to repair them without
explicit authorization. Prefer a reversible patch or a restored snapshot. Do not commit
unrelated files, and do not push unless the user asks.
