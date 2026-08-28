# UX2.2 - Content Migration

Paste `00-global-rules.md` before this prompt.

```text
Rebuild the Quick Action Bar and Notebook directly inside their respective UX2.1 zone containers.

Timebox: 25-30 minutes. At minute 25, run validation; use remaining time only for direct repair or the rollback/abort rule.

Dependencies:
- UX2.1 has passed startup, resize, and no-overlap validation.

Files in scope:
- app_gui.py
- focused UI import/startup tests only if practical

Tasks:
- Update `App._build_ui()` to instantiate the Quick Action Bar directly inside the Quick Action Bar zone frame.
- Update `App._build_ui()` to instantiate the Notebook directly inside the Workspace zone frame.
- Preserve state/config values, callbacks, event bindings, hotkeys, tab behavior, config persistence, and the window/bounds source of truth.
- Let the established `_build_ui()` teardown destroy old children before constructing replacement children in their target parent containers.

Do not:
- Attempt runtime widget reparenting; Tkinter widgets must be constructed with their final target master container.
- Change layout inside HuntTab or SetupTab.
- Create Sidebar content, Bottom Logs content, new status widgets, or new callbacks.
- Change Start/Stop or window selection behavior.

Acceptance criteria:
- Quick Action Bar and Notebook render directly inside their target zone containers.
- Window selection, Refresh, Start, Stop, and every existing tab continue to work.
- No widget is duplicated or orphaned, and rebuilt widgets do not introduce a new/inconsistent state source.

Session boundary gate:
- No selected window: existing recovery feedback remains reachable.
- Language rebuild: zone containers and their newly built child controls rebuild without stale references.
- Repeated tab selection: all tabs remain interactive and stable after rebuilding.

Validation:
- Run the narrowest import/startup smoke test and UI import test if applicable.
- Manually check window selection, Refresh, Start/Stop state, and tab switching.
- Report layout, ownership, boundary, lifecycle, timebox, and recovery evidence.
```