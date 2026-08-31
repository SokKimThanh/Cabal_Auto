# I3B - Hydrate The i18n Registry From The Database

Paste `00-global-rules.md` first, then this prompt.

```text
Implement the Sprint 3 hydration wiring from .jules/i18n-sprint-roadmap.md.

Goal:
Add a load_from_db() path in lib/i18n/__init__.py (or a small new module it calls into) that reads all rows via TranslationService.get_all() and feeds them through the existing register() function during app startup, so the in-memory registry is populated from the database. If the database is empty, missing, or the service errors, the app must fall back to the dict-based self-registration already in place from Sprint 1 with no visible raw-key regression.

Read docs/I18N_DATABASE_COMPATIBILITY_CONTRACT.md. Hydrate once before visible UI rendering; do not query SQLite from each `t()` call or a Tkinter render callback.

Files in scope:
- lib/i18n/__init__.py
- app_gui.py (call load_from_db() at the earliest safe startup point, before any _t() call)

Boundaries:
- This must be additive: deleting the database file must not break the app (dict fallback must still work).
- Do not remove the dict-based self-registration calls yet; both paths coexist until Sprint 4.
- Guard the DB read with a broad try/except that logs and falls back, matching the "JSON file I/O must gracefully fallback" and "robust error handling" conventions used elsewhere in this repo.

Acceptance criteria:
- With the database populated, screens render identically to before.
- With the database file deleted or the translations table empty, screens still render translated strings via the dict fallback, not raw keys.
- Empty/unseeded gameplay catalogue tables do not affect translation hydration or UI rendering.

Validation:
- Run `py -m pytest tests/unit/ -k i18n -v`.
- Delete/rename the database file, run `py .\app_gui.py`, confirm clean startup and correctly translated UI, then restore the database file.
```
