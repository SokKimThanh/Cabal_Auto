# S1C - Extract App Lifecycle Controller

Paste `00-global-rules.md` first, then this prompt.

```text
Implement the Sprint 1 lifecycle extraction from .jules/architecture-sprint-roadmap.md.

Goal:
Move startup lifecycle coordination and close/dispose orchestration out of app_gui.py into ui/controllers/app_lifecycle_controller.py.

Files in scope:
- app_gui.py
- ui/controllers/app_lifecycle_controller.py
- ui/controllers/app_runtime_bridge.py only if compatibility forwarding is required
- ui/controllers/__init__.py
- focused tests only if needed

Boundaries:
- App.__init__ should become bootstrap + composition, not a new large helper inside app_gui.py.
- App.on_close() should delegate to AppLifecycleController.
- Preserve duplicate instance lock behavior and existing shutdown cleanup ordering.
- Do not change hunt loop internals, hotkey internals, or overlay internals in this session.

Acceptance criteria:
- App startup path remains intact.
- on_close() completes without exceptions.
- Cleanup order remains equivalent to current behavior.
- app_gui.py is thinner and clearly delegates lifecycle work.

Validation:
- Run the narrowest App startup/close smoke test available.
- Run `py -m pytest tests/test_ui_imports.py` if no narrower test exists.
- Run any existing duplicate-instance lock test if P0 found one.
```
