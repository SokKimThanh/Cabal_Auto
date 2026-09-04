# Session Prompt CB6: Implement Cabal Horizontal Combo Bar Timing Detector

Timebox: 25–30 minutes.
Priority: High – Enables 20+ hit combo streak without breaking.

---

## Objective
Tạo module chuyên dụng `lib/features/combo/combo_timing_detector.py` để theo dõi thanh Combo Bar nằm ngang của Cabal (vị trí ngay dưới thanh máu Target Bar ở đỉnh giữa màn hình). Module phát hiện chính xác thời điểm vạch sáng di chuyển chạm vào vùng 2 vạch (hit-zone sweet spot) và kích hoạt phím kỹ năng, với độ trễ thực tế bị giới hạn bởi tần suất capture của `ScreenCapture` (xem mục 1) chứ không chỉ bởi `poll_interval_ms`, mà không gây nghẽn CPU hay spam phím đúp.

## Target Files
- Create: `lib/features/combo/combo_timing_detector.py`
- Create: `lib/features/combo/__init__.py`
- Modify: `lib/system/screen_capture.py` (bổ sung hàm `get_latest_frame()`)
- Modify: `lib/features/hunt/hunt_orchestrator.py`
- Modify: `lib/data/hunt_config.json`
- Create Test: `tests/unit/test_combo_timing_detector.py`

---

## Implementation Details

### 1. Nâng cấp Bộ đệm `ScreenCapture` (`lib/system/screen_capture.py`)
- Thêm thuộc tính `self._latest_frame = None` được cập nhật mỗi khi chụp frame mới (từ `_capture_loop()`, đã có buffer-realloc/minimize-handling theo CB5).
- Thêm phương thức `get_latest_frame() -> Optional[np.ndarray]`:
  - Trả về **bản copy** (`self._latest_frame.copy()` nếu không `None`) của frame mới nhất đang có trong bộ đệm, không phải tham chiếu trực tiếp tới mảng đang được `_capture_loop()` ghi đè ở thread khác. Việc này tránh torn-read khi một thread khác đang ghi buffer đúng lúc `wait_for_hit_zone()` đang đọc. Copy một ROI nhỏ (không phải cả frame) là đủ rẻ để không ảnh hưởng tới ngân sách 4ms polling.
  - Không làm rỗng hàng đợi hoặc block, giúp vòng lặp tốc độ cao poll liên tục mà không tốn CPU.
  - Ghi chú giới hạn thực tế: độ chính xác thời điểm phát hiện hit-zone bị giới hạn bởi tần suất frame thực sự mới của `_capture_loop()` (ví dụ nếu capture chạy ~60fps thì frame mới chỉ xuất hiện mỗi ~16.6ms bất kể `poll_interval_ms` nhỏ tới đâu). Mục tiêu "<5ms" trong Objective là độ trễ *xử lý sau khi có frame mới*, không phải độ trễ tuyệt đối kể từ thời điểm vạch sáng thực sự chạm hit-zone.

### 2. Lớp `CabalComboDetector` (`lib/features/combo/combo_timing_detector.py`)
- Constructor:
  ```python
  def __init__(self, hwnd: int,
               y_ratio_range: tuple = (0.052, 0.062),
               x_ratio_range: tuple = (0.415, 0.585),
               hit_zone_x_ratio: float = 0.78,
               poll_interval_ms: int = 4,
               cooldown_guard_ms: int = 120,
               key_press_callback: callable = None):
  ```
  - `cooldown_guard_ms`: thời gian đóng băng sau khi bấm phím (mặc định 120ms) để chống bấm đúp khi vạch sáng lướt qua.

- Phương thức `wait_for_hit_zone(screen_capture, timeout_sec: float = None, is_target_alive_check: callable = None) -> bool`:
  - `timeout_sec`: nếu `None`, đọc từ `cfg["combo"]["hit_zone_timeout_sec"]` (mặc định `2.0`, đồng bộ với giá trị đã chốt ở CB3C — không dùng lại `2.5` như một bản nháp trước đó của file này).
  - Liên tục lấy frame qua `screen_capture.get_latest_frame()`. Nếu `frame is None`, sleep `poll_interval_ms` và tiếp tục.
  - Cắt ROI thanh Combo Bar, kiểm tra cột pixel tại tọa độ `hit_zone_x_ratio`.
  - Nếu phát hiện vạch sáng (HSV Value > 210 — giá trị khởi điểm cần hiệu chỉnh thực nghiệm theo theme UI/độ sáng màn hình của client, không coi là hằng số tuyệt đối đúng mọi cấu hình):
    - Gọi `key_press_callback()` để gửi phím skill và trả transport result (`SENT`/`FAILED`). Không coi callback không ném exception là game đã nhận skill.
    - Không gọi `mark_cast()` hoặc tăng rotation pointer ngay sau `SENT`. CB3D sở hữu bước hậu kiểm; chỉ acknowledgment `ACCEPTED` mới commit cooldown/pointer/stats. CB6 chỉ phát `TRIGGER_READY` và transport evidence.
    - Thay vì `time.sleep(cooldown_guard_ms / 1000.0)` một khối liền mạch, chia cooldown-guard thành các lát nhỏ (~20-30ms mỗi lát, tổng cộng đủ `cooldown_guard_ms`), và nếu có truyền `is_target_alive_check` (thường là `target_bar_detector.is_target_alive`), kiểm tra sau mỗi lát: nếu mục tiêu đã chết giữa lúc cooldown-guard đang chạy, thoát sớm khỏi cooldown-guard và trả về `True` ngay để nhường quyền cho luồng fast-break (CB3) xử lý, thay vì buộc chờ đủ 120ms mới được ngắt.
  - Trả về `False` khi chạm ngưỡng `timeout_sec`.

### 3. Cấu hình Schema (`lib/data/hunt_config.json`)
Thêm cấu hình:
```json
"combo": {
  "enabled": true,
  "combo_start_key": "alt+3",
  "hit_zone_x_ratio": 0.78,
  "hit_zone_timeout_sec": 2.0,
  "poll_interval_ms": 4,
  "cooldown_guard_ms": 120
}
```
(Lưu ý: `hit_zone_timeout_sec` là field đã được CB3C tham chiếu — session này chỉ hiện thực hoá, không đổi giá trị mặc định.)

### 4. Tích hợp vào Vòng lặp Chiến đấu (Hunt Loop)
Trong `HuntOrchestrator.worker()` / `HuntRunner._try_cast_skills()`:
- Nếu `combo.enabled` là `True`: nhấn `combo_start_key` **đúng một lần** khi Combo Mode bắt đầu cho một lượt mục tiêu mới (ví dụ tại thời điểm khoá mục tiêu mới hoặc khi combo mode vừa được bật) — không nhấn lại `combo_start_key` ở mỗi vòng lặp rotation bên trong cùng một lượt combo, tránh spam phím kích hoạt.
- Trước khi gửi phím skill tiếp theo trong chuỗi xoay tua, gọi `wait_for_hit_zone()` (truyền kèm `is_target_alive_check` để hỗ trợ ngắt sớm) để căn đúng nhịp vạch vào vùng 2 vạch. Trả trigger/transport evidence cho CB3D; không commit cast tại detector.
- Khi quái chết giữa chừng (Fast-Break qua `TargetBarDetector`, theo CB3): ngắt ngay vòng lặp chờ combo (kể cả nếu đang trong cooldown-guard, theo mục 2), nhấn phím `Z` để bắt mục tiêu mới.

## Validation & Testing

Unit Test (`tests/unit/test_combo_timing_detector.py`):
- Đưa vào frame giả lập chứa cột pixel sáng: Assert callback chỉ được kích hoạt duy nhất 1 lần (nhờ Cooldown Guard).
- Test hiệu năng CPU: Chạy vòng lặp 4ms trong 10 giây với `get_latest_frame()` → Assert mức chiếm dụng CPU duy trì < 2%.
- (Added) Test `get_latest_frame()` trả về bản copy độc lập: sửa đổi mảng trả về, assert buffer nội bộ của `ScreenCapture` không bị ảnh hưởng (xác nhận không phải tham chiếu chung).
- (Added) Test ngắt sớm cooldown-guard khi target chết: giả lập `is_target_alive_check` trả `False` giữa lúc cooldown-guard đang chạy (sau lát thứ 2 trong ví dụ 120ms/~25ms mỗi lát), assert `wait_for_hit_zone()` thoát sớm thay vì chờ đủ 120ms.
- (Added) Test hit-zone chỉ phát một `TRIGGER_READY`; transport `SENT` không gọi `mark_cast()` hoặc tăng rotation index trước CB3D acknowledgment.
- (Added) Test `combo_start_key` chỉ được gửi một lần mỗi lượt mục tiêu mới, không lặp lại trong vòng rotation của cùng lượt combo đó.

## Session Boundary Gate

**PASSED nếu:**
- Module import bình thường, vượt qua unit test không bị double-press.
- Tọa độ ROI khớp chính xác với thanh Combo Bar ở DPI 100%-150%.
- Không làm nghẽn Main Thread Tkinter.
- `hit_zone_timeout_sec` đọc từ config, khớp giá trị đã chốt ở CB3C (không có giá trị mặc định lệch trong code).
- Cooldown-guard có thể bị ngắt sớm khi target chết, không chặn fast-break tới 120ms.
- Detector không gọi `mark_cast()`; CB3D là nơi commit sau acknowledgment.

**REVERTED nếu:**
- Xuất hiện tình trạng spam phím đúp hoặc tràn bộ nhớ GDI.
- `get_latest_frame()` trả về tham chiếu dùng chung gây torn-read.
- Báo cáo kết quả PASSED/REVERTED ở phút thứ 25.