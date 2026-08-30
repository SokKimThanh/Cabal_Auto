# UX4B.1 - UI Collapsible Container

Paste `00-global-rules.md` before this prompt.

```text
Build only the empty Bottom Status / Logs container and its expand/collapse behavior.

Timebox: 20-25 minutes. At minute 20, run validation; use remaining time only for direct repair or the rollback/abort rule.

Dependencies:
- UX2.2 has passed the outer-shell content migration checks.

Files in scope:
- app_gui.py
- focused UI import/startup tests only if practical

Tasks:
- Create the Bottom Logs frame in Vùng C2.
- Target `1640 x 200 px` at 1920x1080/100% DPI; use grid/minsize/weight rather than fixed placement.
- Add an explicit accessible expand/collapse control.
- Default to collapsed when window height is below `900 px`.

Do not:
- Connect or render log data.
- Change logging format, persistence, workers, polling, config, hunt runtime, bounds flow, or status warning behavior.

Acceptance criteria:
- Container does not overlap 444Sidebar or Workspace.
- Expand/collapse does not reduce primary panels below `360 px`.
- No log source, worker, or scheduled callback is added.

Session boundary gate:
- Collapsed state at height below `900 px`.
- Repeated expand/collapse remains stable.
- Blocking bounds warning remains in Vùng A/B, not the empty container.

Validation:
- Run the narrowest import/startup smoke test and UI import test if applicable.
- Manually check the three boundary cases at baseline and reduced height/DPI.
- Report layout, ownership, visual, lifecycle, timebox, and recovery evidence.
```