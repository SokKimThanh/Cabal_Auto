# Review Prompt 024: Extract Vision UI Handlers

## Verification Steps
1. Open `app_gui.py` and confirm the removal of `_scan_region`, `_add_template`, `_manage_templates`, and `_open_vision_wizard`.
2. Verify these methods have been relocated to `VisionUIController`, `OverlayController`, or `AppWindowController`.
3. Test the vision-related keyboard shortcuts (e.g., Ctrl+Shift+V) to ensure they still function and route to the correct new controller.
4. Ensure no memory leaks occur when overlays are toggled rapidly.

## Checklist
- [ ] Vision handler methods removed from God Class.
- [ ] Logic successfully relocated to a dedicated controller.
- [ ] Shortcuts and menu items bound correctly to the new controller.
- [ ] No regression in vision functionality.
