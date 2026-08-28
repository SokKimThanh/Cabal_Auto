# S4E - Split Real Skill Editing UI Out Of LibraryManagerWindow Into SkillManagerWin

Paste `00-global-rules.md` first, then this prompt.

```text
Implement the Sprint 4 follow-up (S4E) from .jules/architecture-sprint-roadmap.md.

Context:
S4C (merged via PR #102) extracted SkillManagerController and SkillRuntimeService, but
ui/windows/skill_manager_win.py was left as the exact same kind of empty placeholder
Toplevel that S4B left for monsters: _build_ui() only creates an unused Frame (30 lines
total, no widgets). Discovered on 2026-08-28 as the same live-regression pattern as S4D:
Ctrl+K and _open_skill_manager() route through SkillManagerController.open_window(),
which opens the empty SkillManagerWin shell, so users see a blank window instead of
skill-management functionality.

Unlike Monster Manager, there is no standalone equivalent to QuickMonsterEditor for
skills. The only surviving real skill-editing UI is the "Skills" tab (_build_skill_tab)
and SkillDialog embedded inside the large, shared ui/windows/library_manager.py
(LibraryManagerWindow, 4600+ lines), which also owns Monster and Timing Calculator tabs
and requires a non-trivial constructor (parent, hunt_cfg, monsters, skills, lang,
on_close_callback) wired today only by LibraryManagerController.open_library_manager().
A simple "swap the constructor" hotfix like S4D's is not directly available here, which
is why this is its own sprint rather than a one-line patch.

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
  Option A: Extract SkillDialog + the Skills-tab table/list/add/edit/delete logic out of
  library_manager.py into skill_manager_win.py as a real, standalone SkillManagerWin,
  backed by SkillRuntimeService/skill_repo.py directly. Then decide whether the Skills
  tab inside LibraryManagerWindow should be removed or kept as a read-only/simplified view.
  Option B: Keep skill editing inside LibraryManagerWindow as the single source of truth,
  and have SkillManagerController.open_window() open LibraryManagerWindow (with all
  required constructor args sourced from self.root) instead of the empty SkillManagerWin,
  deleting skill_manager_win.py once proven unused. This is the smaller, lower-risk option
  if a full extraction is not worth the churn right now.
- Whichever option is chosen, do not end up with two independent, divergent copies of
  skill add/edit/delete logic; there must be exactly one place that owns skill CRUD UI
  after this sprint.
- SkillManagerController must keep owning open/focus/dedup lifecycle; the window class
  itself must not manage its own singleton state.
- Preserve skill_service.reload_skills() and _refresh_skill_slots_options()
  refresh-on-close behavior already implemented in SkillManagerController.on_window_closed().
- Do not delete library_manager.py's Skills tab or skill_manager_win.py until the chosen
  target is fully working and validated end-to-end.
- Do not combine this migration with an unrelated fix in the same session.

Acceptance criteria:
- There is exactly one working skill-management UI reachable from Ctrl+K /
  _open_skill_manager(); no empty placeholder window remains.
- No duplicated/divergent skill CRUD logic exists in two places at once after this sprint.
- Existing skill-related tests pass against the final module path (update imports only,
  not test assertions/expectations).

Validation:
- Open, close, and reopen the skill manager repeatedly via Ctrl+K and via
  _open_skill_manager(); confirm no duplicate windows and no stale
  app.skill_manager_win reference after close.
- Add, edit, and delete a skill; confirm data persists via
  SkillRuntimeService/skill_repo.py as before, and that skill slot dropdowns elsewhere in
  the app refresh correctly after close.
- Run the relevant skill-dialog/skill-editor tests (find exact file names via repository
  search first).
- Run `py .\app_gui.py` and manually confirm Ctrl+K opens the real UI, not a blank window.
```
