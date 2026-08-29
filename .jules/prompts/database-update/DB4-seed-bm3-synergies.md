# DB4 - Seed BM3 Synergies

Paste `00-global-rules.md` before this prompt.

```text
Authorized source ID: `bm3_synergy_catalogue` only.
Authorized file: `lib/data/bm2-bm3-skill-db-cabal.txt` only.
Forbidden inputs: `bm2-bm3-detail-skill-db-cabal.txt`, `skills.json`, `skill-db-cabal-2.txt`, `color-skill-character-db-cabal.txt`, and all user/config files.

Implement only a tested extractor and idempotent import of BM3 synergies/effects from the authorized source.

Parse only the class-keyed BM3 synergy object and its `rows/effects` arrays. Resolve class_id using the source class slug against the unique class_code seeded by DB2. Insert synergy parent before effect children; store raw effect value and duration text before parsed numeric/unit/scaled fields. Use one explicit transaction across synergies and effects.

Do not create class-skill mappings or change UI/runtime behavior.

Validate missing/duplicate class resolution, malformed source, repeat import, expected parser counts, no orphan effect/synergy rows, and PRAGMA foreign_key_check. Report source ID, parser boundary, source/accepted/rejected counts, unmatched class slugs, relationship result, and file hash.
```