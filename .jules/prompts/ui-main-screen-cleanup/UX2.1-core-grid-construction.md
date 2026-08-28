# UX2.1 - Core Grid Construction

Paste `00-global-rules.md` before this prompt.

```text
Create only the empty four-zone outer grid shell inside an isolated main container.

Timebox: 25-30 minutes. At minute 25, run validation; use remaining time only for direct repair or the rollback/abort rule.

Files in scope:
- app_gui.py
- focused UI import/startup tests only if practical

Tasks:
- Create a dedicated `main_shell` container managed by `pack()` inside the `App` root.
- Inside `main_shell`, create empty parent frames for Quick Action Bar, Secondary Sidebar, Active Hunt Workspace, and Bottom Status / Logs.
- Configure grid row/column weight, minsize, and sticky="nsew" for the four zones inside `main_shell`.
- Treat `1920x1080` as a 100% DPI design target. Use minsize and weight; do not hardcode absolute layout positions or use place().

Do not:
- Mix `grid` directly onto the `App` root where `pack` is currently used.
- Destroy, hide, move, reparent, or resize existing top controls, Notebook, tabs, status bar, or global apply section.
- Change callbacks, bindings, config, hotkeys, hunt logic, window/bounds flow, or add logging data integration.

Acceptance criteria:
- The application starts with all current UI controls still in their current containers.
- The `main_shell` and its four empty parent frames have stable grid behavior and do not crash or overlap at 1920x1080/100% DPI.
- At 125%-150% DPI or reduced width, the grid stays usable through minsize/weight without geometry-manager conflicts or clipped primary controls.

Session boundary gate:
- Existing UI remains usable because no widget was moved.
- No `TclError` occurs from mixing `pack` and `grid` in the same parent.
- Language rebuild does not retain a destroyed outer-shell widget reference.

Validation:
- Run the narrowest import/startup smoke test.
- Verify grid/no-overlap at baseline and one DPI/responsive condition.
- Report layout, ownership, boundary, visual, lifecycle, timebox, and recovery evidence.
```