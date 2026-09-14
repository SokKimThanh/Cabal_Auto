# Sprint 30 Phase 4 Prompt 024: Extract Vision UI Handlers

## Goal
Move Vision and Template-related UI logic out of the `App` class.

## Details
- Identify vision-related methods in `app_gui.py`: `_scan_region`, `_add_template`, `_manage_templates`, and `_open_vision_wizard`.
- Relocate these functions into `OverlayController`, `AppWindowController`, or a newly created `VisionUIController`.
- Update the menu (extracted in prompt 022) to route shortcuts and clicks to the new controller instead of `app`.

## Risks and Things to Avoid
- **Avoid migrating Tkinter UI logic deeply into the Vision Engine core.**
- **Risk:** If `VisionUIController` holds strong references to overlay windows, it could cause memory leaks when overlays are destroyed and recreated.
- **Risk:** Key bindings (Ctrl+Shift+V) might conflict or fail to register if the global hotkey system and Tkinter bind system step on each other.

## Acceptance Criteria
- `app_gui.py` no longer contains vision shortcut handler methods.
- Vision functionalities remain accessible via shortcuts and menu.
- `pylint app_gui.py` remains at 10.0.
