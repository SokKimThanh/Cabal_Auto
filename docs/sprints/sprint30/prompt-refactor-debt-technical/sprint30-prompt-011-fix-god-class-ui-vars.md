# Sprint 30: Refactor Debt Technical - Fix God Class UI Variables Initialization
**File:** `sprint30-prompt-011-fix-god-class-ui-vars.md`
**Previous Context:** `sprint30-prompt-re-excecute-order.md` (Issue #1)
**Estimated Time:** < 30 minutes

## 1. Title & Objective
**Title:** Fix God Class Violation by Centralizing UI Variables Initialization
**Objective:** Resolve the issue where UI components (Panels, Tabs) are dynamically creating `tk.StringVar()`, `tk.BooleanVar()`, and `tk.Listbox()` instances and attaching them to `self.app` or manually manipulating `self.app.state_controller.ui_vars` at runtime. All definitions must reside in the constructor of `AppStateController`.

## 2. Context
Although Prompt 002 and 005 attempted to encapsulate state by introducing `self.ui_vars` and `self.ui_widgets` inside `AppStateController`, a critical God Class violation remains. Files like `ui/panels/monster_target_panel.py`, `ui/tabs/hunt_tab.py`, and `ui/tabs/setup_tab.py` are defining Tkinter variables themselves. This breaks the Single Source of Truth and pollutes the object lifecycle.

## 3. Files to Modify
- `ui/controllers/app_state_controller.py` (to centralize initializations)
- `ui/panels/monster_target_panel.py`
- `ui/tabs/hunt_tab.py`
- `ui/tabs/setup_tab.py`
- `ui/controllers/monster_manager_controller.py`
- `ui/controllers/library_manager_controller.py`

## 4. Detailed Implementation Guide

### Step 4.1: Move Initialization to AppStateController
Open `ui/controllers/app_state_controller.py`. Inside `__init__`, explicitly declare all missing variables in `self.ui_vars` and widgets in `self.ui_widgets`.
Since Tkinter variables require a root window, you may need to initialize them as `None` in `__init__`, and instantiate them in a new method like `init_tkinter_vars(self, root)`.

*Variables to migrate:*
- `target_policy`, `monster_status`, `training_mode_hint`
- `hunt_mode`, `target_key`, `attack_press`, `target_cycle`, `search_interval`, `attack_interval`, `lost_timeout`, `attack_duration`, `template`, `bring_front`
- `global_hotkey_enabled`, `global_hotkey_start`, `global_hotkey_stop` (and other setup vars)
- The Listboxes: `monster_rotation_listbox`, `detected_monsters_listbox`

### Step 4.2: Update Consumers to Read/Write Securely
In `ui/panels/monster_target_panel.py`, `hunt_tab.py`, and `setup_tab.py`:
- **REMOVE** lines like: `self.app.monster_status_var = tk.StringVar()`
- **REPLACE** widget configurations with the safely initialized references. For example: `textvariable=self.app.state_controller.ui_vars['monster_status']`.
- **REMOVE** direct assignment to UI Widgets dictionary in the view: `self.app.state_controller.ui_widgets['monster_rotation_listbox'] = tk.Listbox(...)`. The Listbox can be created in the view, but assign it via a setter method or keep it as a local attribute of the Panel, rather than forcing the StateController to track Tkinter visual components (which violates MVC).

## 5. Acceptance Criteria
- [ ] No UI Panel or Tab uses `self.app.xxxx = tk.StringVar()` or `self.app.xxxx = tk.Listbox()`.
- [ ] `AppStateController` correctly manages the initialization lifecycle.
- [ ] The application boots without `_tkinter.TclError` (variable missing or destroyed).
