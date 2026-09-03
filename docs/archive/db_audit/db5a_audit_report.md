# DB5A - Class-Skill Mapping Audit (Melee: WA, BL, GL)

## 1. Source Identification

- **Source ID**: `class_skill_evidence`
- **Source File**: `lib/data/bm2-bm3-detail-skill-db-cabal.txt`
- **Parser Boundary**: `className` and `slug` objects, `featuredSkillSections`, and `comboSection`.
- **Forbidden Inputs**: Generic UI sprite files like `skill-db-cabal-2.txt` for inferring ownership, `skills.json` user configuration, or matching just based on names.
- **Target Relation (Downstream DB6)**: `class_skill_assignments`
- **Expected Record Count**: 110 total elements audited.
- **Partition Hash (SHA-256)**: `1bc4137a576ec20bc8a5584b1ce2a72b0a8d2ecbd0ed851f330ebe382e1cf8e1`

## 2. Coverage Report

| Class Code | Mapped (HIGH/AMBIGUOUS) | Rejected (LOW Confidence) |
| --- | --- | --- |
| `warrior` | 34 | 3 |
| `blader` | 35 | 3 |
| `gladiator` | 32 | 3 |

### Rejected Records

**warrior**
- `lancer-attack-2`: Skill 'lancer_attack_2' not found in skill_sprite_catalogue and has no valid alias
- `lancer-attack-3`: Skill 'lancer_attack_3' not found in skill_sprite_catalogue and has no valid alias
- `lancer-attack-4`: Skill 'lancer_attack_4' not found in skill_sprite_catalogue and has no valid alias

**blader**
- `grappler-attack-2`: Skill 'grappler_attack_2' not found in skill_sprite_catalogue and has no valid alias
- `grappler-attack-3`: Skill 'grappler_attack_3' not found in skill_sprite_catalogue and has no valid alias
- `grappler-attack-4`: Skill 'grappler_attack_4' not found in skill_sprite_catalogue and has no valid alias

**gladiator**
- `scyther-attack-2`: Skill 'scyther_attack_2' not found in skill_sprite_catalogue and has no valid alias
- `scyther-attack-3`: Skill 'scyther_attack_3' not found in skill_sprite_catalogue and has no valid alias
- `scyther-attack-4`: Skill 'scyther_attack_4' not found in skill_sprite_catalogue and has no valid alias

## 3. Manifest Partition (Sample)

| Class Code | Skill Code | Resolved Sprite | Category | Confidence | Original Slug |
| --- | --- | --- | --- | --- | --- |
| `warrior` | `lancer` | `lancer` | `battle-mode-2` | `HIGH` | `lancer` |
| `warrior` | `lancer_attack_1` | `lancer` | `battle-mode-2` | `AMBIGUOUS` | `lancer-attack-1` |
| `warrior` | `lancer_attack_2` | `None` | `battle-mode-2` | `LOW` | `lancer-attack-2` |
| `warrior` | `lancer_attack_3` | `None` | `battle-mode-2` | `LOW` | `lancer-attack-3` |
| `warrior` | `lancer_attack_4` | `None` | `battle-mode-2` | `LOW` | `lancer-attack-4` |
| `warrior` | `lance_drive` | `lance_drive` | `battle-mode-2` | `HIGH` | `lance-drive` |
| `warrior` | `axe_destroyer` | `axe_destroyer` | `battle-mode-3` | `HIGH` | `axe-destroyer` |
| `warrior` | `axe_attack_a` | `axe_attack_a` | `battle-mode-3` | `HIGH` | `axe-attack-a` |
| `warrior` | `axe_attack_b` | `axe_attack_b` | `battle-mode-3` | `HIGH` | `axe-attack-b` |
| `warrior` | `axe_specialty_level_1` | `axe_specialty_level_1` | `battle-mode-3` | `HIGH` | `axe-specialty-level-1` |
| `warrior` | `axe_specialty_level_2` | `axe_specialty_level_2` | `battle-mode-3` | `HIGH` | `axe-specialty-level-2` |
| `warrior` | `axe_specialty_level_3` | `axe_specialty_level_3` | `battle-mode-3` | `HIGH` | `axe-specialty-level-3` |
| `warrior` | `instant_immunity` | `instant_immunity` | `warrior-buffs` | `HIGH` | `instant-immunity` |
| `warrior` | `morale_shout` | `morale_shout` | `warrior-buffs` | `HIGH` | `morale-shout` |
| `warrior` | `cats_recovery` | `cats_recovery` | `warrior-buffs` | `HIGH` | `cats-recovery` |

*(Full manifest available in `db5a_audit_report.json`)*
