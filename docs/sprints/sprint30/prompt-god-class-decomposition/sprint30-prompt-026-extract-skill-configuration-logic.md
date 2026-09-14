# Sprint 30 Phase 4 Prompt 026: Extract Skill Configuration Logic

## Goal
Extract skill configuration (Skill Slots) and Global Apply logic from the God Class.

## Details
- Move methods such as `_collect_skill_slots`, `_clear_skill_slot`, and `_update_attack_keys_from_slots` to a dedicated `SkillConfigView` or `SetupTab`.
- Remove the massive `on_global_apply` button handler from `App`. This global save logic should be managed by a unified `GlobalConfigController` or delegated to `HuntConfigController`.
- Ensure all skill-related Views read/write data directly via `AppStateController` and do not rely on `self.app`.

## Risks and Things to Avoid
- **Avoid saving the Hunt Configuration multiple times.**
- **Risk:** The `on_global_apply` logic handles data from multiple tabs. If extracted improperly, parts of the configuration (like advanced setup or monster rotation) might get lost or overwritten with defaults.
- **Risk:** Skill key duplicates validation must occur *before* the configuration is applied and saved, otherwise invalid hotkeys will be persisted.

## Acceptance Criteria
- `app_gui.py` no longer contains skill slot UI management.
- The "Global Apply" functionality saves correctly but is housed in a Controller, decoupled from `app_gui.py`.
- `pylint app_gui.py` remains at 10.0.
