# DB5 - Class-Skill Mapping Audit

Paste `00-global-rules.md` before this prompt.

```text
Documentation/read-only session, 20-25 minutes.

Authorized source ID: `class_skill_evidence` only.
Authorized file: `lib/data/bm2-bm3-detail-skill-db-cabal.txt` only.
Supplemental lookup allowed: `skill_sprite_catalogue` only to verify a pre-existing skill_code, never to infer ownership.
Forbidden inputs: `skills.json`, `image-count-skill-db-cabal.txt`, `color-skill-character-db-cabal.txt`, user/config files, and untraceable prose.

Audit the authorized source for explicit class-to-skill evidence. Produce a versioned mapping manifest proposal and a coverage report: source class, source skill code, category, evidence location, parser boundary, source hash, confidence, and unresolved aliases.

Do not insert mapping rows. Do not infer mappings from sprite names, display names, or prose without traceable source evidence.

Block DB6 if the manifest is incomplete, ambiguous, or cannot be parsed reproducibly.
```