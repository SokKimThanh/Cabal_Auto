# Session Prompt CB2: Fix Hunt Loop & Remove Target Key Spam

Timebox: 25-30 minutes.

Objective:
Refactor `HuntOrchestrator.py` worker loop to stop spamming target key 'Z' during attack mode and remove artificial `attack_min_duration_sec` lock that breaks combo flow.

Target Files:
- Modify: `lib/features/hunt/hunt_orchestrator.py`
- Modify: `lib/features/hunt/hunt_runner.py`
- Reference: `lib/vision/target_bar_detector.py`

Implementation Details:
1. In `lib/features/hunt/hunt_orchestrator.py`:
   - Remove `tap(cfg.get("target_key", "z"))` inside `if mode == "attack":` before calling `try_cast_skills`.
   - Only trigger `tap(target_key)` when `mode == "search"` or when target transitions from ALIVE -> DEAD.
   - In `target_active` evaluation: Remove `(now - attack_started) <= attack_min_duration`. Base target presence strictly on `have_target` and `(now - last_seen) <= lost_timeout`.
2. Hook `TargetBarDetector` into the target location step:
   - When detecting target, query `is_target_alive()` from the screen frame.
   - Update `have_target = is_alive`.

Validation & Test:
- Run: `python -m pytest tests/integration/test_orchestrator_loop.py` or smoke test hunt orchestrator mock.
- Verify:
  1. In attack phase, `tap('z')` is NOT called repeatedly.
  2. Target lost triggers immediately when target bar disappears, switching back to search.

Session Boundary Gate:
- Ensure no Tkinter UI calls occur outside `schedule_ui_task`.
- Report PASSED/REVERTED at minute 25.