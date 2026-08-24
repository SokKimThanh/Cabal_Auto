# S2B - Add Hunt Config Validator

Paste `00-global-rules.md` first, then this prompt.

```text
Implement the Sprint 2 config validation extraction from .jules/architecture-sprint-roadmap.md.

Goal:
Create lib/features/hunt/config_validator.py and centralize guard logic for hunt_area, target/window bounds, and malformed values.

Files in scope:
- lib/features/hunt/hunt_config.py
- lib/features/hunt/config_validator.py
- lib/features/hunt/config_migrator.py only if validator integration requires a small adjustment
- app_gui.py only for removing duplicated low-level validation
- focused tests for validation

Boundaries:
- Validation should return normalized safe data or clear validation results; avoid scattered nested `.get()` chains.
- Preserve existing behavior for absent or malformed settings.
- Do not change image scanning or runtime loop behavior.

Acceptance criteria:
- There is one central guard for `hunt_area.window_bounds` compatibility.
- app_gui.py no longer performs low-level hunt config validation directly.
- Tests cover malformed, missing, and valid bounds.

Validation:
- Run focused hunt config validator tests.
- Run existing scan controller or hunt config tests if present.
```
