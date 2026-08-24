# S5B - Architecture Boundary Documentation And Final Smoke

Paste `00-global-rules.md` first, then this prompt.

```text
Finish the architecture cleanup sprint from .jules/architecture-sprint-roadmap.md.

Goal:
Document the new boundaries and run final smoke validation.

Files in scope:
- docs/architecture/README.md or another existing architecture doc if more appropriate
- .jules/architecture-cleanup-baseline.md only if updating final status is useful
- no application code unless a tiny documentation-reference fix is required

Deliverable:
- Document which modules own app lifecycle, app state, window/modal lifecycle, hunt config migration/validation, hunt orchestration, hotkeys, overlay lifecycle, window tracking, monster services, and skill services.
- Include a short contributor note: do not add new orchestration logic to app_gui.py; add it to the relevant controller/service.
- Include final validation command list and results.

Validation:
- Run the full targeted smoke suite identified by P0.
- If affordable, run the broader pytest suite.
- Confirm `py .\app_gui.py` still exits cleanly or document why it requires manual GUI interaction.
```
