# Sprint 30 Phase 4 Prompt 026: Extract Skill Configuration Logic

## Goal
Extract skill configuration (Skill Slots) and Global Apply logic from the God Class.

## Details
- Move methods such as `_collect_skill_slots`, `_clear_skill_slot`, and `_update_attack_keys_from_slots` to a dedicated `SkillConfigView` or `SetupTab`.
- Remove the massive `on_global_apply` button handler from `App`. This global save logic should be managed by a unified `GlobalConfigController` or delegated to `HuntConfigController`.
- Ensure all skill-related Views read/write data directly via `AppStateController` and do not rely on `self.app`.

## Acceptance Criteria
- `app_gui.py` no longer contains skill slot UI management.
- The "Global Apply" functionality saves correctly but is housed in a Controller, decoupled from `app_gui.py`.
- `pylint app_gui.py` remains at 10.0.
