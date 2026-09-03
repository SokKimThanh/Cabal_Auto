# Session Prompt CB2-FIX: Hunt Orchestrator Runtime Wiring

**Timebox:** 25-30 phút  
**Priority:** Critical  
**Dependency:** Không có; chạy độc lập trên branch hiện tại

## Objective

Sửa các lỗi còn lại của CB2 trong `HuntOrchestrator`, đặc biệt dependency runtime bị thiếu khi chạy app thật. Giữ nguyên contract đã chốt: target key chỉ được tap trong search mode khi chưa có target; attack mode không tap target key; target mất phải debounce theo số frame.

Session này chỉ sửa foundation của CB2 và test. Không triển khai CB2C target policy, UX3/UX3B UI, CB2E background input hoặc CB3 skill acknowledgment.

## Verified Starting Evidence

- `HuntOrchestrator.start_hunt()` truy cập `self.bot_manager.screen_capture`, nhưng constructor hiện không nhận hoặc gán `bot_manager`.
- `App` tạo `HuntRunner` có `bot_manager`, nhưng không truyền dependency đó sang `HuntOrchestrator`.
- Test hiện tại tự gán `orch.bot_manager = MagicMock()`, nên chưa bắt được wiring lỗi khi chạy app thật.
- `attack_started` và `attack_min_duration` còn sót dù artificial attack-duration lock đã bị loại khỏi logic.
- Các test CB2 hiện kiểm tra loop bằng mock, chưa có test constructor/App wiring.

## Target Files

- Modify: `lib/features/hunt/hunt_orchestrator.py`
- Modify: `app_gui.py` để truyền dependency runtime rõ ràng
- Modify: `tests/integration/test_orchestrator_loop.py`
- Modify/Add: `tests/test_hunt_orchestrator.py`
- Modify/Add: focused CB2 runtime wiring tests

Không sửa `HuntRunner` để tạo thêm runtime path; không thêm `hasattr()` fallback nhằm che dependency bắt buộc. Không sửa target policy hoặc UI.

## Implementation Requirements

### 1. Explicit Bot Manager Dependency

Chọn một contract rõ ràng và dùng nhất quán:

```python
HuntOrchestrator(..., bot_manager: BotManager, ...)
```

hoặc dependency interface tương đương đã tồn tại trong project.

- Constructor phải nhận và lưu `bot_manager`.
- `App` truyền đúng `self.hunt_runner.bot_manager` hoặc owner runtime tương đương.
- Không tự tạo BotManager thứ hai trong Orchestrator.
- Nếu dependency bắt buộc bị thiếu, fail rõ ràng khi khởi tạo bằng lỗi có thông tin; không để worker chạy rồi nuốt `AttributeError`.
- Test phải chạy theo wiring production, không cần gán thủ công `orch.bot_manager` sau constructor.

### 2. Preserve CB2 Hunt Loop Contract

- Target key chỉ được gọi trong search mode khi `have_target` là false.
- Không thêm tap riêng ở ALIVE -> DEAD.
- Attack mode gọi `try_cast_skills()` hoặc fallback attack hiện có nhưng không gửi target key.
- Một lần alive cập nhật `last_seen` và reset consecutive false count.
- Chỉ sau `target_lost_debounce_frames` lần false liên tiếp mới chuyển `have_target=False`.
- Không dùng `attack_min_duration_sec` để giữ target active.
- Xóa `attack_started`, `attack_min_duration` và các phép gán dead code liên quan.
- Một frame capture được dùng lại cho các kiểm tra trong cùng tick.

### 3. Safe Runtime Failure

- Nếu screen capture không có frame, xử lý theo boundary hiện có, không crash worker.
- UI state/error/target clear vẫn gọi qua `schedule_ui_task()`.
- Worker phải kết thúc sạch và log nguyên nhân khi dependency/capture lỗi.
- Không gọi Tkinter trực tiếp từ worker.

### 4. Test Coverage

Bổ sung hoặc cập nhật test:

1. Constructor nhận bot manager và worker dùng đúng instance.
2. Production-style `App -> HuntRunner.bot_manager -> HuntOrchestrator` wiring không có `AttributeError`.
3. Search mode tap target key; attack mode không tap target key.
4. Một false xen giữa true không làm mất target.
5. Ba false liên tiếp mới làm mất target mặc định.
6. `last_seen` cập nhật ở mọi tick alive.
7. Không còn `attack_started`/`attack_min_duration` trong CB2 implementation.
8. UI callbacks đều qua scheduler.
9. Stop Hunt kết thúc worker sạch.

## Validation

```powershell
py -m pytest tests/integration/test_orchestrator_loop.py -q
py -m pytest tests/test_hunt_orchestrator.py tests/unit/features/hunt/test_orchestrator_ocr_fallback.py -q
py -c "from app_gui import App; app=App(); print('APP_STARTUP_OK'); print('ORCH_BOT_MANAGER_WIRED', hasattr(app.hunt_orchestrator, 'bot_manager')); app.destroy()"
py -m py_compile app_gui.py lib/features/hunt/hunt_orchestrator.py
```

Repository search sau sửa:

```powershell
rg "attack_started|attack_min_duration|self\.bot_manager" lib/features/hunt/hunt_orchestrator.py app_gui.py tests
```

Kết quả phải chứng minh Orchestrator có dependency rõ ràng, dead code CB2 đã xóa, và test không còn workaround bằng cách gán `bot_manager` thủ công.

## Session Boundary Gate

**PASSED khi:**

- App production wiring truyền `bot_manager` hợp lệ vào `HuntOrchestrator`.
- CB2 integration và focused tests pass.
- Target key không spam trong attack và không double-tap khi target chết.
- Debounce/`last_seen` đúng contract.
- Không còn dead code artificial attack-duration lock.
- Worker/UI thread boundary được giữ nguyên.
- Startup smoke pass.

**BLOCKED/REVERTED khi:**

- Cần sửa CB2C/UX3B để làm Orchestrator khởi động.
- Dependency vẫn được che bằng `hasattr()` hoặc gán thủ công trong test.
- Target key được gửi trong attack mode hoặc ở ALIVE -> DEAD branch.
- Focused test còn fail mà chưa phân loại code/fixture.

Báo cáo `PASSED`, `BLOCKED_RUNTIME_WIRING`, `UNVERIFIED` hoặc `REVERTED` sau validation cuối.
