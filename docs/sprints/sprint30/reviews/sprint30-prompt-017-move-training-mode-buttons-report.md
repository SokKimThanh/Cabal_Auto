# Review Prompt 017: Move Training Mode UI Logic

## Verification Steps
1. Verify `_update_training_mode_buttons` is completely gone from `app_gui.py`.
2. Check `ui/panels/monster_target_panel.py` for the new `update_training_mode_buttons` method.
3. Ensure the method references the correct buttons (`self.btn_add`, `self.btn_move_up`, `self.btn_move_down`).
4. Confirm that the panel binds to the `training_mode` UI variable (either via `trace_add` or EventBus) to trigger the update method automatically.
5. Search for `self.btn_add_monster` in `app_gui.py` and ensure legacy fallbacks have been removed.

## Checklist
- [ ] Logic moved from `app_gui.py` to `MonsterTargetPanel`.
- [ ] Widget references updated (`btn_add_monster` -> `btn_add`).
- [ ] Auto-update binding implemented on state change.
- [ ] Legacy variables removed from `app_gui.py`.
