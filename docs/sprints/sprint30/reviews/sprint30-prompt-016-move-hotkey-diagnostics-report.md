# Review Prompt 016: Move Hotkey Diagnostics Logic

## Verification Steps
1. Open `app_gui.py` and confirm that `_update_hotkey_diagnostics_ui` has been deleted.
2. Check `ui/controllers/hotkey_controller.py` to ensure `update_diagnostics_ui_state` has been added.
3. Verify that the new method only updates state variables (`hotkey_status`, `hotkey_status_detail`) via `self.app.state_controller.set_ui_var` and does not attempt to manipulate `_hotkey_status_label` or other legacy direct widgets.
4. Ensure `AppLifecycleController` now calls `self.app.hotkey_controller.update_diagnostics_ui_state()`.

## Checklist
- [ ] `_update_hotkey_diagnostics_ui` removed from `app_gui.py`.
- [ ] Logic correctly moved to `HotkeyController`.
- [ ] Legacy widget manipulations removed.
- [ ] Callers updated successfully.
