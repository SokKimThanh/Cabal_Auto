# DB7 - Runtime Integration

Paste `00-global-rules.md` before this prompt.

```text
Session Type: Architecture / Read-Only Runtime Integration & Adapters
Timebox: Max 30 minutes (Stop scope expansion at minute 25 for focused validation. At minute 30, abort/revert with a deliberate patch if validation fails. Never use git reset or broad discard commands).

Prerequisites & Governance:
- Read docs/UI_DATABASE_INTEGRATION_CONTRACT.md before editing.
- Preceding checkpoints mandatory: DB2, DB3, DB5, and DB6 must be PASSED.
- Dedicated service location: `lib/db/services/` and dedicated adapter package. SQLite connections must close in `finally` blocks.

Scope & Boundary Rules:
- DB7 adds ONLY read-only adapters, explicit view models, fallback strategies, and focused unit tests.
- HARD BOUNDARY: Do NOT wire/bind adapters directly into Tkinter UI components in this session (UI binding is a separate UX session).
- THREADING RULE: Catalogue lookups must respect UI thread boundaries (read-only snapshots, asynchronous queries off-main-thread when needed, no direct Tkinter mutation from DB routines).
- ZERO-MUTATION RULE: `lib/data/skills.json`, `lib/data/monsters.json`, and `lib/data/hunt_config.json` remain the sole source of truth for runtime/user configs. Do NOT alter hunt runtime, config shapes, UI layout, `SkillRuntimeService`, `load_skill_library()`, or `load_monster_library()`.

Required Adapter Implementations:
1. `MonsterCatalogueLookup`: Input stable monster ID/name -> Output immutable reference metadata. Fallback: return no-match result, preserve user monster untouched.
2. `SkillCatalogueLookup`: Input `skill_code` / canonical mapping -> Output class/category/icon references. Fallback: preserve user skill untouched, never block hunt runtime.
3. `SkillRuntimeView`: Combines user skill library record + optional catalogue record -> Emits runtime fields strictly from user JSON and reference fields from DB. Never infer/guess key, cooldown, cast_time, or image.

Mandatory Validation Scenarios (Cheapest Validation):
1. Seeded DB + Valid Assignment: Verify adapter enriches reference metadata while strictly preserving user key, cooldown, cast_time, image, rotation, templates, bounds, and hotkeys.
2. Empty/Unseeded DB: Verify fallback path activates, no exceptions raised, user library behavior and hunt remain 100% operational.
3. Missing Item / Unmapped Assignment: Verify no-match result emitted cleanly without fabricating class/category.
4. User Library Mutation: Add/edit/select user skills and monsters to confirm JSON read/write persistence is unchanged.

Post-Session Reporting:
- Report adapter test suite results (seeded, empty DB, unmapped fallbacks).
- Report confirmation of 0 schema mutations, 0 user config overwrites, and thread-boundary compliance.
- Report Timebox Status and declare session outcome: PASSED or ABORTED/REVERTED.