# Sprint 30: Refactor Debt Technical - AppStateController
**File:** `sprint30-prompt-002-encapsulate-tkinter-vars.md`
**Previous Context:** `sprint30-prompt-001-encapsulate-simple-state.md`
**Estimated Time:** < 30 minutes

## 1. Title & Objective
**Title:** Encapsulate Tkinter Variables and UI References
**Objective:** Continue eliminating the "God Class" pattern by moving `tk.StringVar` and UI widget references from `self.root` to managed dictionaries/objects within `AppStateController`.

## 2. Context
In the previous step, we moved simple variables. Now, `app_state_controller.py` still binds numerous `tk.StringVar` and widget references (like `app.monster_select_var`, `app.skill_listbox`, `app.monster_bounds_vars`) to the `app` instance. This creates a messy "Service Locator" anti-pattern where components pull random UI widgets from the App root. We need to encapsulate them cleanly inside the Controller.

## 3. Files to Modify
- `ui/controllers/app_state_controller.py`

## 4. Detailed Implementation Guide

### Step 4.1: Group and Encapsulate UI State in `__init__`
Inside `AppStateController.__init__`, create structured dictionaries to hold the `tk.StringVar` instances and widget references, removing them from `app`:

```python
# Instead of:
# app.monster_select_var = tk.StringVar(master=root)
# app.monster_select_combo = None

# Do:
self.ui_vars = {
    # Monster Selection
    "monster_select": tk.StringVar(master=root),
    "monster_name": tk.StringVar(master=root),
    "monster_hp": tk.StringVar(master=root),
    "monster_damage": tk.StringVar(master=root),
    "monster_template": tk.StringVar(master=root),
    "monster_estimate": tk.StringVar(master=root, value=""),

    # Skill Panel
    "skill_name": tk.StringVar(master=root),
    "skill_key": tk.StringVar(master=root),
    "skill_type": tk.StringVar(master=root, value=skill_type_default),
    "skill_cooldown": tk.StringVar(master=root),
    "skill_cast_time": tk.StringVar(master=root),
    "skill_duration": tk.StringVar(master=root),
    "skill_pre_refresh": tk.StringVar(master=root),
    "skill_image": tk.StringVar(master=root),

    # Template Editor
    "monster_template_name": tk.StringVar(master=root),
    "monster_template_path": tk.StringVar(master=root),
    "monster_template_threshold": tk.StringVar(master=root, value="0.85"),

    # Hunt Status
    "window_bounds_display": tk.StringVar(master=root, value=""),
    "hunt_status": tk.StringVar(master=root, value=idle_text),
    "hunt_target_info": tk.StringVar(master=root, value=app._t("target_card.target_none"))
}

self.ui_widgets = {
    "monster_select_combo": None,
    "monster_manager_win": None,
    "skill_manager_win": None,
    "monster_listbox": None,
    "skill_listbox": None,
    "skill_preview_label": None,
    "monster_description_text": None,
    "monster_template_listbox": None,
    "monster_template_preview_label": None,
    "monster_template_preview_image": None,
    "hunt_intermediate_widgets": [],
    "hunt_advanced_widgets": []
}

# Also encapsulate the grouped vars:
self.monster_template_region_vars = { ... }
self.monster_bounds_vars = { ... }
```

### Step 4.2: Update Controller Methods
Any method in `AppStateController` that accessed `app.monster_estimate_var` or `app.skill_name_var` needs to be updated to use `self.ui_vars["monster_estimate"]`.
For example, inside `_update_monster_estimate_label`, change `app.monster_estimate_var.set(...)` to `self.ui_vars["monster_estimate"].set(...)`.

## 5. Pitfalls & Notes
- Be meticulous. Missing a single `app.xxx_var` will cause `AttributeError` regressions later.
- Remove the `try...except` block around `i18n_t` inside `__init__` as per memory guidelines (let i18n handle its own fallbacks natively).
- Make sure `master=self.root` is used for all `StringVar` initializations.

## 6. Acceptance Criteria
- [ ] No `tk.StringVar` or widget references are attached directly to `app`.
- [ ] Controller methods reference the structured `self.ui_vars` or `self.ui_widgets`.
- [ ] The `try..except` block around `i18n_t("skill_type_attack")` is removed in favor of direct execution.

## 7. Identified Risks & Current State Assessment (Auto-Updated)
**Current State Analysis:**
- `app_state_controller.py` creates many `tk.StringVar` instances (e.g., `app.monster_select_var`, `app.skill_name_var`) and attaches them to `app` (the root window).
- It also assigns numerous UI widgets (like `app.monster_manager_win`, `app.monster_listbox`, `app.monster_select_combo`) as properties of `app`.

**Identified Risks & Pitfalls:**
- **Incomplete Variable Grouping:** The current `__init__` has over 40 variables. Missing even one when moving them to dictionaries like `self.ui_vars` or `self.ui_widgets` will result in silent UI failures or `AttributeError` exceptions when views try to read/write them.
- **Reference Updates:** `AppStateController` contains methods (like `_update_monster_estimate_label`) that actively use these variables. All internal method references must be updated simultaneously with the `__init__` changes.
- **i18n Try-Except Block:** As per memory rules, the `try...except Exception` block around `i18n_t` (used for `skill_type_default`) must be removed, relying on the translation module's native error handling. The prompt correctly notes this, but it requires careful execution to avoid startup crashes if the translation key is missing.
