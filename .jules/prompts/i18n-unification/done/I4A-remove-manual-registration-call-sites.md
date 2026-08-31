# I4A - Remove Remaining Manual Registration Call Sites

Paste `00-global-rules.md` first, then this prompt.

```text
Implement the Sprint 4 consumer cleanup from .jules/i18n-sprint-roadmap.md.

Goal:
Now that lib/i18n/__init__.py hydrates the registry from the database at startup (I3B), remove any remaining manual i18n_register_bulk(...) call sites in consumer/UI modules. Keep the *_TRANSLATIONS dict files in place; they remain the seed data source for scripts/migrate_translations_to_db.py, they are simply no longer registered directly by consumer modules.

Files in scope:
- ui/windows/*.py (any file still calling i18n_register_bulk directly)
- app_gui.py

Boundaries:
- Before removing a call site, search the repository to confirm no other code depends on that specific call's timing (e.g. a screen that must register before another screen is imported).
- Do not delete the *_TRANSLATIONS dict definitions themselves in this session.

Acceptance criteria:
- No consumer module calls i18n_register_bulk directly; all registration flows through the DB hydration path from I3B.
- All screens still render translated strings correctly in en and vi.

Validation:
- Run `py -m pytest tests/unit/ -k i18n -v`.
- Manually spot-check every screen touched in Sprint 1 (Library Manager, Setup Wizard, Monster Editor, Vision Wizard) in both languages.
```
