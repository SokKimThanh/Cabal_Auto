# Session Prompt CB3C: Harmonize Timing Calculator with Combo Mode & Fast-Break

Timebox: 25-30 minutes.
Priority: High – Resolves timing conflicts between standard rotation and combo engine.
Dependency: CB3D Skill Command Delivery Verification đã đạt gate hoặc có trạng thái acknowledgment được phê duyệt rõ ràng.

---

## Objective
Refactor `timing_calculator.py` and `lib/features/skills/runtime.py` to support dual-mode timing: Dynamic Trigger Timing for Combo Mode (driven by Combo Bar detection) and Predictive APS Timing for Standard Hunt mode.

## Target Files
- Modify: `lib/features/hunt/timing_calculator.py`
- Modify: `lib/features/skills/runtime.py`
- Modify: `lib/features/hunt/hunt_orchestrator.py`
- Create Test: `tests/unit/test_combo_timing_integration.py`

---

## Implementation Details

### 0. Single Source of Truth for Rotation Position (resolves conflict with CB3)
- CB3 established that the skill rotation index increments in exactly one place, at the end of `_try_cast_skills()`, once per cast call (completed or fast-broken).
- When Combo Mode is enabled, `SkillRuntime` becomes the authoritative owner of rotation position instead: `get_next_combo_skill()` exposes the next skill without advancing. Theo CB3D, chỉ `commit_cast()` sau outcome `ACCEPTED` mới advance pointer/cooldown; transport `SENT`, `UNVERIFIED`, `REJECTED` hoặc `CANCELLED` không được advance.
- `_try_cast_skills()` must NOT separately increment its own rotation index while Combo Mode is active — nó dùng reservation token và `commit_cast()` của CB3D để tránh double-advance hoặc desync.
- In Standard Mode (`combo.enabled == False`), cũng phải dùng reservation/ack contract của CB3D; không giữ hành vi `get_attack_to_cast()` advance trước khi xác nhận.
- Toggling `combo.enabled` mid-run: on transition, sync the two positions once (e.g. set `SkillRuntime`'s combo pointer to match the current standard-mode index, or vice versa) so switching modes does not skip or repeat a skill in the chain. Define and test this handoff explicitly rather than leaving the two counters to drift independently.

### 1. Dual-Mode Support in `SkillRuntime` (`lib/features/skills/runtime.py`)
- Add method `get_next_combo_skill(current_time: float) -> Optional[SkillInfo]`:
  - Returns/reserves the strictly sequential skill in the designated Combo Lane without advancing the pointer until outcome `ACCEPTED` được commit.
  - Ensures cooldowns (`skill.is_ready(current_time)`) are respected before returning the key.
  - If the next skill in sequence is not ready (on cooldown), return `None` rather than skipping ahead in the sequence — the caller decides whether to wait or fall back (see §2).
- Nếu cần giữ `get_attack_to_cast()` cho compatibility, biến nó thành wrapper không advance hoặc deprecate nó; standard mode phải dùng reservation/commit contract của CB3D giống Combo mode.

### 2. Conditional Timing in `HuntOrchestrator`
- In `worker()` loop:
  - If `cfg.get("combo", {}).get("enabled", False)`:
    * Bypass static sleep intervals (`attack_interval`, `attack_min_duration_sec`).
    * Let `CabalComboDetector.wait_for_hit_zone()` determine the exact moment of key press.
    * `wait_for_hit_zone()` must accept a timeout (e.g. `cfg.get("combo", {}).get("hit_zone_timeout_sec", 2.0)`). If the hit zone does not appear within the timeout (target disappeared, animation stall, detection miss), do not block indefinitely — abandon this combo attempt, log it, and fall back to a single static-timing cast for that skill (or skip to re-evaluating `have_target`/mode on the next tick), rather than hanging the worker loop.
  - Else (Standard Mode):
    * Use calculated parameters from `TimingRecommendation` (`attack_interval`, `target_cycle_delay`).

### 3. Safety Margin & Validation in `TimingCalculator`
- In `calculate_timing()`:
  - When calculating for combo rotations, check whether the total rotation cast time is **less than** the longest individual skill cooldown in the chain (`total_rotation_cast_time < max(cooldowns)`). This is the actual bottleneck condition: if the full rotation completes faster than a skill's cooldown resets, that skill will not be ready when its turn comes again, stalling the combo. (Note: an earlier draft of this spec described the check in the opposite direction — confirm this corrected direction before implementing.)
  - On detecting this condition, emit a warning (log line is sufficient for this session; do not block combo mode from starting) identifying which skill(s) in the chain have the longest cooldown, so the user can rearrange the combo or accept the expected stall.

---

## Validation & Testing
- Unit Test (`tests/unit/test_combo_timing_integration.py`):
  1. Standard Mode: Verify skill rotation advances using static timing intervals and APS recommendations, unaffected by combo-mode code paths.
  2. Combo Mode: Verify skill keys are reserved sequentially without skipping slots, and only CB3D `commit_cast(ACCEPTED)` advances the pointer.
  3. (Added) Mode-switch handoff: start in Standard Mode, advance a few slots, toggle `combo.enabled = True` mid-run, and assert the combo pointer picks up from the correct next skill (no skip, no repeat). Repeat toggling back to Standard Mode.
  4. (Added) `wait_for_hit_zone()` timeout: mock a hit zone that never appears, assert the worker loop falls back (static cast or re-evaluation) within the configured timeout instead of blocking.
  5. (Added) Combo Mode + fast-break interaction: target chết trong pending cast tạo `CANCELLED` hoặc outcome đã được xác nhận theo evidence; không tự mark success và không double-advance.
  6. (Added) Cooldown bottleneck warning: construct a combo chain where total cast time < max cooldown, assert the warning is emitted and correctly identifies the longest-cooldown skill.
- Ensure zero breakage to existing `SkillStats` tracking in training mode.

## Session Boundary Gate
- **PASSED if:**
  * Unit tests pass for both standard APS calculations and combo rotation queries, including the mode-switch handoff and fast-break interaction tests.
  * No timing conflicts or premature/duplicate index advancement between `SkillRuntime`'s combo pointer and any standard-mode rotation index.
  * `wait_for_hit_zone()` cannot block the worker loop indefinitely (timeout confirmed).
- **REVERTED if:**
  * Legacy hunt loop execution fails or timing parameters produce negative intervals. (`calculate_timing()` must clamp or raise on invalid/negative inputs rather than passing a negative value into any sleep/wait call.)
  * Report PASSED/REVERTED at minute 25.