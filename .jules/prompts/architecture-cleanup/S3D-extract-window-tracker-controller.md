# S3D - Extract Window Tracker Controller

Paste `00-global-rules.md` first, then this prompt.

```text
Implement the Sprint 3 window tracker extraction from .jules/architecture-sprint-roadmap.md.

Goal:
Create ui/controllers/window_tracker_controller.py for window detection, refresh loops, duplicate/flood control, and tracker lifecycle.

Files in scope:
- ui/controllers/window_tracker_controller.py
- ui/utils/window_tracker.py
- ui/controllers/app_runtime_bridge.py only for forwarding
- app_gui.py only for composition/delegation
- focused tests for tracker behavior if practical

Boundaries:
- Keep platform-specific detection details in ui/utils/window_tracker.py if they already live there.
- Controller owns lifecycle, refresh scheduling, and duplicate/flood-control decisions.
- Do not change hunt config migration in this session.

Acceptance criteria:
- Tracking logic is observable and unit-testable.
- Repeated trigger paths do not open duplicate windows.
- App root delegates tracker lifecycle to the controller.

Validation:
- Run focused window tracker tests if present.
- Add a small fake-based test for duplicate prevention if practical.
```
