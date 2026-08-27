# I5A - Final Cleanup, Docs, And Definition Of Done

Paste `00-global-rules.md` first, then this prompt.

```text
Implement the Sprint 5 consolidation from .jules/i18n-sprint-roadmap.md.

Goal:
Confirm no dead registration code paths remain (search for register_bulk usages; every call site should be inside lib/i18n/ internals or the migration script), update docs/guides/I18N_GUIDE.md to describe the DB-backed flow as current, update /memories/repo/i18n-conventions.md with the final architecture summary, and run the full targeted i18n test suite plus a full app smoke start.

Files in scope:
- docs/guides/I18N_GUIDE.md
- .jules/i18n-sprint-roadmap.md (status update only)
- full test suite (read-only validation)

Boundaries:
- This session is consolidation and documentation only; it should not introduce new runtime behavior.
- Do not mark the roadmap done unless every acceptance criterion in .jules/i18n-sprint-roadmap.md section 7 (Definition of done) is verifiably true.

Acceptance criteria:
- Exactly one i18n package exists; no shadowed duplicate module.
- Every translation dictionary self-registers; no consumer module manually calls register_bulk.
- The namespace-agnostic integrity test passes and is part of the standard test run.
- A DB-backed store is the runtime source of truth, with dict files retained only as migration seed data.
- Adding a new language requires zero Python code changes for existing namespaces.

Validation:
- Run the full test suite (or at least all i18n-related tests) and `py .\app_gui.py` for a clean smoke start.
- List the definition-of-done checklist in the final response with a pass/fail mark for each item.
```
