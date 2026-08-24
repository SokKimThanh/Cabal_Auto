# S3C - Extract Overlay Controller

Paste `00-global-rules.md` first, then this prompt.

```text
Implement the Sprint 3 overlay extraction from .jules/architecture-sprint-roadmap.md.

Goal:
Move overlay start/stop lifecycle decisions into ui/controllers/overlay_controller.py.

Files in scope:
- ui/controllers/overlay_controller.py
- ui/utils/overlay_controller.py
- ui/utils/overlay_settings.py
- ui/controllers/app_runtime_bridge.py only for forwarding
- app_gui.py only for composition/delegation
- focused tests for overlay lifecycle if practical

Boundaries:
- Keep ui/utils/overlay_controller.py as the low-level overlay utility if it already serves that role.
- The new controller should coordinate lifecycle and settings, not duplicate rendering internals.
- Do not change hotkey registration except where it calls overlay start/stop methods.

Acceptance criteria:
- Overlay can start/stop repeatedly without stale handles.
- Overlay lifecycle is independent from direct app root methods.
- app_runtime_bridge.py remains a compatibility layer.

Validation:
- Run focused overlay/settings tests if present.
- If no automated GUI-safe test exists, run import/syntax validation and document manual smoke path.
```
