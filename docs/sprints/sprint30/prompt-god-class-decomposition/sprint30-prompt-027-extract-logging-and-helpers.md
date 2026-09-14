# Sprint 30 Phase 4 Prompt 027: Extract Logging and Helpers

## Goal
Clean up utility, logging, and helper methods.

## Details
- Extract `_poll_log_queue` and `_update_logs_metrics` into a dedicated `LogConsoleView` component.
- Move tooltip generation (`_create_tooltip`, `_destroy_widget_tooltip`) and icon caching (`_icon`) into a global utility namespace (e.g., `ui.helpers.UIHelper`) so any view can invoke them without requiring an `App` instance reference.
- Refactor any child views calling `self.app._icon()` to use the new utility class.

## Acceptance Criteria
- Tooltips and icons load correctly across the app.
- Log polling no longer pollutes the God Class.
- `pylint app_gui.py` remains at 10.0.
