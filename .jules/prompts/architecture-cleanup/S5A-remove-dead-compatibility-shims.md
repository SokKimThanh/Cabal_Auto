# S5A - Remove Dead Compatibility Shims

Paste `00-global-rules.md` first, then this prompt.

```text
Implement Sprint 5 dead-shim cleanup from .jules/architecture-sprint-roadmap.md.

Goal:
Remove compatibility shims and forwarding methods that are no longer needed after Sprints 1 through 4, while preserving stable public APIs still used by tests or UI callbacks.

Files in scope:
- app_gui.py
- ui/controllers/*.py
- lib/features/hunt/*.py only where prior shims remain
- focused tests only

Boundaries:
- Do not delete compatibility code unless repository search confirms no active caller remains.
- Do not change behavior or public config shape.
- Keep app_gui.py as a composition root with explicit controller construction.

Acceptance criteria:
- No stale duplicated lifecycle/config/window/modal logic remains.
- Remaining bridge code is justified by active callers.
- app_gui.py is visibly thin and explicit.

Validation:
- Run targeted smoke suite found in P0.
- Run `py -m pytest tests/test_ui_imports.py tests/test_scan_controller.py` if those tests are still relevant.
```
