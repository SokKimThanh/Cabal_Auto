# S2D - Extract Window Selection Service

Paste `00-global-rules.md` first, then this prompt.

```text
Implement the Sprint 2 window selection service from .jules/architecture-sprint-roadmap.md.

Goal:
Create lib/features/hunt/window_selection_service.py for target window and bounds validation logic used by hunt setup/runtime.

Files in scope:
- lib/features/hunt/window_selection_service.py
- lib/features/hunt/config_validator.py if it needs shared value objects/helpers
- app_gui.py only for delegation cleanup
- ui/controllers/app_window_controller.py only if Sprint 1 established it as the caller
- focused tests for bounds normalization

Boundaries:
- Do not duplicate logic already centralized in config_migrator/config_validator.
- Keep service UI-agnostic: no direct Tk widget ownership.
- Preserve existing behavior when the target window disappears or bounds are missing.

Acceptance criteria:
- Target/window bounds validation has a service API.
- No repeated direct `hunt_cfg.get("hunt_area", {}).get("window_bounds")` access remains in UI/runtime code outside the migration/validation layer.

Validation:
- Run focused config/window-selection tests.
- Run any existing target-window smoke test found in baseline.
```
