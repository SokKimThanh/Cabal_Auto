# Architecture Cleanup Jules Prompt Copybook

Split one-session prompt files are available in `.jules/prompts/architecture-cleanup/`. Use those files when launching Jules sessions to avoid overloading one session with the full roadmap.

Use these prompts as separate Jules sessions. Each prompt is intentionally scoped to one reviewable responsibility boundary. Do not combine prompts unless a previous session explicitly finished cleanly and the next prompt says it can start after that result.

## Global Rules For Every Jules Session

Paste this block at the top of every prompt if Jules does not already have it in context:

```text
You are working in the Cabal_Auto repository. Follow .jules/architecture-sprint-roadmap.md as the source of truth.

Hard constraints:
- Keep the change small, reversible, and scoped to the files named in this prompt.
- Preserve current behavior and config compatibility.
- Do not move logic back into app_gui.py after extracting it.
- Do not perform broad rewrites, style-only refactors, or unrelated cleanup.
- Do not commit changes.
- Do not delete code unless the prompt explicitly asks for deletion and repository search proves the code is unused.
- Do not remove compatibility paths, callbacks, imports, or public attributes just because they look redundant; first prove all callers have moved.
- Do not overwrite or revert user changes outside this session's scope.
- Prefer moving code intact before simplifying it; behavior-preserving extraction comes before cleanup.
- Prefer controller/service boundaries over large helper files.
- Add or update focused tests when practical.
- Run the narrowest useful validation command before finishing.

Before editing:
- Identify the current controlling code path.
- State one local hypothesis about the extraction.
- State the cheapest validation that can falsify it.
- Identify at least 3 boundary/edge cases relevant to this session.

Boundary checks:
- Cover empty, missing, malformed, legacy, repeated-call, cleanup/dispose, and startup/shutdown boundaries when relevant.
- Add or run an automated test for the riskiest boundary case when practical.
- If a boundary case requires manual GUI confirmation, document the exact manual check in the final response.
- Treat compatibility behavior as a boundary: legacy config shapes, existing callbacks, existing public attributes, and repeated open/close flows must keep working unless the prompt explicitly says otherwise.

Code preservation checks:
- Before deleting or heavily rewriting a block, search for references and document why deletion is safe.
- Prefer extraction by moving existing logic into the new controller/service with minimal edits, then validate, then simplify only if still inside scope.
- Keep fallback paths until the replacement path is validated and all active callers are updated.
- Review the diff before final response and call out any removed code intentionally.

Before final response:
- Summarize changed files.
- List validation commands and results.
- List boundary/edge cases checked, including any that remain manual-only.
- List any code removed or replaced and why it was safe.
- Call out any residual risks or follow-up tasks.
```

## Execution Waves

Wave 0 can run first and is read-only. Wave 1 must run after Wave 0. Later waves can run in parallel only when their dependency note is satisfied.

| Wave | Sessions | Parallel? | Dependency |
| --- | --- | --- | --- |
| 0 | P0 | No | None |
| 1 | S1A, S1B, S1C | Mostly sequential | P0 complete; run S1A first, then S1B/S1C can split if S1A leaves clean boundaries |
| 2 | S2A, S2B, S2C, S2D | Partial parallel | Sprint 1 merged/clean |
| 3 | S3A, S3B, S3C, S3D | Parallel after S3A interface pass | Sprint 1 merged/clean; S2 not required unless touching hunt window selection |
| 4 | S4A, S4B, S4C | Parallel with care | Sprint 1 merged/clean; avoid touching the same modal registry code simultaneously |
| 4b | S4D | No | S4C merged/clean; migrates QuickMonsterEditor UI into MonsterManagerWin, touches the same modal window area as S4C so must land after it |
| 4c | S4E | No | S4D merged/clean; splits real skill editing UI out of LibraryManagerWindow into SkillManagerWin, same modal window area as S4D so must land after it |
| 5 | S5A, S5B | Sequential | All prior sprint changes merged/clean |

## Wave 0 - Baseline Mapping

### P0 - Baseline Architecture And Smoke Inventory

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
- Existing tests or smoke commands that validate app startup, close, hotkeys, overlay, hunt config, and modal reuse.
- A suggested order for Sprint 1 sessions if app_gui.py has hidden coupling.

Do not edit application code in this session. Only create or update .jules/architecture-cleanup-baseline.md.
Run no broad test suite unless it is already documented as cheap. If no cheap command exists, say so.
```

## Wave 1 - Sprint 1 App Shell And Lifecycle

### S1A - Extract App State Controller

```text
Implement the Sprint 1 app state extraction from .jules/architecture-sprint-roadmap.md.

Goal:
Move bound state management and non-widget root state bookkeeping out of app_gui.py into ui/controllers/app_state_controller.py.

Files in scope:
- app_gui.py
- ui/controllers/app_state_controller.py
- ui/controllers/__init__.py
- focused tests only if needed

Boundaries:
- app_gui.py may keep actual Tk widgets and composition references.
- app_state_controller.py should own state initialization/access patterns that are not themselves Tk widget construction.
- Preserve existing public attribute names on App when needed for compatibility, but route new state ownership through the controller where practical.
- Do not move window open/focus lifecycle in this session.
- Do not move close/dispose behavior in this session.

Acceptance criteria:
- App can instantiate with the same externally visible behavior.
- app_gui.py has less direct state setup logic.
- No config shape or startup behavior changes.

Validation:
- Run the narrowest existing App instantiation or GUI smoke test.
- If no narrow test exists, run `py -m pytest tests/test_ui_imports.py` and a syntax/import check for touched files.
- Also run `py .\app_gui.py` only if it is already safe/non-blocking in this repo.
```

### S1B - Extract App Window Controller

```text
Implement the Sprint 1 window ownership extraction from .jules/architecture-sprint-roadmap.md.

Goal:
Move dialog/window ownership tracking and target window selection lifecycle out of app_gui.py into ui/controllers/app_window_controller.py.

Files in scope:
- app_gui.py
- ui/controllers/app_window_controller.py
- ui/controllers/app_runtime_bridge.py only if compatibility forwarding is required
- ui/controllers/__init__.py
- focused tests only if needed

Boundaries:
- Keep actual UI view classes unchanged unless a tiny call-site adjustment is required.
- app_gui.py should delegate window open/focus/reuse/selection lifecycle to AppWindowController.
- Do not change hunt behavior, overlay behavior, or hotkey behavior beyond adapting calls to the controller.
- Do not introduce duplicate window registries.

Acceptance criteria:
- Repeated window open actions reuse/focus existing windows where current behavior expects that.
- Target window selection still starts/stops without startup regressions.
- app_gui.py is no longer the direct owner of generic window lifecycle bookkeeping.

Validation:
- Run focused tests for UI imports/window behavior if present.
- Run `py -m pytest tests/test_ui_imports.py` at minimum if no narrower test exists.
- Document any manual GUI path that still needs human confirmation.
```

### S1C - Extract App Lifecycle Controller

```text
Implement the Sprint 1 lifecycle extraction from .jules/architecture-sprint-roadmap.md.

Goal:
Move startup lifecycle coordination and close/dispose orchestration out of app_gui.py into ui/controllers/app_lifecycle_controller.py.

Files in scope:
- app_gui.py
- ui/controllers/app_lifecycle_controller.py
- ui/controllers/app_runtime_bridge.py only if compatibility forwarding is required
- ui/controllers/__init__.py
- focused tests only if needed

Boundaries:
- App.__init__ should become bootstrap + composition, not a new large helper inside app_gui.py.
- App.on_close() should delegate to AppLifecycleController.
- Preserve duplicate instance lock behavior and existing shutdown cleanup ordering.
- Do not change hunt loop internals, hotkey internals, or overlay internals in this session.

Acceptance criteria:
- App startup path remains intact.
- on_close() completes without exceptions.
- Cleanup order remains equivalent to current behavior.
- app_gui.py is thinner and clearly delegates lifecycle work.

Validation:
- Run the narrowest App startup/close smoke test available.
- Run `py -m pytest tests/test_ui_imports.py` if no narrower test exists.
- Run any existing duplicate-instance lock test if P0 found one.
```

## Wave 2 - Sprint 2 Hunt Runtime And Config

### S2A - Centralize Hunt Config Migration

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

### S2B - Add Hunt Config Validator

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

### S2C - Extract Hunt Orchestrator Runtime Boundary

```text
Implement the Sprint 2 hunt orchestration extraction from .jules/architecture-sprint-roadmap.md.

Goal:
Create lib/features/hunt/hunt_orchestrator.py so hunt loop orchestration and scan state transitions are not controlled directly by app_gui.py.

Files in scope:
- lib/features/hunt/hunt_runner.py
- lib/features/hunt/scan_controller.py
- lib/features/hunt/scanner.py only if a narrow adapter is required
- lib/features/hunt/hunt_orchestrator.py
- app_gui.py only for delegating to the orchestrator
- focused tests for start/stop behavior

Boundaries:
- hunt_runner.py should receive explicit runtime config instead of reading UI state directly.
- The orchestrator may adapt UI/controller callbacks, but should not own Tk widgets.
- Do not change monster detection/gameplay behavior beyond dependency injection and delegation.

Acceptance criteria:
- Start/stop scan behavior is preserved.
- Runtime config is passed explicitly.
- app_gui.py no longer owns hunt loop orchestration.

Validation:
- Run focused scan controller/hunt tests.
- Run `py -m pytest tests/test_scan_controller.py` if applicable.
```

### S2D - Extract Window Selection Service

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

## Wave 3 - Sprint 3 Hotkey, Overlay, Window Tracker

### S3A - Define Controller Interfaces For Runtime Bridge

```text
Prepare Sprint 3 by tightening ui/controllers/app_runtime_bridge.py into a compatibility layer.

Goal:
Define the small interfaces app_runtime_bridge.py should call for hotkeys, overlay lifecycle, and window tracking without implementing all extracted behavior in this session.

Files in scope:
- ui/controllers/app_runtime_bridge.py
- app_gui.py only if needed to pass controller instances
- ui/controllers/__init__.py
- tests only if a small bridge test exists or is easy to add

Boundaries:
- The bridge should forward/delegate; it should not become the permanent home for hotkey, overlay, or tracking logic.
- Do not move substantial overlay/window tracker code yet.
- Keep runtime behavior equivalent.

Acceptance criteria:
- Later sessions can implement HotkeyController, OverlayController, and WindowTrackerController independently.
- Existing bridge callers still work.

Validation:
- Run focused import/bridge tests.
- Run `py -m pytest tests/test_ui_imports.py` if no narrower test exists.
```

### S3B - Extract Hotkey Controller

```text
Implement the Sprint 3 hotkey extraction from .jules/architecture-sprint-roadmap.md.

Goal:
Create ui/controllers/hotkey_controller.py to own global hotkey registration, enable/disable behavior, and callback dispatch.

Files in scope:
- ui/controllers/hotkey_controller.py
- lib/system/hotkey_manager.py
- ui/controllers/app_runtime_bridge.py only for forwarding
- app_gui.py only for composition/delegation
- focused tests for hotkey registration/toggle behavior

Boundaries:
- Do not change overlay or window tracker internals except callback wiring.
- HotkeyController should expose clear methods for registration, teardown, and action dispatch.
- Preserve existing hotkey names and behavior.

Acceptance criteria:
- Hotkey actions are registered through HotkeyController, not app instance code.
- Hotkeys can enable/disable cleanly.
- Cleanup unregisters/disposes hotkeys without exceptions.

Validation:
- Run focused hotkey tests if present.
- If no tests exist, add small unit tests around controller behavior using fakes/mocks where practical.
```

### S3C - Extract Overlay Controller

```text
Implement the Sprint 3 overlay extraction from .jules/architecture-sprint-roadmap.md.

Goal:
Move overlay start/stop lifecycle decisions into ui/controllers/overlay_controller.py.

Files in scope:
- ui/controllers/overlay_controller.py
- ui/utils/overlay_controller.py
- ui/utils/overlay_settings.py
- ui/controllers/app_runtime_bridge.py only for forwarding
- app_gui.py only for composition/delegation
- focused tests for overlay lifecycle if practical

Boundaries:
- Keep ui/utils/overlay_controller.py as the low-level overlay utility if it already serves that role.
- The new controller should coordinate lifecycle and settings, not duplicate rendering internals.
- Do not change hotkey registration except where it calls overlay start/stop methods.

Acceptance criteria:
- Overlay can start/stop repeatedly without stale handles.
- Overlay lifecycle is independent from direct app root methods.
- app_runtime_bridge.py remains a compatibility layer.

Validation:
- Run focused overlay/settings tests if present.
- If no automated GUI-safe test exists, run import/syntax validation and document manual smoke path.
```

### S3D - Extract Window Tracker Controller

```text
Implement the Sprint 3 window tracker extraction from .jules/architecture-sprint-roadmap.md.

Goal:
Create ui/controllers/window_tracker_controller.py for window detection, refresh loops, duplicate/flood control, and tracker lifecycle.

Files in scope:
- ui/controllers/window_tracker_controller.py
- ui/utils/window_tracker.py
- ui/controllers/app_runtime_bridge.py only for forwarding
- app_gui.py only for composition/delegation
- focused tests for tracker behavior if practical

Boundaries:
- Keep platform-specific detection details in ui/utils/window_tracker.py if they already live there.
- Controller owns lifecycle, refresh scheduling, and duplicate/flood-control decisions.
- Do not change hunt config migration in this session.

Acceptance criteria:
- Tracking logic is observable and unit-testable.
- Repeated trigger paths do not open duplicate windows.
- App root delegates tracker lifecycle to the controller.

Validation:
- Run focused window tracker tests if present.
- Add a small fake-based test for duplicate prevention if practical.
```

## Wave 4 - Sprint 4 Monster, Skill, Library Management

### S4A - Extract Library Manager Controller

```text
Implement the Sprint 4 library manager lifecycle extraction from .jules/architecture-sprint-roadmap.md.

Goal:
Create ui/controllers/library_manager_controller.py to own library manager open/focus/reuse behavior and callback dispatch.

Files in scope:
- ui/controllers/library_manager_controller.py
- ui/windows/library_manager.py only for tiny callback/interface adjustments
- ui/controllers/app_runtime_bridge.py only for forwarding
- app_gui.py only for composition/delegation
- focused tests for duplicate window prevention if practical

Boundaries:
- Do not make library_manager.py the sole lifecycle source of truth.
- Preserve existing UI behavior and callbacks.
- Do not refactor monster/skill repos in this session except callback wiring.

Acceptance criteria:
- Repeated library manager actions reuse/focus the existing window.
- Closing and reopening does not leave stale handles.
- App no longer owns library modal lifecycle directly.

Validation:
- Run focused UI import/window tests.
- Add fake-based lifecycle tests if practical.
```

### S4B - Extract Monster Manager Controller And Service

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

### S4C - Extract Skill Manager Controller And Runtime Service

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

### S4D - Migrate QuickMonsterEditor UI Into MonsterManagerWin

```text
Implement the Sprint 4 follow-up (S4D) from .jules/architecture-sprint-roadmap.md.

Context:
S4B extracted MonsterManagerController (lifecycle) and MonsterLibraryService (data), but
ui/windows/monster_manager_win.py was left as an empty placeholder Toplevel - its
_build_ui() only creates an unused Frame. All real monster-management UI (data table,
search/filter, add/edit/delete, template manager, column settings, ~2000 lines) still
lives in the separate ui/windows/quick_monster_editor.py (QuickMonsterEditor). This caused
a live regression on 2026-08-27 where the Ctrl+Shift+M hotkey opened a blank window; a
temporary hotfix repointed MonsterManagerController.open_window() to construct
QuickMonsterEditor directly. This session is the real, permanent fix.

Goal:
Make there be exactly one monster-manager window implementation, wired correctly through
MonsterManagerController, with no empty placeholder class left behind.

Files in scope:
- ui/windows/monster_manager_win.py
- ui/windows/quick_monster_editor.py
- ui/controllers/monster_manager_controller.py
- lib/features/monsters/monster_library_service.py
- lib/hotkey/monster_editor_handler.py (confirm dead vs. still referenced; do not delete without proof)
- tests/unit/ui/test_monster_editor_*.py

Boundaries:
- Decide the target shape first, before moving any code: either (a) absorb
  QuickMonsterEditor's implementation into MonsterManagerWin and delete
  quick_monster_editor.py, or (b) keep QuickMonsterEditor as the real class and delete the
  empty MonsterManagerWin shell, updating the controller and all imports accordingly.
  State which option you are taking and why before editing.
- Preserve every behavior listed in quick_monster_editor.py's module docstring.
- MonsterManagerController must keep owning open/focus/dedup lifecycle; the window class
  itself must not manage its own module-level singleton state.
- Do not delete quick_monster_editor.py or monster_manager_win.py (whichever loses) until
  the chosen target class is fully working and validated end-to-end.

Acceptance criteria:
- Exactly one monster-manager window implementation remains; no empty placeholder window class.
- Ctrl+Shift+M / _open_monster_manager() opens the fully-featured monster manager with no
  regression versus current QuickMonsterEditor behavior.
- All existing test_monster_editor_* tests pass against the final module path.

Validation:
- Open, close, and reopen the monster manager repeatedly via hotkey and via
  _open_monster_manager(); confirm no duplicate windows and no stale reference after close.
- Run `py -m pytest tests/unit/ui -k monster_editor -v`.
- Run `py .\app_gui.py` and manually confirm the hotkey opens the real UI, not a blank window.
```

### S4E - Split Real Skill Editing UI Out Of LibraryManagerWindow Into SkillManagerWin

```text
Implement the Sprint 4 follow-up (S4E) from .jules/architecture-sprint-roadmap.md.

Context:
S4C extracted SkillManagerController and SkillRuntimeService, but
ui/windows/skill_manager_win.py was left as the same kind of empty placeholder Toplevel
that S4B left for monsters - _build_ui() only creates an unused Frame. Ctrl+K and
_open_skill_manager() route through SkillManagerController.open_window(), which opens
this empty shell, so users see a blank window. Unlike Monster Manager, there is no
standalone equivalent to QuickMonsterEditor for skills - the only real skill-editing UI
is the "Skills" tab (_build_skill_tab) and SkillDialog embedded inside the large, shared
ui/windows/library_manager.py (LibraryManagerWindow), which also owns Monster and Timing
Calculator tabs.

Goal:
Make SkillManagerWin (or a properly extracted standalone skill editor module) the real,
working skill-management view reachable via Ctrl+K / _open_skill_manager(), without
duplicating or forking the skill-editing logic.

Files in scope:
- ui/windows/skill_manager_win.py
- ui/windows/library_manager.py (Skills tab / SkillDialog only; do not touch Monster tab
  or Timing Calculator tab logic)
- ui/controllers/skill_manager_controller.py
- lib/features/skills/skill_runtime_service.py
- lib/features/skills/skill_repo.py
- skill-dialog-focused tests (search first to confirm exact file names)

Boundaries:
- Decide the target shape first, before editing, and state the choice explicitly:
  Option A: Extract SkillDialog + the Skills-tab logic out of library_manager.py into
  skill_manager_win.py as a real, standalone SkillManagerWin, backed by
  SkillRuntimeService/skill_repo.py directly, then decide whether the Skills tab inside
  LibraryManagerWindow should be removed or kept as a read-only/simplified view.
  Option B: Keep skill editing inside LibraryManagerWindow as the single source of truth,
  and have SkillManagerController.open_window() open LibraryManagerWindow instead of the
  empty SkillManagerWin, deleting skill_manager_win.py once proven unused.
- Whichever option is chosen, do not end up with two independent, divergent copies of
  skill add/edit/delete logic.
- SkillManagerController must keep owning open/focus/dedup lifecycle.
- Preserve skill_service.reload_skills() and _refresh_skill_slots_options()
  refresh-on-close behavior already implemented in SkillManagerController.on_window_closed().
- Do not delete library_manager.py's Skills tab or skill_manager_win.py until the chosen
  target is fully working and validated end-to-end.

Acceptance criteria:
- Exactly one working skill-management UI reachable from Ctrl+K / _open_skill_manager();
  no empty placeholder window remains.
- No duplicated/divergent skill CRUD logic exists in two places at once.
- Existing skill-related tests pass against the final module path.

Validation:
- Open, close, and reopen the skill manager repeatedly via Ctrl+K and via
  _open_skill_manager(); confirm no duplicate windows and no stale reference after close.
- Add, edit, and delete a skill; confirm data persists and skill slot dropdowns elsewhere
  in the app refresh correctly after close.
- Run `py .\app_gui.py` and manually confirm Ctrl+K opens the real UI, not a blank window.
```

## Wave 5 - Final Consolidation

### S5A - Remove Dead Compatibility Shims

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

### S5B - Architecture Boundary Documentation And Final Smoke

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

## Suggested Parallel Launch Plan

Use this plan when launching multiple Jules sessions.

1. Start `P0` alone.
2. Start `S1A` alone.
3. After `S1A` is clean, start `S1B` and `S1C` only if they touch different methods. If both need the same `App.__init__` or `on_close()` area, run `S1B` first, then `S1C`.
4. After Sprint 1 is merged cleanly, start `S2A` and `S2B` in parallel only if they agree on migrator/validator API names first. Run `S2C` after their APIs stabilize. Run `S2D` after `S2B`.
5. Start `S3A` before other Sprint 3 sessions. After it lands, `S3B`, `S3C`, and `S3D` can run in parallel because they own different controller files.
6. Start `S4A`, `S4B`, and `S4C` in parallel only if app-level modal registry code has already been isolated by Sprint 1. If they conflict in app_gui.py, land `S4A` first because it establishes the modal lifecycle pattern.
7. Run `S5A`, then `S5B` sequentially.

## Merge Discipline For Parallel Sessions

After each Jules session returns a patch:

```text
Review only for this session's stated acceptance criteria. Reject broad unrelated cleanup. Before merging, run the validation commands from the session and inspect for conflicts in app_gui.py, ui/controllers/app_runtime_bridge.py, and any shared controller __init__.py exports. Check the diff specifically for accidental deletion, removed callbacks, removed imports with active callers, removed public App attributes, and lost compatibility fallbacks.
```

When two parallel sessions both touched the same file:

```text
Resolve by keeping the smallest public controller/service API. Do not duplicate app root forwarding methods. If both sessions added similar helper logic, move the shared logic into the controller/service named by the roadmap, not into app_gui.py or app_runtime_bridge.py.
```

When a session removes code:

```text
Require evidence in the session summary: reference search result, replaced call path, validation command, and boundary case covered. If the evidence is missing, keep the old compatibility path and ask for a smaller follow-up cleanup prompt.
```
