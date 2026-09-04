# Session Prompt CB3D: Skill Command Delivery Verification

**Timebox:** 25-30 phút  
**Priority:** Critical  
**Dependencies:** CB1, CB2E, CB4, UX4.2 và ✅ CB6 (hoàn tất - merged PR #274)

## Objective

Phân biệt rõ việc Windows đã gửi phím với việc game thực sự nhận và thi triển
skill. Chỉ commit cooldown, rotation pointer và thống kê thành công sau khi có
acknowledgment phù hợp; không đánh dấu `success=True` chỉ vì hàm input không ném
exception.

**CB6 Status (✅ COMPLETE - PR #274 merged):**
- `CabalComboDetector` có sẵn trong `lib/features/combo/combo_timing_detector.py`
- CB6 detect hit-zone trước khi gửi phím (TRIGGER_READY)
- CB6 có callback để gửi phím từ app_state_controller
- CB6 không tự commit success - chỉ phát hiện trigger và gọi callback
- CB3D sẽ dùng CB6 làm pre-cast signal detection, không phải acknowledgment

**CB3D Scope (NEW - này là session này):**
- Tạo framework để phân biệt `SENT` (phím được gửi) vs `ACCEPTED` (game thực thi)
- Tạo `skill_cooldown_detector.py` để verify hotbar cooldown visual
- Tạo `cast_delivery.py` để manage CastOutcome state machine
- Cập nhật skill runtime để sử dụng reservation/commit pattern
- Test + manual validation với Combo mode (sử dụng CB6 trigger + post-send verification)

Session này tạo framework verification và ít nhất một acknowledgment strategy có
bằng chứng thực tế (combo bar hoặc hotbar cooldown). Không được tuyên bố mọi skill đã được xác minh nếu chưa có ROI
hoặc tín hiệu quan sát tương ứng.

---

## ✅ REVIEW SUMMARY: CB3D Architecture Complete, Orchestrator Integration Pending

**TL;DR:** 
CB3D framework (85-90% complete) provides the contract, state machine, and verification detectors. The unit tests all pass (16/16). **Immediate next step:** Integrate CastDeliveryManager into hunt_orchestrator worker loop so it actually uses the framework instead of calling _try_cast_skills() directly.

### Architecture Strengths:
1. **Clear separation of concerns:**
   - CastDeliveryManager: Handles reservation/commit/release state
   - SkillCooldownDetector: Analyzes ROI pixels, no input sending
   - SkillRuntime: Exposes reserve/commit/release transaction methods
   - app_state_controller: Calls send_key(), maps outcomes to stats
   - hunt_orchestrator: (TODO) Coordinate the full flow

2. **Outcome-based stats instead of boolean:**
   - SkillStats now tracks: attempt_count, transport_sent_count, accepted_count, rejected_count, unverified_count, cancelled_count
   - Success rate = accepted_count / attempt_count (meaningful)
   - Legacy `success=True` flag supported but deprecated

3. **CB6 ready for post-send verification:**
   - wait_for_hit_zone() returns bool (did_trigger)
   - Callback fires key press
   - app_state_controller handles outcome mapping
   - Ready for orchestrator to wait for post-send combo bar state

### Known Gaps:
1. **hunt_orchestrator not integrated:** Still calls _try_cast_skills() directly instead of using reserve → send → wait_ack → commit flow
2. **Acknowledgment detection:** Framework exists but orchestrator doesn't loop/poll for acknowledgment
3. **Policy enforcement:** CastOutcome enums defined but no pause_skill/stop_hunt/degraded_state actions in orchestrator yet
4. **Testing:** Unit tests mock; manual game validation needed for both hotbar_cooldown and combo strategies

### Next Session Action (To Hit PASSED Gate):
1. Modify hunt_orchestrator to use CastDeliveryManager (20-25 min)
2. Implement acknowledgment polling loop with timeout (5-10 min)
3. Manual testing with live game for 1 skill (5-10 min)
4. Report PASSED with orchestrator + 1 ack strategy validated

---

## Hiện Trạng Mã Nguồn

**✅ CB3D IMPLEMENTATION STATUS: 85-90% COMPLETE**

### Completed Files & Components:
- ✅ `lib/features/skills/cast_delivery.py` - CastDeliveryManager, TransportStatus, CastOutcome enums, CastReservation dataclass (2 tests passing)
- ✅ `lib/vision/skill_cooldown_detector.py` - Baseline capture + pixel diff detection (2 tests passing)
- ✅ `lib/features/skills/runtime.py` - reserve_next_skill(), commit_cast(), release_cast() methods (1 test passing)
- ✅ `lib/features/skills/skill_stats.py` - outcome-based counters (attempt_count, accepted_count, rejected_count, unverified_count, cancelled_count)
- ✅ `ui/controllers/app_state_controller.py` - Using CastOutcome enum, outcome-based recording via record_cast(outcome=...)
- ✅ `lib/features/combo/combo_timing_detector.py` - CB6 (PR #274 merged, 11 tests passing)
- ✅ `hunt_config.json` - Combo section added (enabled: false)
- ✅ **All 16 tests passing:** cast_delivery (2), skill_runtime_reservation (1), skill_cooldown_detector (2), combo_timing_detector (11)

### Remaining Integration Gaps:
- ❌ `lib/features/hunt/hunt_orchestrator.py` - Chưa fully tích hợp CastDeliveryManager vào worker loop
  - Cần: reserve_next_skill() → send key → wait_for_acknowledgment() → commit_cast()/release_cast()
  - Hiện tại: Vẫn gọi _try_cast_skills() trực tiếp mà chưa integrate reservation flow
- ❓ **Acknowledgment strategies** - Framework đã có nhưng chưa fully hooked vào worker:
  - `hotbar_cooldown` strategy: skill_cooldown_detector sẵn có, cần callback từ orchestrator
  - `combo` strategy: CB6 sẵn có, cần post-send verification logic trong orchestrator
- ⚠️ **Policy enforcement** - CastOutcome constants có nhưng chưa áp dụng failure policy (pause_skill, stop_hunt, degraded_state)

## Remaining Work

**Priority 1: Orchestrator Integration** (Needed for PASSED gate)
- Modify: `lib/features/hunt/hunt_orchestrator.py`
  - Integrate CastDeliveryManager into worker loop
  - Implement: `reserve_next_skill()` → `send_key()` → `wait_for_acknowledgment()` loop
  - Handle: `CANCELLED` outcome when target dies mid-acknowledgment (fast-break)
  - Failure policy: REJECTED (transport fail) → stop_hunt; UNVERIFIED (timeout) → pause_skill
  - Status: Orchestrator must NOT commit success unless outcome is ACCEPTED

**Priority 2: Acknowledgment Verification** (Validation testing)
- hotbar_cooldown: Script phải calibrate hotbar_roi + test skill_cooldown_detector với real frame samples
- combo: CB6 trigger (TRIGGER_READY) + post-send combo bar state detection (state machine validation)
- Test: Manual validation with 3+ skill rotations in actual game

**Priority 3: Policy Enforcement** (If time permits)
- Add degraded_state tracking and stop_hunt triggers
- Add UI notifications for UNVERIFIED/REJECTED skills

Không thêm fallback `keyboard.press_and_release()` ngoài CB2E backend. Không gọi
Tkinter từ worker.

## Thuật Ngữ Và Contract

```python
class TransportStatus(Enum):
    SENT = "sent"
    FAILED = "failed"

class CastOutcome(Enum):
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    UNVERIFIED = "unverified"
    CANCELLED = "cancelled"
```

- `SENT`: backend đã gửi keydown/keyup; chưa nói game có nhận.
- `ACCEPTED`: có tín hiệu hậu kiểm đáng tin cậy.
- `REJECTED`: transport fail hoặc có tín hiệu rõ ràng rằng cast không thể xảy ra.
- `UNVERIFIED`: hết timeout nhưng không đủ bằng chứng kết luận.
- `CANCELLED`: target chết, Stop Hunt hoặc session đổi trước khi acknowledgment.

Không chuyển `UNVERIFIED` thành `REJECTED` chỉ vì timeout.

## Cast Reservation State Machine

```text
READY
  -> reserve skill/token                 -> RESERVED
RESERVED
  -> InputBackend.tap() failed           -> REJECTED
  -> transport SENT                      -> WAITING_ACK
WAITING_ACK
  -> visual acknowledgment               -> ACCEPTED
  -> timeout, no conclusive evidence     -> UNVERIFIED
  -> target/session cancelled            -> CANCELLED
ACCEPTED
  -> commit cooldown + advance pointer + success stats
REJECTED/UNVERIFIED/CANCELLED
  -> do not report success
  -> release reservation according to guarded policy
```

Chỉ một skill command được pending trên một lane tại một thời điểm, trừ khi Combo
contract chứng minh cần pipeline khác và có test riêng.

## SkillRuntime Transaction Contract

Thay API chọn rồi advance sớm bằng reservation:

```python
reservation = runtime.reserve_next_skill(lane, now)
runtime.commit_cast(reservation.token, accepted_at)
runtime.release_cast(reservation.token, outcome)
```

Yêu cầu:

- `reserve_next_skill()` không advance pointer và không bắt đầu cooldown.
- Reservation có token, skill ID/key, lane, created time và expected strategy.
- Pending reservation ngăn gửi lại cùng skill mỗi worker tick.
- Chỉ `commit_cast(ACCEPTED)` cập nhật `last_cast_time` và advance pointer đúng một
  lần.
- `release_cast()` không advance pointer.
- Token stale/double commit bị từ chối idempotently.
- Stop/reset cancel reservation và release key qua CB2E.
- Standard và Combo mode dùng cùng transaction contract; không có pointer thứ
  hai tự advance trước acknowledgment.

## Acknowledgment Strategies

### 1. `hotbar_cooldown`

Dùng cho skill thường/buff khi cấu hình có normalized `hotbar_roi`:

1. Chụp ROI baseline ngay trước khi gửi phím.
2. Sau `SENT`, lấy frame mới có timestamp lớn hơn thời điểm gửi.
3. So sánh ROI bằng tín hiệu ổn định, ví dụ giảm brightness/saturation hoặc
   overlay cooldown khác baseline, với threshold được cấu hình/test bằng frame
   mẫu.
4. Yêu cầu tín hiệu ổn định ít nhất hai frame mới trước khi `ACCEPTED`.
5. ROI invalid, frame stale/None hoặc biến đổi không đủ rõ -> `UNVERIFIED`, không
   giả success.

`skill_cooldown_detector.py` chỉ phân tích ROI; không gửi input và không update UI.

### 2. `combo`

Dùng CB6 (✅ hoàn tất) làm trigger timing và hậu kiểm trạng thái Combo Bar sau khi gửi:

- Hit-zone trước key press chỉ là `TRIGGER_READY` (do CB6 phát hiện).
- CB2E trả `SENT` chỉ là transport evidence.
- **THAY ĐỔI:** CB6 `wait_for_hit_zone()` không tự commit success; thay vào đó nó gọi callback và trả `bool did_trigger`.
  - Nếu `did_trigger=True`: frame đó cho tín hiệu hit-zone, nhưng chưa là game acknowledgment.
  - `ACCEPTED` cần frame sau-send cho thấy Combo Bar tiến/reset sang trạng thái kế tiếp theo contract đã calibrate.
  - Nếu không có hậu kiểm đáng tin cậy, outcome là `UNVERIFIED`; không gọi `mark_cast()` như success.
- CB6 callback và app_state_controller sẽ gửi phím, sau đó cast_delivery framework chờ acknowledgment từ vision

### 3. `none`

Không có detector phù hợp:

- command có thể được gửi;
- outcome phải là `UNVERIFIED`;
- UI/stats không được hiển thị là thành công;
- policy quyết định pause skill, stop hunt hoặc cho phép tiếp tục ở degraded mode.

### Tín Hiệu Không Đủ Làm Acknowledgment

Không dùng riêng các tín hiệu sau để xác nhận một skill cụ thể:

- `PostMessage`/`SendInput` trả thành công;
- Target Bar vẫn alive;
- HP target giảm mà không chứng minh skill nào gây ra;
- hết `cast_time` theo cấu hình;
- không có exception.

HP delta có thể là telemetry phụ, không phải per-skill acceptance mặc định.

## Failure Policy

Config dùng chung:

```json
{
  "skill_delivery": {
    "unverified_policy": "pause_skill",
    "transport_failure_policy": "stop_hunt",
    "max_transport_retries": 1,
    "retry_backoff_ms": 300,
    "degraded_threshold": 3
  }
}
```

Policy:

- Transport `FAILED`: retry tối đa giới hạn sau backoff; vẫn fail thì stop Hunt
  mặc định.
- `UNVERIFIED`: mặc định quarantine/pause riêng skill đó trong phiên, không retry
  ngay vì game có thể đã nhận nhưng detector bỏ lỡ.
- Không fallback âm thầm từ background sang foreground input.
- N outcome `UNVERIFIED/REJECTED` liên tiếp làm backend/session `DEGRADED`, cập
  nhật status và dừng theo policy.
- Người dùng phải chủ động chọn foreground mode nếu background không tương thích.
- Không hiện modal lặp trong worker; status/log và một notification main-thread
  là đủ.

## SkillStats Contract

Thay thống kê boolean mơ hồ bằng counters/outcome rõ ràng:

- `attempt_count`
- `transport_sent_count`
- `accepted_count`
- `rejected_count`
- `unverified_count`
- `cancelled_count`
- `last_outcome`

`success_rate = accepted_count / attempt_count`. Không để default
`success=True`; caller phải truyền outcome tường minh.

Nếu cần giữ API cũ, adapter legacy phải map rõ là `UNVERIFIED`, không tự map sang
`ACCEPTED`.

## Tích Hợp Orchestrator

1. CB2C phải cho phép attack target trước khi reserve attack skill.
2. Reserve skill từ runtime; lấy frame baseline theo acknowledgment strategy.
3. **CB6 integration (✅ sẵn có):**
   - Khi combo mode bật: `combo_detector.wait_for_hit_zone()` được gọi từ `app_state_controller._try_cast_skills()` với callback để gửi phím
   - CB6 đã có orchestrator hierarchy navigation (`getattr(app, "hunt_orchestrator", None)` → `bot_manager` → `screen_capture`)
   - Combo Bar acknowledgment sẽ được xử lý bởi CB3D framework trong `cast_delivery.py`
4. Gửi skill qua cùng CB2E InputBackend của hunt session.
5. Transport fail -> release `REJECTED`, áp failure policy.
6. Transport sent -> chờ acknowledgment có timeout nhưng vẫn kiểm tra Stop/target death theo lát nhỏ, không block worker bằng sleep nguyên khối.
7. Accepted -> commit runtime, stats accepted và tiếp tục timing.
8. Unverified -> không commit success; áp policy và không spam lại skill.
9. Target chết trong pending -> `CANCELLED`; CB3C xử lý fast-break sau đó.
10. Mọi UI update đi qua `schedule_ui_task()`.

## Automated Tests

### Cast Delivery / Runtime

1. Reserve không advance pointer/cooldown.
2. Accepted commit đúng một lần và advance đúng một lần.
3. Rejected/unverified/cancelled không advance.
4. Pending reservation ngăn duplicate send mỗi tick.
5. Double commit/stale token không mutation state.
6. Stop/reset cancel pending reservation.
7. Standard và Combo mode dùng cùng transaction API.

### Cooldown Detector

1. Synthetic baseline -> dark/overlay frames ổn định hai frame -> accepted.
2. Một frame nhiễu rồi baseline -> không accepted.
3. ROI invalid/frame stale/None -> unverified, không crash.
4. Resolution/DPI khác nhau với normalized ROI vẫn crop đúng.

### Orchestrator / Backend

1. InputBackend `FAILED` không gọi commit và không ghi success.
2. `SENT` nhưng không ack -> unverified, không ghi accepted.
3. Unverified không retry ngay; skill bị quarantine theo policy.
4. Retry transport không vượt max/backoff.
5. Không fallback background -> foreground tự động.
6. Target chết/Stop trong WAITING_ACK thoát sớm và cancel.
7. Ba failure liên tiếp đưa session vào degraded state đúng policy.

### Stats

1. Attempt/sent/accepted/rejected/unverified/cancelled tăng đúng outcome.
2. Success rate chỉ tính accepted/attempt.
3. API legacy không tự ghi accepted.

**Current Test Status (✅ 16/16 PASSING):**

```powershell
# Run all CB3D-related tests
py -m pytest tests/unit/features/skills/test_cast_delivery.py tests/unit/features/skills/test_skill_runtime_reservation.py tests/unit/vision/test_skill_cooldown_detector.py tests/unit/test_combo_timing_detector.py -v

# Results:
# ✅ test_cast_delivery_manager_add_remove (1/2)
# ✅ test_cast_delivery_manager_lane_limit (2/2)
# ✅ test_reserve_commit_release (1/1)
# ✅ test_cooldown_detection_success (1/2)
# ✅ test_cooldown_detection_no_baseline (2/2)
# ✅ CB6: 11 combo timing detector tests PASSING
# Total: 16/16 ✅
```

## Manual Calibration Và Validation

1. Chọn một skill thường có vị trí hotbar cố định.
2. Calibrate `hotbar_roi` và lưu frame baseline/cooldown mẫu phục vụ test.
3. Gửi skill ở foreground mode, xác nhận cooldown detector chuyển `ACCEPTED`.
4. Gửi bằng background mode đã CB2E verify, xác nhận cùng tín hiệu.
5. Cố tình dùng sai key hoặc skill chưa sẵn sàng, xác nhận không báo accepted.
6. Đưa cửa sổ khác lên foreground; xác nhận không nhận phím skill ngoài ý muốn.
7. Stop giữa WAITING_ACK; xác nhận không stuck key/thread.
8. Với skill `ack_strategy=none`, xác nhận UI hiển thị `Chưa xác minh`, không phải
   `Thành công`.

## Session Boundary Gate

**PASSED khi:**

✅ **All framework pieces implemented & unit tested:**
- CastDeliveryManager with lane-based reservation ✓
- SkillCooldownDetector with baseline ROI comparison ✓
- SkillRuntime.reserve/commit/release methods ✓
- SkillStats outcome counters ✓
- CastOutcome enum in place ✓
- CB6 trigger detection (PR #274 merged) ✓

✅ **Orchestrator integration complete:**
- hunt_orchestrator uses reservation flow for attack & buff skills
- Transport failed → outcome=REJECTED, skill not committed
- Acknowledgment timeout → outcome=UNVERIFIED, skill not committed  
- Target died mid-ack → outcome=CANCELLED, fast-break to CB3C
- Cooldown/pointer only advance after outcome=ACCEPTED

✅ **Acknowledgment verification working:**
- At least ONE strategy fully validated:
  - `hotbar_cooldown`: Real hotbar ROI + sample frames tested
  - OR `combo`: CB6 trigger + post-send combo bar state verified in game
- Manual testing confirms: Send skill → wait ack → commit only if ACCEPTED
- Non-ACCEPTED skills do NOT advance rotation or update cooldown

✅ **All 16 unit tests pass** + manual validation complete

**UNVERIFIED / BLOCKED_NO_ACK_SIGNAL khi:**

- Framework đúng nhưng orchestrator chưa tích hợp (hunt_orchestrator vẫn bypass)
- Chỉ mock frame tests pass; chưa có real game evidence
- hotbar_cooldown chưa calibrate hoặc combo bar verification chưa implement
- CB6 vẫn bypass thay vì fully integrate vào cast delivery flow

**REVERTED khi:**

- Rotation/cooldown vẫn advance trước acknowledgment.
- Stats vẫn mặc định success khi chỉ gửi command.
- Retry có thể spam skill hoặc background mode chiếm input người dùng.

Báo cáo `PASSED`, `UNVERIFIED`, `BLOCKED_NO_ACK_SIGNAL` hoặc `REVERTED` ở phút 25.
