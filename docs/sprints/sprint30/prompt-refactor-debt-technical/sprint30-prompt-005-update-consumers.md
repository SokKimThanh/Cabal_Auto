# Sprint 30: Refactor Debt Technical - AppStateController
**File:** `sprint30-prompt-005-update-consumers.md`
**Previous Context:** `sprint30-prompt-004-extract-skill-logic.md`
**Estimated Time:** < 30 minutes

## 1. Title & Objective
**Title:** Update Downstream Consumers for State Encapsulation
**Objective:** Now that `AppStateController` correctly encapsulates state (as `self.xxx` and `self.ui_vars`), update other classes (like `App` in `app_gui.py` and other views) to use the correct getters or properties instead of referencing the old `app.xxx` God Class properties.

## 2. Context
In Prompts 01 and 02, we moved variables like `app.monster_select_var` into `app.state_controller.ui_vars["monster_select"]`, and `app.click_running` to `app.state_controller.click_running`. However, many views and controllers across the system are still trying to read `app.monster_select_var` directly. This prompt fixes these regressions system-wide.

## 3. Files to Modify
- `app_gui.py` (specifically `_build_...` methods)
- Any UI View or Frame that interacts with these variables (e.g., `ui/views/...`)
- Callers of the extracted business logic (e.g., `HuntOrchestrator`).

## 4. Detailed Implementation Guide

### Step 4.1: Update Tkinter Variable References
Run a codebase search (e.g., `grep -r "app\.monster_select_var" .`) to find all files referencing the old variables.
Change them systematically:
- `app.monster_select_var` -> `app.state_controller.ui_vars["monster_select"]`
- `app.skill_name_var` -> `app.state_controller.ui_vars["skill_name"]`
- `app.monster_bounds_vars["left"]` -> `app.state_controller.monster_bounds_vars["left"]`

### Step 4.2: Update Simple State References
Find references to:
- `app.hunt_selected` -> `app.state_controller.hunt_selected`
- `app.win_items` -> `app.state_controller.win_items`
- `app.click_running` -> `app.state_controller.click_running`
And update them similarly.

### Step 4.3: Update Business Logic Calls
Ensure that background threads or the `HuntOrchestrator` are now calling the new `SkillCasterService` (from Prompt 04) and `WindowSelectionService` (from Prompt 03) instead of `app.state_controller._try_cast_skills`.

## 5. Pitfalls & Notes
- This is the most dangerous step regarding regressions. Use global search extensively.
- Be mindful of `hasattr(app, 'monster_select_var')`. You will need to change these to `if "monster_select" in app.state_controller.ui_vars:` or similar.
- If you find a component that passes `app` around just to read one variable, consider passing the variable directly to the component's constructor to reduce coupling further (as per `ui_architecture_review.md`).

## 6. Acceptance Criteria
- [ ] Codebase search for `app\.monster_select_var` and similar old bindings yields zero results.
- [ ] `app_gui.py` boots without crashing and successfully constructs the UI using the new encapsulated variables.
- [ ] Hunt functionalities function correctly with the new Service imports.