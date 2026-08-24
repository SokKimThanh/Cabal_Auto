# S4A - Extract Library Manager Controller

Paste `00-global-rules.md` first, then this prompt.

```text
Implement the Sprint 4 library manager lifecycle extraction from .jules/architecture-sprint-roadmap.md.

Goal:
Create ui/controllers/library_manager_controller.py to own library manager open/focus/reuse behavior and callback dispatch.

Files in scope:
- ui/controllers/library_manager_controller.py
- ui/windows/library_manager.py only for tiny callback/interface adjustments
- ui/controllers/app_runtime_bridge.py only for forwarding
- app_gui.py only for composition/delegation
- focused tests for duplicate window prevention if practical

Boundaries:
- Do not make library_manager.py the sole lifecycle source of truth.
- Preserve existing UI behavior and callbacks.
- Do not refactor monster/skill repos in this session except callback wiring.

Acceptance criteria:
- Repeated library manager actions reuse/focus the existing window.
- Closing and reopening does not leave stale handles.
- App no longer owns library modal lifecycle directly.

Validation:
- Run focused UI import/window tests.
- Add fake-based lifecycle tests if practical.
```
