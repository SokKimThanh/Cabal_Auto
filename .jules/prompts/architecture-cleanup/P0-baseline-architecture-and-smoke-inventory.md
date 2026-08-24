# P0 - Baseline Architecture And Smoke Inventory

Paste `00-global-rules.md` first, then this prompt.

```text
Read .jules/architecture-sprint-roadmap.md and inspect only the files named in Sprint 1 through Sprint 4 scope lists. Produce a short architecture baseline document at .jules/architecture-cleanup-baseline.md.

Scope:
- app_gui.py
- ui/controllers/app_runtime_bridge.py
- lib/features/hunt/hunt_runner.py
- lib/features/hunt/hunt_config.py
- ui/utils/overlay_controller.py
- ui/utils/window_tracker.py
- lib/system/hotkey_manager.py
- ui/windows/monster_manager_win.py
- ui/windows/skill_manager_win.py
- ui/windows/library_manager.py
- existing nearby tests under tests/

Deliverable:
- A concise map of responsibilities currently owned by app_gui.py.
- A comparison plan for checking original app_gui behavior against split modules during later sessions.
- Existing tests or smoke commands that validate app startup, close, hotkeys, overlay, hunt config, and modal reuse.
- Boundary/edge cases already covered by tests and boundary cases still missing.
- A lost-code watchlist: callbacks, public App attributes, imports, compatibility fallbacks, config migration, UI event bindings, cleanup paths, and helper methods that must not disappear during extraction.
- A suggested order for Sprint 1 sessions if app_gui.py has hidden coupling.

Do not edit application code in this session. Only create or update .jules/architecture-cleanup-baseline.md.
Run no broad test suite unless it is already documented as cheap. If no cheap command exists, say so.
```
