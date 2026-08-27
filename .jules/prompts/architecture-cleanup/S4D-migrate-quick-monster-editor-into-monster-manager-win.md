# S4D - Migrate QuickMonsterEditor UI Into MonsterManagerWin

Paste `00-global-rules.md` first, then this prompt.

```text
Implement the Sprint 4 follow-up (S4D) from .jules/architecture-sprint-roadmap.md.

Context:
S4B extracted MonsterManagerController (lifecycle) and MonsterLibraryService (data), but
ui/windows/monster_manager_win.py was left as an empty placeholder Toplevel - its
_build_ui() only creates an unused Frame. All real monster-management UI (data table,
search/filter, add/edit/delete, template manager, column settings, ~2000 lines) still
lives in the separate ui/windows/quick_monster_editor.py (QuickMonsterEditor).

On 2026-08-27 this caused a live regression: the Ctrl+Shift+M hotkey and
_open_monster_manager() were wired to MonsterManagerController.open_window(), which
opened the empty MonsterManagerWin shell instead of QuickMonsterEditor, so users saw a
blank window with no functionality. A temporary hotfix repointed
MonsterManagerController.open_window() to construct QuickMonsterEditor directly (still
going through the controller's existing open/focus/dedup logic). This session is the
real, permanent fix for that gap.

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
- Preserve every behavior listed in quick_monster_editor.py's module docstring (master
  table, search/filter, column visibility, add/edit/delete, template manager tab, display
  settings dialog, dirty-state tracking, database-backed load/save).
- MonsterManagerController must keep owning open/focus/dedup lifecycle; the window class
  itself must not manage its own module-level singleton state.
- Do not delete quick_monster_editor.py or monster_manager_win.py (whichever loses) until
  the chosen target class is fully working and validated end-to-end.
- Do not touch lib/hotkey/monster_editor_handler.py beyond confirming via repository search
  whether it is truly dead code; if it is still referenced anywhere, reconcile it with
  HotkeyController.on_monster_editor() instead of leaving two competing hotkey paths.
- This is a large, reviewable-on-its-own change; do not combine it with unrelated fixes.

Acceptance criteria:
- Exactly one monster-manager window implementation remains; no empty placeholder window class.
- Ctrl+Shift+M / _open_monster_manager() opens the fully-featured monster manager with no
  regression versus current QuickMonsterEditor behavior.
- All existing test_monster_editor_* tests pass against the final module path (update
  imports only, not test assertions/expectations).
- No leftover dead file unless proven unused and explicitly removed.

Validation:
- Open, close, and reopen the monster manager repeatedly via hotkey and via
  _open_monster_manager(); confirm no duplicate windows and no stale
  app.monster_manager_win reference after close.
- Add, edit, and delete a monster; confirm data persists via MonsterLibraryService/database as before.
- Run `py -m pytest tests/unit/ui -k monster_editor -v`.
- Run `py .\app_gui.py` and manually confirm the hotkey opens the real UI, not a blank window.
```
