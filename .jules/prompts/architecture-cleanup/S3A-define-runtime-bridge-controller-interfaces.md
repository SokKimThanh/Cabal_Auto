# S3A - Define Controller Interfaces For Runtime Bridge

Paste `00-global-rules.md` first, then this prompt.

```text
Prepare Sprint 3 by tightening ui/controllers/app_runtime_bridge.py into a compatibility layer.

Goal:
Define the small interfaces app_runtime_bridge.py should call for hotkeys, overlay lifecycle, and window tracking without implementing all extracted behavior in this session.

Files in scope:
- ui/controllers/app_runtime_bridge.py
- app_gui.py only if needed to pass controller instances
- ui/controllers/__init__.py
- tests only if a small bridge test exists or is easy to add

Boundaries:
- The bridge should forward/delegate; it should not become the permanent home for hotkey, overlay, or tracking logic.
- Do not move substantial overlay/window tracker code yet.
- Keep runtime behavior equivalent.

Acceptance criteria:
- Later sessions can implement HotkeyController, OverlayController, and WindowTrackerController independently.
- Existing bridge callers still work.

Validation:
- Run focused import/bridge tests.
- Run `py -m pytest tests/test_ui_imports.py` if no narrower test exists.
```
