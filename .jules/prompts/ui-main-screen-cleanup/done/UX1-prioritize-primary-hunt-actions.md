# UX1 - Ưu Tiên Các Hành Động Hunt Chính Trên Màn Hình Chính

Paste `00-global-rules.md` before this prompt.

```text
Implement the first UI refinements for the main screen based on docs/UX_ANALYSIS_AND_INTERFACE_REDESIGN.md.

Goal:
Improve the main screen so the most-used actions are visually dominant and easy to reach, without changing the underlying hunt logic or config model.

Timebox and scope split:
- Maximum 30 minutes; target implementation time is 25 minutes, leaving time for validation.
- This session owns only the existing Quick Action Bar controls.
- Do not add the new bounds readiness widget in this session; that is UX1B in SESSION_WORKLOAD_AND_PRIORITY.md.

Files in scope:
- app_gui.py
- ui/tabs/hunt_tab.py
- ui/tabs/setup_tab.py
- focused tests only if needed

Primary UX objective:
Re-prioritize the main screen around the frequent workflow:
1. select target window
2. refresh window list
3. start hunt
4. stop hunt
5. review current monster rotation and target situation
6. confirm that the target window and its bounds are valid
7. open quick managers when needed

Design intent:
The main screen should read as a command center for the hunt workflow, not as a generic settings dashboard. Primary actions must be visually stronger than secondary config.

Layout contract for this session:
- Work only in Vùng A: Quick Action Bar at `x=0, y=56`, `1920 x 80 px` on the `1920x1080` baseline.
- Use `32 px` horizontal padding and `12 px` gaps between controls.
- Keep Window selector `420 x 36 px`, Refresh `44 x 36 px`, Bounds state at least `260 x 36 px`, and Start/Stop `160 x 44 px`.
- Start/Stop must not shrink below `140 x 40 px`; the bounds state must remain readable and visible.
- Use `UIStyle.BTN_PRIMARY_BG` for Start while idle, `UIStyle.BTN_DANGER_BG` for Stop while running, and `UIStyle.BTN_INFO_BG` for Refresh.
- Render every visible label through `self._t(...)`. Reuse existing global keys where available; defer new bounds-status copy to UX1B.

Boundaries:
- do not rewrite the whole UI system
- do not remove behavior or config fields
- keep hotkeys and config compatibility intact
- prefer explicit layout changes over hidden complexity
- if advanced settings are moved, keep an obvious access path
- keep the change narrow and reviewable

Tasks:
- make the top action bar clearly reflect the primary hunt workflow
- ensure Start / Stop / Window selection / Refresh are the most visible controls
- do not edit Monster Rotation, Active Target/Status, Sidebar, Bottom Logs, or helper tabs
- reserve the documented bounds-state space without changing the bounds data flow
- preserve all current non-primary functionality; only rearrange emphasis and grouping
- if there is a crowded layout, prioritize hierarchy rather than adding new controls

Acceptance criteria:
- the primary hunt controls are visually grouped and prioritized above secondary settings
- the main screen reads as a command center for hunt rather than a generic settings dashboard
- existing behavior and hotkeys remain intact
- no config shape or current runtime flow is broken
- the user can reach the main hunt loop without scanning unrelated controls
- no current target-window/bounds feedback is removed or made less visible

Session boundary gate:
- valid selected window: Refresh and the displayed bounds state remain correct
- missing selected window: UI clearly directs the user to select or refresh a window
- minimized or invalid window: UI prevents ambiguity and directs the user to restore or reselect
- report results for all three cases before ending the session

Validation:
- run the narrow smoke checks for app startup and UI importability
- run `py -m pytest tests/test_ui_imports.py` if still relevant
- if a manual GUI check is needed, document the exact steps in the final response
- confirm that the app still opens and the key hunt controls remain usable
- manually confirm: select a valid game window, refresh it, then verify the visible bounds state updates; verify a missing/minimized window gives a clear recovery action
- at `1920x1080`, manually confirm the Quick Action Bar remains `80 px` high and no primary control wraps, clips, or moves into a secondary zone
- manually confirm `vi → en → vi`: Window selector, Refresh, Start and Stop labels/tooltips rebuild correctly without losing selected-window or hunt state
```
