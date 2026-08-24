# S4B - Extract Monster Manager Controller And Service

Paste `00-global-rules.md` first, then this prompt.

```text
Implement the Sprint 4 monster manager decoupling from .jules/architecture-sprint-roadmap.md.

Goal:
Create ui/controllers/monster_manager_controller.py and lib/features/monsters/monster_library_service.py to separate modal lifecycle from monster data refresh/persistence.

Files in scope:
- ui/controllers/monster_manager_controller.py
- lib/features/monsters/monster_library_service.py
- ui/windows/monster_manager_win.py only for tiny interface/callback adjustments
- lib/features/monster_service.py
- lib/features/monster_manager.py
- lib/features/monsters/monster_repo.py
- app_gui.py only for composition/delegation
- focused tests for service/controller behavior

Boundaries:
- Do not change monster data schema or gameplay mapping.
- Keep UI view code focused on rendering and user interaction.
- Service owns repo refresh/persistence logic exposed through a small API.

Acceptance criteria:
- Monster manager reuses/focuses existing windows.
- Monster refresh repopulates selectors through controller/service callbacks.
- App root no longer mutates monster manager state ad hoc.

Validation:
- Run focused monster manager/service tests if present.
- Add small service tests around refresh/persistence boundaries if practical.
```
