# DB2 - Seed Classes

Paste `00-global-rules.md` before this prompt.

```text
Authorized source ID: `class_metadata` only.
Authorized file: `lib/data/color-skill-character-db-cabal.txt` only.
Forbidden inputs: `skills.json`, `skill-db-cabal-2.txt`, `bm2-bm3-skill-db-cabal.txt`, `bm2-bm3-detail-skill-db-cabal.txt`, and all user/config files.

Implement only a tested extractor and idempotent class seed from the authorized source.

Extract the class map boundary containing source slug, class display name, icon path, and base STR/INT/DEX. Seed exactly those records with `class_code`, name, icon path, and base stats. Do not accept partial records or infer data from other bundle sections. Use explicit transaction and a DB service. Do not seed skills/synergies or change UI/runtime behavior.

Validate empty DB, malformed/missing source, repeat seed, unique class_code, expected source count, rejected partial records, and PRAGMA foreign_key_check. Report source ID, parser boundary, source/accepted/rejected counts, and file hash.
```