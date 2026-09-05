# Review: CB4A vs Tình Trạng Hiện Tại (2026-09-05)

**Tóm tắt:** CB4A là **bước nâng cấp của UX5.1** (thêm real-time HP + status state machine). Codebase **80% sẵn sàng** cho CB4A nhưng cần **tích hợp UX5.1 base trước** (shell + fallback schema). CB4A có thể implement ngay sau UX5.1 đầy đủ.

---

## 1. Quan Hệ CB4A ↔ UX5.1: **Confirmed - Phụ Thuộc Chuỗi**

### Dependency Chain

```
UX5.1 (Base Layer)
  ├─ get_target_monster_info() - 2-tầng fallback (DB → JSON → mặc định)
  ├─ Target Card Panel UI - 776x552px, 1 Label widget
  ├─ PhotoImage memory management (clear-before-set pattern)
  ├─ i18n keys (target_card.level, target_card.status_*, etc.)
  └─ Tests: Schema fallback, zero-asset, memory stability

      ↓ CB4A (Enhancement Layer - depends on UX5.1)
      ├─ target_hp_reader.py - wraps CB1.get_hp_percentage()
      ├─ HP% throttling + smoothing (150-200ms intervals)
      ├─ Status FSM (APPROACHING → ATTACKING → DEAD)
      ├─ Race condition handling (rapid re-target)
      └─ Tests: HP transition, rapid re-target, placeholder flag
```

### Key Points

- **UX5.1 is a prerequisite** for CB4A: CB4A assumes `get_target_monster_info()` exists and works
- **CB4A enhances, not replaces** UX5.1: Adds HP reader + FSM on top of existing panel
- **Same i18n namespace**: Both use `target_card.*` keys (no duplication)
- **Same fallback schema**: Both use `is_placeholder` flag + `hp: 10000` default

---

## 2. Tình Trạng Codebase: **80% Sẵn Sàng**

### ✅ Đã Có (Sẵn dùng cho CB4A)

| Component | File | Status | Note |
|---|---|---|---|
| **hunt_tab.py** | `ui/tabs/hunt_tab.py` | ✅ Framework | Chưa có target card panel, nhưng structure sẵn |
| **MonsterDatabase** | `database.py` | ✅ Hoạt động | Connects to monsters.db, schema ready |
| **MonsterRepository** | `repositories/monster_repository.py` | ✅ Hoạt động | load_all_monsters(), save_monster(), transaction safe |
| **monsters.db** | Root folder | ✅ Tồn tại | SQLite DB with 9 tables (schema ready) |
| **monsters.json** | `lib/data/monsters.json` | ✅ Tồn tại | Fallback library (minimal seed data for now) |
| **CB1 Vision Layer** | `lib/vision/target_bar_detector.py` | ✅ Hoạt động | `get_hp_percentage()` method available |
| **i18n System** | `lib/i18n/translations.py` | ✅ Ready | Self-registers GLOBAL_TRANSLATIONS |
| **UIStyle** | `lib/ui_style.py` | ✅ Ready | Colors, fonts, DPI scaling support |
| **schedule_ui_task** | `ui/controllers/app_state_controller.py` | ✅ Available | Thread-safe UI scheduling callback |

### ⚠️ Thiếu / Chưa Implement

| Component | Purpose | Severity | Notes |
|---|---|---|---|
| **get_target_monster_info()** | Tra cứu quái 2-tầng DB→JSON | **BLOCKING** | Cần implement ở UX5.1 trước |
| **Target Card Panel UI** | Giao diện thẻ quái | **BLOCKING** | Cần implement ở UX5.1 trước |
| **target_hp_reader.py** | HP% calculation + throttling | HIGH | Cần create; phải gọi vào CB1 |
| **Status FSM** | APPROACHING → ATTACKING → DEAD states | HIGH | Cần implement ở hunt_orchestrator |
| **i18n keys** | target_card.* dịch | MEDIUM | Chỉ cần thêm ~10 keys (5 min work) |
| **Test suite** | `tests/unit/test_target_card_*.py` | MEDIUM | Cần merge CB4A + UX5.1 tests |
| **Race condition handling** | Cancel pending clear on rapid re-target | MEDIUM | `self.after_cancel(pending_clear_id)` |

### 🔴 **Critical Blocker: UX5.1 Must Implement First**

CB4A **cannot start** until UX5.1 provides:
1. ✅ `get_target_monster_info()` function
2. ✅ Target Card Panel widget
3. ✅ PhotoImage lifecycle management (`clear_target_photo()`, `set_target_photo()`)
4. ✅ i18n namespace + keys

**Without these, CB4A has no foundation to build on.**

---

## 3. CB4A-Specific Dependencies & Integrations

### 3a. **CB1 Dependency: TargetBarDetector.get_hp_percentage()**

**Status:** ✅ Available

```python
# CB1 signature (from lib/vision/target_bar_detector.py)
def get_hp_percentage(self, frame: np.ndarray) -> float:
    # Returns: float in range [0.0, 100.0]
```

**CB4A Usage:**
- `target_hp_reader.py` must call this method
- No duplication of pixel-reading logic
- Wrap CB1 result for throttling + smoothing

**Action:** Verify CB1 method exists and signature matches when implementing CB4A

---

### 3b. **Thread-Safety Requirements (CB4A extends UX5.1)**

**Background Thread:**
- Read frame from screen capture
- Call `TargetBarDetector.get_hp_percentage(frame)` → float %
- Apply throttling (150-200ms interval)
- Apply smoothing (1% delta threshold)
- **Post result to Main Thread**

**Main Thread (via schedule_ui_task):**
- Receive pre-calculated % from background thread
- Update ttk.Progressbar: `progressbar.config(value=hp_percent)`
- Update Label: `status_label.config(text=f"HP: {hp_percent:.1f}%")`
- **Never call OpenCV/vision logic here**

**Pattern:**
```python
# Background thread
hp_percent = calculate_hp_percent(frame)  # Throttled + smoothed
self.schedule_ui_task(lambda: self.update_hp_display(hp_percent))

# Main thread (inside lambda)
def update_hp_display(self, hp_percent):
    self.hp_progressbar.config(value=hp_percent)
    self.hp_label.config(text=f"{hp_percent:.1f}%")
```

---

### 3c. **Status FSM: Orchestrator Integration**

**HuntOrchestrator must track states:**

```
State Machine:
  IDLE
    → target locked + HP detected → APPROACHING
    
  APPROACHING
    → HP starts decreasing → ATTACKING
    
  ATTACKING
    → HP reaches 0 → TARGET_DEAD
    
  TARGET_DEAD
    → (schedule 0.2s clear) → IDLE
```

**What Orchestrator Must Do:**

1. **Lock target:**
   ```python
   # When target found
   self.target_state = "APPROACHING"
   self.schedule_ui_task(lambda: ui.set_target_card(monster_info))
   ```

2. **Combat begins:**
   ```python
   # When HP changes
   if hp_percent < last_hp_percent:
       self.target_state = "ATTACKING"
       self.schedule_ui_task(lambda: ui.update_status("ATTACKING"))
   ```

3. **Target dies:**
   ```python
   # When HP reaches 0
   self.target_state = "TARGET_DEAD"
   self.schedule_ui_task(lambda: ui.update_status("DEAD"))
   # Schedule clear after 0.2s
   pending_clear_id = self.after(200, lambda: ui.clear_target_card())
   ```

4. **Rapid re-target (race condition fix):**
   ```python
   # New target locked before 0.2s clear completes
   if pending_clear_id:
       self.after_cancel(pending_clear_id)  # Cancel old clear
   self.target_state = "APPROACHING"
   self.schedule_ui_task(lambda: ui.set_target_card(new_monster_info))  # Show new card
   ```

**Key Insight:** All state transitions must go through `schedule_ui_task()` to maintain order and prevent race conditions.

---

## 4. Implementation Order: **2-Phase Approach**

### Phase 1: UX5.1 (Required First)
**Timebox:** 40-50 min
**Deliverable:** Working Target Card panel with safe fallback + memory management
- `get_target_monster_info()` 2-tầng fallback
- Target Card UI (776x552px, PhotoImage)
- i18n keys
- Test suite (8+ tests)

### Phase 2: CB4A (After Phase 1)
**Timebox:** 40-50 min
**Deliverable:** Real-time HP + Status FSM
- `target_hp_reader.py` (HP% + throttling + smoothing)
- Status FSM in orchestrator
- Race condition handling
- Test suite (6 tests from CB4A)

**Total Effort:** 80-100 min (2 focused sprints)

---

## 5. CB4A-Specific Implementation Checklist

### Before Code: Verify Prerequisites
- [ ] UX5.1 fully implemented + passing tests
- [ ] `get_target_monster_info()` verified working
- [ ] Target Card Panel rendering correctly
- [ ] PhotoImage lifecycle tested
- [ ] CB1 `get_hp_percentage()` method confirmed available

### Phase 2 Code Tasks
- [ ] Create `lib/vision/target_hp_reader.py`
  - `def calculate_target_hp_percent(frame) -> float:` (wraps CB1)
  - Implement throttling (150-200ms intervals)
  - Implement smoothing (1% delta threshold)
  - Thread-safe queue/callback to Main Thread
- [ ] Update `hunt_orchestrator.py`
  - Add `target_state` tracking (IDLE/APPROACHING/ATTACKING/DEAD)
  - Implement state transitions with `schedule_ui_task()`
  - Implement 0.2s clear delay + race condition cancellation
- [ ] Update `hunt_tab.py` (Target Card panel from UX5.1)
  - Add `update_status(status_string)` method
  - Add `update_hp_display(hp_percent)` method
  - Add `clear_target_card()` method
- [ ] Add i18n keys *(if not already done by UX5.1)*
  - `target_card.status_idle`
  - `target_card.status_approaching`
  - `target_card.status_attacking`
  - `target_card.target_dead`
- [ ] Implement test suite (6 tests from CB4A spec)
  - Test Case 1: Valid Monster
  - Test Case 2: Missing Asset / Unlisted Mob
  - Test Case 3: Combat Transition
  - Test Case 4: Rapid Re-target Race
  - Test Case 5: Placeholder HP not leaking
  - Test Case 6: No duplicate HP logic

### Phase 2 Validation
- [ ] HP% updates smoothly (no jitter)
- [ ] Status transitions in correct order
- [ ] Race condition: rapid re-target doesn't clear new card
- [ ] All 6 tests pass
- [ ] DPI rendering: 100%-150% looks good
- [ ] i18n: Vietnamese + English text correct

---

## 6. Known Issues & Design Constraints

### Issue 1: **MonsterRepository lacks get_by_id/get_by_name**
- **Current:** `MonsterRepository.load_all_monsters()` returns all
- **Problem:** Inefficient for single lookup
- **Solution (for UX5.1):** Either
  - Add `get_by_id(id: str) -> Optional[Dict]` method to MonsterRepository
  - OR implement `get_target_monster_info()` in `lib/features/monsters/monster_repo.py` which queries manually
- **Recommendation:** Add method to MonsterRepository for consistency

### Issue 2: **monsters.json has minimal seed data**
- **Current:** Only 1 test monster ('a')
- **Impact:** Fallback layer will be heavily used
- **Note:** Not a CB4A blocker; fallback mechanism is designed for this scenario

### Issue 3: **hunt_orchestrator integration point unclear**
- **Current:** hunt_orchestrator.py has basic structure
- **Problem:** Unclear where to hook status updates
- **Solution (for CB4A):** Document exact integration points in CB4A prompt before coding
- **Action:** Add pseudo-code example to CB4A prompt if not already there

---

## 7. Timing Estimates

| Task | Component | Effort | Blocker |
|---|---|---|---|
| **UX5.1: get_target_monster_info()** | monster_repo.py | 5-10 min | YES (blocks CB4A) |
| **UX5.1: Target Card Panel** | hunt_tab.py | 10-15 min | YES |
| **UX5.1: PhotoImage mgmt** | hunt_tab.py | 5 min | YES |
| **UX5.1: i18n keys** | translations.py | 5 min | YES |
| **UX5.1: Tests** | test_target_card_shell.py | 10-15 min | No (for MVP) |
| **CB4A: target_hp_reader.py** | target_hp_reader.py | 10-15 min | Depends on UX5.1 |
| **CB4A: FSM + orchestrator** | hunt_orchestrator.py | 15-20 min | Depends on UX5.1 |
| **CB4A: Race condition** | hunt_orchestrator.py | 5 min | Depends on UX5.1 |
| **CB4A: Tests** | test_target_card_cb4a.py | 10-15 min | Depends on UX5.1 |

**Total:** 80-100 min (2 focused sprints, ~40-50 min each)

---

## 8. Decision Points for CB4A

| Question | Options | Recommendation |
|---|---|---|
| **Implement CB4A now or after UX5.1?** | Now (risky) / After UX5.1 (safer) | **After UX5.1** (de-risk) |
| **Where to put get_target_monster_info()?** | monster_repo.py / lib/features/monsters/ | **monster_repo.py** (existing pattern) |
| **Add get_by_id() to MonsterRepository?** | Yes / No, inline lookup | **Yes** (reusable, clean) |
| **HP throttle interval (150-200ms)?** | Configurable / Hardcoded | **Configurable in hunt_cfg** |
| **Smoothing threshold (1% delta)?** | Configurable / Hardcoded | **Hardcoded** (UI preference, not user config) |

---

## 9. Summary Table: Readiness Assessment

| Criterion | Status | Details |
|---|---|---|
| **Architecture Clarity** | ✅ Clear | CB4A = UX5.1 enhancement; dependency chain defined |
| **Blocking Issues** | 🔴 UX5.1 First | CB4A cannot start without UX5.1 base |
| **Codebase Readiness** | ✅ 80% | DB, repository, vision layer all in place |
| **Dependencies** | ✅ Available | CB1, i18n, UIStyle, schedule_ui_task ready |
| **Documentation** | ✅ Complete | Detailed CB4A prompt + UX5.1 prompt |
| **Orchestrator Clarity** | ⚠️ Needs detail | FSM integration points need pseudo-code example |
| **Test Plan** | ✅ Ready | 6 tests specified in CB4A prompt |
| **Risk Level** | 🟡 MEDIUM | Depends entirely on UX5.1 success |

---

## Recommendation

### ✅ **Proceed with UX5.1 First (This Sprint)**
1. Implement UX5.1 (40-50 min)
2. Pass all UX5.1 tests + manual validation
3. Report UX5.1 PASSED to gate review
4. **Then** CB4A can proceed safely next sprint

### 🔴 **Do NOT Start CB4A Until UX5.1 Complete**
- Risk: Duplicated work if UX5.1 implementation differs
- Risk: CB4A test failures due to missing UX5.1 foundation
- Better: Sequential implementation with verified handoff

### 📋 **CB4A Pre-Implementation Checklist**
Before coding CB4A (when UX5.1 is PASSED):
- [ ] Add `get_by_id()` method to MonsterRepository (if not done by UX5.1)
- [ ] Add pseudo-code example to CB4A prompt showing exact orchestrator integration points
- [ ] Verify CB1 `get_hp_percentage()` signature and availability
- [ ] Decide: HP throttle interval configurable or hardcoded?

---

**Report Date:** 2026-09-05  
**Reviewed By:** Copilot Agent  
**Status:** Ready for Phase 1 (UX5.1) implementation; CB4A scheduled for Phase 2
