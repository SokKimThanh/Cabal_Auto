# Session Prompt CB2C: Target Rotation Acquisition Coordinator

**Timebox:** 25-30 phút  
**Priority:** Critical  
**Dependencies:** CB1, CB2, CB2B, CB2D, CB2E, CB4, UX3 và UX3B đã đạt gate

## Objective

Thực thi `target_policy` đã chọn trong UX3B và đồng bộ nguồn desired target với
mục tiêu mà `HuntOrchestrator` thực sự đánh trong game.

Trong hai mode kiểm tra danh tính, Orchestrator chỉ được chuyển từ `search` sang
`attack` khi target OCR/DB có ID hợp lệ và phù hợp policy. Mode `any_target` bỏ
kiểm tra ID nhưng vẫn bắt buộc CB1 xác nhận target bar sống.

## Hiện Trạng Mã Nguồn

- `HuntOrchestrator` hiện chuyển `search -> attack` khi CB1 thấy bất kỳ target bar
  nào còn sống.
- CB2B đã OCR tên và gọi `find_monster_by_name_api()`, nhưng kết quả chỉ dùng để
  cập nhật text UI; chưa gate quyết định attack.
- `target_key` hiện được tap trong search mode, mặc định là `z`.
- `monster_rotation` chưa được Orchestrator dùng để sở hữu desired target/pointer.
- CB2D cung cấp `runtime_attack_queue` transient từ scene detection.
- CB2E cung cấp injected input backend gắn với selected HWND.
- CB1 chỉ trả alive/not-alive; không có kill event độc lập.

Vì vậy app hiện có thể đánh target không nằm trong danh sách rotation.

## Target Files

- Create: `lib/features/hunt/target_rotation_coordinator.py`
- Modify: `lib/features/hunt/hunt_orchestrator.py`
- Modify: `lib/features/hunt/config_validator.py` chỉ khi cần default/validation
  cho giới hạn cycle
- Modify: `lib/system/hunt_logger.py` chỉ để thêm event có cấu trúc nếu logger
  hiện tại chưa biểu diễn được acquisition decision
- Create: `tests/unit/features/hunt/test_target_rotation_coordinator.py`
- Modify/Add: test tích hợp Orchestrator tương ứng

Không sửa layout UX3, không ghi config và không đọc lại file JSON trong worker
loop.

CB2C dùng runtime snapshot từ CB2D như hint về quái đang hiện diện, nhưng vẫn sở
hữu duy nhất desired pointer. Queue runtime rỗng hoặc item hết TTL không được sửa
`monster_rotation` persist.

## Preflight Gate

Trước khi code, xác nhận:

1. `cfg["monster_rotation"]` là list dict canonical từ CB4.
2. Mỗi entry dùng `{monster_id, name, priority, dungeon_id}`.
3. UX3 round-trip entry mà không làm mất ID/priority/dungeon.
4. UX3B round-trip một trong ba `target_policy` hợp lệ và khóa mode khi Hunt chạy.
5. CB1 `TargetBarDetector.is_target_alive(frame)` và CB2B OCR/DB resolver hoạt
   động qua test riêng.
6. Không còn runtime path chính dùng `monster_list`.
7. CB2D publish immutable runtime snapshot; unknown/unmapped detection không nằm
  trong attack queue.
8. CB2E cung cấp backend hợp lệ; background mode chưa verified phải fail closed.

Nếu fail, báo dependency cụ thể (`BLOCKED_BY_CB4`, `BLOCKED_BY_CB2D`,
`BLOCKED_BY_CB2E` hoặc `BLOCKED_BY_UX3B`); không thêm fallback schema thứ ba.

## Ownership Và Nguồn Sự Thật

- `target_policy`, `monster_rotation` và runtime snapshot được chụp tại Start.
- `TargetRotationCoordinator` sở hữu duy nhất active desired source/index trong
  một hunt session; UI và CB2D không tự advance pointer.
- UX3 chỉ chỉnh cấu hình trước Start và phản ánh trạng thái; UI không tự advance
  pointer hoặc ra lệnh attack.
- Worker không reload `hunt_config.json` mỗi tick.
- Runtime snapshot phải là copy riêng để Apply All giữa phiên không làm mutation
  danh sách đang chạy. Thay đổi cấu hình có hiệu lực ở lần Start tiếp theo.

## Semantics Ba Mode

### `configured_only`

- Desired target lấy từ `monster_rotation` theo sequence/priority.
- Chỉ `resolved_id == desired.monster_id` mới trả `MATCHED`.
- Mismatch/unknown không attack và tiếp tục cycle.
- Completion gate advance configured pointer.

### `all_resolved`

- Desired candidates lấy từ `runtime_attack_queue` của CB2D.
- Chỉ candidate `db_match`, ID > 0 mới hợp lệ.
- Target OCR/DB phải khớp một candidate runtime còn TTL trước khi attack.
- Queue thay đổi được reconcile bằng runtime ID/monster ID; không persist và
  không mutation `monster_rotation`.
- Khi candidate hoàn tất/hết TTL, coordinator chọn candidate resolved kế tiếp
  theo thứ tự ổn định được test (first_seen rồi confidence tie-break).

### `any_target`

- Không yêu cầu OCR hoặc DB match để attack.
- CB1 phải xác nhận target bar sống đủ gate; sau đó mới vào attack.
- Không tạo ID giả, không thêm configured record và không ghi DB/config.
- UI/log phải hiển thị rõ identity có thể là unknown.
- Đây là mode opt-in; nếu game có thể target player/NPC mà CB1 không phân loại
  được, tài liệu/UI phải cảnh báo rủi ro thay vì tuyên bố lọc được.

## State Machine Bắt Buộc

```text
SEARCH_DESIRED
  -> target bar alive
  -> any_target             -> ATTACK_MATCHED
  -> otherwise OCR + DB resolve
  -> ID allowed by policy   -> ATTACK_MATCHED
  -> ID mismatch/unknown    -> CYCLE_TARGET

CYCLE_TARGET
  -> tap target_key qua CB2E InputBackend có rate limit
  -> quay lại SEARCH_DESIRED

ATTACK_MATCHED
  -> CB1 alive              -> tiếp tục cast
  -> CB1 false chưa đủ gate -> DEATH_CONFIRM

DEATH_CONFIRM
  -> target sống lại trong grace window -> ATTACK_MATCHED
  -> false đủ debounce + grace           -> ADVANCE_ROTATION

ADVANCE_ROTATION
  -> tăng pointer theo mode
  -> SEARCH_DESIRED
```

Không dùng `have_target=True` đơn thuần để cho phép attack.

## Matching Contract

Các rule ID dưới đây áp dụng cho `configured_only` và `all_resolved`;
`any_target` dùng CB1 alive gate thay cho identity gate.

1. Normalize desired `monster_id` và DB result ID về cùng kiểu so sánh. DB hiện
   trả ID dạng string; schema CB4 dùng int.
2. ID hợp lệ phải lớn hơn 0.
3. So sánh bằng ID là điều kiện chính.
4. Tên chỉ dùng cho status/log, không dùng để cho phép attack nếu desired ID hoặc
   resolved ID bằng 0.
5. Khi resolve theo tên, truyền `desired.dungeon_id` cho
   `find_monster_by_name_api()` nếu có để giảm ambiguity.
6. OCR rỗng, exception, DB miss hoặc ID 0 đều là `UNKNOWN`; không attack.
7. Không persist OCR result, HP hoặc runtime state vào `monster_rotation`.

## Rotation Và Runtime Semantics

- `sequence`: giữ thứ tự snapshot từ UX3.
- `priority`: sort snapshot một lần theo `priority` tăng dần, tie-break theo thứ
  tự cấu hình ban đầu.
- Sau `ADVANCE_ROTATION`, pointer wrap về 0 khi hết danh sách.
- Rotation rỗng hoặc không có entry ID hợp lệ: không Start attack; chuyển state
  error/status rõ ràng, không fallback đánh target bất kỳ.
- Training mode giữ hành vi riêng hiện tại và không cycle target nếu cấu hình quy
  định không tap target key.
- `all_resolved` không dùng configured pointer; nó dùng active runtime candidate
  do cùng coordinator sở hữu.
- `any_target` không có desired ID pointer; completion chỉ quay về search/cycle.

## Cycle Guard

Dùng default có validation:

- `target_cycle_min_interval_sec`: 0.20
- `target_acquire_timeout_sec`: 8.0
- `target_cycle_max_attempts`: 20
- `target_death_confirm_sec`: 0.35
- tiếp tục dùng `target_lost_debounce_frames` của CB1/CB2

Yêu cầu:

- Không tap `target_key` nhanh hơn min interval.
- Timeout/max attempts không làm worker treo hoặc spam phím.
- Khi hết giới hạn: log warning, cập nhật status và retry có backoff hoặc chuyển
  desired target theo policy được test; không tự attack target hiện tại.
- Stop Hunt phải ngắt mọi state ngay, không chờ hết timeout.

## Tích Hợp HuntOrchestrator

1. Tạo coordinator từ immutable rotation snapshot trước worker loop.
2. Trong search mode, khi có target bar sống, chạy OCR/DB theo cache/throttle của
  CB2B rồi đưa resolved ID vào coordinator, trừ `any_target` không cần OCR gate.
3. Chỉ đặt `mode="attack"` khi coordinator trả `MATCHED` theo active policy.
4. Với `MISMATCH` hoặc `UNKNOWN`, không gọi attack skills; cycle target theo guard.
5. Mọi target/skill tap đi qua InputBackend của CB2E; không import global `tap`
  trong coordinator.
6. Trong attack mode, giữ nguyên CB2: không tap target key và chỉ cast skills.
7. Chỉ vào death-confirm nếu target trước đó đã `MATCHED`, đã có ít nhất một frame
   alive trong attack phase và sau đó false đủ debounce.
8. Nếu target bar sống lại trong grace window, hủy advance và tiếp tục đánh cùng
   desired target.
9. Sau confirmed completion, advance pointer rồi clear cached OCR/target UI và
   quay về search.
10. Mọi cập nhật Tkinter phải qua `schedule_ui_task()`; coordinator không import
   Tkinter.

## Status Và Logging

Phát status/log tối thiểu:

- desired target ID/name;
- resolved target ID/name;
- decision: `MATCHED`, `MISMATCH`, `UNKNOWN`, `TIMEOUT`;
- pointer advance từ target nào sang target nào;
- số cycle attempts.

Không log mỗi worker tick; chỉ log khi decision/state thay đổi để tránh spam.

UI có thể hiển thị chuỗi ngắn:

```text
Đang tìm: [#101] Slime Xanh
Bỏ qua: [#205] Orc
Đang đánh: [#101] Slime Xanh
Tiếp theo: [#205] Orc
```

## Automated Tests

### Unit: TargetRotationCoordinator

1. Rotation rỗng không cho phép attack.
2. Sequence giữ thứ tự và wrap pointer.
3. Priority sort ổn định theo priority.
4. Desired ID `101`, resolved ID `101` -> `MATCHED`.
5. Desired ID `101`, resolved ID `205` -> `MISMATCH`.
6. OCR/DB miss hoặc ID 0 -> `UNKNOWN`, không attack.
7. ID string `"101"` khớp schema int `101` sau normalize.
8. Mismatch không advance persistent pointer và không sửa snapshot.
9. Confirmed completion advance đúng một lần.
10. Target sống lại trong grace window không advance.
11. Stop/reset xóa state runtime an toàn.
12. `configured_only` không match quái ngoài rotation.
13. `all_resolved` match candidate DB-resolved còn TTL và bỏ unknown.
14. `all_resolved` queue thay đổi không mutation configured rotation.
15. `any_target` cho phép target bar alive mà không cần OCR ID.
16. `any_target` không tạo/persist monster record.

### Integration: HuntOrchestrator

1. Target sai: `try_cast_skills(..., attack_phase=True)` không được gọi.
2. Target đúng: transition search -> attack và cho phép attack skills.
3. Unknown OCR: cycle có rate limit, không attack.
4. N target sai liên tiếp: số lần tap không vượt max/rate limit.
5. Matched alive -> false ngắn -> alive: không advance.
6. Matched alive -> false đủ debounce/grace: advance một lần và search target kế.
7. Stop Hunt trong acquisition timeout kết thúc worker.
8. UI callbacks chỉ được gọi qua `schedule_ui_task()`.
9. Mỗi policy chỉ có một đường đi vào attack phase đúng contract.
10. Đổi mode trong UI khi Hunt chạy không làm thay policy snapshot.

Chạy:

```powershell
py -m pytest tests/unit/features/hunt/test_target_rotation_coordinator.py -q
py -m pytest tests/integration/test_orchestrator_loop.py -q
py -m pytest tests/test_migration.py tests/unit/test_monster_rotation_queue.py -q
```

## Manual Validation

Với rotation `[Slime #101, Orc #205]`:

1. Khóa Orc khi desired là Slime: bot không cast và tiếp tục cycle.
2. Khóa Slime: bot bắt đầu cast.
3. Làm target bar mất thoáng qua rồi xuất hiện lại: pointer không đổi.
4. Slime chết, target bar mất đủ gate: desired chuyển Orc.
5. Target OCR không rõ: bot không đánh bừa.
6. Dừng Hunt trong lúc tìm: cycle dừng ngay.

## Session Boundary Gate

**PASSED khi:**

- Attack chỉ xảy ra sau `MATCHED` theo active policy.
- Với `configured_only/all_resolved`, attack chỉ xảy ra sau ID match policy.
- Với `any_target`, attack chỉ xảy ra sau CB1 alive gate và không giả mạo ID.
- Mismatch/unknown không thể đi vào attack phase.
- Pointer chỉ do coordinator sở hữu và advance đúng một lần sau completion gate.
- Không spam target key và Stop luôn phản hồi.
- Không mutation config/runtime từ UI thread sai ranh giới.
- Test unit và integration mục tiêu pass.

**BLOCKED/REVERTED khi:**

- `monster_list` vẫn là runtime source.
- OCR/DB result chưa có contract ID ổn định.
- Bất kỳ target sống nào vẫn có thể kích hoạt attack.
- Mất target thoáng qua làm advance pointer.
- Có Tkinter call từ worker hoặc có nguồn pointer thứ hai.

Báo cáo `PASSED`, dependency `BLOCKED_*` cụ thể hoặc `REVERTED` ở phút 25.
