# S2A - Centralize Hunt Config Migration

Paste `00-global-rules.md` first, then this prompt.

```text
Implement the Sprint 2 config migration extraction from .jules/architecture-sprint-roadmap.md.

Goal:
Create lib/features/hunt/config_migrator.py and centralize legacy/current hunt config shape normalization there.

Files in scope:
- lib/features/hunt/hunt_config.py
- lib/features/hunt/config_migrator.py
- app_gui.py only for replacing duplicated migration calls
- focused tests for config migration

Boundaries:
- Preserve compatibility with legacy list and current dict config shapes.
- Do not change scan loop execution.
- Do not move window selection behavior in this session except where required to normalize config inputs.

Acceptance criteria:
- hunt_cfg mutation/normalization has one clear migration entry point.
- Existing callers can load legacy and current config shapes.
- Malformed or partial config does not crash startup.

Validation:
- Add or run focused config migration tests.
- Include cases for current dict shape, legacy list shape, missing hunt_area, and malformed window_bounds.
```
