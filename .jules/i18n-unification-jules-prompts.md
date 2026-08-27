# i18n Unification Jules Prompt Copybook

Split one-session prompt files are available in `.jules/prompts/i18n-unification/`. Use those files when launching Jules sessions to avoid overloading one session with the full roadmap. Follow `.jules/i18n-sprint-roadmap.md` as the source of truth.

Use these prompts as separate Jules sessions. Each prompt is intentionally scoped to one reviewable responsibility boundary. Do not combine prompts unless a previous session explicitly finished cleanly and the next prompt says it can start after that result.

## Global Rules For Every Jules Session

Paste `.jules/prompts/i18n-unification/00-global-rules.md` at the top of every prompt if Jules does not already have it in context.

## Execution Waves

Wave 0 can run first and is read-only/low-risk. Wave 1 must run after Wave 0. Later waves must run in order because each sprint's runtime source of truth depends on the previous sprint's storage layer.

| Wave | Sessions | Parallel? | Dependency |
| --- | --- | --- | --- |
| 0 | P0 | No | None |
| 1 | I1A, I1B | Sequential | P0 complete; run I1A first so I1B's dead-module deletion and integrity test see the fully self-registering set |
| 2 | I2A, I2B | I2A then I2B | Sprint 1 merged/clean |
| 3 | I3A, I3B | Sequential | Sprint 2 merged/clean |
| 4 | I4A, I4B | Sequential | Sprint 3 merged/clean (DB hydration must exist before removing manual registration) |
| 5 | I5A | No | All prior sprints merged/clean |

## Session Index

- `P0` — Baseline i18n Inventory
- `I1A` — Self-Register Remaining Translation Dictionaries
- `I1B` — Remove Dead i18n Module And Generalize The Integrity Test
- `I2A` — Add A Namespace-Agnostic Registry Audit Helper
- `I2B` — Document The Mandatory Pattern For New Screens
- `I3A` — Schema, Translation Service, And Migration Script
- `I3B` — Hydrate The i18n Registry From The Database
- `I4A` — Remove Remaining Manual Registration Call Sites
- `I4B` — Missing-Key Report Tool And Pilot Third Language
- `I5A` — Final Cleanup, Docs, And Definition Of Done

Full prompt text for each session lives in `.jules/prompts/i18n-unification/` — see the session files there for the exact copy-pasteable Jules prompt (same format as `.jules/architecture-cleanup-jules-prompts.md`).
