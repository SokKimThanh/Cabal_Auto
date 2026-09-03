# Session Prompt R1: Core Gate Remediation, Current-State Reconciliation And CB2E Readiness

**Timebox:** 25-30 phút  
**Priority:** Critical  
**Dependency:** Không có. Có thể chạy ngay trên branch hiện tại.

## Objective

Khép các blocker còn lại đã được kiểm chứng trong CB5, CB2D, UX3, UX3A và CB4 thành một maintenance gate độc lập. Session này cũng xác nhận precondition để bắt đầu CB2E, nhưng không triển khai background input trong R1. CB1/CB2/CB2B chỉ được recheck khi cần để bảo toàn contract; không triển khai UX3B, CB2C hoặc thay đổi thiết kế UI mới.

Kết quả cần đạt là các foundation contract nhất quán để các session tiếp theo không xây UI trên config/runtime chưa hoàn chỉnh.

## Verified Starting Evidence On Current HEAD

- CB1/CB2/CB2B focused tests: `12 passed`; CB2 integration hiện pass và Orchestrator đã truyền HWND cho TargetBarDetector.
- CB2D queue/detector/publish tests: `7 passed`; callback đã wire và `maybe_publish()` được gọi sau `process_frame()`.
- UX3 rotation tests: `8 passed`; canonical add/remove/reorder và Apply serialization đã được sửa.
- UX3A/UX3B UI tests: **12 failed**; UX3A fail vì headless fixture trộn `DummyWidget` với Tk thật, UX3B fail vì `DummyVar` thiếu `trace_add`. Đây là test infrastructure drift cần sửa trước khi gate UI.
- CB4 migration/config tests: `28 passed`; `ui/windows/auto_hunt.py` đã đổi sang `monster_rotation`, nhưng `DataSyncManager`/lifecycle/setup còn legacy `monster_list` references cần phân loại.
- CB5 scanner test: `1 passed`; ScreenCapture suite `28 passed, 4 failed`: FPS vẫn `0.0`, resize không gọi reallocation, minimize path còn `NameError: win_rect`, và có GDI cleanup warning.
- App startup smoke: `APP_STARTUP_OK`.
- CB2E: **chưa triển khai**; chưa có `InputBackend`, background backend, `PostMessage`, capability state hoặc tests.

Không coi các dòng trên là lý do để bỏ preflight: xác minh lại trên HEAD trước khi sửa. Nếu evidence không tái hiện, ghi `UNVERIFIED` kèm command/output ngắn thay vì sửa theo giả định.

## Target Files

- Modify: `ui/windows/auto_hunt.py` và các active normal-Hunt consumer được xác minh
- Modify: `conftest.py` hoặc `tests/unit/dialogs/test_monster_picker.py` để test UX3A dùng cùng một Tk/headless strategy
- Modify: `dialogs/monster_picker.py` chỉ để sửa contract/lifecycle đã chứng minh sai
- Modify: `lib/system/screen_capture.py` để sửa CB5 resize/minimize/stats regression
- Modify: `tests/sprints/sprint23/test_screen_capture.py` fixtures/assertions khi chúng lệch contract đã chốt
- Modify: `tests/ui/tabs/test_hunt_target_modes.py` headless variable fixture để hỗ trợ `trace_add`
- Add: focused CB2B tests dưới `tests/unit/vision/` hoặc `tests/unit/features/hunt/`
- Add: focused CB2D publish callback test
- Modify: `lib/features/hunt/hunt_orchestrator.py` chỉ nếu test phát hiện publish/client-geometry regression

Không sửa `monster_rotation` UI, không tạo dialog picker, không thêm `target_policy` UI, không đổi target-selection policy của CB2C, và không sửa file JSON trực tiếp từ view.

## Work Items

### 1. Recheck CB1/CB2 Foundation

- Xác nhận bằng test hiện tại rằng HWND được lấy trước khi khởi tạo detector và truyền đúng vào `TargetBarDetector`.
- `GetClientRect(hwnd)` chỉ là nguồn kích thước client; ROI cuối cùng vẫn phải tính theo frame capture thực tế nếu hai kích thước khác nhau.
- Không gọi Win32 hoặc Tkinter từ worker ngoài contract hiện có; không thay đổi HSV/ROI authoritative của CB1.
- Thêm test mock `win32gui.GetClientRect()` xác minh detector dùng client size hợp lệ và fallback frame size khi mismatch.

### 2. CB5 ScreenCapture Repair

- Sửa `GetClientRect()` block để mọi biến dùng sau đó (`left`, `top`, `right`, `bottom`, `width`, `height`) được định nghĩa trong cùng scope.
- Giữ kiểm tra `IsWindow()` mỗi vòng, refresh client rect mỗi cycle, reallocate bitmap khi kích thước thay đổi và dùng `_frame_lock` cho swap/read.
- Minimized trả last known good frame; window lost set Event và gọi callback đúng một lần.
- Khôi phục stats update ổn định; cleanup GDI không phát sinh handle warning trong mocked/real lifecycle.
- Bổ sung hoặc sửa focused tests cho resize, minimize, lost signal, concurrent read và FPS. Không hạ assertion chỉ để test pass.

### 3. UX3A Picker Test And Contract

- Reproduce `tests/unit/dialogs/test_monster_picker.py`; sửa test fixture/adapter để không trộn `DummyWidget` với Tk thật.
- Giữ `MonsterPickerDialog` dùng public DB APIs, callback ba field, cache/debounce và modal cleanup.
- Bỏ `minsize` nếu vẫn còn trái prompt; clear `_item_map` trước mỗi render; validate ID/name/dungeon trước khi tạo callback.
- Confirm bằng nút, double-click và Enter phải gọi cùng một method đúng một lần.
- Không để picker tự mutation `monster_rotation`, dirty state hoặc config.

### 4. UX3 Canonical Queue Integration

- Xác nhận result UX3A đi qua một entry point duy nhất của UX3.
- Rotation entry phải chỉ gồm `monster_id`, `name`, `priority`, `dungeon_id`; duplicate theo `(monster_id, dungeon_id)` bị từ chối.
- Add/remove/reorder chỉ dirty RAM; Apply All mới gọi writer và chỉ clear dirty khi save thành công.
- Không để `enabled`, `training_mode`, `level`, `hp` lọt vào normal `monster_rotation`.

### 5. CB2B Focused Evidence

- Thêm focused tests cho ROI preprocess/OCR failure-safe, exact/fuzzy DB lookup, cache/throttle 2 giây, UI scheduling và clear cache khi target mất.
- Fallback unknown phải có contract đầy đủ cho consumer hiện tại, gồm `id=0`, `name`, `hp=None`, `defense=None` nếu field này là một phần record contract.
- Fuzzy lookup nhiều candidate phải log warning có query và số candidate.
- Không yêu cầu Tesseract thật trong unit test; không gọi Tkinter từ worker.

### 6. CB4 Remove Active Legacy Rotation Consumers

- Search production code cho `monster_list`, `monsters`, `attack_keys` và `skills`; phân loại migration/test/docs/training-only versus active normal-Hunt path.
- Mọi active normal-Hunt path phải đọc canonical `monster_rotation` dict. Không chuyển list canonical thành list tên/ID rồi ghi ngược legacy.
- `training_monster_list` chỉ giữ lại nếu là training-only và không được dùng làm normal-Hunt source.
- Không tạo compatibility read/write adapter ngoài migration boundary. Nếu một consumer thực sự đã retired, xóa/disable path sau khi repository search chứng minh không còn caller.
- Giữ CB4 atomic writer/single writer nguyên vẹn; R1 không tạo đường save thứ hai.

### 7. CB2D Publish Contract

- Giữ `HuntOrchestrator` nhận optional detection snapshot callback theo dependency injection; App/UI adapter phải schedule callback về Main Thread.
- Xác nhận test rằng `RuntimeMonsterQueue` được khởi tạo với callback và `maybe_publish(schedule_ui_task)` được gọi sau `scene_detector.process_frame(frame)`.
- Không import Tkinter vào CB2D, không tự tạo Treeview/Listbox, không persist snapshot và không tự promote runtime item sang rotation.
- Publish phải giữ rate limit tối đa 5 FPS, immutable tuple/copy, và callback absent là no-op an toàn.

### 8. CB2E Start Gate

- Chỉ được chuyển sang CB2E sau khi CB5 compile và focused tests pass.
- Xác nhận `win_input.py` hiện là foreground `SendInput` và chưa được coi là background support.
- Không tạo implementation CB2E trong R1; chỉ ghi rõ contract còn thiếu và test entry points cần dùng.
- CB2E phải bắt đầu bằng backend abstraction/injected dependency, không thêm `PostMessage` rời rạc vào Orchestrator.

## Mandatory Validation

```powershell
py -m pytest tests/unit/test_target_bar_detector.py -q
py -m pytest tests/integration/test_orchestrator_loop.py -q
py -m pytest tests/test_migration.py tests/unit/features/hunt/test_config_migrator.py -q
py -m pytest tests/unit/features/hunt/test_runtime_monster_queue.py tests/unit/features/hunt/test_scene_monster_detector.py -q
py -m pytest tests/unit/dialogs/test_monster_picker.py tests/unit/test_monster_rotation_queue.py -q
py -m pytest tests/ui/tabs/test_hunt_target_modes.py -q
py -m pytest tests/features/hunt/test_scanner.py tests/sprints/sprint23/test_screen_capture.py -q
py -m pytest <new-CB2B-tests> <new-CB2D-publish-tests> -q
py -c "from app_gui import App; app=App(); print('APP_STARTUP_OK'); app.destroy()"
```

Thêm repository search assertion hoặc command evidence: không còn active normal-Hunt production consumer đọc/ghi `monster_list`; mọi kết quả còn lại phải thuộc migration, docs, test, training-only hoặc UI widget name không phải config source.

## Session Boundary Gate

**PASSED khi:**

- CB1 runtime có HWND/client geometry contract đã kiểm chứng; unit test CB1 pass.
- Integration test CB2 pass, target key không spam trong attack và không double-tap khi target chết.
- CB2B có focused test pass cho OCR/DB fallback/cache/UI scheduling.
- Không còn active normal-Hunt legacy `monster_list` consumer.
- UX3A picker tests pass với test strategy nhất quán; dialog không còn minsize/trạng thái lifecycle sai.
- UX3 canonical queue tests pass và không leak metadata/legacy flags.
- CB5 ScreenCapture tests pass cho resize, minimize, lost signal, stats và frame-lock.
- CB2D publish callback hoạt động, rate-limited, immutable và có focused test pass.
- CB2E precondition được xác nhận; chưa đánh dấu background input supported trước session CB2E.
- Không có Tkinter call từ worker, không có config write mới, và toàn bộ command validation pass.

**BLOCKED/REVERTED khi:**

- Cần thay đổi UX3/UX3B/CB2C để che một foundation contract còn thiếu.
- Không phân loại được legacy consumer trước khi xóa/chuyển đổi.
- Detection callback yêu cầu UI widget hoặc worker gọi Tkinter.
- UX3A test suite còn fail do fixture/environment hoặc picker còn hai implementation active.
- CB5 ScreenCapture còn `NameError`, FPS failure, reallocation failure hoặc GDI leak/warning chưa phân loại.
- Focused validation còn fail ở phút 25; phút 25-30 chỉ dành cho direct repair hoặc revert các thay đổi của R1.

Báo `PASSED`, `BLOCKED_BY_LEGACY_CONSUMER`, `UNVERIFIED` hoặc `REVERTED` kèm danh sách command đã chạy và kết quả.
