# DB5A - Class-Skill Mapping Audit (Melee: WA, BL, GL)

Paste `00-global-rules.md` before this prompt.

```text
Session Type: Documentation / Read-Only Audit
Scope: Target classes `warrior`, `blader`, `gladiator` only.
Timebox: Max 30 minutes (Stop scope at minute 25 for validation report. At minute 30, abort/revert if incomplete).

Source Configuration:
- Authorized Source ID: `class_skill_evidence`
- Authorized File: `lib/data/bm2-bm3-detail-skill-db-cabal.txt`
- Supplemental Lookup: `skill_sprite_catalogue` (Verification only; NEVER to infer ownership)
- Target Relation (Downstream DB6): `class_skill_assignments`
- Forbidden Inputs: `skills.json`, user configs, untraceable prose.

Execution Steps:
1. Parse sections `et` (Warrior), `$` (Blader), `ea` (Gladiator).
2. Normalize slugs (kebab-to-snake), evaluate confidence (HIGH/AMBIGUOUS/LOW), and record rejection reasons for unmapped entries.
3. Output manifest partition table for WA, BL, GL.
4. Output Coverage Report & Rejected Records for these 3 classes.
5. Validate idempotency and output partial SHA-256 partition hash.