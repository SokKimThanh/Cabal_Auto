# Data Manifest Cho Cập Nhật CSDL

## 1. Mục đích

Manifest này là nguồn bắt buộc để chọn đúng data file cho từng DB session. Không thay thế source bằng file có tên gần giống, dữ liệu UI runtime, cache, hoặc JavaScript bundle khác nếu prompt không chỉ định rõ.

## 2. Data source registry

| Source ID | File chính xác | Entity được phép tạo/cập nhật | Không được dùng để suy ra | Parser boundary / nhận dạng |
| --- | --- | --- | --- | --- |
| `monster_catalogue` | `lib/data/monster-db-cabal.txt` | `monsters`, `dungeons` từ monster `dungeonId/locationId` | classes, skills, synergies | JSON array bên trong `JSON.parse('...')` |
| `dungeon_reference` | `lib/data/location-db-cabal.txt` | `dungeons.id`, `dungeons.name` | monster/class/skill mapping | JS pairs `id: "name"` |
| `monster_type_reference` | `lib/data/type-monster-db-cabal.txt` | `monster_type.value`, `monster_type.label` | class type hoặc skill type | JS objects `value`, `label` |
| `class_metadata` | `lib/data/color-skill-character-db-cabal.txt` | `classes.class_code`, `name`, `icon_path`, `str_base`, `int_base`, `dex_base` | full skill catalogue, class-skill assignment, synergy effects | class map includes all base attributes; `class_code` normalizes hyphen/underscore consistently |
| `skill_sprite_catalogue` | `lib/data/skill-db-cabal-2.txt` | `skills.skill_code`, `icon_x`, `icon_y`, `icon_w`, `icon_h` | class ownership, skill type, cooldown/cast time, recommendation | embedded `sprites` JSON with coordinate objects |
| `bm3_synergy_catalogue` | `lib/data/bm2-bm3-skill-db-cabal.txt` | `synergies`, `synergy_effects` | full class-skill mapping, complete game skill catalogue | map keyed by class slug; `rows` with `synergyName`, `activationSequence`, `recommendation`, `effects` |
| `class_skill_evidence` | `lib/data/bm2-bm3-detail-skill-db-cabal.txt` | DB5 mapping manifest only; DB6 only after manifest approval | direct production seed without reproducible manifest; generic sprite ownership | class-guide objects with `className`, `slug`, `featuredSkillSections`, `skillSlugs`, `comboSection` |
| `user_skill_library` | `lib/data/skills.json` | User-configured skill library only | canonical `skills` catalogue, class metadata, automatic class-skill mapping | JSON list: `name`, `key`, `type`, `cooldown`, `cast_time`, `image` |
| `monster_user_library` | `lib/data/monsters.json` | User-created hunt/rotation configuration only | canonical `monsters` source, dungeons, class/skill data | JSON user state; separate from `monster_catalogue` |

## 3. Source precedence and identity rules

1. Data importer reads exactly one authoritative source ID unless its prompt explicitly names a verified join.
2. Source filenames are part of the contract. Do not use `image-count-skill-db-cabal.txt` as a substitute for `skill-db-cabal-2.txt`; it is an unrelated large bundle despite similar content markers.
3. `class_code` is the normalized source slug from `class_metadata`; do not use display name as an identity key.
4. `skill_code` is the normalized sprite key from `skill_sprite_catalogue`; it does not establish class ownership.
5. A class-skill row requires evidence from `class_skill_evidence` recorded in a versioned manifest. A matching display name, icon, or slug is not sufficient evidence.
6. User library files are read/write runtime configuration. Importers must not update, replace, or use them as seed data for canonical tables.
7. Preserve source provenance: every seeded row needs the source ID, source file, parser version/content hash, and source key in the session report or manifest.

## 4. File-specific parsing contracts

### `class_metadata`

- Expected output: exactly one record per class slug.
- Required fields: source slug, display name, icon path, base `str`, `int`, `dex`.
- Current source coverage: 9 class slugs: `blader`, `warrior`, `wizard`, `dark-mage`, `force-archer`, `force-shielder`, `force-blader`, `gladiator`, `force-gunner`.
- Source Hash: `7a62cdaee09db0c0b2255f3f8b70f295`
- Reject record if slug/name/base stat cannot be extracted together; do not insert partial class row.

### `skill_sprite_catalogue`

- Expected output: one record per `sprites` key.
- Required fields: key, `x`, `y`, `width`, `height`.
- Current measured count: 460 sprite entries. Count is an audit expectation, not a hard-coded application constant.
- Source Hash: `0abe0f4848fe99738a41c1640effc53b`
- Duplicate/alias sprite keys such as spelling variants must remain separate source records until a dedicated alias audit approves normalization.

### `bm3_synergy_catalogue`

- Expected output: synergy parent rows and child effect rows keyed by source class slug and source sequence/name.
- Required parent fields: class slug, synergy name, activation sequence, recommendation.
- Required child fields: stat, raw value text, duration raw text, target.
- Current measured coverage: 9 classes, 35 synergy rows, 120 effects. These values validate the current source snapshot only.
- Source Hash: `7b60d69705f315d8fa8a1aaa5e0ec970`
- Preserve `value_text` and `duration_text` before parsing numeric/unit/scaled derivatives. Never coerce `+30%` or `-3% (scaled)` directly into a lossy number.

### `class_skill_evidence`

- This is a documentation/detail bundle, not a direct seed file.
- DB5 must create a reproducible manifest with: class_code, skill_code, category, source section/path, evidence excerpt or stable locator, parser version/hash, and confidence.
- Source Hash: `e751ba727757fec4c2be784a1b94b513`
- DB6 imports only records with unambiguous class/skill identity and explicit category evidence. Unresolved aliases remain excluded and are reported.

## 5. Prohibited cross-source assumptions

- Do not assign a sprite to a class because a class guide mentions a similar skill name.
- Do not assign class ownership from `skills.json`; its records are user choices and may mix classes.
- Do not convert display strings to database keys without a normalization and alias report.
- Do not infer synergy effect duration/unit from a numeric-looking string; preserve raw source text first.
- Do not merge `monster-db-cabal.txt` with user `monsters.json`.
- Do not seed `scans` or `builds`; they are runtime/user data tables with no supplied seed source.

## 6. Evidence required in every DB session

Before writing data, report: source ID, exact path, parser boundary, expected entity, source record count, target table, key strategy, and forbidden inputs. After writing, report source count, accepted count, rejected count, duplicate count, target count, orphan count, and `PRAGMA foreign_key_check` result.