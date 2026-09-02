# Architecture Cleanup Baseline

## Responsibilities of app_gui.py
Based on the roadmap and file inspection, `app_gui.py` directly handles or delegates:
- UI Initialization and single instance locking (`main()` function).
- UI structure and layout (subclass of `tk.Tk`).
- Connecting controllers, like `HotkeyManager`, `ScanController`, `AppRuntimeBridgeMixin` and `ConfigManager`.
- Opening various windows directly (e.g. `_open_monster_manager`, `_open_skill_manager`, `on_monster_calculate_timing`).
- The `AppRuntimeBridgeMixin` contains window management logic (e.g., `_open_library_manager`, `try_close_library_manager`) and app lifecycle logic (`on_close()`).

## Existing Tests and Smoke Commands
- The normal run command `python app_gui.py` is the main smoke test.
- The unit tests under `tests/unit/ui/` (e.g. `test_button_state_mixin.py`) work via `xvfb-run -a python3 -m pytest tests/unit/ui/`.
- No broad test suite covers the specific window management/lifecycle flows in a cheap way, manual GUI confirmation or new unit tests are needed.

## Boundary/Edge Cases
- Duplicate instance locking (`SingleInstanceLock` handles this, need to ensure we don't break the existing usage in `main()`).
- Window tracking edge cases (closing windows multiple times, missing references, overlapping windows).
- Startup/shutdown boundaries: ensure `app.mainloop()` is called appropriately and `app.on_close()` cleans up background processes.
- Legacy configuration compatibility: ensuring `config_mgr` and `app` initialization don't choke on missing/legacy configs.
- Repeated calls to opening managers (e.g., calling `_open_monster_manager` multiple times should not spawn duplicate windows).

## Sprint 1 Ordering
1. **Create App Lifecycle Controller:** Extract the `on_close()` logic from `ui/controllers/app_runtime_bridge.py` and `app_gui.py` into a new `ui/controllers/app_lifecycle_controller.py`.
2. **Create App Window Controller:** Extract window ownership and open/close dialog logic (e.g., `_open_monster_manager`, `try_close_library_manager`) into `ui/controllers/app_window_controller.py`.
3. **Create App State Controller:** Move bounds state management and config saving into `ui/controllers/app_state_controller.py`.
4. **Update `app_gui.py`:** Refactor `App` to initialize and delegate to these new controllers. Keep `App.__init__` thin and focused on UI composition and bootstrap.

## Final Status
Architecture Cleanup Sprint completed.
- App initialization and dependency wiring are contained in `app_gui.py`.
- Application orchestration, state handling, window/modal lifecycle, config parsing, background looping (hunt logic), global hotkeys, application overlays, bounds targeting, monster state, and skill management are separated into decoupled controllers and services.
- Application lifecycle runs correctly and is decoupled from the view.
