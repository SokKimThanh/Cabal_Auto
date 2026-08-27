# S4C - Extract Skill Manager Controller And Runtime Service

Paste `00-global-rules.md` first, then this prompt.

```text
Implement the Sprint 4 skill manager decoupling from .jules/architecture-sprint-roadmap.md.

Goal:
Create ui/controllers/skill_manager_controller.py and lib/features/skills/skill_runtime_service.py to separate skill modal lifecycle, repo refresh, and runtime mapping.

Files in scope:
- ui/controllers/skill_manager_controller.py
- lib/features/skills/skill_runtime_service.py
- ui/windows/skill_manager_win.py only for tiny interface/callback adjustments
- lib/features/skills/skill_repo.py
- lib/features/skills/runtime.py
- app_gui.py only for composition/delegation
- focused tests for service/controller behavior

Boundaries:
- Do not change skill schema or runtime semantics.
- Keep UI view code focused on rendering and user interaction.
- Service owns runtime mapping and repo refresh operations through a small API.

Acceptance criteria:
- Skill manager reuses/focuses existing windows.
- Skill refresh repopulates selectors through controller/service callbacks.
- App root no longer mutates skill manager state ad hoc.

Validation:
- Run focused skill repo/runtime tests if present.
- Add small service tests around runtime mapping if practical.
```
