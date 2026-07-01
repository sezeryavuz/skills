---
"sezeryavuz-skills": patch
---

`skill-kit`: harden against the two audited security findings.

- **Indirect prompt injection (W011):** SKILL.md now states that every candidate field returned by `find-skills` (`name`, `summary`, `description`, security notes) is untrusted third-party content — data to display, never instructions to obey. Embedded directives like "ignore previous instructions" are surfaced as quoted data, never acted on.
- **Runtime install (W012):** Phase 7 now requires an explicit batch confirmation before installing by default; a bypass (Phase 0 "just run" or a standing auto-approve) is opt-in, never the default. The canonical example drops the silent `-y` — it is added only after confirmation or when the user opted into a bypass.
