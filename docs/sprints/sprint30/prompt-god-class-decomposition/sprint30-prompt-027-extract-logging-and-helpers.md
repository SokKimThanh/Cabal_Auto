# Sprint 30 Phase 4 Prompt 027: Extract Logging and Helpers

## Goal
Clean up utility, logging, and helper methods.

## Details
- Extract `_poll_log_queue` and `_update_logs_metrics` into a dedicated `LogConsoleView` component.
- Move tooltip generation (`_create_tooltip`, `_destroy_widget_tooltip`) and icon caching (`_icon`) into a global utility namespace (e.g., `ui.helpers.UIHelper`) so any view can invoke them without requiring an `App` instance reference.
- Refactor any child views calling `self.app._icon()` to use the new utility class.

## Risks and Things to Avoid
- **Avoid using `Thread()` or `self.after` inside the new LogConsoleView.**
- **Risk:** Log polling requires the `TaskScheduler`. If extracted poorly, infinite loops of 0ms UI updates could freeze the application.
- **Risk:** Icon cache (`_icon`) must maintain a strong reference dictionary (`self._icon_cache`). If moved to a static helper without maintaining this cache, Python's Garbage Collector will destroy the `PhotoImage` objects, resulting in blank icons across the entire app.

## Acceptance Criteria
- Tooltips and icons load correctly across the app.
- Log polling no longer pollutes the God Class.
- `pylint app_gui.py` remains at 10.0.
