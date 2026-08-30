# DB0 - Schema And Source Audit

Paste `00-global-rules.md` before this prompt.

```text
Documentation/read-only session, 20-25 minutes.

Inspect monsters.db schema, row counts, PRAGMA foreign_key_check, database.py, lib/db/schema.py, and the source IDs in docs/DATABASE_SOURCE_DATA_MANIFEST.md. Write or update the current-state section of docs/DATABASE_SKILL_CLASS_UPDATE_ROADMAP.md.

Do not modify schema or data.

Report: all table columns/FKs/counts; each source ID/path/parser boundary/entity/forbidden input; class/skill/synergy source counts; whether a canonical class-skill mapping source is actually available; and blockers for later sessions.
```