# S2C - Extract Hunt Orchestrator Runtime Boundary

Paste `00-global-rules.md` first, then this prompt.

```text
Implement the Sprint 2 hunt orchestration extraction from .jules/architecture-sprint-roadmap.md.

Goal:
Create lib/features/hunt/hunt_orchestrator.py so hunt loop orchestration and scan state transitions are not controlled directly by app_gui.py.

Files in scope:
- lib/features/hunt/hunt_runner.py
- lib/features/hunt/scan_controller.py
- lib/features/hunt/scanner.py only if a narrow adapter is required
- lib/features/hunt/hunt_orchestrator.py
- app_gui.py only for delegating to the orchestrator
- focused tests for start/stop behavior

Boundaries:
- hunt_runner.py should receive explicit runtime config instead of reading UI state directly.
- The orchestrator may adapt UI/controller callbacks, but should not own Tk widgets.
- Do not change monster detection/gameplay behavior beyond dependency injection and delegation.

Acceptance criteria:
- Start/stop scan behavior is preserved.
- Runtime config is passed explicitly.
- app_gui.py no longer owns hunt loop orchestration.

Validation:
- Run focused scan controller/hunt tests.
- Run `py -m pytest tests/test_scan_controller.py` if applicable.
```
