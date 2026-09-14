# Sprint 30 Phase 4 Prompt 022: Extract Main Menu

## Goal
Extract the main menu (`tk.Menu`) construction logic out of the God Class `app_gui.py`.

## Details
- Create a new component `ui/components/main_menu_bar.py` or a dedicated `MenuController`.
- Relocate all logic that constructs the top-level menu (Settings, Vision).
- Move the settings toggle for `global_hotkeys_enabled_legacy` to this component.
- Ensure the menu interactions use `EventBus` to notify about state changes, rather than retaining direct callbacks to the `App` instance.
- Instantiate this menu component properly within `app_gui.py` after the root Tk instance is initialized.

## Risks and Things to Avoid
- **Avoid tightly coupling the MenuController to Tkinter specific lifecycle events.**
- **Risk:** Menus might fail to render on certain OS environments (like macOS) if created before the root window is fully initialized.
- **Risk:** Disconnecting the Hotkey toggles might break global shortcuts if EventBus is not used correctly to bridge the menu state and the HotkeyController.

## Acceptance Criteria
- `app_gui.py` no longer contains direct `tk.Menu` instantiations or `add_command`/`add_cascade` calls.
- Global hotkey toggle and vision shortcuts (Ctrl+Shift+V, etc.) still function correctly.
- `pylint app_gui.py` remains at 10.0.
# Sprint 30 - Prompt 022: Extract Main Menu from App GUI

## Goal
Extract the main menu (`tk.Menu`) construction logic out of the `app_gui.py` God Class to decouple menu definitions from the core application bootstrapping loop.

## Context (Nợ Kỹ Thuật)
Hiện tại, logic tạo menu (bao gồm Vision, Settings, Help) và quản lý hotkey global được viết trực tiếp vào `__init__` của `app_gui.App` thông qua các lệnh gọi hardcode. Điều này vi phạm nguyên tắc Single Responsibility Principle (SRP) và khiến file `app_gui.py` phình to.

## Required Actions

1. **Create Menu Controller Component**
   - Create a new file `lib/ui/components/main_menu_bar.py` (or `ui/controllers/menu_controller.py`).
   - Define a class `MainMenuBar` that accepts `parent` (usually `root` or `AppShell`) and `app_state_controller`.
   - Move the entire `_create_menus` (or equivalent menu creation block) from `app_gui.py` into this new class.

2. **Decouple Menu Logic**
   - Di dời logic Settings toggle cho `global_hotkeys`.
   - Di dời các menu toggle của Vision (như start/stop template).
   - Ensure these menu items trigger updates via the `EventBus` or directly interact with their specific domain controllers (e.g., `HotkeyController`) instead of calling functions on the `App` instance.

3. **Refactor `app_gui.py`**
   - Remove the hardcoded menu setup from `app_gui.py`.
   - Instantiate the new `MainMenuBar` inside `app_gui.py` during initialization.

## Acceptance Criteria
- Menu functions exactly as before (hotkeys toggle, vision menu works).
- `app_gui.py` no longer contains `tk.Menu` construction code.
- EventBus is utilized for state changes triggered by the menu.
