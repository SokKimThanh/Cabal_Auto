# Session Prompt UX3B: Three-Mode Detection Workspace

**Timebox:** 25-30 phút  
**Priority:** High  
**Dependencies:** CB4, UX3A, UX3 và CB2D đã đạt gate

## Objective

Mở rộng panel Monster Rotation thành workspace ba chế độ săn, đồng thời hiển thị
hai danh sách độc lập trong chế độ tự nhận diện:

- danh sách quái chỉ định đánh (`monster_rotation`, persist);
- danh sách quái phát hiện (`runtime_detection_snapshot`, transient).

Cho phép người dùng kéo một quái đã resolve DB từ danh sách phát hiện sang danh
sách chỉ định đánh. Thao tác tương đương phải dùng được bằng nút `+`, double-click
và phím Enter.

UX3B chỉ điều khiển UI/state cấu hình. CB2C sở hữu quyết định attack; CB2D sở hữu
detection snapshot.

## Ba Mode

Dùng segmented control cố định ở đầu panel, không dùng dropdown:

```text
[ Quái đã chọn | Tự nhận diện | Mọi mục tiêu ]
```

Mapping config:

- `Quái đã chọn` -> `target_policy="configured_only"`
- `Tự nhận diện` -> `target_policy="all_resolved"`
- `Mọi mục tiêu` -> `target_policy="any_target"`

Mode mặc định là `configured_only`.

Không hiển thị đồng thời toàn bộ nội dung của ba mode. Segmented control giữ
kích thước ổn định; content bên dưới thay đổi theo mode.

## Target Files

- Modify: `ui/tabs/hunt_tab.py`
- Modify: `app_gui.py` cho callback/state hiện đang thuộc App
- Modify: `ui/controllers/app_state_controller.py` để round-trip `target_policy`
- Modify: `lib/i18n/translations.py`
- Create: `tests/ui/tabs/test_hunt_target_modes.py`
- Create/Add: test promotion/drag-drop phù hợp

Không sửa CB2D detector, CB2C state machine, input backend hoặc file config trực
tiếp từ view.

## Layout Theo Mode

### 1. Quái Đã Chọn

Chỉ hiển thị configured list của UX3:

```text
Danh sách sẽ đánh                         [+] [↑] [↓] [Xóa]
[#101] Slime Xanh - Lv.3 | HP: 150
[#205] Orc - Lv.8 | HP: 900
```

Mọi thao tác giữ semantics UX3 và chỉ persist qua Apply All.

### 2. Tự Nhận Diện

Layout rộng:

```text
Quái phát hiện trong khu vực       Danh sách sẽ đánh
✓ Slime #101   Có trong DB    ->    Slime #101
✓ Orc #205     Có trong DB          
⚠ Unknown      Không có DB
```

Layout hẹp: xếp hai danh sách theo chiều dọc, detected list ở trên, configured
list ở dưới. Không ép minsize làm vỡ 1366x768.

Detected rows:

- `db_match`: hiển thị ID, tên, level/HP nếu có, confidence và action `+`.
- `db_miss`: hiển thị tên OCR an toàn nếu có, badge `Không có trong DB`, không có
  action promote.
- `unmapped_visual`: hiển thị `Chưa xác định`, template label phục vụ diagnostics,
  không tuyên bố tên quái và không promote.
- stale item được CB2D loại theo TTL; UI không tự sở hữu timer thứ hai.

Configured rows giữ nguyên từ UX3.

### 3. Mọi Mục Tiêu

Không hiển thị rotation editor như nội dung chính. Hiển thị trạng thái ngắn:

```text
Cảnh báo: Không kiểm tra danh tính mục tiêu
Target hiện tại: <OCR name hoặc Không xác định>
Trạng thái: Đang tìm / Đang đánh
```

Không dùng modal cảnh báo mỗi lần Start. Cảnh báo luôn hiện trong mode bằng
`UIStyle.COLOR_WARNING`.

Configured list vẫn tồn tại trong RAM/persist và phải xuất hiện lại nguyên vẹn
khi quay về `configured_only`.

## Promotion Từ Detected Sang Configured

Chỉ item `resolution_state="db_match"` và `monster_id > 0` được promote.

Các cách thao tác tương đương:

1. Kéo-thả detected row sang configured list.
2. Nhấn icon `+` trên row hoặc toolbar.
3. Double-click row.
4. Chọn row rồi nhấn Enter.

Tất cả gọi một method duy nhất, ví dụ:

```python
promote_detected_monster(runtime_item) -> PromotionResult
```

Method phải:

- copy đúng bốn field canonical: `monster_id`, `name`, `priority`, `dungeon_id`;
- không copy bbox/confidence/timestamp/HP/level;
- chống trùng theo `(monster_id, dungeon_id)`;
- thêm cuối danh sách và normalize priority 1..N;
- mark `has_unsaved_changes=True`;
- không gọi `save_hunt_config()`;
- không tự chuyển mode khi chỉ promote.

Sau promote thành công, row detected có trạng thái `Đã thêm`; không biến mất khỏi
snapshot nếu quái vẫn đang được phát hiện.

Unknown/unmapped drop phải bị từ chối, không mutation configured list và phát
status không gây modal.

## Drag-and-Drop Contract

Không thêm dependency DnD ngoài nếu Tkinter bindings hiện có đủ dùng.

- Bắt đầu drag chỉ từ detected list.
- Payload là runtime item ID hoặc immutable item snapshot, không phải index hiển
  thị vì list có thể cập nhật trong lúc drag.
- Khi drop, resolve payload theo snapshot mới nhất; stale/missing item bị từ chối.
- Highlight vùng drop hợp lệ, dọn highlight ở release/cancel.
- Không reorder configured list bằng cùng handler; reorder vẫn dùng UX3 controls.
- Không gọi Tkinter từ CB2D worker; snapshot được schedule về main thread.

## Chuyển Mode Và Hunt Lifecycle

- Khi Hunt chưa chạy: đổi mode cập nhật state RAM và mark unsaved.
- Khi Hunt đang chạy: segmented control bị disable; mode snapshot tại Start không
  đổi giữa combat.
- Stop Hunt: control được enable lại.
- Đổi mode không xóa configured list hoặc runtime snapshot.
- `all_resolved` tự cho phép CB2C dùng resolved runtime candidates, nhưng không tự
  persist chúng.
- `any_target` không tự tạo DB record hoặc configured entry.

## Update Hiệu Năng

- Nhận immutable detection snapshot tối đa 5 FPS từ CB2D.
- Reconcile row theo `runtime_id`; không xóa và dựng lại toàn widget mỗi tick nếu
  dữ liệu không đổi.
- Giữ selection/scroll khi snapshot cập nhật.
- Không auto-scroll nếu người dùng đang xem row cũ.
- Không truy vấn DB trong render loop; dùng metadata đã resolve/cache từ CB2D/UX3.

## I18n

Thêm key `vi/en`:

- `hunt_policy_configured`
- `hunt_policy_auto_detect`
- `hunt_policy_any_target`
- `detected_monsters_title`
- `configured_monsters_title`
- `monster_db_match`
- `monster_db_missing`
- `monster_unidentified`
- `monster_promote`
- `monster_promoted`
- `monster_duplicate`
- `any_target_warning`

## Automated Tests

1. Ba segment map đúng ba giá trị `target_policy`.
2. Mode mặc định `configured_only`.
3. Chuyển mode không mất configured list.
4. Hunt running disable mode control; Stop enable lại.
5. Detection `db_match` xuất hiện với action promote.
6. `db_miss/unmapped_visual` vẫn hiển thị nhưng không promote được.
7. Drag, `+`, double-click và Enter gọi cùng promotion method.
8. Promote copy đúng bốn field canonical, không copy runtime metadata.
9. Duplicate `(monster_id, dungeon_id)` không được thêm lần hai.
10. Promote mark dirty nhưng không gọi save config.
11. Stale runtime ID trong lúc drag không mutation configured list.
12. Snapshot reconcile giữ selection/scroll và không tạo row churn khi unchanged.
13. Layout rộng/hẹp không overlap hoặc minsize overflow.
14. Chuyển `vi/en` giữ mode và dữ liệu.

Chạy:

```powershell
py -m pytest tests/ui/tabs/test_hunt_target_modes.py -q
py -m pytest tests/unit/test_monster_rotation_queue.py -q
py -m pytest tests/unit/features/hunt/test_runtime_monster_queue.py -q
```

## Manual Validation

1. Chạy app ở 1366x768 và chuyển qua cả ba mode.
2. Trong Auto Detect, xác nhận hai list hiển thị đúng.
3. Kéo quái DB-match sang configured list; xác nhận dirty indicator bật.
4. Thử kéo unknown; xác nhận bị từ chối và app không crash.
5. Thử `+`, double-click và Enter.
6. Start Hunt; xác nhận mode bị khóa. Stop; mode dùng lại được.
7. Quay về Quái đã chọn; configured list vẫn nguyên.
8. Apply All rồi reload; chỉ configured list và `target_policy` được persist.

## Session Boundary Gate

**PASSED khi:**

- Ba mode có UI/semantics rõ ràng và map đúng config.
- Auto Detect có hai danh sách độc lập.
- Chỉ DB-match được promote và không tự save.
- Unknown vẫn hiển thị nhưng không trở thành configured/attack candidate.
- Mode không đổi giữa Hunt session.
- Runtime updates mượt, giữ selection/scroll và không chặn main thread.
- Test mục tiêu pass.

**BLOCKED/REVERTED khi:**

- CB2D chưa publish detection snapshot có `resolution_state`.
- Promote dựa vào list index hoặc có race với snapshot update.
- Runtime item tự ghi vào `monster_rotation`.
- Mode switching làm mutation Orchestrator đang chạy.
- Unknown được promote hoặc tự động đánh trong mode có kiểm tra danh tính.

Báo cáo `PASSED`, `BLOCKED_BY_CB2D` hoặc `REVERTED` ở phút 25.
