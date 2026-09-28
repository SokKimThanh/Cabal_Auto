# Sprint 35 - Hunt Window ROI UX Fix

## Objective
Fix the issue where drawing the Region of Interest (ROI) for game capture doesn't automatically bring the selected game window to the front. The issue affected both "Hunt Area" in the Hunt Tab and "System ROIs" in the Setup Tab.

## Scope
- Modify `CaptureHelper.start_region_selection` in `ui/helpers/capture_helper.py` to support an optional `pre_wait_hook`.
- Update `_on_draw_hunt_area` in `ui/panels/monster_target_panel.py` to provide a hook that brings the selected game window to the foreground before screen capture.
- Update `_make_on_draw` in `ui/tabs/setup_tab.py` to provide a hook that brings the selected game window to the foreground before screen capture.

## Definition of Done
- When a user clicks "Set Hunt Area" (Quét vùng săn) or "Vẽ lại" (Redraw) for System ROIs, if a game window is selected, it must automatically be brought to the foreground *before* the screen capture overlay is shown.
- Tests (if any) or manual code inspection confirm that `WindowManager.set_foreground` is successfully triggered via the `pre_wait_hook`.

## Impact Analysis
- UX is significantly improved. Users no longer have to manually switch to the game window before clicking the Draw ROI button.
- Low impact on other functionalities as `pre_wait_hook` defaults to `None`.

## Acceptance Test
1. Select a valid Cabal game window from the dropdown.
2. Minimize or put another window over the game.
3. Go to Hunt Tab -> Click "Set Hunt Area" (Quét vùng săn).
4. Verify the game window pops to the front and the screen is frozen for selection over the game window.
5. Repeat steps for Setup Tab -> System ROI Manager -> "Vẽ lại" (Redraw).

## Risks
- Depending on OS permissions and window states, `set_foreground` may occasionally fail or flash the taskbar icon without popping the window. This is a known OS limitation, but `restore(hwnd)` followed by `set_foreground(hwnd)` mitigates it in most cases.

## Anti-patterns
- Do not implement custom sleep logic in UI components; rely on `CaptureHelper` which already handles window hiding and sleeping gracefully.

## Rollback plan
- Revert changes to `capture_helper.py`, `monster_target_panel.py`, and `setup_tab.py` using standard Git revert on the single commit.

## Technical Debt Handling
- The `WindowManager` calls correctly extract the `hwnd` directly from `hunt_selected` in the application state, maintaining a single source of truth for the active game session.

## Commit Strategy
- Isolate the changes into one logic batch related exclusively to fixing the ROI foreground window issue.

## Implementation Plan
1. Add `pre_wait_hook` parameter to `start_region_selection`.
2. Inject caller's window foreground code via `pre_wait_hook`.
3. Propagate changes to `ui/panels/monster_target_panel.py`.
4. Propagate changes to `ui/tabs/setup_tab.py`.

## Report
Changes executed successfully. Code has been verified via regex and `grep` ensuring exact syntax placement for the hook calls.

## Tech Notes
- Windows API restrictions sometimes block `SetForegroundWindow` if the current foreground process does not relinquish control, but since the user just clicked our UI, our application is the active one and holds the right to change foreground windows.
