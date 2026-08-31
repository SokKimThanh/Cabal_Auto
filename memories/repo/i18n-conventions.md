# i18n Conventions & Architecture Summary

## Overview

The i18n system uses a hybrid approach, where a SQLite database (`translations` table) is the primary source of truth, and file-based Python dictionaries (`lib/i18n/*_TRANSLATIONS.py`) serve as fallback seed data.

## Key Principles

1. **Database as Source of Truth:** At runtime, the application hydrates its translation registry from the database using `lib.i18n.load_from_db()`.
2. **Resilience & Fallback:** If the database is missing, corrupted, or empty, the application falls back to a self-registration mechanism. All dictionary files in `lib/i18n/` automatically call `register_bulk()` upon import. This ensures the application never silently displays raw keys to the user.
3. **Zero Manual Registration:** Consumer modules (like UI classes) must **never** manually register translations. They should simply import the relevant `lib/i18n/*_TRANSLATIONS.py` module to trigger the self-registration fallback, and rely on `load_from_db()` for the primary hydration.

## Workflow & Tooling

* **Adding a New Screen/Translations:**
  1. Create a dictionary file (e.g., `lib/i18n/my_screen_translations.py`) and include `register_bulk('my_screen', MY_SCREEN_TRANSLATIONS)` at the bottom.
  2. Import this dictionary in your UI code to trigger self-registration.
  3. Run `scripts/migrate_translations_to_db.py` to upsert the new keys into the database.
* **Checking for Missing Keys:** Run `python scripts/i18n_report.py --lang [lang_code]` to generate a report of missing translation keys for a specific language.
* **Integrity Auditing:** The test suite (`tests/unit/test_i18n_registry_integrity.py`) verifies that all dictionaries defined in `lib/i18n/` are properly self-registered, ensuring no namespace is left dangling.
