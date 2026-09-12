# Sprint 30: Refactor Debt Technical - App GUI
**File:** `sprint30-prompt-009-app-gui-dialog-service.md`
**Previous Context:** `sprint30-prompt-008-app-gui-sidebar.md`
**Estimated Time:** < 30 minutes

## 1. Title & Objective
**Title:** Extract Dialog Service
**Objective:** Replace direct, hardcoded calls to `tkinter.messagebox` across `app_gui.py` and other UI components with a centralized `DialogService`.

## 2. Context
As noted in the architecture review (Item 6), calling `messagebox.showinfo()` directly scatters UI framework dependencies throughout the codebase. If the project ever decides to switch to custom styled dialogs (like Toasts or custom modals matching UI Style V2), it requires refactoring hundreds of lines. We need a `DialogService` proxy.

## 3. Files to Modify
- `lib/ui/dialog_service.py` (Create)
- `ui/app_gui.py`
- (Optional) Other views/controllers relying heavily on `messagebox`.

## 4. Detailed Implementation Guide

### Step 4.1: Create DialogService
Create `lib/ui/dialog_service.py`.
Define a class `DialogService` with methods like:
- `show_info(title, message, parent=None)`
- `show_error(title, message, parent=None)`
- `show_warning(title, message, parent=None)`
- `ask_yes_no(title, message, parent=None)` -> bool

Internally, these methods will import and call `tkinter.messagebox`.

### Step 4.2: Refactor `app_gui.py`
In `app_gui.py`, search for `messagebox` imports and calls.
Replace them with the newly created `DialogService`.
Example:
```python
# Old
import tkinter.messagebox as messagebox
messagebox.showerror("Error", "Something went wrong", parent=self.root)

# New
from lib.ui.dialog_service import DialogService
DialogService.show_error("Error", "Something went wrong", parent=self.root)
```

### Step 4.3: Export Service Initialization
If the service needs the `app.root` as a default parent to avoid passing `parent=self.root` everywhere, initialize it in `App.__init__` and set the global default root.

## 5. Pitfalls & Notes
- Ensure the `DialogService` handles `parent=None` gracefully by falling back to the main `tk.Tk` instance if possible, to prevent dialogs from popping up behind the main window on Windows OS.
- Do not refactor complex custom modals (like `PresetDialog`) in this prompt, only the standard system message boxes.

## 6. Acceptance Criteria
- [ ] `tkinter.messagebox` is no longer imported or called directly inside `app_gui.py`.
- [ ] All info, error, and confirmation popups function correctly via the `DialogService`.

## 7. Identified Risks & Current State Assessment (Auto-Updated)
**Current State Analysis:**
- There are multiple hardcoded calls to `tkinter.messagebox` across `app_gui.py` and potentially nested controllers.

**Identified Risks & Pitfalls:**
- **Lost Thread Safety:** If `messagebox` is called from a background thread (e.g., inside a scan or hunt loop), standard Tkinter crashes. The new `DialogService` should ideally route dialog calls through the main Tkinter event loop (using `.after(0, ...)`) if called off-thread, or at least document that it expects to be called from the main thread.
- **Parent Window Focus:** Explicitly passing `parent=self.root` is crucial in the current implementation to prevent popups from appearing underneath the main game window. `DialogService` must have a mechanism to reliably obtain the main window reference to use as the default parent.
