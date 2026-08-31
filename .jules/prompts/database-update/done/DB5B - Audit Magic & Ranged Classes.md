### Phần 2: DB5B - Audit Magic & Ranged Classes (Wizard, Force Archer, Force Gunner, Dark Mage)

```markdown
# DB5B - Class-Skill Mapping Audit (Magic & Ranged: WI, FA, FG, DM)

Paste `00-global-rules.md` before this prompt.

```text
Session Type: Documentation / Read-Only Audit
Scope: Target classes `wizard`, `force-archer`, `force-gunner`, `dark-mage` only.
Timebox: Max 30 minutes (Stop scope at minute 25 for validation report. At minute 30, abort/revert if incomplete).

Source Configuration:
- Authorized Source ID: `class_skill_evidence`
- Authorized File: `lib/data/bm2-bm3-detail-skill-db-cabal.txt`
- Supplemental Lookup: `skill_sprite_catalogue` (Verification only)
- Target Relation (Downstream DB6): `class_skill_assignments`
- Forbidden Inputs: `skills.json`, user configs, untraceable prose.

Execution Steps:
1. Parse sections `es` (Wizard), `J` (Force Archer), `Q` (Force Gunner), `V` (Dark Mage).
2. Handle lance/cannon variants with numeric suffix stripping (e.g., `terra-lance-439`, `fire-lance-543`).
3. Normalize slugs, evaluate confidence (HIGH/AMBIGUOUS/LOW), and isolate rejected entries.
4. Output manifest partition table for WI, FA, FG, DM.
5. Output Coverage Report & Rejected Records for these 4 classes.
6. Validate idempotency and output partial SHA-256 partition hash.