# Session Prompt R1: Core Gate Remediation

**Timebox:** 25-30 phút  
**Priority:** Critical  
**Dependency:** Không có. Có thể chạy ngay trên branch hiện tại.

## Objective

Khép các blocker đã được kiểm chứng trong CB1, CB2, CB2B, CB4 và CB2D thành một maintenance gate. Session này sửa contract/runtime/test đang sai; không triển khai UX3A, UX3, UX3B, CB2C hoặc thay đổi thiết kế UI mới.

Kết quả cần đạt là các foundation contract nhất quán để các session tiếp theo không xây UI trên config/runtime chưa hoàn chỉnh.

## Verified Starting Evidence

- `tests/unit/test_target_bar_detector.py` pass, nhưng `HuntOrchestrator` tạo `TargetBarDetector()` không truyền HWND/client bounds.
- `tests/integration/test_orchestrator_loop.py` fail vì assertion target-key search mode không khớp hành vi loop hiện tại.
- CB2B OCR -> DB mapping có code nhưng không có focused test cho `TargetNameReader`/lookup contract.
- CB4 migration/config tests pass, nhưng production code còn normal-Hunt legacy consumer `monster_list`, gồm `ui/windows/auto_hunt.py` và các path cần xác minh qua repository search.
- CB2D queue/detector tests pass, nhưng `RuntimeMonsterQueue(publish_callback=None)` và `maybe_publish()` chưa được gọi, nên không có detection snapshot callback cho UI tương lai.

Không coi các dòng trên là lý do để bỏ preflight: xác minh lại trên HEAD trước khi sửa. Nếu evidence không tái hiện, ghi `UNVERIFIED` kèm command/output ngắn thay vì sửa theo giả định.

## Target Files

- Modify: `lib/features/hunt/hunt_orchestrator.py`
- Modify: `lib/vision/target_bar_detector.py` chỉ nếu cần để nhận client geometry đã xác minh
- Modify: `tests/integration/test_orchestrator_loop.py`
- Create/Add: focused tests cho CB2B dưới `tests/unit/vision/` hoặc `tests/unit/features/hunt/`
- Modify: active legacy consumer(s) xác minh được qua `monster_list` production search
- Modify: `lib/features/hunt/runtime_monster_queue.py` chỉ nếu cần publish contract
- Add: focused callback publish test cho CB2D

Không sửa `monster_rotation` UI, không tạo dialog picker, không thêm `target_policy` UI, không đổi target-selection policy của CB2C, và không sửa file JSON trực tiếp từ view.

## Work Items

### 1. CB1 Runtime Client Geometry

- Lấy HWND đã được xác minh của cửa sổ game trước khi khởi tạo detector; truyền `hwnd` vào `TargetBarDetector` hoặc truyền client geometry từ capture owner có contract tương đương.
- `GetClientRect(hwnd)` chỉ là nguồn kích thước client; ROI cuối cùng vẫn phải tính theo frame capture thực tế nếu hai kích thước khác nhau.
- Không gọi Win32 hoặc Tkinter từ worker ngoài contract hiện có; không thay đổi HSV/ROI authoritative của CB1.
- Thêm test mock `win32gui.GetClientRect()` xác minh detector dùng client size hợp lệ và fallback frame size khi mismatch.

### 2. CB2 Search/Attack Regression

- Reproduce `tests/integration/test_orchestrator_loop.py` trước khi sửa.
- Giữ invariant: target key chỉ được tap khi `mode == "search"` và không có active target; không thêm tap riêng cho ALIVE -> DEAD.
- Sửa test fixture/sequence nếu assertion không mô hình hóa đúng state transition; chỉ sửa loop nếu runtime thực sự vi phạm invariant.
- Xóa biến CB2 không còn dùng sau khi test pass, không để dead state che semantics.

### 3. CB2B Evidence And Fallback Contract

- Thêm focused tests cho ROI preprocess/OCR failure-safe bằng mock `pytesseract`, `find_monster_by_name_api` exact/fuzzy lookup, cache/throttle 2 giây, UI callback được schedule về Main Thread và clear target cache khi mất target.
- Fallback unknown phải có contract đầy đủ cho consumer hiện tại, gồm `id=0`, `name`, `hp=None`, `defense=None` nếu field này là một phần record contract.
- Khi fuzzy lookup có nhiều candidate hợp lệ, log warning có query và số candidate; vẫn dùng heuristic đã công bố.
- Không yêu cầu cài Tesseract thật để unit test; không gọi Tkinter từ worker.

### 4. CB4 Remove Active Legacy Rotation Consumers

- Search production code cho `monster_list`, `monsters`, `attack_keys` và `skills`; phân loại migration/test/docs/training-only versus active normal-Hunt path.
- Mọi active normal-Hunt path phải đọc canonical `monster_rotation` dict. Không chuyển list canonical thành list tên/ID rồi ghi ngược legacy.
- `training_monster_list` chỉ giữ lại nếu là training-only và không được dùng làm normal-Hunt source.
- Không tạo compatibility read/write adapter ngoài migration boundary. Nếu một consumer thực sự đã retired, xóa/disable path sau khi repository search chứng minh không còn caller.
- Giữ CB4 atomic writer/single writer nguyên vẹn; R1 không tạo đường save thứ hai.

### 5. CB2D Publish Contract

- `HuntOrchestrator` nhận optional detection snapshot callback theo dependency injection; App/UI adapter phải schedule callback về Main Thread.
- Khởi tạo `RuntimeMonsterQueue` với callback đó và gọi `maybe_publish(schedule_ui_task)` sau mỗi `scene_detector.process_frame(frame)` hoặc ngay sau queue mutation có thể thay snapshot.
- Không import Tkinter vào CB2D, không tự tạo Treeview/Listbox, không persist snapshot và không tự promote runtime item sang rotation.
- Publish phải giữ rate limit tối đa 5 FPS, immutable tuple/copy, và callback absent là no-op an toàn.

## Mandatory Validation

```powershell
py -m pytest tests/unit/test_target_bar_detector.py -q
py -m pytest tests/integration/test_orchestrator_loop.py -q
py -m pytest tests/test_migration.py tests/unit/features/hunt/test_config_migrator.py -q
py -m pytest tests/unit/features/hunt/test_runtime_monster_queue.py tests/unit/features/hunt/test_scene_monster_detector.py -q
py -m pytest <new-CB2B-tests> <new-CB2D-publish-tests> -q
```

Thêm repository search assertion hoặc command evidence: không còn active normal-Hunt production consumer đọc/ghi `monster_list`; mọi kết quả còn lại phải thuộc migration, docs, test, training-only hoặc UI widget name không phải config source.

## Session Boundary Gate

**PASSED khi:**

- CB1 runtime có HWND/client geometry contract đã kiểm chứng; unit test CB1 pass.
- Integration test CB2 pass, target key không spam trong attack và không double-tap khi target chết.
- CB2B có focused test pass cho OCR/DB fallback/cache/UI scheduling.
- Không còn active normal-Hunt legacy `monster_list` consumer.
- CB2D publish callback hoạt động, rate-limited, immutable và có focused test pass.
- Không có Tkinter call từ worker, không có config write mới, và toàn bộ command validation pass.

**BLOCKED/REVERTED khi:**

- Cần thay đổi UX3/UX3B/CB2C để che một foundation contract còn thiếu.
- Không phân loại được legacy consumer trước khi xóa/chuyển đổi.
- Detection callback yêu cầu UI widget hoặc worker gọi Tkinter.
- Focused validation còn fail ở phút 25; phút 25-30 chỉ dành cho direct repair hoặc revert các thay đổi của R1.

Báo `PASSED`, `BLOCKED_BY_LEGACY_CONSUMER`, `UNVERIFIED` hoặc `REVERTED` kèm danh sách command đã chạy và kết quả.
