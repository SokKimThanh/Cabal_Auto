### Phần 3: DB5C - Audit Force Hybrids & Final Consolidation (Force Blader, Force Shielder)

```markdown
# DB5C - Class-Skill Mapping Audit (Hybrids: FB, FS) & Manifest Consolidation

Paste `00-global-rules.md` before this prompt.

```text
Session Type: Documentation / Read-Only Audit & Gatekeeping Consolidation
Scope: Target classes `force-blader`, `force-shielder` + Final 9-Class Consolidated Manifest.
Timebox: Max 30 minutes (Stop scope at minute 25 for consolidation report. At minute 30, abort/revert if incomplete).

Source Configuration:
- Authorized Source ID: `class_skill_evidence`
- Authorized File: `lib/data/bm2-bm3-detail-skill-db-cabal.txt`
- Partition Inputs: Outputs from DB5A and DB5B.
- Supplemental Lookup: `skill_sprite_catalogue`
- Forbidden Inputs: `skills.json`, user configs, untraceable prose.

Execution Steps:
1. Parse sections `Z` (Force Blader with Blade Buff Conditionals) and `ee` (Force Shielder).
2. Merge DB5A, DB5B, and DB5C into the final versioned manifest (`v1.0.0`).
3. Generate the 9-Class Consolidated Coverage Report & All Rejected Records summary.
4. Run Hard Gatekeeping Checklist (>=95% coverage, zero critical unresolved).
5. Declare final gatekeeping outcome: APPROVE DB6 or BLOCK DB6.