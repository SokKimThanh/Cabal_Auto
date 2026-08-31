# DB8 - Integrity Tests And Documentation

Paste `00-global-rules.md` before this prompt.

```text
Session Type: Quality Assurance / Integrity Verification & Documentation Update
Timebox: Max 30 minutes (Stop scope at minute 25 for report consolidation. At minute 30, abort/revert with a deliberate patch if integrity checks fail. Never use git reset or broad discard commands).

Prerequisites & Context:
- Read docs/DATABASE_RELATIONSHIP_CONTRACT.md before executing test assertions.
- Read docs/DATABASE_SOURCE_DATA_MANIFEST.md and docs/DATABASE_SKILL_CLASS_UPDATE_ROADMAP.md.
- Service Location: Test suites under test directories; SQLite connections closed in `finally` blocks.

Execution Rules & Scope Freeze:
- STRICT SCOPE FREEZE: Do NOT add, alter, or migrate database schemas or insert new business data features in this session.
- USER CONFIG PROTECTION: Verify that `lib/data/skills.json`, `lib/data/monsters.json`, and `lib/data/hunt_config.json` remain completely intact and untouched.

Required Test Coverage Matrix:
1. Schema & Migration Lifecycle:
   - Additive upgrade execution against existing SQLite schemas.
   - Clean initialization behavior on an Empty DB.
2. Idempotency & Parity Checks:
   - Re-importing classes, skills, synergies, and class_skill_assignments produces zero duplicate rows and zero key inflation.
   - Exact record count parity between source manifests and populated tables.
3. Constraint & Relationship Integrity:
   - Enforce unique constraints on `class_code`, `skill_code`, and composite mapping key `(class_id, skill_id)`.
   - Foreign-Key Delete Actions: Verify expected behavior (RESTRICT / CASCADE) matches relationship contract.
   - Orphan Checks: Query for orphan mappings, orphan synergy effects, and unlinked parent entities.
   - Execute `PRAGMA foreign_key_check;` across all database tables.
4. Runtime / Adapter Protection:
   - Verify read-only adapters handle valid mappings, unmapped items, and empty DB without throwing unhandled exceptions.

Documentation Deliverables:
- Update `docs/DATABASE_SOURCE_DATA_MANIFEST.md` with measured record counts and final hashes.
- Update `docs/DATABASE_RELATIONSHIP_CONTRACT.md` status table with audit results.
- Explicitly document unresolved/unmapped class-skill coverage metrics and reasons.

Final Post-Session Report Checklist:
- Matrix of test results (All Passed / Failed).
- Report final row counts for all canonical catalogue tables and mapping assignments.
- Output of `PRAGMA foreign_key_check;` and orphan verification queries.
- Report Timebox Status and declare session outcome: PASSED or ABORTED/REVERTED.