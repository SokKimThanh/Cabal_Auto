# Sprint 30: Refactor Debt Technical - Fix AppShell Theme and Window Title
**File:** `sprint30-prompt-012-fix-app-shell-theme-title.md`
**Previous Context:** `sprint30-prompt-re-excecute-order.md` (Issue #2)
**Estimated Time:** < 30 minutes

## 1. Title & Objective
**Title:** Fix AppShell Initialization of UIStyle and Window Title
**Objective:** Resolve the remaining AppShell architectural leaks. First, ensure the main window title is managed by `AppShell` (even during language changes). Second, investigate and fix the missing `UIStyleV2.apply()` theme initialization step. Third, fix the confusing parameter passing during `AppShell` instantiation.

## 2. Context
In Prompt 006, the `AppShell` was created to encapsulate the main window configuration. However, the review report highlighted three issues:
1. `app_gui.py` still manually sets the window title using `self.title(self._t("app_title"))` inside `on_language_change()`.
2. The UI theme initialization (supposedly `UIStyleV2.apply(...)`) disappeared. We need to verify how styles are applied (or if they are purely a namespace now) and correctly implement them.
3. The instantiation syntax `self.shell = AppShell(self)` is somewhat confusing because `self` inside `App` represents both the logic controller and the `tk.Tk` root window.

## 3. Files to Modify
- `ui/components/app_shell.py`
- `app_gui.py`
- `lib/ui_style_v2.py` (if necessary to verify theme logic)

## 4. Detailed Implementation Guide

### Step 4.1: Clean up AppShell Instantiation
In `app_gui.py`, change the instantiation to be explicit:
```python
self.shell = AppShell(root=self, app=self)
```
Update `AppShell.__init__` in `ui/components/app_shell.py` to handle this explicitly without the fallback logic.

### Step 4.2: Encapsulate Title Updates
Add a method `update_title(self)` or `apply_language(self)` to `AppShell`.
Move the logic `self.root.title(self.app._t("app_title"))` into this method.
In `app_gui.py`, inside `on_language_change()`, replace the direct `self.title(...)` call with `self.shell.update_title()`.

### Step 4.3: Investigate and Fix Theme Initialization
Examine `lib/ui_style_v2.py`. If it acts purely as a namespace for constants and lacks an `.apply()` method, document this and ensure `AppShell` sets any required background colors (e.g., `self.root.configure(bg=UIStyleV2.BG_MAIN)`). If `apply` is missing but required, re-implement it.

## 5. Acceptance Criteria
- [ ] `self.title` is no longer called directly from `app_gui.py`.
- [ ] Theme/background colors are successfully and clearly applied during `AppShell.build()`.
- [ ] The app launches successfully without layout or styling regressions.
