# UX4B.2 - Log Data Integration

Paste `00-global-rules.md` before this prompt.

```text
Connect the existing thread-safe recent-log source to the Bottom Logs container and render bounded text only.

Timebox: 25-30 minutes. At minute 25, run validation; use remaining time only for direct repair or the rollback/abort rule.

Dependencies:
- UX4B.1 has passed container layout and collapse checks.
- Identify an existing thread-safe log source and its Main Thread delivery path within the first 10 minutes. If no suitable source exists, abort implementation and report the blocker without adding infrastructure.

Files in scope:
- focused existing log/status UI helper
- app_gui.py only for existing container integration
- focused tests only if practical

Tasks:
- Read snapshots from an existing thread-safe source only.
- Render a bounded, independently scrollable recent-activity view into the existing Bottom Logs container.
- Deliver worker-produced data through an existing UI scheduler or queue; define cleanup for close/rebuild before implementing.

Do not:
- Add a worker, polling loop, logging framework, persistence, log format change, or runtime warning policy.
- Move blocking bounds/status recovery out of Vùng A/B.

Acceptance criteria:
- Empty log source renders a stable empty state.
- Long/repeated entries scroll without resizing the `200 px` container.
- Close/rebuild does not schedule rendering into destroyed widgets.

Session boundary gate:
- Empty entries.
- Long/repeated entries.
- App close/rebuild while no stale render callback occurs.

Validation:
- Run the narrowest import/startup smoke test and UI import test if applicable.
- Verify Main Thread delivery and cleanup path before manual GUI checks.
- Report source of truth, ownership, layout, boundary, lifecycle, timebox, and recovery evidence.
```