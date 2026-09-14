# Sprint 30 Phase 4: Finalizing God Class Decomposition

## Overview
During the execution of Phase 1 and 2 in Sprint 30, we identified that `app_gui.py` is still functioning heavily as a "God Class" (`app_gui.App`). With over 300 methods remaining on the `App` class (which inherits from `tk.Tk`), there are still significant architecture violations.

The application logic inside `app_gui.py` needs to be aggressively decoupled. This document outlines the required tasks to complete this final phase of decomposition, moving strictly towards MVC/MVVM patterns.

## Remaining Architecture Smells
- **Top-Level Menu & Dialog Initialization:** The main menu bar (Vision, Settings, Help) and application-wide dialog handlers are hardcoded directly into the main class `__init__`.
- **Hotkey Registration & Overrides:** While `HotkeyController` exists, `app_gui.py` still intercepts `bind()` events and manages menu toggles directly instead of delegating entirely to the Controller.
- **Vision Engine Binding:** `_scan_region`, `_add_template`, `_manage_templates` are directly mapped in `App`, mixing Tkinter windowing with Vision capabilities.
- **App Layout Remnants:** While `AppShell` extracts core layout geometries, many sub-views (like `ActionBarView`, `StatusBarView`) still depend on the full `App` instance to function, expecting various `App` level methods to exist.

## Action Plan (Execution Prompts)

### 1. `sprint30-prompt-022-extract-main-menu.md`
**Goal:** Extract the main menu (`tk.Menu`) construction logic out of `app_gui.py`.
**Details:**
- Create a `MenuController` or `MainMenuBar` component in `ui/components/`.
- Move the settings toggle for `global_hotkeys` and the vision toggles to this new controller/component.
- Ensure the menu uses `EventBus` to notify about state changes instead of direct `App` callbacks.

### 2. `sprint30-prompt-023-decouple-action-and-status-bars.md`
**Goal:** Remove strict dependencies on the `App` class from `ActionBarView` and `StatusBarView`.
**Details:**
- These components should only accept a reference to `AppStateController` and necessary controllers (like `HuntController`), rather than passing the God Class `app` argument.
- Use `EventBus` for global UI updates triggered from these bars (e.g., updating language `on_language_change`).

### 3. `sprint30-prompt-024-extract-vision-ui-handlers.md`
**Goal:** Move Vision/Template related UI logic out of `App`.
**Details:**
- Move `_scan_region`, `_add_template`, `_manage_templates` out of `App` into `OverlayController` or a new `VisionUIController`.

### 4. `sprint30-prompt-025-finalize-app-class.md`
**Goal:** Strip the `App` class down to its bare essentials.
**Details:**
- The `App` class should only be responsible for:
  - Initializing `tk.Tk()` (via `AppShell`).
  - Instantiating dependency injection container services.
  - Starting the `AppLifecycleController` and Tkinter main loop.
- All other event handlers (`on_start_stop_clicked`, `on_monster_select_change`, etc.) must be moved to their respective domain controllers (`HuntController`, `MonsterRotationController`).

## Acceptance Criteria
- `app_gui.App` contains no more than 20-30 methods, strictly related to application bootstrapping and shutdown.
- Running `python -c 'import app_gui; print(len([x for x in dir(app_gui.App) if callable(getattr(app_gui.App, x))]))'` shows a significant reduction (e.g., < 100 methods, mostly inherited Tkinter methods).
- `pylint app_gui.py` remains at 10.0/10.0.
