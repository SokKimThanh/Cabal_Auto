1.  **Refactor `ui.helpers.UIHelper`**:
    *   I've already created the base `ui/helpers/ui_helper.py` and exported it in `ui/helpers/__init__.py`. I'll verify it has all the needed logic.
    *   The `UIHelper` has `create_tooltip`, `destroy_widget_tooltip`, and `icon` methods.
    *   It maintains the `_tooltips` and `_icon_cache` dictionaries to prevent garbage collection.
2.  **Move `_poll_log_queue` and `_update_logs_metrics` to `ActivityLogsFrame`**:
    *   Extract `_poll_log_queue` and `_update_logs_metrics` from `app_gui.py` and put them into `ui/views/activity_logs_frame.py`.
    *   Make sure `ActivityLogsFrame` gets the `TaskScheduler` instance (e.g., via `app.task_scheduler`).
    *   In `ActivityLogsFrame.__init__`, set up the scheduled recurring tasks using `self.app.task_scheduler.schedule_recurring_task`.
    *   Ensure we use `lib.system.hunt_logger.get_hunt_logger` within the moved methods inside `ActivityLogsFrame`.
3.  **Update `app_gui.py`**:
    *   Remove `_poll_log_queue`, `_update_logs_metrics`, `_create_tooltip`, `_destroy_widget_tooltip`, and `_icon` from `App`.
    *   Remove scheduling of `_poll_log_queue` and `_update_logs_metrics` from `App._build_ui`.
    *   In `app_gui.py`, replace any remaining `self._t` or tooltip usages with the updated logic or leave as is if only used internally (though prompt says child views should be updated).
    *   The UI helper should be available to other modules.
4.  **Refactor child views**:
    *   Child views in `ui/panels/monster_target_panel.py`, `ui/tabs/hunt_tab.py`, `ui/windows/library_manager.py`, and `app_gui.py` itself that call `app._create_tooltip`, `app._destroy_widget_tooltip`, or `app._icon` will be refactored to use `UIHelper.create_tooltip`, `UIHelper.destroy_widget_tooltip`, and `UIHelper.icon`.
    *   Fix any tests that mock these methods on `app` (e.g., `tests/unit/ui/tabs/test_hunt_target_modes.py`).
5.  **Pre-commit steps**:
    *   Run `pre_commit_instructions` and make sure testing, verification, review, and reflection are done.
    *   Run pylint on `app_gui.py` to ensure it is at 10.0.
6.  **Submit the changes**.
