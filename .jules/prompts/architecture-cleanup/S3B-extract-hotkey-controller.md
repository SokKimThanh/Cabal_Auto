# S3B - Extract Hotkey Controller

Paste `00-global-rules.md` first, then this prompt.

```text
Implement the Sprint 3 hotkey extraction from .jules/architecture-sprint-roadmap.md.

Goal:
Create ui/controllers/hotkey_controller.py to own global hotkey registration, enable/disable behavior, and callback dispatch.

Files in scope:
- ui/controllers/hotkey_controller.py
- lib/system/hotkey_manager.py
- ui/controllers/app_runtime_bridge.py only for forwarding
- app_gui.py only for composition/delegation
- focused tests for hotkey registration/toggle behavior

Boundaries:
- Do not change overlay or window tracker internals except callback wiring.
- HotkeyController should expose clear methods for registration, teardown, and action dispatch.
- Preserve existing hotkey names and behavior.

Acceptance criteria:
- Hotkey actions are registered through HotkeyController, not app instance code.
- Hotkeys can enable/disable cleanly.
- Cleanup unregisters/disposes hotkeys without exceptions.

Validation:
- Run focused hotkey tests if present.
- If no tests exist, add small unit tests around controller behavior using fakes/mocks where practical.
```
