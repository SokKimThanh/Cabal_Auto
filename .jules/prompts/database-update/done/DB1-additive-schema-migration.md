# DB1 - Additive Schema Migration

Paste `00-global-rules.md` before this prompt.

```text
Implement only an additive migration for class/skill identity, the canonical `class_skill_assignments` many-to-many relation, and lossless synergy effect values.

Files in scope: lib/db/schema.py, database.py only if startup schema hook requires it, a focused migration/service/test file.

Add class_code and skill_code unique identities; `class_skill_assignments` with composite primary key plus `CASCADE` foreign keys to classes/skills; and lossless synergy value fields without dropping/recreating existing tables. Preserve the existing legacy `skills.class_id` relation. Make migration safe for empty/existing DB and repeat execution.

Do not seed classes, skills, mappings, synergies, or modify UI/runtime readers.

Validate: migration twice, PRAGMA table_info/index_list/foreign_key_list/foreign_key_check, no duplicate class_code/skill_code, no assignment/effect/synergy orphan rows, and focused tests for existing DB upgrade plus empty DB.
```