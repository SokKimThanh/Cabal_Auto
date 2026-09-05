# 📋 Review: CB3C Requirements vs Current Project State

**Status: PARTIALLY READY** - CB3D Framework restored but NOT YET INTEGRATED  
**Date:** 2026-09-05  
**Timebox:** CB3C 25-30 minutes (dependent on CB3D integration complete)

---

## 1. Dependency Status: CB3D

✅ **CB3D Framework Files RESTORED (8b07203 commit)**
- ✅ `lib/features/skills/cast_delivery.py` - CastDeliveryManager, CastOutcome enums
- ✅ `lib/features/skills/skill_stats.py` - Outcome tracking
- ✅ `lib/vision/skill_cooldown_detector.py` - Hotbar cooldown detection
- ✅ `lib/features/combo/combo_timing_detector.py` - CB6 sweet-spot detection
- ✅ `lib/features/combo/__init__.py`
- ✅ All 16 CB3D unit tests restored

⚠️ **CB3D Integration Status: NOT YET WIRED**
- ❌ `hunt_orchestrator.py` NOT using `CastDeliveryManager`
- ❌ `hunt_orchestrator.py` NOT calling `wait_for_hit_zone()`
- ❌ `hunt_orchestrator.py` NOT checking `combo.enabled` config
- ❌ `runtime.py` does NOT have CB3D methods yet:
  - ❌ `get_next_combo_skill()` (required by CB3C §1)
  - ❌ `reserve_next_skill()` (required by CB3C §1)
  - ❌ `commit_cast()` (required by CB3C §1)
  - ❌ `release_cast()` (required by CB3C §1)

**Verdict:** CB3D gate can technically open (unit tests pass), but **orchestrator hookup is still TODO** — CB3C cannot proceed cleanly without this wiring.

---

## 2. CB3C Target Files & Current State

### 📄 `lib/features/timing/calculator.py`
**✅ EXISTS** (but location differs from prompt)
- Prompt expected: `lib/features/hunt/timing_calculator.py`
- Actual location: `lib/features/timing/calculator.py`
- **Status:** File organized under different structure; migration/rename not needed if working

**Current Implementation:**
- ✅ `TimingRecommendation` dataclass with fields:
  - `lost_timeout_sec`, `attack_min_duration_sec`
  - `attack_interval`, `target_cycle_delay`
- ✅ `calculate_timing()` function accepts optional `skill_rotation` param
- ✅ Calculates rotation cycle time for skill chains
- ❌ **MISSING:** Cooldown bottleneck validation (§3 requirement)
  - Should check: `total_rotation_cast_time < max(cooldowns)` ← **MUST ADD**
  - Should emit warning if bottleneck detected
  - Status: **NOT IMPLEMENTED**

### 📄 `lib/features/skills/runtime.py`
**✅ EXISTS** - Large file with core skill management

**Current Implementation:**
- ✅ `SkillInfo` dataclass with cooldown, cast_time, duration_sec
- ✅ `SkillRuntime` class with attack/buff lanes
- ✅ `get_attack_to_cast()` - rotates through attacks sequentially
- ✅ `get_buff_to_cast()` - refreshes buffs before expiration
- ✅ `mark_cast()` - updates last_cast_time
- ✅ `attack_rotation_index` - tracks position in attack rotation

**REQUIRED by CB3C (§1) - NOT YET IMPLEMENTED:**
- ❌ `get_next_combo_skill(current_time) -> Optional[SkillInfo]`
  - Must return next skill WITHOUT advancing pointer
  - Must respect cooldowns
  - Must return `None` if not ready (rather than skip)
- ❌ `reserve_next_skill()` - Reserve a skill without casting
- ❌ `commit_cast(outcome: CastOutcome)` - Advance pointer ONLY on ACCEPTED
- ❌ `release_cast()` - Revert reservation on REJECTED/CANCELLED
- ❌ Separate `combo_rotation_index` for dual-mode operation

**Issue with Current `get_attack_to_cast()`:**
```python
def get_attack_to_cast(self, current_time: float) -> Optional[str]:
    for _ in range(len(self.attack_skills)):
        skill = self.attack_skills[self.attack_rotation_index]
        self.attack_rotation_index = (self.attack_rotation_index + 1) % len(self.attack_skills)  # ⚠️ ADVANCES IMMEDIATELY
        if skill.is_ready(current_time):
            return skill.key
    return None
```
**Problem:** Advances rotation index BEFORE checking if cast succeeds. CB3D requires pointer only advances when outcome ACCEPTED. → **MUST REFACTOR**

### 📄 `lib/features/hunt/hunt_orchestrator.py`
**✅ EXISTS** - Core orchestrator loop

**Current Implementation:**
- ✅ `start_hunt()` - Initializes input backend
- ✅ `worker()` method exists (not fully shown in excerpt)
- ✅ Uses callbacks for skill casting

**REQUIRED by CB3C (§2) - NOT YET IMPLEMENTED:**
- ❌ Check for `cfg.get("combo", {}).get("enabled", False)`
- ❌ If combo enabled:
  - ❌ Bypass static sleep intervals
  - ❌ Call `CabalComboDetector.wait_for_hit_zone(screen_capture, timeout_sec)`
  - ❌ Handle timeout gracefully (don't block indefinitely)
  - ❌ Fall back to single static-timing cast if hit zone not detected
- ❌ If standard mode:
  - ✅ Use `TimingRecommendation` parameters (framework in place)

### 📄 `lib/data/hunt_config.json`
**✅ EXISTS** - Configuration file

**Required Config Fields (CB3C §2):**
- ✅ `combo.enabled` - Boolean flag to toggle mode
- ✅ `combo.hit_zone_timeout_sec` - Timeout for sweet-spot detection
- ✅ `combo.poll_interval_ms` - Frame check frequency
- ✅ `combo.cooldown_guard_ms` - Post-press blocking duration

**Verdict:** Config structure appears ready; just needs orchestrator to consume it.

---

## 3. Implementation Gap Analysis

| Requirement | File | Status | Effort |
|--|--|--|--|
| **§0: Single source of truth** | runtime.py | ❌ Not enforced | 30 min (large refactor) |
| **§1.1: `get_next_combo_skill()`** | runtime.py | ❌ Missing | 15 min |
| **§1.2: Separate combo_index** | runtime.py | ❌ Missing | 5 min |
| **§1.3: CB3D methods** | runtime.py | ❌ Missing 4 methods | 20 min |
| **§2.1: Dual-mode check in worker()** | hunt_orchestrator.py | ❌ Missing | 10 min |
| **§2.2: `wait_for_hit_zone()` call** | hunt_orchestrator.py | ❌ Missing | 5 min |
| **§2.3: Timeout fallback** | hunt_orchestrator.py | ❌ Missing | 10 min |
| **§3: Cooldown bottleneck validation** | calculator.py | ❌ Missing | 5 min |
| **Testing: Unit tests (6 scenarios)** | tests/unit/test_combo_timing_integration.py | ❌ File missing | 25 min |

**Total Estimated Work:** ~2.5 hours (far exceeds 25-30 min timebox)

---

## 4. Critical Issues to Resolve Before CB3C

### Issue A: Pointer Advancement Conflict
**Problem:** `get_attack_to_cast()` advances `attack_rotation_index` BEFORE confirming cast success  
**CB3D Contract:** Index must only advance when outcome is `ACCEPTED`  
**Impact:** Standard mode will skip skills on failed/rejected casts  
**Solution:** 
1. Rename `get_attack_to_cast()` to `get_next_attack_key()` (no side effects)
2. Add `reserve_next_skill()` → `commit_cast(outcome)` → `release_cast()`
3. `attack_rotation_index` only advances in `commit_cast()` when outcome ACCEPTED
4. Standard mode also uses reservation/commit pattern (not just combo mode)

### Issue B: Missing Combo Mode Integration
**Problem:** `hunt_orchestrator._try_cast_skills()` doesn't check `combo.enabled`  
**Impact:** Combo timing (sweet-spot detection) is never triggered  
**Solution:** 
```python
if cfg.get("combo", {}).get("enabled", False):
    # Call wait_for_hit_zone with timeout
    # Use CabalComboDetector
    # Fall back on timeout
else:
    # Use standard APS timing
```

### Issue C: Bottleneck Detection Missing
**Problem:** `calculate_timing()` doesn't validate rotation time < max cooldown  
**Impact:** User may enable combo with a stalled rotation and blame system  
**Solution:** Add warning log if `total_rotation_cast_time >= max(cooldowns)`

---

## 5. Readiness Assessment

| Component | Ready? | Blocker? |
|--|--|--|
| CB3D framework files | ✅ Yes (restored) | ⚠️ Not integrated |
| CB6 combo detector | ✅ Yes (PR #274 merged) | ⚠️ Not wired to orchestrator |
| Runtime skill management | ⚠️ Partial | 🔴 **YES** - needs refactor |
| Orchestrator loop | ⚠️ Partial | 🔴 **YES** - needs dual-mode logic |
| Timing calculator | ✅ Most ready | ⚠️ Missing one validation |
| Config structure | ✅ Yes | ✅ No |
| Tests | ❌ No | 🔴 **YES** - must write 6 test scenarios |

---

## 6. Recommended Actions for CB3C Session

**Option A: Full CB3C Implementation (30 min timebox may not be enough)**
1. Add CB3D methods to `runtime.py` (20 min)
2. Add dual-mode logic to `hunt_orchestrator.py` (15 min)
3. Add bottleneck validation to `calculator.py` (5 min)
4. Write unit tests (25 min) ← **Exceeds timebox**
5. Manual game validation (5 min)
→ **Total: ~70 minutes** (2.3x timebox)

**Option B: MVP Release (Split into 2 phases) - RECOMMENDED**
- **Phase 1 (Session CB3C-A, 30 min):**
  1. Add CB3D methods to `runtime.py`
  2. Add dual-mode check to `hunt_orchestrator.py`
  3. Add bottleneck warning to `calculator.py`
  4. Write 3 quick unit tests (standard mode, combo mode, mode-switch)
  5. **Gate:** Code compiles, basic tests pass, no runtime errors
  
- **Phase 2 (Session CB3C-B, 20 min):**
  1. Write remaining 3 unit tests (timeout, fast-break, bottleneck)
  2. Manual game validation (combo mode enabled)
  3. Edge case testing (target death during cooldown guard)
  4. **Gate:** All 6 tests pass, combo timing works in live game

**Option C: Async Refactor Track**
- CB3C does minimum viable integration (30 min)
- Schedule separate "pointer cleanup" task to consolidate index advancement logic
- Allows CB3C gate to open faster; technical debt tracked separately

---

## 7. Deployment Risk

🟡 **MODERATE RISK**

- ✅ CB3D framework tested independently (16 tests passing)
- ✅ CB6 combo detection tested independently (11 tests passing)
- ⚠️ **Untested Integration:** Runtime ↔ Orchestrator ↔ Combo Detector
- ⚠️ **Pointer Logic Change:** `get_attack_to_cast()` refactor may break training mode if not careful
- 🔴 **No integration tests yet** for dual-mode switch mid-hunt

**Mitigation:**
- Keep existing `get_attack_to_cast()` behavior intact for standard mode initially
- Add new methods without breaking old ones
- Add feature flag in config to disable combo mode if needed
- Extensive testing before merge to main

---

## 8. Summary Table

| Area | Status | Notes |
|--|--|--|
| **CB3D Dependency** | ⚠️ Restored but not integrated | Files present; wiring needed |
| **CB6 Dependency** | ✅ Complete | Already in app_state_controller |
| **Timing Calculator** | ✅ Ready | Just needs bottleneck check |
| **SkillRuntime Methods** | ❌ Needs 4 methods | Priority: `get_next_combo_skill()`, `commit_cast()` |
| **Orchestrator Dual-Mode** | ❌ Missing | Core CB3C work item |
| **Unit Tests** | ❌ 0/6 scenarios | Need all 6 for gate pass |
| **Manual Validation** | ⏳ Pending | Blocked on code completion |

---

## 9. Next Session Checklist

- [ ] Read CB3D PROMPT to understand reservation/commit model fully
- [ ] Review `cast_delivery.py` CastDeliveryManager API
- [ ] Plan pointer refactor carefully (potential breaking change)
- [ ] Decide: Phase 1 (MVP) or Phase 2 (Full) approach
- [ ] If Phase 1: identify which 3 tests to write first
- [ ] Create branch: `feature/cb3c-timing-integration` or similar
- [ ] Set timer for 25 min; reassess at checkpoint

---

**Prepared by:** Code Review Agent  
**for CB3C Session Prompt:** "Harmonize Timing Calculator with Combo Mode & Fast-Break"
