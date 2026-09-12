# Sprint 30: Refactor Debt Technical - App GUI
**File:** `sprint30-prompt-007-app-gui-navigation.md`
**Previous Context:** `sprint30-prompt-006-app-gui-extract-shell.md`
**Estimated Time:** < 30 minutes

## 1. Title & Objective
**Title:** Extract Navigation Controller
**Objective:** Resolve the "Hardcoded View Registry" anti-pattern in `app_gui.py` by extracting `self._views` and the screen transition logic (`show_frame`) into a dedicated `NavigationController`.

## 2. Context
`App` currently hardcodes the instantiation of all major UI Views (`HuntView`, `SetupView`, `SkillPanelView`, etc.) into a `self._views` dictionary and manages switching between them via `show_frame`. This tightly couples the `App` to every single view in the application.

## 3. Files to Modify
- `ui/app_gui.py`
- Create `ui/controllers/navigation_controller.py`

## 4. Detailed Implementation Guide

### Step 4.1: Create NavigationController
Create `ui/controllers/navigation_controller.py`. Define `NavigationController`.
It should accept the `main_content_frame` (from `AppShell`) as the parent container where views will be rendered.

### Step 4.2: Move View Registry
Move the instantiation of views from `app_gui.py` to `NavigationController`.
```python
# In NavigationController
def register_views(self, app_instance):
    self.views["hunt"] = HuntView(self.container, app=app_instance)
    self.views["setup"] = SetupView(self.container, app=app_instance)
    # etc...
```
*Note: A more advanced approach uses dynamic import/lazy loading, but for this session, simply moving the hardcoded dictionary to the controller is sufficient to decouple `App`.*

### Step 4.3: Move `show_frame`
Move the logic of `show_frame` (hiding current views, packing the new view, emitting navigation events) into `NavigationController.navigate_to(view_name)`.

### Step 4.4: Update App
In `app_gui.py`:
- Remove `self._views` and `self.show_frame`.
- Initialize `self.navigation = NavigationController(self.shell.main_content_frame)`
- Call `self.navigation.navigate_to("hunt")` instead of `self.show_frame(...)`.

## 5. Pitfalls & Notes
- Views currently expect `app` as a parameter. Pass the app instance to the NavigationController so it can distribute it to the views upon registration.
- Ensure that any sidebar buttons calling `lambda: self.show_frame(...)` are updated to call `lambda: self.navigation.navigate_to(...)`.

## 6. Acceptance Criteria
- [ ] `self._views` and `show_frame` no longer exist in `app_gui.py`.
- [ ] Navigation is handled entirely by `NavigationController`.
- [ ] Clicking sidebar items correctly switches views without crashing.