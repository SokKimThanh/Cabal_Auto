# Sprint 30: Refactor Debt Technical - App GUI
**File:** `sprint30-prompt-006-app-gui-extract-shell.md`
**Previous Context:** Must complete Prompts 001 through 005 (Phase 1) first.
**Estimated Time:** < 30 minutes

## 1. Title & Objective
**Title:** Extract Root Window Setup into AppShell
**Objective:** Decompose the massive `App` God Class in `app_gui.py` by extracting the fundamental Tkinter window configuration, theme initialization, and UI Grid definitions (Shell Zones) into a dedicated `AppShell` component.

## 2. Context
Currently, the `__init__` and `_build` methods in `App` (`app_gui.py`) handle everything from configuring the main Tkinter window dimensions, title, and styles, to defining grid geometries for "shell_zone_a", "shell_zone_b", etc. This clutters the core app instance. We need a structural `AppShell` to hold the foundation.

## 3. Files to Modify
- `ui/app_gui.py`
- Create `ui/components/app_shell.py` (or `ui/views/app_shell.py`)

## 4. Detailed Implementation Guide

### Step 4.1: Create AppShell Class
Create `ui/components/app_shell.py`. Define a class `AppShell` that inherits from `tk.Frame` or just acts as a manager.
Move the grid weight configurations, window geometry settings (`root.geometry(...)`, `root.title(...)`), and theme initialization (`UIStyleV2.apply(...)`) from `App.__init__` and `App._build` into `AppShell.__init__` or `AppShell.build()`.

### Step 4.2: Move Shell Zones
In `App._build` (in `app_gui.py`), there are numerous frames created like `self.sidebar_frame = tk.Frame(...)` and attached to `self.root`.
Move the creation of these primary layout frames (Sidebar, Main Content Area, Footer/Status bar) into `AppShell`.

### Step 4.3: Refactor App
In `app_gui.py`, replace the raw window configuration lines with the instantiation of `AppShell`.
```python
# In app_gui.py App.__init__
self.shell = AppShell(self.root, app=self)
self.shell.build()

# Access zones via shell
self.main_content_frame = self.shell.main_content_frame
```

## 5. Pitfalls & Notes
- Ensure that the App instance passed to `AppShell` is stored as `self.app` to access configurations or state if absolutely necessary, but try to keep the Shell dumb (only concerned with geometry and layout).
- Do not move the actual contents of the sidebar or views yet (that happens in subsequent prompts). Only move the outer layout containers.

## 6. Acceptance Criteria
- [ ] `AppShell` successfully encapsulates `root.geometry`, `root.title`, and `UIStyle` initialization.
- [ ] The grid definitions (`grid_rowconfigure`, `grid_columnconfigure`) are moved to `AppShell`.
- [ ] `app_gui.py` instantiates `AppShell` and no longer configures the raw `root` window layout itself.