# S1B - Extract App Window Controller

Paste `00-global-rules.md` first, then this prompt.

```text
Implement the Sprint 1 window ownership extraction from .jules/architecture-sprint-roadmap.md.

Goal:
Move dialog/window ownership tracking and target window selection lifecycle out of app_gui.py into ui/controllers/app_window_controller.py.

Files in scope:
- app_gui.py
- ui/controllers/app_window_controller.py
- ui/controllers/app_runtime_bridge.py only if compatibility forwarding is required
- ui/controllers/__init__.py
- focused tests only if needed

Boundaries:
- Keep actual UI view classes unchanged unless a tiny call-site adjustment is required.
- app_gui.py should delegate window open/focus/reuse/selection lifecycle to AppWindowController.
- Do not change hunt behavior, overlay behavior, or hotkey behavior beyond adapting calls to the controller.
- Do not introduce duplicate window registries.

Acceptance criteria:
- Repeated window open actions reuse/focus existing windows where current behavior expects that.
- Target window selection still starts/stops without startup regressions.
- app_gui.py is no longer the direct owner of generic window lifecycle bookkeeping.

Validation:
- Run focused tests for UI imports/window behavior if present.
- Run `py -m pytest tests/test_ui_imports.py` at minimum if no narrower test exists.
- Document any manual GUI path that still needs human confirmation.
```
