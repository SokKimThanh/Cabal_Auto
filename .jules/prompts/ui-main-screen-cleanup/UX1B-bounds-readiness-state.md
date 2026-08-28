# UX1B - Bounds Readiness State

Paste `00-global-rules.md` before this prompt.

```text
Implement one compact, actionable target-window/bounds readiness state next to the existing Window selector and Refresh control.

Timebox:
- Maximum 30 minutes; reserve the final 5 minutes for validation and the session report.
- If the required UI state cannot be derived from existing data within 15 minutes, stop and report the missing binding instead of creating duplicate bounds state.

Dependencies:
- UX1 must have passed its startup and layout checks.

Files in scope:
- app_gui.py
- ui/controllers/app_window_controller.py only if an existing UI update hook needs to notify the new display
- focused tests only if an existing UI-test pattern supports this cheaply

Do not edit:
- HuntTab, SetupTab, config schema, window-selection service, runtime hunt logic, Sidebar, Workspace, or Bottom Logs.

Goal:
Expose the current readiness of the selected target window before Start Hunt without changing the existing selection and normalized-bounds flow.

Required data flow:
- Reuse the existing `normalize_window_bounds_value` and `WindowSelectionService.update_bounds` flow.
- Do not create an independent UI-owned copy of window bounds.
- Update the display after the existing select-window and refresh-window paths, including `_update_window_bounds_display` if that is the established hook.

Layout contract at 1920x1080:
- Work only in Vùng A: Quick Action Bar, `1920 x 80 px`.
- Bounds state stays immediately after Refresh, has at least `260 x 36 px`, and does not cause Start/Stop to wrap or shrink below `140 x 40 px`.

Visual design:
- Use UIStyle semantic tokens; do not hard-code colors.
- Ready uses accent/ready semantics; missing or invalid bounds uses warning semantics; blocking unavailable/minimized state may use danger only when Start is blocked.
- Every state includes readable text and the recovery action. Do not rely on color alone.

Required states:
1. Valid selected window and valid bounds: show ready state and window identity.
2. No selected window or missing bounds: show select-window or Refresh recovery action.
3. Invalid/malformed or minimized/unavailable window when existing runtime data exposes it: show a clear restore, reselect, or Refresh recovery action.

Acceptance criteria:
- State is visible without opening Setup, Sidebar, or logs.
- Existing selection, refresh, config persistence, Start/Stop callbacks, and hotkeys remain unchanged.
- UI always reflects the current normalized bounds state after a successful select or refresh.
- No config shape or duplicate bounds model is introduced.

Session boundary gate:
- valid selected window: display reports ready after select and refresh
- no selected window: display gives select/refresh recovery action
- invalid or minimized/unavailable window: display gives reselect/restore/refresh recovery action when the existing state can identify it

Validation:
- run `py -m pytest tests/test_ui_imports.py` if applicable
- run the narrowest startup/import smoke check available
- manually check the three required states and report each as passed, failed, or manual-only
- report Layout evidence for `1920x1080`, UIStyle tokens used, and confirmation that no hard-coded color or duplicate bounds state was introduced
```