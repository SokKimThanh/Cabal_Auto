1. **`lib/vision/target_hp_reader.py`**:
   - Update `calculate_target_hp_percent` to enforce the 100ms throttle and 0.5% delta logic accurately using AND logic: `if (time_elapsed >= self.throttle_ms) and (delta >= self.min_delta_percent)`. Ensure death signal (0.0) bypasses the throttle.

2. **`ui/tabs/hunt_tab.py`**:
   - In `_build_ui`, instantiate `self.recovery_frame` within the active target card context. Inside it, create a button `[ Khôi Phục Cửa Sổ Game ]` using the key `target_card.recovery_btn`. Initialize it as hidden (`pack_forget` or don't pack initially).
   - Implement a `show_recovery()` method to show this frame, and update the UI style (if desired) to `STATE_WARN`.
   - Implement `hide_recovery()` method.
   - Implement the button command which disables the button and calls `WindowRecoveryController.instance().start_async_recovery`.
   - Update `on_progress(step)` to change the button text to `target_card.recovery_retry`.
   - Update `on_failure()` to change the frame color/label to `UIStyle.STATE_ERROR` (red) and show toast/label `target_card.recovery_failed`, re-enable the button.
   - Note on Canvas rendering: Ensure that `update_hp_display` does not use `delete("all")` and instead uses `coords` and `itemconfig` (it already does, just ensure it stays that way).
   - Note on Graceful death reset: Verify that it retains `self.after_cancel(self._pending_clear_id)` on retarget (which it does in `update_target_card`).

3. **`lib/features/hunt/window_selection_service.py`**:
   - The shared retry logic `WindowRecoveryController` is mostly there, but review its `_execute_retry_step` to ensure it precisely uses the passed `schedule_after_ms` function (e.g. `self.root.after`) without blocking the thread. (It already uses `self._schedule_after_ms`).

4. **`tests/unit/test_target_hp_recovery.py`**:
   - Write granular tests:
     - `test_stress_hp_throttling`: Send 2000 events in 5s. Assert canvas draw called exactly 50 times (mocking time).
     - `test_delta_threshold_skip`: Check that after 100ms, if delta < 0.5, no draw is called.
     - `test_graceful_death_delay`: Verify 0% HP sets state to dead and schedules clear card in 200ms.
     - `test_rapid_retarget_cancels_pending_clear`: Verify setting 0% then retargeting within 200ms calls `after_cancel`.
     - `test_3_step_recovery_retry_and_failure`: Mock `WindowManager.restore` to return False, assert 3 steps execute via scheduled callbacks and failure triggers.
     - `test_shared_retry_lock_with_ux1`: Trigger recovery twice concurrently; assert only one executes.

5. **`lib/i18n/translations.py`**:
   - Ensure the required translation keys are fully registered.

6. **Run Tests**:
   - Execute the test suite via `pytest tests/unit/test_target_hp_recovery.py` to confirm the implementation.

7. **Pre-commit step**: Complete pre commit steps to make sure proper testing, verifications, reviews and reflections are done.
