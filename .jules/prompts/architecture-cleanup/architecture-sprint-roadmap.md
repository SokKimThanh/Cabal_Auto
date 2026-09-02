# Architecture Cleanup Sprint Roadmap

## 1. Context and objective

PR #64 exposed a launch regression caused by a risky cleanup chain after the modular split started in PR #47. The app recovered from the immediate failure, but the architectural debt remains: `app_gui.py` is still the coordinator for too many concerns and still holds lifecycle, state, window-selection, hotkey, overlay, and hunt orchestration logic.

This roadmap is designed to continue the modularization in controlled, reviewable increments without re-introducing the startup regression.

### Goal

Reduce the remaining god-class responsibilities while preserving the PR #47 split and keeping each follow-up PR small, testable, and reversible.

### Non-goals

- Rewriting the whole app in one PR
- Changing gameplay logic beyond the cleanup required to move responsibilities out of the app root
- Replacing the UI stack or broad refactoring unrelated to architecture debt

## 2. Principles for every sprint

1. Keep each PR scoped to one responsibility boundary.
2. Do not reintroduce logic into `app_gui.py` once it has been extracted.
3. Preserve compatibility with existing config shapes during transition.
4. Add smoke validation after each sprint, not only at the end.
5. Prefer a small controller/service boundary over a bigger helper file.
6. If a file is acting as a view and a controller at the same time, split it.

## 3. Current debt summary

### High-risk files still carrying architectural debt

- `app_gui.py`
- `ui/controllers/app_runtime_bridge.py`
- `lib/features/hunt/hunt_runner.py`
- `lib/features/hunt/hunt_config.py`
- `ui/utils/overlay_controller.py`
- `ui/utils/window_tracker.py`
- `lib/system/hotkey_manager.py`
- `ui/windows/monster_manager_win.py`
- `ui/windows/skill_manager_win.py`
- `ui/windows/library_manager.py`

### Observed patterns

- Large state objects are stored directly on the app root (`self.*`)
- App root is acting as window owner, lifecycle manager, and callback hub
- Window, overlay, config migration, and app lifecycle concerns are mixed together
- Some modules still depend on direct app attributes instead of a dedicated controller/service API

## 4. Sprint plan

## Sprint 1 — App shell and lifecycle extraction

### Objective

Turn `app_gui.py` into a thin shell while preserving startup and close behavior.

### Files in scope

- `app_gui.py`
- `ui/controllers/app_runtime_bridge.py`
- `ui/controllers/__init__.py`

### Planned extraction

Create new controller modules:

- `ui/controllers/app_lifecycle_controller.py`
- `ui/controllers/app_window_controller.py`
- `ui/controllers/app_state_controller.py`

### Responsibilities to move out

- initialization sequence
- close/dispose sequence
- dialog and window ownership tracking
- bound state management
- target window selection lifecycle
- app-level cleanup and destroy orchestration

### Acceptance criteria

- `app_gui.py` no longer owns app lifecycle logic directly
- `App.__init__` is reduced to bootstrap + composition
- `on_close()` is delegated to a lifecycle controller
- `main()` and startup path remain intact and smoke-tested
- no direct dependency on app root state for window tracking logic

### Validation checklist

- instantiate `App()` successfully
- `mainloop()` and `on_close()` complete without exceptions
- duplicate instance lock still works
- targeted GUI smoke tests still pass

### Risk to avoid

Do not move startup logic back into a larger helper method inside `app_gui.py` without preserving a clear boundary.

---

## Sprint 2 — Hunt runtime and config migration separation

### Objective

Separate hunt execution and config normalization from UI state and app shell logic.

### Files in scope

- `lib/features/hunt/hunt_runner.py`
- `lib/features/hunt/hunt_config.py`
- `lib/features/hunt/scan_controller.py`
- `lib/features/hunt/scanner.py`
- `app_gui.py`

### Planned extraction

Create new modules:

- `lib/features/hunt/hunt_orchestrator.py`
- `lib/features/hunt/window_selection_service.py`
- `lib/features/hunt/config_migrator.py`
- `lib/features/hunt/config_validator.py`

### Responsibilities to move out

- hunt loop orchestration
- target and window bounds validation
- config normalization and migration logic
- scan state transitions
- hunt-area compatibility handling

### Acceptance criteria

- `hunt_cfg` mutation logic is centralized in a migrator/validator
- `hunt_runner.py` receives explicit runtime config instead of reading UI state directly
- legacy list/dict config shapes are handled in one migration layer
- `app_gui.py` no longer performs low-level config validation logic directly

### Validation checklist

- config loads from legacy and current shapes
- hunt area bounds are normalized consistently
- scan loop still starts/stops correctly
- app does not crash when config is partially migrated or malformed

### Risk to avoid

Do not continue to read `hunt_cfg.get("hunt_area", {}).get("window_bounds")` in multiple UI and runtime files with no central guard.

---

## Sprint 3 — Hotkey, overlay, and window tracker extraction

### Objective

Move non-UI event orchestration out of app root.

### Files in scope

- `ui/controllers/app_runtime_bridge.py`
- `ui/utils/overlay_controller.py`
- `ui/utils/window_tracker.py`
- `ui/utils/overlay_settings.py`
- `lib/system/hotkey_manager.py`

### Planned extraction

Create new modules:

- `ui/controllers/hotkey_controller.py`
- `ui/controllers/overlay_controller.py`
- `ui/controllers/window_tracker_controller.py`

### Responsibilities to move out

- global hotkey registration and callback dispatch
- overlay start/stop lifecycle
- window detection and refresh loops
- flood-control / duplicate window handling

### Acceptance criteria

- hotkey actions are registered through a controller, not app instance code
- overlay lifecycle is independent from the app root
- repeated trigger paths do not open duplicate windows
- tracking logic is observable and unit-testable

### Validation checklist

- hotkeys can enable/disable cleanly
- overlay can start/stop repeatedly
- repeated hotkey presses do not duplicate dialogs/windows
- single-instance behavior remains intact

### Risk to avoid

Do not embed overlay decisions inside `app_runtime_bridge.py` without a dedicated controller; the bridge is only a compatibility layer, not a permanent functional home.

---

## Sprint 4 — Monster, skill, and library management decoupling

### Objective

Reduce the remaining cross-window ownership patterns and keep modal windows lifecycle-driven rather than app-driven.

### Files in scope

- `ui/windows/monster_manager_win.py`
- `ui/windows/skill_manager_win.py`
- `ui/windows/library_manager.py`
- `lib/features/monster_service.py`
- `lib/features/monster_manager.py`
- `lib/features/skills/skill_repo.py`
- `lib/features/skills/runtime.py`
- `lib/features/monsters/monster_repo.py`
- `ui/controllers/app_runtime_bridge.py`

### Planned extraction

Create new modules:

- `ui/controllers/library_manager_controller.py`
- `ui/controllers/monster_manager_controller.py`
- `ui/controllers/skill_manager_controller.py`
- `lib/features/skills/skill_runtime_service.py`
- `lib/features/monsters/monster_library_service.py`

### Responsibilities to move out

- modal open/focus/reuse behavior
- repo data refresh and persistence
- UI update callback dispatch
- duplicate window prevention
- monster and skill runtime mapping

### Acceptance criteria

- windows are reused instead of duplicated on repeated actions
- library manager updates are synced to repo and UI state through controller callbacks
- app no longer owns modal lifecycle as a side effect
- data refresh is handled through service methods, not ad hoc attribute mutation

### Validation checklist

- open close reopen library and monster managers without stale handles
- monster/skill refresh still repopulates selectors correctly
- no duplicate windows remain after repeated hotkey triggers

### Risk to avoid

Do not keep `monster_manager_win` and `library_manager_win` as the only source of truth for lifecycle state; registry through controllers is safer and easier to reason about.

---

## Sprint 4 follow-up — S4D: Migrate QuickMonsterEditor UI into MonsterManagerWin

### Context

S4B extracted `MonsterManagerController` (lifecycle: open/focus/dedup) and `MonsterLibraryService` (data), but `ui/windows/monster_manager_win.py` was left as an empty placeholder `Toplevel` (`_build_ui()` only creates an unused `Frame`). All real monster-management UI (data table, search/filter, add/edit/delete, template manager, column settings) still lives in the large, separate `ui/windows/quick_monster_editor.py` (`QuickMonsterEditor`, ~2000 lines).

On 2026-08-27 this was discovered as a live regression: the Ctrl+Shift+M hotkey and `_open_monster_manager()` had been wired to `MonsterManagerController.open_window()`, which opened the empty `MonsterManagerWin` shell instead of `QuickMonsterEditor`, so users saw a blank window with no monster-management functionality. A temporary hotfix repointed `MonsterManagerController.open_window()` to construct `QuickMonsterEditor` directly (still going through the controller's existing open/focus/dedup logic), restoring functionality without moving any UI code. This sprint is the follow-up to do the real migration properly.

### Objective

Make `MonsterManagerWin` the real monster-management view (or have `QuickMonsterEditor` become that view class, whichever requires less churn once inspected), so `ui/windows/monster_manager_win.py` is no longer a dead placeholder and the window class name matches what the controller/service architecture expects.

### Files in scope

- `ui/windows/monster_manager_win.py`
- `ui/windows/quick_monster_editor.py`
- `ui/controllers/monster_manager_controller.py`
- `lib/features/monsters/monster_library_service.py`
- `lib/hotkey/monster_editor_handler.py` (confirm dead vs. still referenced; do not delete without proof)
- tests under `tests/unit/ui/test_monster_editor_*.py`

### Planned approach

1. Decide the target shape first (do not start moving code before this is settled): either (a) rename/absorb `QuickMonsterEditor`'s implementation into `MonsterManagerWin` and delete the now-redundant `quick_monster_editor.py`, or (b) keep `QuickMonsterEditor` as the real class and delete the empty `MonsterManagerWin` shell, updating the controller and all imports to point at whichever file wins.
2. Preserve every existing behavior documented in `quick_monster_editor.py`'s module docstring (master table, search/filter, column visibility, add/edit/delete, template manager tab, display settings dialog, dirty-state tracking, database-backed load/save).
3. Update `MonsterManagerController.open_window()` to construct the final class directly (no more temporary hotfix comment).
4. Update or remove `tests/unit/ui/test_monster_editor_*.py` imports to match the final module path; do not change test assertions/behavior expectations.
5. Confirm whether `lib/hotkey/monster_editor_handler.py` (currently unreferenced from `app_gui.py`) is fully dead code before removing it; if it is still wired anywhere, reconcile it with `HotkeyController.on_monster_editor()` instead of leaving two competing hotkey paths.

### Acceptance criteria

- There is exactly one monster-manager window implementation; no empty placeholder window class remains.
- Ctrl+Shift+M / `_open_monster_manager()` opens the fully-featured monster manager (table, search, add/edit/delete, templates) with no regression versus current `QuickMonsterEditor` behavior.
- `MonsterManagerController` still owns open/focus/dedup lifecycle; the window class itself does not manage its own singleton state.
- All existing `test_monster_editor_*` tests pass against the final module path.
- No leftover dead file (`monster_manager_win.py` or `quick_monster_editor.py`, whichever loses) unless proven unused and explicitly removed.

### Validation checklist

- Open, close, and reopen the monster manager repeatedly via hotkey and via `_open_monster_manager()`; confirm no duplicate windows and no stale `app.monster_manager_win` reference after close.
- Add, edit, and delete a monster; confirm data persists via `MonsterLibraryService`/database as before.
- Run `py -m pytest tests/unit/ui -k monster_editor -v`.
- Run `py .\app_gui.py` and manually confirm the hotkey opens the real UI, not a blank window.

### Risk to avoid

Do not attempt this migration inside the same session as an unrelated fix; `QuickMonsterEditor` is large (~2000 lines) and this must be its own reviewable, revertible change. Do not delete `quick_monster_editor.py` or `monster_manager_win.py` until the chosen target class is fully working and validated end-to-end.

### Sequencing

Run this after Sprint 4's S4C (skill manager decoupling) session has completed, since S4C also touches modal window patterns in the same area and should land first to avoid overlapping edits.

---

## Sprint 4 follow-up — S4E: Split real skill editing UI out of LibraryManagerWindow into SkillManagerWin

### Context

S4C (merged via PR #102) extracted `SkillManagerController` and `SkillRuntimeService`, but `ui/windows/skill_manager_win.py` was left as the exact same kind of empty placeholder `Toplevel` that S4B left for monsters: `_build_ui()` only creates an unused `Frame` (30 lines total, no widgets). Discovered on 2026-08-28 as the same live-regression pattern as S4D: Ctrl+K and `_open_skill_manager()` route through `SkillManagerController.open_window()`, which opens the empty `SkillManagerWin` shell, so users see a blank window instead of skill-management functionality.

Unlike Monster Manager, there is no standalone equivalent to `QuickMonsterEditor` for skills. The only surviving real skill-editing UI is the "Skills" tab (`_build_skill_tab`) and `SkillDialog` embedded inside the large, shared `ui/windows/library_manager.py` (`LibraryManagerWindow`, 4600+ lines), which also owns Monster and Timing Calculator tabs and requires a non-trivial constructor (`parent, hunt_cfg, monsters, skills, lang, on_close_callback`) wired today only by `LibraryManagerController.open_library_manager()`. A simple "swap the constructor" hotfix like S4D's is not directly available here, which is why this is its own sprint rather than a one-line patch.

### Objective

Make `SkillManagerWin` (or a properly extracted standalone skill editor module) the real, working skill-management view reachable via Ctrl+K / `_open_skill_manager()`, without duplicating or forking the skill-editing logic that still needs to keep working inside `LibraryManagerWindow`'s Skills tab (if that tab is kept) or by retiring that tab in favor of the new standalone window (if it is not).

### Files in scope

- `ui/windows/skill_manager_win.py`
- `ui/windows/library_manager.py` (Skills tab / `SkillDialog` only; do not touch Monster tab or Timing Calculator tab logic)
- `ui/controllers/skill_manager_controller.py`
- `lib/features/skills/skill_runtime_service.py`
- `lib/features/skills/skill_repo.py`
- `tests/unit/ui/test_monster_edit_dialog_flow.py` and any skill-dialog-focused tests (search first to confirm exact file names)

### Planned approach

1. Decide the target shape first (do not start moving code before this is settled) and state the choice explicitly before editing:
   - Option A: Extract `SkillDialog` + the Skills-tab table/list/add/edit/delete logic out of `library_manager.py` into `skill_manager_win.py` as a real, standalone `SkillManagerWin`, backed by `SkillRuntimeService`/`skill_repo.py` directly (mirrors the eventual Monster Manager target shape from S4D). Then decide whether the Skills tab inside `LibraryManagerWindow` should be removed (to avoid duplicated skill-editing UI/logic) or kept as a read-only/simplified view.
   - Option B: Keep skill editing inside `LibraryManagerWindow` as the single source of truth, and have `SkillManagerController.open_window()` open `LibraryManagerWindow` (with all required constructor args sourced from `self.root`) instead of the empty `SkillManagerWin`, deleting `skill_manager_win.py` once proven unused. This is the smaller, lower-risk option if a full extraction is not worth the churn right now.
2. Whichever option is chosen, do not create two independent, divergent copies of skill add/edit/delete logic; there must be exactly one place that owns skill CRUD UI after this sprint.
3. Update `SkillManagerController.open_window()`/`on_window_closed()` to construct and clean up whichever window wins, keeping its existing open/focus/dedup lifecycle contract intact.
4. Preserve `skill_service.reload_skills()` and `_refresh_skill_slots_options()` refresh-on-close behavior already implemented in `SkillManagerController.on_window_closed()`.

### Acceptance criteria

- There is exactly one working skill-management UI reachable from Ctrl+K / `_open_skill_manager()`; no empty placeholder window remains.
- No duplicated/divergent skill CRUD logic exists in two places at once after this sprint lands.
- `SkillManagerController` still owns open/focus/dedup lifecycle; the window class itself does not manage its own singleton state.
- Existing skill-related tests pass against the final module path (update imports only, not test assertions/expectations).

### Validation checklist

- Open, close, and reopen the skill manager repeatedly via Ctrl+K and via `_open_skill_manager()`; confirm no duplicate windows and no stale `app.skill_manager_win` reference after close.
- Add, edit, and delete a skill; confirm data persists via `SkillRuntimeService`/`skill_repo.py` as before, and that skill slot dropdowns elsewhere in the app refresh correctly after close.
- Run the relevant skill-dialog/skill-editor tests (find exact file names via repository search first).
- Run `py .\app_gui.py` and manually confirm Ctrl+K opens the real UI, not a blank window.

### Risk to avoid

Do not attempt this migration inside the same session as an unrelated fix; deciding between Option A (full extraction) and Option B (redirect to `LibraryManagerWindow`) up front is required before any code moves, to avoid ending up with two half-finished skill editors. Do not delete `library_manager.py`'s Skills tab or `skill_manager_win.py` until the chosen target is fully working and validated end-to-end.

### Sequencing

Run this after S4D (Monster Manager migration) has completed and merged, since both sessions touch the Sprint 4 modal-window pattern and establishing the Monster Manager target shape first gives S4E a proven template to follow or deliberately diverge from.

---

## Sprint 5 — Final consolidation and architectural cleanup

### Objective

Remove the final leftover responsibilities from the root app and establish a stable architecture boundary.

### Files in scope

- `app_gui.py`
- `ui/controllers/*.py`
- `lib/features/hunt/*.py`
- `ui/windows/*.py`
- any remaining root-level helper methods still referencing app state

### Tasks

- remove remaining root-level app orchestration methods
- ensure each module does one job: view, controller, service, or data access
- delete dead compatibility shims once migration is complete
- reduce `self.*` state to the minimum required for actual Tk widgets

### Acceptance criteria

- `app_gui.py` is a thin composition root
- root app state is small and explicit
- hotkeys, window selection, overlay, and hunt logic are all in dedicated modules
- launch and close smoke tests remain green

### Validation checklist

- full targeted smoke suite passes
- code review confirms no app root lifecycle logic remains
- custom docs note the new boundaries for future contributors

---

## 5. Exact file-by-file migration map

### App shell and bootstrap

- Keep: `app_gui.py`
- Add: `ui/controllers/app_lifecycle_controller.py`
- Add: `ui/controllers/app_window_controller.py`
- Add: `ui/controllers/app_state_controller.py`

### Hunt orchestration and config

- Keep: `lib/features/hunt/hunt_runner.py`
- Keep: `lib/features/hunt/hunt_config.py`
- Add: `lib/features/hunt/hunt_orchestrator.py`
- Add: `lib/features/hunt/window_selection_service.py`
- Add: `lib/features/hunt/config_migrator.py`
- Add: `lib/features/hunt/config_validator.py`

### UI controller extraction

- Keep: `ui/controllers/app_runtime_bridge.py` as compatibility layer temporarily
- Add: `ui/controllers/hotkey_controller.py`
- Add: `ui/controllers/overlay_controller.py`
- Add: `ui/controllers/window_tracker_controller.py`
- Add: `ui/controllers/library_manager_controller.py`
- Add: `ui/controllers/monster_manager_controller.py`
- Add: `ui/controllers/skill_manager_controller.py`

### Runtime services

- Add: `lib/features/skills/skill_runtime_service.py`
- Add: `lib/features/monsters/monster_library_service.py`

## 6. Test plan by sprint

### Required baseline smoke checks for every sprint

1. `App()` instantiation
2. `mainloop()` and close path execution
3. duplicate-instance lock behavior
4. target window selection and bounds validation
5. minimal app startup test with no crash
6. repeated hotkey or modal actions do not duplicate windows

### Recommended targeted tests

- tests for config migration compatibility
- tests for `hunt_area` normalization and malformed-value recovery
- tests for duplicate-window prevention when reopen actions fire repeatedly
- tests for hotkey registration toggle behavior

## 7. Suggested PR limits

Keep each PR small enough for fast review:

- Sprint 1: 1–2 files + new controller modules
- Sprint 2: hunt/config pair only
- Sprint 3: hotkey + overlay + tracker only
- Sprint 4: monster/skill/library only
- Sprint 5: final cleanup and dead-shim removal

## 8. Definition of done for the architecture cleanup

The architecture cleanup is complete when:

- `app_gui.py` is reduced to UI composition and bootstrap only
- no root-level business logic lives on `self` for hunt, hotkeys, overlay, or library lifecycle
- window ownership and modal lifecycle are centralized behind controllers/services
- config normalization is centralized and migration-safe
- all smoke tests remain green after every PR

## 9. Recommended next action

Proceed with Sprint 1 first, because it is the safest and most surgical change set. The goal is not to refactor everything at once, but to split the root app into just enough controller boundaries to stop the app from re-growing into a god class again.
