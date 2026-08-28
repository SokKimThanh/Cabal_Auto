# UX3 - Sidebar Navigation Cho Cấu Hình Phụ

Paste `00-global-rules.md` before this prompt.

```text
Implement only the Secondary Configuration Sidebar navigation slice based on docs/UX_ANALYSIS_AND_INTERFACE_REDESIGN.md.

Goal:
Keep the main screen focused on daily workflows while exposing clear navigation to secondary configuration and managers.

Timebox and scope split:
- Timebox: 25-30 minutes. At minute 25, run validation; use remaining time only for direct repair or the rollback/abort rule.
- This prompt owns Sidebar entry points only.
- Do not move all SetupTab content, alter manager windows, or change persistence in this session.
- Progressive disclosure is UX3B and must be deferred.

Files in scope:
- app_gui.py
- ui/tabs/setup_tab.py
- ui/tabs/hunt_tab.py
- focused tests only if needed

Primary UX objective:
Advanced configuration should not compete with the primary hunt loop for visual prominence.

Design intent:
Basic usage should be fast and clear. Advanced controls should remain accessible, but visibly subordinate so they do not distract from the active hunt workflow.

Layout contract for this session:
- Work primarily in Vùng C1: Secondary Configuration Sidebar, `280 x 944 px` at the `1920x1080` baseline.
- Use `16 px` horizontal and `20 px` vertical padding; do not widen the Sidebar above `300 px`.
- Keep Sidebar as navigation and manager entry points, not a full detail editor.
- Use `UIStyle.BG_PANEL` or `UIStyle.BG_SECTION` for this subordinate surface. Do not reuse the green/red primary-action colors for Sidebar navigation.

Tasks:
- create or arrange clear Sidebar entry points in this order: Quick Setup, Managers, Configuration, Support
- keep each entry point wired to its existing callback or tab route
- keep target-window/bounds feedback in Vùng A/B; Sidebar may link to configuration but cannot own blocking runtime feedback
- keep Sidebar within `280 px` baseline and `250-300 px` responsive range

Acceptance criteria:
- Sidebar is visually subordinate and exposes each existing secondary route
- no manager callback, mode persistence, or configuration access path is removed
- boundary validation remains visible enough to prevent hunting against a missing, minimized, or invalid game window

Session boundary gate:
- no selected window: bounds warning and recovery remain in Vùng A/B while Sidebar is visible
- manager entry point: repeated open/close does not break the parent UI
- narrow layout `1280-1599 px`: Sidebar remains within `250-300 px` or follows the documented accordion fallback
- report results for all three cases before ending the session

Validation:
- run startup smoke checks
- run `py -m pytest tests/test_ui_imports.py` if still relevant
- document manual verification of every Sidebar entry point used
- verify that Sidebar does not push Workspace below `1640 x 744 px` or hide bounds feedback from Vùng A/B
```
