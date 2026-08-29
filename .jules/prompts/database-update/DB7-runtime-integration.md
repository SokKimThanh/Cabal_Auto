# DB7 - Runtime Integration

Paste `00-global-rules.md` before this prompt.

```text
Read docs/UI_DATABASE_INTEGRATION_CONTRACT.md before editing.

Integrate DB-backed class/skill catalogue reads through read-only adapters without changing lib/data/skills.json or lib/data/monsters.json user-library behavior.

Use dedicated services and explicit adapter view models. Keep fallback behavior explicit if seed data, mapping, or catalogue rows are unavailable. Do not alter hunt runtime, config shape, UI layout, `SkillRuntimeService`, `load_skill_library()`, `load_monster_library()`, or overwrite user skills/monsters.

Validate seeded DB, empty DB fallback, missing catalogue item/mapping, and current skill-manager/user-library behavior. Verify reference metadata never overwrites user key, cooldown, cast_time, image, rotation, templates, bounds, or hotkeys.
```