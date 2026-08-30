# Session Prompt CB6: Implement Cabal Horizontal Combo Bar Timing Detector

Timebox: 25–30 minutes.  
Priority: High – Enables 20+ hit combo streak without breaking.

---

## Objective
Tạo module chuyên dụng `lib/features/combo/combo_timing_detector.py` để theo dõi thanh Combo Bar nằm ngang của Cabal (vị trí ngay dưới thanh máu Target Bar ở đỉnh giữa màn hình). Module phát hiện chính xác thời điểm vạch sáng di chuyển chạm vào vùng 2 vạch (hit-zone sweet spot) và kích hoạt phím kỹ năng với độ trễ dưới 5ms mà không gây nghẽn CPU hay spam phím đúp.

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
- Thêm thuộc tính `self._latest_frame = None` được cập nhật mỗi khi chụp frame mới.
- Thêm phương thức `get_latest_frame() -> Optional[np.ndarray]`:
  - Trả về frame mới nhất đang có trong bộ đệm mà không làm rỗng hàng đợi hoặc bị block, giúp vòng lặp tốc độ cao poll liên tục mà không tốn CPU.

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
cooldown_guard_ms: Thời gian đóng băng sau khi bấm phím (mặc định 120ms) để chống bấm đúp khi vạch sáng lướt qua.

Phương thức wait_for_hit_zone(screen_capture, timeout_sec=2.5) -> bool:

Liên tục lấy frame qua screen_capture.get_latest_frame(). Nếu frame is None, sleep poll_interval_ms và tiếp tục.

Cắt ROI thanh Combo Bar, kiểm tra cột pixel tại tọa độ hit_zone_x_ratio.

Nếu phát hiện vạch sáng (HSV Value > 210):

Gọi ngay key_press_callback() để gửi phím skill.

Kích hoạt time.sleep(cooldown_guard_ms / 1000.0) để triệt tiêu toàn bộ các lần quét trùng lặp của cùng một vạch.

Trả về True.

Trả về False khi chạm ngưỡng timeout_sec.

3. Cấu hình Schema (lib/data/hunt_config.json)
Thêm cấu hình:

JSON
"combo": {
  "enabled": true,
  "combo_start_key": "alt+3",
  "hit_zone_x_ratio": 0.78,
  "poll_interval_ms": 4,
  "cooldown_guard_ms": 120
}
4. Tích hợp vào Vòng lặp Chiến đấu (Hunt Loop)
Trong HuntOrchestrator.worker() / HuntRunner._try_cast_skills():

Nếu combo.enabled là True: Kích hoạt Combo Mode bằng cách nhấn combo_start_key.

Trước khi gửi phím skill tiếp theo trong chuỗi xoay tua, gọi wait_for_hit_zone() để căn đúng nhịp vạch vào vùng 2 vạch.

Khi quái chết giữa chừng (Fast-Break qua TargetBarDetector): Ngắt ngay vòng lặp chờ combo, nhấn phím Z để bắt mục tiêu mới.

Validation & Testing
Unit Test (tests/unit/test_combo_timing_detector.py):

Đưa vào frame giả lập chứa cột pixel sáng: Assert callback chỉ được kích hoạt duy nhất 1 lần (nhờ Cooldown Guard).

Test hiệu năng CPU: Chạy vòng lặp 4ms trong 10 giây với get_latest_frame() -> Assert mức chiếm dụng CPU duy trì < 2%.

Session Boundary Gate
PASSED nếu:

Module import bình thường, vượt qua unit test không bị double-press.

Tọa độ ROI khớp chính xác với thanh Combo Bar ở DPI 100%-150%.

Không làm nghẽn Main Thread Tkinter.

REVERTED nếu:

Xuất hiện tình trạng spam phím đúp hoặc tràn bộ nhớ GDI.

Báo cáo kết quả PASSED/REVERTED ở phút thứ 25.