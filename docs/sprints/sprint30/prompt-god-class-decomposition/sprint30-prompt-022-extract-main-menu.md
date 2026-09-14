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
