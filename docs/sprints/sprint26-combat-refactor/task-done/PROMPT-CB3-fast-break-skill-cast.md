# Session Prompt CB3: Implement Fast-Break Skill Casting for Combos

Timebox: 25-30 minutes.

Objective:
Update skill execution in `HuntRunner._try_cast_skills` and `SkillRuntime` to support polling target state during `cast_time` and fast-breaking as soon as the target dies, preserving Cabal combo timing.

Target Files:
- Modify: `lib/features/hunt/hunt_runner.py`
- Modify: `lib/features/skills/runtime.py` (or `SkillRuntimeService`)

## Implementation Details

1. In `_try_cast_skills()`:
   - Instead of a monolithic `time.sleep(runtime["cast_time"])`:
     - Chunk the sleep into fixed `0.04s` polling slices (final value — the earlier "0.03s-0.05s" range in an older draft is superseded by this fixed value for predictable timing).
     - On each slice, check `target_bar_detector.is_target_alive(latest_frame)`.
     - If the target dies mid-cast:
       - Record the cast via `SkillStats.record_cast`, marking it explicitly as a **fast-broken cast** (e.g. a `completed=False` or `broken=True` flag on the record), not a fully completed one. Cooldown timing still starts from cast-begin regardless of break (matches normal game cast/cooldown behavior), but statistics/analytics should be able to distinguish completed vs. broken casts.
       - Immediately press the target key (`tap('z')`) to attempt locking the next adjacent mob.
       - If no adjacent mob is found (target lock attempt fails), do not stay in a waiting state — fall through to the orchestrator's normal `mode == "search"` handling (per CB2) on the next tick, rather than looping or blocking here.
       - Break out of the cast-wait loop immediately to preserve combo streak.
2. Ensure skill cooldowns and stats (`SkillStats.record_cast`) are updated accurately even on fast-break, per the completed/broken distinction above.
3. Rotation index handling:
   - Increment the skill rotation index in exactly one place: at the end of `_try_cast_skills()`, after either a normal completed cast or a fast-break, but not both (i.e. do not increment once for "cast finished" and again for "fast-break happened" if both code paths could run for the same cast). Fast-break and normal completion are two exits from the same call — the index increments once per call, regardless of which exit was taken.
4. Input timing:
   - Add a randomized key-hold duration (`40ms-75ms`) in `win_input.tap()` (or the local cast caller) instead of a fixed hold duration, purely so scripted input doesn't look identically timed on every press. Do not otherwise tune this value against any specific anti-cheat detection behavior — that framing is out of scope here; treat it as a generic "avoid perfectly uniform timing" input detail, nothing more.

## Validation

- Mock target alive state toggling to `False` at 30% of `cast_time`.
- Verify total wait time is truncated and the next target-lock attempt (`tap('z')`) is initiated promptly after detection (measure relative to your own test harness's timing rather than asserting a fixed cross-machine ceiling like `<60ms`, since real-world latency depends on input lag and game client responsiveness on the test machine).
- (Added) Mock a fast-break where no adjacent mob is found after `tap('z')`: assert the orchestrator falls back to `mode == "search"` on the next tick rather than blocking or looping.
- (Added) Verify `SkillStats.record_cast` distinguishes a fast-broken cast from a normally completed one (e.g. assert the `completed`/`broken` flag is set correctly in both cases).
- (Added) Run a sequence of casts mixing normal completions and fast-breaks: assert the rotation index advances exactly once per cast call, with no double-increment or skipped skill in the rotation.

## Session Boundary Gate

- Check that skill rotation index increments cleanly without getting out of sync (verified by the mixed-sequence test above).
- Confirm cast records distinguish completed vs. fast-broken casts.
- Confirm the "no adjacent mob found" case falls back to search mode instead of stalling.
- Report PASSED/REVERTED at minute 25.# Session Prompt CB3: Implement Fast-Break Skill Casting for Combos

Timebox: 25-30 minutes.

Objective:
Update skill execution in `HuntRunner._try_cast_skills` and `SkillRuntime` to support polling target state during `cast_time` and fast-breaking as soon as the target dies, preserving Cabal combo timing.

Target Files:
- Modify: `lib/features/hunt/hunt_runner.py`
- Modify: `lib/features/skills/runtime.py` (or `SkillRuntimeService`)

## Implementation Details

1. In `_try_cast_skills()`:
   - Instead of a monolithic `time.sleep(runtime["cast_time"])`:
     - Chunk the sleep into fixed `0.04s` polling slices (final value — the earlier "0.03s-0.05s" range in an older draft is superseded by this fixed value for predictable timing).
     - On each slice, check `target_bar_detector.is_target_alive(latest_frame)`.
     - If the target dies mid-cast:
       - Record the cast via `SkillStats.record_cast`, marking it explicitly as a **fast-broken cast** (e.g. a `completed=False` or `broken=True` flag on the record), not a fully completed one. Cooldown timing still starts from cast-begin regardless of break (matches normal game cast/cooldown behavior), but statistics/analytics should be able to distinguish completed vs. broken casts.
       - Immediately press the target key (`tap('z')`) to attempt locking the next adjacent mob.
       - If no adjacent mob is found (target lock attempt fails), do not stay in a waiting state — fall through to the orchestrator's normal `mode == "search"` handling (per CB2) on the next tick, rather than looping or blocking here.
       - Break out of the cast-wait loop immediately to preserve combo streak.
2. Ensure skill cooldowns and stats (`SkillStats.record_cast`) are updated accurately even on fast-break, per the completed/broken distinction above.
3. Rotation index handling:
   - Increment the skill rotation index in exactly one place: at the end of `_try_cast_skills()`, after either a normal completed cast or a fast-break, but not both (i.e. do not increment once for "cast finished" and again for "fast-break happened" if both code paths could run for the same cast). Fast-break and normal completion are two exits from the same call — the index increments once per call, regardless of which exit was taken.
4. Input timing:
   - Add a randomized key-hold duration (`40ms-75ms`) in `win_input.tap()` (or the local cast caller) instead of a fixed hold duration, purely so scripted input doesn't look identically timed on every press. Do not otherwise tune this value against any specific anti-cheat detection behavior — that framing is out of scope here; treat it as a generic "avoid perfectly uniform timing" input detail, nothing more.

## Validation

- Mock target alive state toggling to `False` at 30% of `cast_time`.
- Verify total wait time is truncated and the next target-lock attempt (`tap('z')`) is initiated promptly after detection (measure relative to your own test harness's timing rather than asserting a fixed cross-machine ceiling like `<60ms`, since real-world latency depends on input lag and game client responsiveness on the test machine).
- (Added) Mock a fast-break where no adjacent mob is found after `tap('z')`: assert the orchestrator falls back to `mode == "search"` on the next tick rather than blocking or looping.
- (Added) Verify `SkillStats.record_cast` distinguishes a fast-broken cast from a normally completed one (e.g. assert the `completed`/`broken` flag is set correctly in both cases).
- (Added) Run a sequence of casts mixing normal completions and fast-breaks: assert the rotation index advances exactly once per cast call, with no double-increment or skipped skill in the rotation.

## Session Boundary Gate

- Check that skill rotation index increments cleanly without getting out of sync (verified by the mixed-sequence test above).
- Confirm cast records distinguish completed vs. fast-broken casts.
- Confirm the "no adjacent mob found" case falls back to search mode instead of stalling.
- Report PASSED/REVERTED at minute 25.