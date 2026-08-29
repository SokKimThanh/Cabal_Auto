# DB6 - Import Verified Class-Skill Mappings

Paste `00-global-rules.md` before this prompt.

```text
Authorized source ID: `class_skill_evidence` manifest produced and approved by DB5 only.
Forbidden inputs: direct bundle re-parsing, `skills.json`, sprite-name matching, display-name matching, and unapproved mappings.

Import only mappings approved by DB5's versioned evidence manifest into class_skill_assignments.

Resolve class_code and skill_code to exactly one parent row before inserting the composite `(class_id, skill_id)` assignment. Use explicit transaction and idempotent upsert semantics. Preserve source_ref, category, and recommendation evidence. Do not create mappings for unresolved or duplicate skills/classes; report them as rejected.

Validate manifest count vs imported count, source hash/version match, missing/duplicate class-skill resolution, repeated import, composite-key uniqueness, assignment orphan checks, and PRAGMA foreign_key_check.
```