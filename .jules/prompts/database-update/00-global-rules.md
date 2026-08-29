# Global Rules For Database Update Sessions

Paste this block before each database-update prompt.

```text
You are working in Cabal_Auto. Follow docs/DATABASE_SKILL_CLASS_UPDATE_ROADMAP.md.
Read docs/DATABASE_SOURCE_DATA_MANIFEST.md before editing or parsing data. Use only the source ID and exact file authorized by the active prompt; record parser boundary, source count, target key, and forbidden look-alike inputs.
Read docs/DATABASE_RELATIONSHIP_CONTRACT.md before any schema, seed, or integrity change. Its FK actions, cardinality, seed order, identity rules, and orphan checks are mandatory.
Read docs/UI_DATABASE_INTEGRATION_CONTRACT.md before any runtime/UI data integration. It defines catalogue versus user-configuration ownership, adapters, fallback, and UI thread boundaries.
Read docs/I18N_DATABASE_COMPATIBILITY_CONTRACT.md before coordinating a shared schema-init or connection-lifecycle change with the i18n roadmap.

Hard constraints:
- Maximum 30 minutes. At minute 25, stop scope expansion and run the focused validation.
- If validation still fails at minute 30, revert only the current session's reviewed diff with a deliberate patch, rerun validation, and report ABORTED/REVERTED. Never use git reset, git checkout --, or a broad discard command.
- Use additive, idempotent SQLite migrations. Do not drop/recreate existing tables or overwrite user library data.
- Schema/data changes belong in dedicated services under lib/db/services/; local SQLite connections close in finally blocks.
- Use explicit transactions for multi-table inserts/updates.
- Preserve serverBossType as string or None.
- Do not infer class-skill ownership without a versioned source manifest and an audit report.
- Do not use `skills.class_id` as the canonical class-skill relationship; use `class_skill_assignments` only after DB5 approves evidence.
- Keep lib/data/skills.json as user configuration; do not treat it as the canonical full skill catalogue.
- Keep lib/data/monsters.json and lib/data/hunt_config.json as user/runtime configuration; catalogue DB reads may enrich a view but must not overwrite rotation, templates, bounds, hotkeys, timing, or selected skill fields.
- Do not infer cross-source relationships from matching names, aliases, sprites, or prose. Class-skill assignments require the approved evidence manifest from DB5.

Before editing:
- State the source table/file, source of truth, exact schema/data change, and cheapest validation.
- State the source ID, exact file path, parser boundary, expected record count, target table/key, and forbidden inputs before writing data.
- Identify three boundaries: empty DB, repeated import, and malformed/missing source data.

Before final response:
- Report migration/seed row counts, duplicate/orphan/FK checks, and validation results.
- Report affected parent/child relationships, FK delete action, unique-key result, and the relationship-contract integrity query result.
- Report PASSED or ABORTED/REVERTED, timebox status, and deferred next session.
```