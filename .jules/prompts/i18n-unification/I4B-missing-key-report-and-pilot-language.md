# I4B - Missing-Key Report Tool And Pilot Third Language

Paste `00-global-rules.md` first, then this prompt.

```text
Implement the Sprint 4 tooling and language-scale proof from .jules/i18n-sprint-roadmap.md.

Goal:
Add scripts/i18n_report.py: a CLI that reports, per namespace, which keys are missing a translation for a given language by diffing database rows against the superset of keys across all languages. Use this tool to add a pilot third language for a small representative namespace (e.g. the top 10 most-visible GLOBAL_NS strings), entirely via database rows, with zero Python code changes, as proof the architecture scales.

Files in scope:
- scripts/i18n_report.py (new)
- database rows only for the pilot language (via the migration/service layer, not hand-edited SQL)

Boundaries:
- Do not add a full third-language translation for every namespace; a small representative pilot subset is sufficient to prove the design.
- Do not hardcode the pilot language anywhere in lib/i18n/__init__.py; it must work purely from data.

Acceptance criteria:
- scripts/i18n_report.py correctly flags missing keys when a language is incomplete for a namespace.
- Switching the app's default language to the pilot language renders the pilot namespace's strings correctly, and other namespaces fall back to en/vi without crashing.

Validation:
- Run `py scripts/i18n_report.py --lang <pilot_lang>` and confirm accurate missing-key output before and after populating pilot rows.
- Manually switch language and confirm the pilot namespace displays correctly.
```
