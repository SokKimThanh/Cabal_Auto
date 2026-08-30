# Session Prompt CB3: Implement Fast-Break Skill Casting for Combos

Timebox: 25-30 minutes.

Objective:
Update skill execution in `HuntRunner._try_cast_skills` and `SkillRuntime` to support polling target state during `cast_time` and fast-breaking as soon as the target dies, preserving Cabal combo timing.

Target Files:
- Modify: `lib/features/hunt/hunt_runner.py`
- Modify: `lib/features/skills/runtime.py` (or `SkillRuntimeService`)

Implementation Details:
1. In `_try_cast_skills()`:
   - Instead of monolithic `time.sleep(runtime["cast_time"])`:
     - Chunk sleep into slices of `0.03s - 0.05s`.
     - Check detector callback / `is_target_alive()` on each slice.
     - If target dies mid-cast: record cast, press target key 'Z' immediately to lock next adjacent mob, and break out of cast sleep.
2. Ensure skill cooldowns and stats (`SkillStats.record_cast`) are updated accurately even on fast-break.
3. Add randomized key hold duration (`40ms - 75ms`) in `win_input.tap()` or local cast caller to avoid anti-cheat rhythm detection.

Validation:
- Mock target alive state toggling to False at 30% of `cast_time`.
- Verify total wait time is truncated and next target lock is initiated within <60ms.

Session Boundary Gate:
- Check that skill rotation index increments cleanly without getting out of sync.
- Report PASSED/REVERTED at minute 25.

# Bổ sung vào Implementation Details của CB3:
- In `_try_cast_skills`:
  * Split `time.sleep(cast_time)` into polling chunks of `0.04s`.
  * If `target_bar_detector.is_target_alive(latest_frame) == False`:
    - Target died mid-cast -> immediately trigger `tap('z')` to acquire next target.
    - Break cast-wait loop immediately to maintain combo streak.
    - Increment skill rotation index to prepare next skill in chain.