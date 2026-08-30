# UX4 - Tập Trung Vào Trạng Thái Hunt và Cảnh Báo

Paste `00-global-rules.md` before this prompt.

```text
Improve the focus on runtime status, warnings, and the active hunt state on the main screen.

Goal:
Make the current hunt state, selected target, and warning information immediately understandable in Active Target & Status without reading logs or hunting through tabs.

Timebox and scope split:
- Timebox: 25-30 minutes. At minute 25, run validation; use remaining time only for direct repair or the rollback/abort rule.
- This session owns status presentation only.
- Do not create, move, persist, or reformat Bottom Logs; that is UX4B in SESSION_WORKLOAD_AND_PRIORITY.md.
- Do not change hunt runtime logic or invent new runtime states.

Files in scope:
- app_gui.py
- ui/tabs/hunt_tab.py
- ui/tabs/setup_tab.py
- focused tests only if needed

Primary UX objective:
Expose the real operating status of the bot in a clean, stable, glanceable form.

Design intent:
The user should understand the app state at a glance: whether it is idle, hunting, warning, or in an error condition. Status must remain visible without forcing the user to inspect logs or secondary panels.

Layout contract for this session:
- Work in Vùng B only.
- Treat the dimensions (Workspace `1640 x 744 px`, primary panels `776 x 552 px`, Quick Skill View `1576 x 120 px`) as target baselines at `1920x1080` with Windows DPI `100%`.
- Use `grid` weights and `minsize` to achieve these proportions. Do not hardcode absolute layout coordinates that break at DPI `125%-150%`.
- Put current, actionable hunt status and blocking bounds warnings in Active Target & Status, not only in logs.
- Use UIStyle semantic colors: ready/running is accent, warning is orange, blocking error is red, and every state includes text plus recovery action.

Tasks:
- make hunt status, target info, and active target state easy to read at a glance
- show target-window and bounds validity as an actionable runtime prerequisite
- add or improve clear indicator hierarchy for active, idle, warning, and error states
- ensure warning and validation messages are visible without burying them in secondary panels
- keep the status system compatible with existing config and runtime states
- if multiple statuses exist, expose only the most actionable ones at the top level
- distinguish no selected window, invalid bounds, minimized window, and invalid target region where existing runtime data permits
- render status, warning, and recovery copy through existing i18n keys/templates; add both `en` and `vi` keys to `GLOBAL_TRANSLATIONS` before adding a new visible state
- do not use catalogue DB availability, class mapping, or skill metadata to decide a hunt/bounds warning or block Start Hunt

Acceptance criteria:
- the user can understand the current state of the hunt in a single glance
- important warnings are not buried in secondary UI regions
- no regression in current status logic or config behavior
- the status area communicates the “next action” if the user needs to intervene
- boundary failures tell the user whether to refresh, reselect, restore, or recapture

Session boundary gate:
- valid bounds: status communicates the window is ready for hunt
- no selected window: status gives an actionable select/refresh instruction
- minimized or unavailable window: status gives an actionable restore/reselect instruction
- invalid target region: status gives an actionable recapture or correction instruction when the runtime exposes that state
- report results for all applicable cases before ending the session

Validation:
- run smoke checks for startup and UI importability
- run `py -m pytest tests/test_ui_imports.py` if still relevant
- if manual UI verification is needed, document the exact check steps
- confirm that status/warning messages remain readable before and after the UI change
- test the visible response for valid bounds, no selected window, and a minimized or unavailable game window
- at `1920x1080`, verify that the two primary panels remain visible together and Quick Skill View remains a lower-priority strip
- verify `vi → en → vi` updates status/warning/recovery copy without changing the underlying hunt/bounds state
```
