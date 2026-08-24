# Changelog

## 2026-08-24 — fix app launch regression after PR #64 on top of PR #47

Summary
- Restored the tail of [`app_gui.py`](F:/Cabal_Auto.worktrees/fix-app-launch-issues-pr64-pr47/app_gui.py) that PR #64 accidentally deleted after the `# Phase 3: Multi-Monster Support Handlers` marker.
- Preserved the PR #47 modular split and continued the cleanup by moving missing runtime glue into [`ui/controllers/app_runtime_bridge.py`](F:/Cabal_Auto.worktrees/fix-app-launch-issues-pr64-pr47/ui/controllers/app_runtime_bridge.py) instead of pushing more wiring back into the God Class.
- Fixed startup blockers: broken window-bounds normalization, blank notebook tabs, missing `on_close`, missing app entry flow, and missing runtime callbacks used by the extracted tabs/windows.
- Made [`lib/vision/template_loader.py`](F:/Cabal_Auto.worktrees/fix-app-launch-issues-pr64-pr47/lib/vision/template_loader.py) compatible with the list-based `vision_templates.json` format so startup no longer logs `'list' object has no attribute 'get'`.

Files changed
- [`app_gui.py`](F:/Cabal_Auto.worktrees/fix-app-launch-issues-pr64-pr47/app_gui.py) — restored truncated logic, rewired runtime callbacks, fixed tab mounting, fixed bounds handling, cleaned duplicate methods, restored close flow
- [`ui/controllers/app_runtime_bridge.py`](F:/Cabal_Auto.worktrees/fix-app-launch-issues-pr64-pr47/ui/controllers/app_runtime_bridge.py) — new bridge/mixin for runtime glue between `App` and extracted modules
- [`ui/controllers/__init__.py`](F:/Cabal_Auto.worktrees/fix-app-launch-issues-pr64-pr47/ui/controllers/__init__.py) — package marker for controller helpers
- [`lib/vision/template_loader.py`](F:/Cabal_Auto.worktrees/fix-app-launch-issues-pr64-pr47/lib/vision/template_loader.py) — accept both list and object config payloads, ignore unsupported extra keys during load

Validation
- `python -m py_compile app_gui.py ui\\controllers\\app_runtime_bridge.py lib\\vision\\template_loader.py`
- `python -m pytest tests\\unit\\test_monster_database_startup.py tests\\test_exclusivity.py -q`
- `python -m pytest tests\\integration\\test_template_matcher_integration.py -k app_gui -q`
- startup probe via `tests/unit/app_startup_probe.py` with project root injected into `sys.path`
- GUI smoke: instantiate `App()`, run `mainloop()`, auto-close via `on_close()`
- single-instance smoke: `SingleInstanceLock` first acquire succeeds, second acquire fails

## 2025-10-22 — pr/hotkey-image-2025-10-22

Summary
- Add README section describing Launching & Hotkey Diagnostics and run_venv launchers
- Document intentional use of dynamic image references (`_image_refs`) in `lib/ui`
- Add minimal type-check annotations/ignores to silence static analyzer warnings for dynamic widget attributes

Files changed
- `README.md` — added diagnostics section
- `ui/setup_wizard.py` — type-ignore annotations for LibraryManagerWindow parent arg and safer setattr usage in demo block
- `app_gui.py` — documented `_image_refs` usage and ensured central storage for PhotoImage refs
- `lib/ui/__init__.py` — package note about image refs and type-ignores

Notes
- Tests: targeted unit tests for tooltip/image-ref retention passed locally.
- Static diagnostics: no current errors after changes. Some uses include deliberate `# type: ignore` comments.

## Refactor: decompose app_gui God Class into modular MVC architecture
- Extract core services to lib/system (InstanceLock, HotkeyManager)
- Extract domain repos and runner to lib/features (hunt, monsters, skills)
- Split GUI tabs into standalone components in ui/tabs (Hunt, Setup, Stats, Help)
- Extract dialogs and modals into ui/windows
- Ensure clean separation of concerns and fix all flake8/test regressions
- Solved recursive logic inside Dialog initializations to stop stack overflows.
