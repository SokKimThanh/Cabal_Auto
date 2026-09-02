# Session Prompt CB2E: Background Window Input Adapter

**Timebox:** 25-30 phút  
**Priority:** Critical  
**Dependencies:** CB5 và CB2 đã đạt gate; cần HWND hợp lệ của cửa sổ game

## Objective

Tạo abstraction gửi phím có đích rõ ràng để HuntOrchestrator có thể điều khiển
cửa sổ game mà không mặc định giành foreground và không phát input toàn hệ thống.

Session phải xác minh khả năng nhận background input của game. Không được tuyên
bố hỗ trợ nếu chỉ kiểm tra API Windows trả về thành công nhưng game không phản
ứng.

## Hiện Trạng Mã Nguồn

- `lib/system/win_input.py` chỉ dùng Windows `SendInput` với scan code.
- `SendInput` là input toàn hệ thống và thường cần game ở foreground.
- `HuntOrchestrator.start_hunt()` cố bring cửa sổ game lên foreground trước khi
  chạy; option `bring_to_front_each_cycle` có thể tiếp tục giành focus.
- Chưa có `PostMessage`, input backend interface hoặc capability state.
- Một số game dùng DirectInput/Raw Input và bỏ qua `WM_KEYDOWN/WM_KEYUP` gửi bằng
  message.

## Ranh Giới An Toàn

Chỉ dùng API user-mode chuẩn của Windows. Không triển khai DLL injection, hook,
driver, memory write, anti-cheat bypass hoặc cơ chế che giấu automation.

Nếu game không nhận background window messages, backend phải báo
`UNSUPPORTED`; không tự chuyển sang kỹ thuật can thiệp sâu hơn.

## Target Files

- Create: `lib/system/input_backend.py`
- Create: `lib/system/background_window_input.py`
- Modify: `lib/system/win_input.py` để bọc backend foreground hiện có, giữ API
  tương thích
- Modify: `lib/features/hunt/hunt_orchestrator.py` để nhận injected input backend
- Modify: `ui/controllers/app_state_controller.py` và config validation nếu cần
  persist mode
- Add tests dưới `tests/unit/system/` và integration test Orchestrator

Không sửa scene detector, UX3 hoặc target matching policy.

## Backend Contract

```python
class InputBackend(Protocol):
    mode: str

    def tap(self, key: str, press_ms: int = 50) -> bool: ...
    def key_down(self, key: str) -> bool: ...
    def key_up(self, key: str) -> bool: ...
    def close(self) -> None: ...
```

Triển khai:

1. `ForegroundSendInputBackend`: adapter cho behavior hiện tại.
2. `BackgroundWindowMessageBackend(hwnd)`: gửi `WM_KEYDOWN/WM_KEYUP` vào đúng
   HWND bằng virtual-key/lParam đúng chuẩn.

Không dùng global singleton mutable cho HWND. Mỗi hunt session nhận backend gắn
với selected HWND snapshot.

## Config Và Fallback Policy

```json
{
  "input_mode": "background",
  "background_input_fallback": "stop"
}
```

Mode:

- `background`: không được gọi `SetForegroundWindow` hoặc global `SendInput`.
- `foreground`: dùng behavior hiện tại và có thể focus theo cấu hình.

Fallback mặc định `stop`:

- background unsupported hoặc capability chưa xác nhận -> không Start Hunt;
- hiển thị hướng dẫn chọn foreground mode thủ công;
- không âm thầm fallback vì sẽ bất ngờ chiếm bàn phím người dùng.

`bring_to_front_each_cycle` phải bị bỏ qua/disable khi `input_mode=background`.

## Capability Gate

API `PostMessage` trả `True` không chứng minh game đã xử lý phím. Cần hai tầng:

1. **Transport test:** HWND hợp lệ, message gửi thành công, keydown/keyup đúng thứ
   tự và đúng target.
2. **Behavior test:** thao tác chẩn đoán do người dùng chủ động kích hoạt, gửi một
   key test cấu hình an toàn và xác nhận thay đổi quan sát được qua detector hoặc
   người dùng xác nhận.

Lưu capability theo identity ổn định của process/window class, không chỉ HWND vì
HWND thay đổi mỗi lần chạy. Capability hết hạn khi executable/window class đổi.

Không tự chạy key test khi khởi động app hoặc khi game đang ở trạng thái nguy
hiểm. Không dùng phím tấn công làm probe mặc định.

Nếu chưa có tín hiệu detector đủ tin cậy để xác minh behavior trong timebox,
triển khai trạng thái `UNVERIFIED` và yêu cầu manual confirmation; không đánh dấu
backend `SUPPORTED` chỉ dựa vào mock/API return.

## Input Arbitration

Background automation và người dùng có thể cùng điều khiển game, nên cần tránh
phím bị giữ hoặc interleave sai:

- serialize automation input qua một queue/lock duy nhất;
- luôn gửi keyup trong `finally`;
- `close()`/Stop Hunt release mọi key automation đang giữ;
- không chặn input vật lý của người dùng;
- không điều khiển con trỏ chuột toàn hệ thống;
- rate limit do CB2/CB2C vẫn là nguồn quyết định tần suất tap;
- backend chỉ vận chuyển input, không quyết định target hoặc skill.

## Tích Hợp Orchestrator

- Inject `InputBackend` vào Orchestrator thay vì import trực tiếp `tap` cho luồng
  chính.
- Mọi target key và skill key của cùng hunt session đi qua cùng backend.
- Background mode không gọi các callback bring-to-front ở start hoặc mỗi cycle.
- Foreground mode giữ behavior tương thích.
- Nếu selected HWND mất/đổi: stop backend, không gửi message sang HWND cũ hoặc
  cửa sổ khác.
- Stop Hunt phải đóng backend và release key trong thời gian hữu hạn.

## Automated Tests

1. Background backend gửi keydown rồi keyup vào đúng HWND.
2. Không gọi `SendInput` trong background mode.
3. Không gọi bring-to-front trong background mode.
4. Foreground backend giữ behavior `win_input.tap()` hiện tại.
5. Invalid/destroyed HWND trả failure và không gửi sang HWND khác.
6. Exception giữa keydown/keyup vẫn cố release key.
7. Concurrent tap được serialize, không interleave key pairs.
8. Stop/close release toàn bộ key đang giữ.
9. Unsupported/unverified + fallback `stop` không Start Hunt.
10. Không có API điều khiển chuột toàn hệ thống trong background backend.
11. Orchestrator target và skill taps đều đi qua injected backend.
12. Capability không được đánh dấu supported chỉ vì `PostMessage=True`.

Chạy:

```powershell
py -m pytest tests/unit/system/test_background_window_input.py -q
py -m pytest tests/integration/test_orchestrator_loop.py -q
```

## Manual Capability Test

1. Chọn đúng cửa sổ game và chuyển `input_mode=background`.
2. Chạy diagnostics chủ động với key không gây combat.
3. Đưa app khác lên foreground.
4. Xác nhận game nhận key nhưng app đang foreground không nhận ký tự/phím tắt.
5. Xác nhận chuột không di chuyển và bàn phím vật lý vẫn dùng được.
6. Start rồi Stop Hunt; xác nhận không có phím bị giữ.
7. Nếu game không phản ứng, ghi `UNSUPPORTED` và kiểm tra foreground mode chỉ sau
   khi người dùng chủ động chọn.

## Session Boundary Gate

**PASSED khi:**

- Backend abstraction được inject và tests transport pass.
- Background mode không focus game và không gọi global SendInput.
- Có behavior evidence cho `SUPPORTED`, hoặc trạng thái trung thực `UNVERIFIED`.
- Unsupported/unverified fail closed, không chiếm input người dùng.
- Stop release key và không có stuck input.

**BLOCKED/REVERTED khi:**

- Game chỉ nhận foreground SendInput.
- Session phải dùng injection/hook/driver/anti-cheat bypass.
- Background mode vẫn gọi focus hoặc fallback âm thầm.
- Chỉ dựa vào `PostMessage` return để tuyên bố thành công.

Báo cáo `PASSED`, `UNVERIFIED`, `UNSUPPORTED` hoặc `REVERTED` ở phút 25.
