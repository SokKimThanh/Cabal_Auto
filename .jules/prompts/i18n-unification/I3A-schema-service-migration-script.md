# I3A - Schema, Translation Service, And Migration Script

Paste `00-global-rules.md` first, then this prompt.

```text
Implement the Sprint 3 database foundation from .jules/i18n-sprint-roadmap.md.

Goal:
Add a `translations` table (namespace, key, lang, text, updated_at, unique on namespace+key+lang) and a TranslationService in lib/db/services/translation_service.py (200-300 line budget, following the existing repository connection/finally-close convention) with get_all(namespace=None), upsert(...), and bulk_upsert(...) wrapped in an explicit transaction. Add scripts/migrate_translations_to_db.py: an idempotent importer that reads every existing *_TRANSLATIONS dict (via the Sprint 2 audit helper) and upserts it into the table.

Files in scope:
- database.py (schema init hook only)
- lib/db/services/translation_service.py (new)
- scripts/migrate_translations_to_db.py (new)

Boundaries:
- Do not wire the runtime i18n registry to read from the DB yet; that is I3B.
- Keep the connection-per-call and finally: close() pattern used elsewhere in lib/db/services/.
- The migration script must be safe to run multiple times without creating duplicate rows (rely on the UNIQUE constraint plus upsert semantics).

Acceptance criteria:
- Running the migration script twice in a row produces the same row count both times.
- TranslationService methods have focused unit tests using a temporary/in-memory SQLite database.

Validation:
- Run `py -m pytest -k translation_service -v`.
- Run `py scripts/migrate_translations_to_db.py` twice and confirm row counts are stable.
```
