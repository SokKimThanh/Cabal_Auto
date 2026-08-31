# DB5 - Class-Skill Mapping Audit

Paste `00-global-rules.md` before this prompt.

```text
Session Type: Documentation / Read-Only Audit
Timebox: Max 30 minutes (Stop scope expansion at minute 25 for report consolidation. At minute 30, abort/revert if incomplete).

Source Configuration:
- Authorized Source ID: `class_skill_evidence`
- Authorized File: `lib/data/bm2-bm3-detail-skill-db-cabal.txt`
- Supplemental Lookup: `skill_sprite_catalogue` (Verification of pre-existing skill_code only; NEVER to infer class ownership)
- Target Relation (Downstream DB6): `class_skill_assignments` (Do NOT map via `skills.class_id`)
- Forbidden Inputs: `skills.json`, `image-count-skill-db-cabal.txt`, `color-skill-character-db-cabal.txt`, user/runtime configs (`monsters.json`, `hunt_config.json`), UI layouts, and untraceable prose.

================================================================================
1. ALIAS NORMALIZATION & CONFIDENCE TIERS
================================================================================
- Alias Normalization Rules:
  * Kebab-to-Snake normalization: `[a-z0-9-]+` -> convert `-` to `_`.
  * Numeric suffix stripping/matching: e.g., `terra-lance-439` -> matches base canonical `terra_lance` with source tracking.
  * Strict No-Guess Rule: If an alias normalization matches >1 canonical skill, mark as AMBIGUOUS.

- Confidence Scoring Matrix:
  * HIGH: Explicit technical key in class structure (e.g., `skillSlugs: [...]` inside `featuredSkillSections` or `passiveSkillConfig`).
  * AMBIGUOUS: Skill referenced in combo/scenario lists with multiple variants or conflicting class contexts.
  * LOW / UNRESOLVED: Mentioned only in description text/prose or missing matching entry in `skill_sprite_catalogue`.

================================================================================
2. MANIFEST METADATA & OUTPUT SCHEMA
================================================================================
The output manifest proposal MUST include header metadata:
- Manifest Version: `1.0.0` (Semantic versioning)
- Timestamp: ISO-8601 UTC string
- Auditor: Session Agent / Tool ID
- Source Hash: SHA-256 of `lib/data/bm2-bm3-detail-skill-db-cabal.txt`
- Manifest Checksum: SHA-256 of the generated manifest JSON/table

Proposal Row Columns:
| source_class | canonical_skill_code | raw_source_slug | category | evidence_location (line/offset) | parser_boundary | confidence (HIGH/AMBIGUOUS/LOW) | status (APPROVED/REJECTED) | rejection_reason |

================================================================================
3. REJECTED RECORDS REPORT SPECIFICATION
================================================================================
Explicitly isolate and list all non-approved entries:
- Rejected Record Schema: `raw_slug` | `source_class` | `rejection_reason` | `raw_context`
- Standard Rejection Reasons:
  * `NOT_FOUND_IN_SPRITE_CATALOGUE`: Normalized code does not exist in DB3 sprite catalogue.
  * `CROSS_CLASS_COLLISION`: Same normalized skill claimed by multiple classes without distinct variant codes.
  * `PROSE_ONLY_INFERENCE`: Skill found only in text descriptions without structured slug array.
  * `INVALID_FORMAT`: Unparseable identifier format.

================================================================================
4. CLASS COVERAGE METRICS REPORT
================================================================================
The audit must compile a per-class coverage summary table:
| Class Name | Total Extracted | Approved (HIGH) | Ambiguous | Rejected/Unresolved | Coverage Rate (%) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Warrior | ... | ... | ... | ... | ...% |
| Blader | ... | ... | ... | ... | ...% |
| Wizard | ... | ... | ... | ... | ...% |
| Force Archer | ... | ... | ... | ... | ...% |
| Force Shielder | ... | ... | ... | ... | ...% |
| Force Blader | ... | ... | ... | ... | ...% |
| Gladiator | ... | ... | ... | ... | ...% |
| Force Gunner | ... | ... | ... | ... | ...% |
| Dark Mage | ... | ... | ... | ... | ...% |
| **TOTAL** | **...** | **...** | **...** | **...** | **...%** |

================================================================================
5. VALIDATION SCENARIOS (CHEAPEST VALIDATION)
================================================================================
1. Idempotency Check: Running the extraction twice against the authorized source must produce the EXACT same row count, ordering, and SHA-256 manifest checksum.
2. Empty Source Boundary: Feeding an empty source file must cleanly report 0 records without unhandled exceptions.
3. Malformed / Boundary Test: Any corrupted block or invalid class slug must be routed to the Rejected Records list without halting parser execution.

================================================================================
6. GATEKEEPING CRITERIA (BLOCK / APPROVE DB6)
================================================================================
[ ] HARD CHECK: Overall Class Mapping Coverage must be >= 95.0%.
[ ] HARD CHECK: Zero unresolved critical skills (e.g., BM2/BM3 core skills must be 100% HIGH confidence).
[ ] HARD CHECK: Zero cross-source collisions with user configuration files (`skills.json`).
[ ] HARD CHECK: SHA-256 source hash and manifest checksum are fully validated.
[ ] HARD CHECK: Timebox status within 30 minutes; declaration of PASSED.

*If ANY gatekeeping criterion fails -> Output status: ABORTED / DB6 BLOCKED.*