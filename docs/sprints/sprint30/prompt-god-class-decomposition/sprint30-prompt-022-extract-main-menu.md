# Sprint 30 Phase 4 Prompt 022: Extract Main Menu

## Goal
Extract the main menu (`tk.Menu`) construction logic out of the God Class `app_gui.py`.

## Details
- Create a new component `ui/components/main_menu_bar.py` or a dedicated `MenuController`.
- Relocate all logic that constructs the top-level menu (Settings, Vision).
- Move the settings toggle for `global_hotkeys_enabled_legacy` to this component.
- Ensure the menu interactions use `EventBus` to notify about state changes, rather than retaining direct callbacks to the `App` instance.
- Instantiate this menu component properly within `app_gui.py` after the root Tk instance is initialized.

## Acceptance Criteria
- `app_gui.py` no longer contains direct `tk.Menu` instantiations or `add_command`/`add_cascade` calls.
- Global hotkey toggle and vision shortcuts (Ctrl+Shift+V, etc.) still function correctly.
- `pylint app_gui.py` remains at 10.0.
