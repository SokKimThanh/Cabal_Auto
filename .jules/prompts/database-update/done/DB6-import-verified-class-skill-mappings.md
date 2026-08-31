# DB6 - Import Verified Class-Skill Mappings

Paste `00-global-rules.md` before this prompt.

```text
Session Type: Database Mutation / Data Import
Timebox: Max 30 minutes (Stop scope expansion at minute 25 for focused validation. If validation fails at minute 30, revert reviewed diff with a deliberate patch and report ABORTED/REVERTED. Never use git reset or broad discard commands).

Source Configuration:
- Authorized Source ID: `class_skill_evidence` manifest approved by DB5 only.
- Target Table: `class_skill_assignments` (Composite Primary/Unique Key: `(class_id, skill_id)`).
- Implementation Path: Dedicated migration/service under `lib/db/services/` with SQLite connections closed in `finally` blocks.
- Forbidden Inputs: Direct bundle re-parsing (`bm2-bm3-detail-skill-db-cabal.txt`), `skills.json`, `skills.class_id`, sprite-name matching, display-name matching, user/runtime configs, and unapproved mapping manifests.

Pre-Import Declarations (Mandatory before write):
1. Declare source ID, approved manifest version/hash, exact target table (`class_skill_assignments`), and expected row count.
2. Define behavior for 3 boundaries:
   - Empty DB (fail-fast on missing parent class/skill rows).
   - Repeated import (idempotent upsert, zero row inflation).
   - Malformed / Unresolved source rows (reject and log, do not insert).

Import Execution Rules:
- Execute within an explicit transaction (`BEGIN TRANSACTION` ... `COMMIT`).
- Resolve `class_code` -> `class_id` and `skill_code` -> `skill_id` to exactly one parent row each before inserting the composite `(class_id, skill_id)` assignment.
- Preserve `source_ref`, `category`, and `recommendation` metadata fields.
- Zero-Inference & Strict Rejection: Do not create mappings for unresolved, ambiguous, or duplicate skills/classes. Record and report them in a `rejected_records` summary.
- Idempotency: Use additive, idempotent upsert semantics (`INSERT OR REPLACE` / `ON CONFLICT DO UPDATE`).

Post-Import Validation & Reporting Checklist:
1. Validation Metrics:
   - Manifest row count vs. Imported row count vs. Rejected count.
   - Version/SHA-256 hash match of the input manifest.
   - Idempotency check: Rerun import to verify 0 duplicate rows or key inflation.
   - Integrity Checks: Run orphan check queries and execute `PRAGMA foreign_key_check;`.
2. Final Status Report:
   - Affected parent/child relationships and unique composite-key status.
   - Relationship-contract integrity query result.
   - Session Timebox status and explicit declaration of `PASSED` or `ABORTED/REVERTED`.