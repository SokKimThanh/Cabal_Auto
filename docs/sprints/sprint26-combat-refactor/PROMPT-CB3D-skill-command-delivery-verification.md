# Session Prompt CB3D: Skill Command Delivery Verification

**Timebox:** 25-30 phút  
**Priority:** Critical  
**Dependencies:** CB1, CB2E, CB4, UX4.2 và CB6 đã đạt gate

## Objective

Phân biệt rõ việc Windows đã gửi phím với việc game thực sự nhận và thi triển
skill. Chỉ commit cooldown, rotation pointer và thống kê thành công sau khi có
acknowledgment phù hợp; không đánh dấu `success=True` chỉ vì hàm input không ném
exception.

Session này tạo framework verification và ít nhất một acknowledgment strategy có
bằng chứng thực tế. Không được tuyên bố mọi skill đã được xác minh nếu chưa có ROI
hoặc tín hiệu quan sát tương ứng.

## Hiện Trạng Mã Nguồn

- `AppStateController._try_cast_skills()` gọi `tap()`, cập nhật `_last_cast` và
  `SkillStats.record_cast(success=True)` ngay lập tức.
- `HuntRunner._try_cast_skills()` cũng coi `tap()` hoặc
  `keyboard.press_and_release()` không lỗi là cast thành công.
- `SkillRuntime.get_attack_to_cast()` tăng rotation index trước khi biết input có
  được game nhận hay không.
- `SkillRuntime.mark_cast()` chỉ ghi timestamp, không có pending/ack state.
- `SkillStats.record_cast()` mặc định `success=True` nên success rate hiện phản
  ánh command attempt, không phản ánh game acceptance.
- CB2E chỉ xác minh transport/capability của input backend; API gửi thành công
  không chứng minh một skill cụ thể đã cast.
- CB6 phát hiện hit-zone Combo nhưng hit-zone trước khi gửi phím chưa phải
  acknowledgment sau khi gửi.

## Target Files

- Create: `lib/features/skills/cast_delivery.py`
- Create: `lib/vision/skill_cooldown_detector.py`
- Modify: `lib/features/skills/runtime.py`
- Modify: `lib/features/skills/skill_stats.py`
- Modify: `ui/controllers/app_state_controller.py`
- Modify: `lib/features/hunt/hunt_orchestrator.py`
- Modify: `lib/features/combo/combo_timing_detector.py` để trả transport/trigger
  evidence thay vì tự commit success
- Add tests dưới `tests/unit/features/skills/` và `tests/unit/vision/`

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

Dùng CB6 làm trigger timing và hậu kiểm trạng thái Combo Bar sau khi gửi:

- Hit-zone trước key press chỉ là `TRIGGER_READY`.
- CB2E trả `SENT` chỉ là transport evidence.
- `ACCEPTED` cần frame sau-send cho thấy Combo Bar tiến/reset sang trạng thái kế
  tiếp theo contract đã calibrate.
- Nếu không có hậu kiểm đáng tin cậy, outcome là `UNVERIFIED`; không gọi
  `mark_cast()` như success.

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
3. Gửi skill qua cùng CB2E InputBackend của hunt session.
4. Transport fail -> release `REJECTED`, áp failure policy.
5. Transport sent -> chờ acknowledgment có timeout nhưng vẫn kiểm tra Stop/target
   death theo lát nhỏ, không block worker bằng sleep nguyên khối.
6. Accepted -> commit runtime, stats accepted và tiếp tục timing.
7. Unverified -> không commit success; áp policy và không spam lại skill.
8. Target chết trong pending -> `CANCELLED`; CB3C xử lý fast-break sau đó.
9. Mọi UI update đi qua `schedule_ui_task()`.

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

Chạy:

```powershell
py -m pytest tests/unit/features/skills/test_cast_delivery.py -q
py -m pytest tests/unit/features/skills/test_skill_runtime_reservation.py -q
py -m pytest tests/unit/vision/test_skill_cooldown_detector.py -q
py -m pytest tests/integration/test_orchestrator_loop.py -q
py -m pytest tests/unit/test_combo_timing_detector.py -q
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

- Transport sent và cast accepted là hai trạng thái riêng.
- Ít nhất một strategy có frame/evidence thực tế và test deterministic.
- Cooldown/pointer/stats chỉ commit sau accepted.
- Timeout mơ hồ là unverified, không spam retry.
- Không fallback input âm thầm và Stop luôn phản hồi.
- CB6/CB3C không còn mark success ngay khi gửi phím.
- Test mục tiêu pass.

**UNVERIFIED khi:**

- Framework đúng nhưng chưa có ROI/frame mẫu hoặc game evidence để xác nhận.
- Không được đổi nhãn thành PASSED chỉ vì unit mock pass.

**REVERTED khi:**

- Rotation/cooldown vẫn advance trước acknowledgment.
- Stats vẫn mặc định success khi chỉ gửi command.
- Retry có thể spam skill hoặc background mode chiếm input người dùng.

Báo cáo `PASSED`, `UNVERIFIED`, `BLOCKED_NO_ACK_SIGNAL` hoặc `REVERTED` ở phút 25.
