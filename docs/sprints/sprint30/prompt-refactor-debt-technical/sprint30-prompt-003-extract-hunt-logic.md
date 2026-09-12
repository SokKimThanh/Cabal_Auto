# Sprint 30: Refactor Debt Technical - AppStateController
**File:** `sprint30-prompt-003-extract-hunt-logic.md`
**Previous Context:** `sprint30-prompt-002-encapsulate-tkinter-vars.md`
**Estimated Time:** < 30 minutes

## 1. Title & Objective
**Title:** Extract Hunt Core Logic from AppStateController
**Objective:** Resolve "Business Logic Leaks" by moving `_validate_hunt_prerequisites`, `_hunt_locate_target`, and `_hunt_from_ui` out of `AppStateController` and into dedicated services or utility modules.

## 2. Context
`AppStateController` is supposed to strictly manage UI state. However, it currently contains hardcore business logic for validating windows, compiling hunt configurations, and running template matching (`_hunt_locate_target`). This violates the Single Responsibility Principle and tightens coupling.

## 3. Files to Modify
- `ui/controllers/app_state_controller.py`
- `lib/features/hunt/hunt_manager.py` (Create or update) or `lib/features/hunt/window_selection_service.py`

## 4. Detailed Implementation Guide

### Step 4.1: Extract `_validate_hunt_prerequisites`
This method validates the selected window and templates.
- Move the logic inside `_validate_hunt_prerequisites` into a new static method or service function inside `lib/features/hunt/window_selection_service.py` (e.g., `validate_prerequisites(app_state, hunt_cfg)`).
- Note: It requires access to `app.hunt_selected`, `app.win_items`, and `app.hunt_cfg`. Pass these explicitly as arguments rather than passing the `app` object to avoid God Class dependency.
- In `AppStateController`, either delete the method entirely if the caller can use the new service directly, or keep a 1-line wrapper that calls the external service.

### Step 4.2: Extract `_hunt_locate_target`
This method imports `locate_template` and iterates over bounding boxes.
- Create a new module/class (e.g., `TargetLocatorService` in `lib/features/hunt/target_locator.py` or similar existing file).
- Move the `_hunt_locate_target` logic there.
- Pass `cfg` as the explicit parameter.

### Step 4.3: Extract `_hunt_from_ui`
This method constructs a massive `cfg` dictionary by querying UI variables.
- This is technically UI-related, but it acts as an "Adapter" or "ConfigBuilder".
- Rename it to `build_hunt_config_from_state` and keep it in `AppStateController` but ensure it uses the newly encapsulated `self.ui_vars` instead of `getattr(app, ...)`.
- Alternatively, extract it into a `HuntConfigBuilder` class if it's too large. For this session, just refactor it to remove `getattr(app, ...)` and use `self.ui_vars` and `self.XXX` (from Prompt 01 and 02).

## 5. Pitfalls & Notes
- Take care with translations (`app._t()`). If moving logic to a service, you may need to import the global `i18n_t` and `I18N_GLOBAL` namespace instead of relying on `app._t`.
- When passing state to external services, pass simple dictionaries/values instead of passing the entire `AppStateController` to prevent circular dependencies.

## 6. Acceptance Criteria
- [ ] `_validate_hunt_prerequisites` is moved to a Hunt/Window Service.
- [ ] `_hunt_locate_target` is moved to a Target/Vision Service.
- [ ] `_hunt_from_ui` no longer uses `getattr(app, ...)` and reads from `self.ui_vars` cleanly.
- [ ] Imports are cleaned up in `app_state_controller.py`.

## 7. Identified Risks & Current State Assessment (Auto-Updated)
**Current State Analysis:**
- Methods like `_validate_hunt_prerequisites` and `_hunt_locate_target` contain heavy business logic (e.g., verifying bounding boxes, calling `locate_template` via OpenCV) directly within `AppStateController`.
- `_hunt_from_ui` dynamically builds the hunt configuration dictionary from UI variables.

**Identified Risks & Pitfalls:**
- **Circular Dependencies:** When moving `_validate_hunt_prerequisites` to `WindowSelectionService`, you must avoid passing `app` or the controller itself. Extract only the necessary primitive data (like `app.hunt_selected`, `app.win_items`) to pass as arguments.
- **Translation (`i18n_t`) Dependencies:** `_validate_hunt_prerequisites` relies heavily on `app._t()` to generate status messages (e.g., `bounds_state_select`, `bounds_state_ready`). If this method is moved to a background service, it cannot easily access `app._t()`. The prompt should explicitly instruct using the global `i18n_t` with `I18N_GLOBAL` namespace instead of `app._t()`.
- **UI Label Updates:** `_validate_hunt_prerequisites` directly updates UI labels (`app.bounds_readiness_label.config(fg=...)`). Moving this logic to a service means the service should return a status object (message + status code), and the controller should handle the UI updates based on that returned object.
