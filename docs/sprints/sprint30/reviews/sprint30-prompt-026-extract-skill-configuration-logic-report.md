# Review Prompt 026: Extract Skill Configuration Logic

## Verification Steps
1. Confirm removal of `_collect_skill_slots`, `_clear_skill_slot`, and `_update_attack_keys_from_slots` from `app_gui.py`.
2. Verify the removal of the massive `on_global_apply` handler from the God Class.
3. Ensure these features now reside in a `SkillConfigView` and a dedicated `GlobalConfigController` (or `HuntConfigController`).
4. Check that saving the configuration (Global Apply) correctly handles duplicate hotkey validations before persisting.

## Checklist
- [x] Skill slot management methods removed from `app_gui.py`.
- [x] `on_global_apply` logic extracted into a Controller.
- [x] Views read/write data directly via `AppStateController`.
- [x] Configuration persists correctly across tabs without data loss.

## Notes
- Removed legacy test dependencies to `App._collect_skill_slots` in `test_cb3b_validation_suite.py` by converting tests to instantiate `SkillConfigView`.
- Headless testing crashes (Tkinter `after` and DOM `winfo_children`) bypassed gracefully through mocks.
