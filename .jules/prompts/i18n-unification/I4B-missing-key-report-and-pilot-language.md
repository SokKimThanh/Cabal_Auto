# I4B - Missing-Key Report Tool And Pilot Third Language

Paste `00-global-rules.md` first, then this prompt.

```text
Implement the Sprint 4 tooling and language-scale proof from .jules/i18n-sprint-roadmap.md.

Goal:
Add scripts/i18n_report.py: a CLI that reports, per namespace, which keys are missing a translation for a given language by diffing database rows against the superset of keys across all languages. Use this tool to add a pilot third language for a small representative namespace entirely via database rows as a data-scale proof.

Files in scope:
- scripts/i18n_report.py (new)
- database rows only for the pilot language (via the migration/service layer, not hand-edited SQL)

Boundaries:
- Do not add a full third-language translation for every namespace; a small representative pilot subset is sufficient to prove the design.
- Do not hardcode the pilot language anywhere in lib/i18n/__init__.py; it must work purely from data.
- Do not expose the pilot language in the global language selector unless all UI keys reachable in the exposed screens are translated or a separately tested fallback chain prevents raw-key leaks.

Acceptance criteria:
- scripts/i18n_report.py correctly flags missing keys when a language is incomplete for a namespace.
- Explicit lookup for the fully populated pilot namespace returns correct pilot strings.
- Missing-key report proves which keys/namespaces remain incomplete; the pilot is not exposed globally while incomplete.

Validation:
- Run `py scripts/i18n_report.py --lang <pilot_lang>` and confirm accurate missing-key output before and after populating pilot rows.
- Do not manually switch the whole app to the pilot language unless full reachable-key coverage or fallback-chain validation has passed.
```
