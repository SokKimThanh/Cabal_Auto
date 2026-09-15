# Review Prompt 027: Extract Logging and Helpers

## Verification Steps
1. Ensure `_poll_log_queue` and `_update_logs_metrics` have been moved to a `LogConsoleView` component.
2. Verify that `_create_tooltip` and `_icon` have been refactored into a `ui.helpers.UIHelper` namespace.
3. Check that child views no longer invoke `self.app._icon()` and instead import the helper directly.
4. Confirm that the log polling loop uses `TaskScheduler` rather than blocking `Thread()` or unmanaged `self.after` calls.

## Checklist
- [x] Log polling loops removed from `app_gui.py`.
- [x] Icon caching and tooltip generation moved to `UIHelper`.
- [x] Child views updated to use the new helper namespace.
- [x] Strong references to `PhotoImage` (icon cache) are maintained.
