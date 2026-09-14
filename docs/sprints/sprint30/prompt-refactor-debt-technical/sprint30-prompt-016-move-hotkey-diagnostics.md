# Prompt 016: Move Hotkey Diagnostics Logic

## Objective
The function `_update_hotkey_diagnostics_ui` inside `app_gui.py` is over 100 lines long and handles logic that should belong to the `HotkeyController` and related views. Move this logic to its rightful place.

## Tasks
1. **Move Logic to `HotkeyController`:**
   - Migrate the core logic of `_update_hotkey_diagnostics_ui` (from `app_gui.py`) into a new method `update_diagnostics_ui_state` inside `ui/controllers/hotkey_controller.py`.
   - Ensure the new method correctly reads its internal state (`_failed_hotkeys`, `_hotkeys_registered_ok`) and updates the global UI variables (`hotkey_status`, `hotkey_status_detail`) via `self.app.state_controller.set_ui_var()`.
   - Remove any code attempting to manipulate non-existent direct UI widgets (like `self._hotkey_status_label.config`, `self._hotkey_retry_btn.pack_forget()`) since these were legacy artifacts and don't exist in the new UI architecture.
2. **Update Callers:**
   - In `app_gui.py`, completely remove the `_update_hotkey_diagnostics_ui` method.
   - Update `ui/controllers/hotkey_controller.py` to call its own `update_diagnostics_ui_state` instead of `self.parent._update_hotkey_diagnostics_ui()`.
   - Update `ui/controllers/app_lifecycle_controller.py` to call `self.app.hotkey_controller.update_diagnostics_ui_state()` instead of `self.app._update_hotkey_diagnostics_ui()`.
3. **Verify:**
   - Ensure hotkey diagnostics (status strings) still properly update in `AppStateController` state when hotkeys are toggled or fail.
