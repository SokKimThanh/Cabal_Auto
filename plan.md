1. **Refactor `lib/features/hunt/hunt_orchestrator.py` worker loop**:
   - Add `target_bar_detector` initialization before the loop: `target_bar_detector = TargetBarDetector()`.
   - Update `have_target` evaluation:
     - Remove `box, match_info = self.locate_target(cfg)`.
     - Instead, inside the loop, capture a single `frame` per tick.
     - Evaluate `is_alive = target_bar_detector.is_target_alive(frame)`.
     - Implement debounce logic: keep track of `consecutive_false_readings`. If `is_alive` is True, `have_target = True` and reset `consecutive_false_readings = 0`. If `is_alive` is False, increment counter. If `consecutive_false_readings >= cfg.get("target_lost_debounce_frames", 3)`, then `have_target = False`.
     - Update `last_seen = now` if `is_alive` is True.
   - Adjust `target_active` check inside `mode == 'attack'`:
     - Remove `(now - attack_started) <= attack_min_duration` from target active condition.
     - Remove `tap(cfg.get("target_key", "z"))` in attack mode to stop spamming the target key.
   - In `mode == 'search'`:
     - Update target key tap to use configurable delay: `time.sleep(float(cfg.get("search_tap_delay_sec", 0.08)))`.
2. **Refactor `lib/features/hunt/hunt_runner.py` (not strictly needed since `try_cast_skills` loop logic is mainly in orchestrator, but verify its signature if needed)**.
3. **Write/update `tests/integration/test_orchestrator_loop.py`**:
   - Write integration tests to mock `is_target_alive` and verify state transitions and target key tapping logic according to the new requirements (debounce logic, no target key spam in attack mode).
4. **Pre-commit tasks**: run `pre_commit_instructions` and follow them to ensure tests, verification, and code review pass.
5. **Submit changes**.
