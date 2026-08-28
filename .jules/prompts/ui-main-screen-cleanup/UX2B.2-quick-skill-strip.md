# UX2B.2 - Quick Skill Strip

Paste `00-global-rules.md` before this prompt.

```text
Move and style only the existing skills UI into the subordinate Quick Skill View strip.

Timebox: 25-30 minutes. At minute 25, run validation; use remaining time only for direct repair or the rollback/abort rule.

Dependencies:
- UX2B.1 has passed its primary-panel layout and rotation checks.

Files in scope:
- ui/tabs/hunt_tab.py
- focused UI import/startup tests only if practical

Tasks:
- Move existing skill slots/stats widgets into the Quick Skill View strip.
- Target `1576 x 120 px` at 1920x1080/100% DPI using grid weight/minsize, not fixed coordinates.
- Make the strip visually secondary to Monster Rotation and Active Target & Status.
- Preserve every skill StringVar, combobox selection binding, clear action, stats behavior, tooltip, and manager entry point.

Do not:
- Change primary panel layout, hunt runtime, skill persistence, config, Sidebar, Bottom Logs, or create a new Skill Manager.

Acceptance criteria:
- Skills are visible in a lower-priority strip and no widget is clipped at baseline or DPI 125%-150%.
- The strip does not reduce either primary panel below `360 px`.
- Existing skill selection, clear action, and manager route behave unchanged.

Session boundary gate:
- No configured skills: stable empty/placeholder state.
- Maximum configured skill slots: controls remain reachable or scroll within the strip.
- Repeated skill selection/clear action: no stale widget/binding failures.

Validation:
- Run the narrowest import/startup smoke test and UI import test if applicable.
- Manually verify the three boundary cases.
- Report layout, ownership, visual, lifecycle, timebox, and recovery evidence.
```