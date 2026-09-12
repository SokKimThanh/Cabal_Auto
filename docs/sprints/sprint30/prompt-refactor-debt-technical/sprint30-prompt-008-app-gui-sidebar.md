# Sprint 30: Refactor Debt Technical - App GUI
**File:** `sprint30-prompt-008-app-gui-sidebar.md`
**Previous Context:** `sprint30-prompt-007-app-gui-navigation.md`
**Estimated Time:** < 30 minutes

## 1. Title & Objective
**Title:** Extract Sidebar Component
**Objective:** Move the UI construction logic for the side navigation menu (`_build_sidebar` and related bindings) out of `app_gui.py` into a dedicated `SidebarComponent`.

## 2. Context
The `app_gui.py` contains a lengthy `_build_sidebar` method responsible for creating buttons, setting icons, handling hover states, and binding click events for the main navigation. This is pure UI code that clutters the God Class and should be encapsulated.

## 3. Files to Modify
- `ui/app_gui.py`
- Create `ui/components/sidebar_component.py` (or `ui/views/sidebar.py`)

## 4. Detailed Implementation Guide

### Step 4.1: Create SidebarComponent
Create the file and define `SidebarComponent(tk.Frame)`.
The constructor should accept the parent frame (the sidebar zone created by `AppShell`) and a callback function for navigation (e.g., `on_navigate_callback`).

### Step 4.2: Relocate Code
Move the entire `_build_sidebar` logic from `app_gui.py` into `SidebarComponent._build()`.
Move any helper methods specifically related to the sidebar (like updating active button styling, hover effects) into this new class.

### Step 4.3: Decouple Navigation
The original sidebar buttons call `app.show_frame(...)`. In the new component, they should call the provided `on_navigate_callback(view_name)`.

### Step 4.4: Integrate into App
In `app_gui.py`, instantiate the sidebar:
```python
self.sidebar = SidebarComponent(
    parent=self.shell.sidebar_frame,
    app=self, # If needed for i18n
    on_navigate_callback=self.navigation.navigate_to
)
```

## 5. Pitfalls & Notes
- Ensure all translations (`i18n_t`) remain functional. You may need to import `i18n_t` globally in the new component.
- Icons are managed by `IconHelper`. Make sure the imports for `IconHelper` and `UIStyleV2` are present in `sidebar_component.py`.

## 6. Acceptance Criteria
- [ ] `_build_sidebar` is completely removed from `app_gui.py`.
- [ ] The `SidebarComponent` renders correctly in the left pane.
- [ ] Clicking sidebar buttons routes successfully through the `NavigationController`.