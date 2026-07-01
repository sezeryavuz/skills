---
"sezeryavuz-skills": minor
---

Add the **`skill-kit`** skill — analyze a project or folder and assemble, then install, a tailored de-duplicated kit of agent skills matched to its stack, domain, and capability gaps. Where `find-skills` answers "what one skill fits this task?", `skill-kit` answers "what *combination* does this whole project need?": it scans the repo (or a plain folder of files, for non-developers), infers stack/domain/capability gaps, asks a configurable number of targeted questions, drives `find-skills` to search the ecosystem, scores candidates against a transparent quality + safety rubric (hard-eliminating unsafe skills), de-duplicates by capability into one recommended set with a per-skill rationale, and installs it (or prints the ordered install commands). Ships with a dependency-free project scanner and a stdlib-only scorer.
