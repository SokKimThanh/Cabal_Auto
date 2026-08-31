# DB3 - Seed Skill Sprite Catalogue

Paste `00-global-rules.md` before this prompt.

```text
Authorized source ID: `skill_sprite_catalogue` only.
Authorized file: `lib/data/skill-db-cabal-2.txt` only.
Forbidden inputs: `image-count-skill-db-cabal.txt`, `skills.json`, `bm2-bm3-detail-skill-db-cabal.txt`, `color-skill-character-db-cabal.txt`, and all user/config files.

Implement only a tested extractor and idempotent seed of canonical skill icon metadata from the authorized source.

Parse only the embedded `sprites` object. Store each source sprite key as `skill_code` plus icon coordinates/dimensions. Preserve source key exactly; do not merge aliases. Do not assign class_id, infer class-skill mappings, overwrite lib/data/skills.json, or change runtime UI readers.

Validate empty DB, malformed/missing source, repeat seed, unique skill_code, expected parser count, duplicate source keys, and no orphan rows. Report source ID, parser boundary, source/accepted/rejected counts, and file hash.
```