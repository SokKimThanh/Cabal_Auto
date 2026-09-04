# Session Prompt CB2D: Runtime Scene Monster Detection Queue

**Timebox:** 25-30 phút  
**Priority:** Critical  
**Dependencies:** CB5, CB2B và CB4 đã đạt gate

## Objective

Phát hiện các quái có visual template hợp lệ trong frame của cửa sổ game, resolve
chúng về `monster_id` trong DB, tạo `runtime_detection_snapshot` phục vụ UI và
một `runtime_attack_queue` an toàn để CB2C chọn mục tiêu cần đánh.

Cả hai cấu trúc runtime không được ghi vào `hunt_config.json` và không được thay
thế `monster_rotation`. Chúng chỉ phản ánh candidate detector đang nhìn thấy.

## Giới Hạn Nguồn Dữ Liệu

`monsters.db` chỉ chứa metadata như ID, tên, level và HP; DB không chứa đủ đặc
trưng hình ảnh để tự nhận diện mọi quái trên màn hình.

Code hiện có:

- `ScreenCapture.get_latest_frame()` cung cấp frame theo HWND.
- `VisionEngine.detect_monster_pipeline()` trả `Detection` với bbox, score và
  `template_id`.
- `Template` hiện chỉ có `id/path/threshold/scales/enabled`.
- `vision_templates.json` chưa ánh xạ template với `monster_id`.
- HSV detection trả `template_id="hsv_target"` và không xác định được loại quái.

Vì vậy chỉ detection từ template có mapping DB rõ ràng mới được auto-enqueue.
Không suy diễn ID từ filename và không coi HSV blob là một quái đã resolve.

## Target Files

- Modify: `lib/vision/template_loader.py`
- Modify: `lib/vision/vision_engine.py` chỉ khi cần truyền metadata mapping ra
  detection result
- Create: `lib/features/hunt/runtime_monster_queue.py`
- Create: `lib/features/hunt/scene_monster_detector.py`
- Modify: `lib/features/hunt/hunt_orchestrator.py` để nhận snapshot runtime, không
  để queue điều khiển attack trực tiếp
- Modify: `lib/data/vision_templates.json` chỉ để thêm mapping cho asset thật đang
  tồn tại và đã xác minh
- Create tests tương ứng dưới `tests/unit/features/hunt/`

Không sửa UX3 persistence hoặc tự ghi `monster_rotation`.

## Template Mapping Contract

Mở rộng `Template` bằng metadata optional:

```python
monster_id: int | None = None
dungeon_id: str | None = None
```

Persist trong `vision_templates.json`:

```json
{
  "id": "slime_green_body",
  "path": "assets/images/monsters/slime_green.png",
  "monster_id": 101,
  "dungeon_id": null,
  "threshold": 0.75,
  "scales": [0.8, 1.0, 1.2],
  "enabled": true
}
```

Yêu cầu:

- `monster_id` phải resolve qua `get_monster_by_id_api()` trước khi template được
  dùng cho runtime queue.
- Mapping thiếu/sai: template vẫn có thể dùng cho diagnostics nhưng detection
  không được auto-enqueue.
- Không tự thêm mapping giả vào asset `monster_hp_bar`, skill icon hoặc test
  template.
- Nếu repository chưa có template thân quái phù hợp: báo
  `BLOCKED_NO_VISUAL_ASSETS`; không tuyên bố có thể nhận diện mọi quái DB.

## Runtime Detection Contract

Mỗi item hiển thị là immutable snapshot:

```python
{
    "runtime_id": str,
    "monster_id": int,
    "name": str,
    "dungeon_id": str | None,
    "bbox": tuple[int, int, int, int],
    "center": tuple[int, int],
    "confidence": float,
    "template_id": str,
    "resolution_state": "db_match" | "db_miss" | "unmapped_visual",
    "first_seen": float,
    "last_seen": float,
}
```

`runtime_detection_snapshot` phải:

- deduplicate cùng `monster_id` và bbox có IoU/proximity gần nhau;
- cập nhật `last_seen`, bbox và confidence thay vì append mỗi frame;
- chỉ publish tối đa 5 FPS;
- loại item khi không thấy quá `runtime_detection_ttl_sec`, mặc định 1.0 giây;
- có capacity, mặc định 50 item, và drop confidence thấp nhất khi đầy;
- bảo vệ state worker bằng lock hoặc ownership một thread;
- publish tuple/copy bất biến, không đưa list mutable chung sang UI/Orchestrator.

Candidate chưa resolve vẫn có thể xuất hiện trong snapshot hiển thị với
`monster_id=0`, tên an toàn như `Unknown target` và trạng thái `db_miss` hoặc
`unmapped_visual`. Không được bịa tên/ID từ filename hoặc HSV color.

`runtime_attack_queue` là projection lọc từ detection snapshot:

- chỉ chứa `resolution_state="db_match"` và `monster_id > 0` trong mode
  `configured_only` hoặc `all_resolved`;
- không chứa unknown/unmapped;
- mode `any_target` không dùng queue này để xác nhận danh tính, nhưng CB1 vẫn
  phải xác nhận target bar sống trước khi CB2C cho phép đánh.

## Chính Sách Auto-enqueue

Hỗ trợ ba policy từ `target_policy`:

- `configured_only` mặc định: chỉ enqueue detection có `monster_id` nằm trong
  snapshot `monster_rotation`.
- `all_resolved` opt-in: enqueue mọi detection có mapping DB hợp lệ.
- `any_target`: detection snapshot vẫn phục vụ quan sát, nhưng quyền đánh dựa
  trên target bar của CB1 và không yêu cầu DB match.

Cả hai policy đều chỉ thay đổi runtime queue. Không tự thêm record vào
`monster_rotation` persist và không gọi `save_hunt_config()`.

Unknown, ID 0, mapping DB miss hoặc confidence dưới threshold không được đưa vào
attack queue của hai mode có kiểm tra danh tính. Unknown vẫn được publish cho UI
nếu có detection source hợp lệ.

## Detection Pipeline

1. Lấy latest frame từ ScreenCapture; copy dưới lock theo API hiện có.
2. Chỉ chạy các template ID có `monster_id` hợp lệ.
3. Gọi `VisionEngine.detect_monster_pipeline()` ở worker thread.
4. Không dùng nhánh HSV làm resolved monster candidate.
5. Áp dụng confidence threshold riêng của template và NMS hiện có.
6. Resolve metadata DB một lần cho mỗi monster ID và cache; không query mỗi frame.
7. Cập nhật `RuntimeMonsterQueue`.
8. Publish detection snapshot tới UX3B và attack snapshot tới CB2C qua callback
  thread-safe hoặc queue bounded.
9. UI update, nếu có, phải qua `schedule_ui_task()`; detector không import
   Tkinter.

## Quan Hệ Với UX3, UX3B Và CB2C

- CB4 cung cấp canonical `monster_rotation` và `target_policy` snapshot cho runtime. UX3 chỉ là UI editor của configured list, không là prerequisite của detector.
- UX3B hiển thị detection snapshot, ba mode và thao tác promote sang configured
  list; UX3B không tự quyết định attack.
- CB2D cung cấp detection snapshot cho UX3B và attack queue cho CB2C.
- CB2C vẫn sở hữu desired pointer và quyền quyết định attack.
- CB2D không tap phím, không chọn target và không cast skill.
- Detection biến mất chỉ xóa item runtime, không advance configured rotation.

## Automated Tests

1. Template mapping round-trip giữ `monster_id/dungeon_id`.
2. Mapping thiếu hoặc DB miss không enqueue.
3. HSV `template_id="hsv_target"` không enqueue như monster resolved.
4. Hai detection gần nhau cùng monster được deduplicate.
5. Detection khác bbox đủ xa tạo hai runtime item riêng.
6. TTL loại stale item nhưng không sửa `monster_rotation`.
7. `configured_only` loại monster ngoài config.
8. `all_resolved` nhận monster ngoài config nhưng không gọi save config.
9. Unknown có trong detection snapshot nhưng không có trong resolved attack queue.
10. `any_target` không giả mạo resolved ID cho unknown.
11. Publish rate không vượt 5 FPS.
12. Capacity drop item confidence thấp nhất.
13. Snapshot publish không bị mutation sau đó.
14. Không có Tkinter call trong worker.

Chạy:

```powershell
py -m pytest tests/unit/features/hunt/test_runtime_monster_queue.py -q
py -m pytest tests/unit/features/hunt/test_scene_monster_detector.py -q
py -m pytest tests/vision -k "template or monster" -q
```

## Manual Validation

- Chọn cửa sổ Cabal và xác nhận frame tiếp tục cập nhật khi app không foreground.
- Với một template quái đã map DB, đưa quái vào frame và thấy runtime item xuất
  hiện rồi hết hạn khi quái biến mất.
- Xác nhận không có thay đổi trong `hunt_config.json`.
- So sánh `configured_only` và `all_resolved`.
- Xác nhận CPU không tăng không giới hạn và queue không phình theo frame count.

## Session Boundary Gate

**PASSED khi:**

- Ít nhất một asset quái thật có mapping DB đã được xác minh end-to-end.
- Runtime queue ổn định, deduplicate, bounded và có TTL.
- Không persist auto-detected monsters.
- Unknown/HSV generic không thể trở thành attack candidate.
- CB2D không điều khiển input/attack.
- Test mục tiêu pass.

**BLOCKED/REVERTED khi:**

- Không có visual asset map được với monster DB.
- ID được suy diễn từ tên file hoặc detection generic.
- Runtime queue sửa `monster_rotation`.
- Worker gọi Tkinter hoặc state mutable bị chia sẻ không bảo vệ.

Báo cáo `PASSED`, `BLOCKED_NO_VISUAL_ASSETS` hoặc `REVERTED` ở phút 25.
