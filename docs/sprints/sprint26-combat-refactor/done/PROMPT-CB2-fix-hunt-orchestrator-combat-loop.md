# Session Prompt CB2: Fix Hunt Loop & Remove Target Key Spam

Timebox: 25-30 minutes.

Objective:
Refactor `HuntOrchestrator.py` worker loop to stop spamming target key 'Z' during attack mode and remove artificial `attack_min_duration_sec` lock that breaks combo flow.

Target Files:
- Modify: `lib/features/hunt/hunt_orchestrator.py`
- Modify: `lib/features/hunt/hunt_runner.py`
- Reference: `lib/vision/target_bar_detector.py`

## Implementation Details

1. In `lib/features/hunt/hunt_orchestrator.py`:
   - Remove `tap(cfg.get("target_key", "z"))` inside `if mode == "attack":` before calling `try_cast_skills`.
   - Tap the target key **only** when `mode == "search"`. The previous "or when target transitions from ALIVE → DEAD" branch is now redundant and should be removed: once the target dies, `is_target_alive()` returns `False` on the next frame, `have_target` becomes `False`, `target_active` evaluates to `False`, the orchestrator switches to `mode == "search"` on its own, and the search branch already taps the key there. Do not keep a separate ALIVE→DEAD tap path — it would double-tap.
   - In `target_active` evaluation: Remove `(now - attack_started) <= attack_min_duration`. Base target presence strictly on `have_target` and `(now - last_seen) <= lost_timeout`.
     - `last_seen` update rule: update `last_seen = now` on **every** worker tick where `is_target_alive(frame) == True` (not only on first detection). This makes `last_seen` a rolling "last confirmed alive" timestamp, and `lost_timeout` acts as the grace window after the last confirmed-alive frame before the target is considered gone.
   - Debounce for `have_target`: do not flip `have_target` to `False` on a single `is_target_alive() == False` reading. Require `N` consecutive `False` readings (default `N = 3`, configurable via `cfg.get("target_lost_debounce_frames", 3)`) before setting `have_target = False`. This absorbs transient detector noise from skill/particle effects briefly occluding the HP bar, or a frame not yet updated, without reintroducing a fixed time-based lock like the old `attack_min_duration_sec`. A single `True` reading immediately resets the consecutive-`False` counter to 0 and sets `have_target = True`.
2. Hook `TargetBarDetector` into the target location step:
   - When detecting target, query `is_target_alive()` from the screen frame.
   - Update `have_target = is_alive` (subject to the debounce rule above).

## Bổ sung vào Implementation Details của CB2 (giữ nguyên, đã làm rõ)

- Decouple `locate_target` from legacy `AppStateController._hunt_locate_target` template loop.
- In `worker()` loop:
  * Replace `box, match_info = self.locate_target(cfg)` with direct check: `have_target = target_bar_detector.is_target_alive(frame)` (through the debounce logic above).
  * `frame` source and capture cadence: capture one fresh frame per `worker()` tick at the top of the loop (e.g. `frame = capture_client_area(hwnd)`), and reuse that single captured frame for all per-tick checks (`is_target_alive`, any other vision calls) rather than re-capturing per check. Throttle the loop tick rate itself (e.g. via the existing worker sleep/interval, not an extra capture-specific throttle) to bound CPU usage from screen capture.
  * In `mode == "search"`: Send `tap(cfg.get("target_key", "z"))` with delay `cfg.get("search_tap_delay_sec", 0.08)`. Expose this as a config value rather than a hard-coded literal so it can be tuned; the default `0.08s` is meant to cover input-processing/animation lag on the target-lock action before the next check reads the result — confirm/adjust empirically per client build rather than treating it as fixed.
  * In `mode == "attack"`: DO NOT send target key. Directly call `try_cast_skills()`.

## Validation & Test

- Run: `python -m pytest tests/integration/test_orchestrator_loop.py` or smoke test hunt orchestrator mock.
- Verify:
  1. In attack phase, `tap('z')` is NOT called repeatedly.
  2. Target lost triggers immediately when target bar disappears, switching back to search.
  3. (Added) Simulate a single transient `False` reading from `is_target_alive()` followed immediately by `True` (e.g. one frame occluded by a skill effect): assert `have_target` stays `True` and `mode` does NOT switch to `search`.
  4. (Added) Simulate `N` (default 3) consecutive `False` readings: assert `have_target` becomes `False` only after the `N`-th reading, and `mode` switches to `search` at that point, not earlier.

## Session Boundary Gate

- Ensure no Tkinter UI calls occur outside `schedule_ui_task`.
- Confirm the ALIVE→DEAD tap branch has been removed (not duplicated with the search-mode tap).
- Confirm `last_seen` update rule and debounce counter are implemented as specified above.
- Report PASSED/REVERTED at minute 25.