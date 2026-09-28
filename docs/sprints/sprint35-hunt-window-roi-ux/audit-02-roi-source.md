# Audit: ROI Scanner Image Source and Coordinate Origin

## Overview
This document investigates the source of the images used by the ROI scanner, to determine if they come from the user-selected window, the active window, or the full screen, and to verify coordinate origins and thread-safety.

## Capture Pipeline Details

| Component/Function | Image Source | Coordinate Origin | Thread-safe? |
| :--- | :--- | :--- | :--- |
| `ScreenCapture.start(window_title)` | Selected window (finds HWND by title substring) | Screen coordinates (`ClientToScreen` mapped to `window_rect`) | No explicit locking around `window_rect` but updated in capture thread |
| `ScreenCapture._capture_loop()` | Selected window's client area | Screen coordinates mapped to client area bounding box | Runs in background thread, writes frames to queue |
| `ScreenCapture._capture_frame()` | dxcam (grab region) or BitBlt (PrintWindow/BitBlt) | Uses `self.window_rect` (Screen coordinates for dxcam, window DC for BitBlt) | Called by `_capture_loop` |
| `ScanController.run_scan()` | Uses `window_info["hwnd"]` (preferring UI selection over auto-detect) | Inherits from `ScreenCapture` (Screen -> Client mapped) | Worker thread, but accesses UI/DB non-safely if not careful (has some try/except) |
| `AutoScanner.scan_screen()` | Calls `ScreenCapture.get_frame()` | ROI applies locally to the captured frame (relative to frame/client area) | Uses thread-safe queue in `ScreenCapture` |
| `VisionEngine.match_templates()` | Uses ROI directly on the frame array | Relative to the top-left of the provided `frame` array | Locks used for snapshot, safe |

## Detailed Analysis

### 1. Hàm capture nào được ROI dùng?
ROI scanner thông qua `AutoScanner.scan_screen()` và `ScanController.run_scan()` dùng `ScreenCapture.get_frame(timeout=1.0)` để lấy frame mới nhất từ hàng chờ. Hàng chờ này được cập nhật bởi một thread chạy nền gọi `ScreenCapture._capture_loop()`, sử dụng `_capture_frame()`. Bên dưới, hàm này ưu tiên dùng `dxcam` để chụp vùng màn hình `window_rect`, nếu lỗi sẽ fallback sang `BitBlt` chụp từ device context của window.

### 2. Nguồn ảnh
Ảnh chụp đến từ **cửa sổ đã chọn**.
- Trong `ScanController.run_scan()`, nó ưu tiên dùng hàm callback `self.get_hwnd()` để lấy HWND từ UI (selected window).
- Nếu không có, `AutoScanner.detect_window()` sẽ tự động tìm cửa sổ dựa trên tên (Cabal, CABAL, etc.).
- Khi có HWND, `ScreenCapture.start(title)` được gọi. Hàm này tìm lại HWND dựa trên `title` và lấy tọa độ `ClientToScreen`.
**⚠️ Nguy cơ Mismatch:**
Trong `ScanController.run_scan()`:
```python
                    title = win32gui.GetWindowText(window_info["hwnd"])
                    if not scanner.screen_capture.start(title):
```
Nó lấy `title` từ `hwnd` đã chọn, sau đó truyền vào `start(title)`. Tuy nhiên, `ScreenCapture.start(title)` lại dùng `find_window(title)` để lấy HWND mới:
```python
        # Find window
        self.hwnd = self.find_window(window_title)
```
Nếu có nhiều cửa sổ cùng tên, `find_window` có thể trả về một HWND khác với cái đã được UI chọn! Đây là nguyên nhân khiến nguồn ảnh không phải lúc nào cũng là `selected_window` nếu có nhiều client chạy cùng lúc.

### 3. Tọa độ ROI tính theo origin nào?
Tọa độ ROI được lưu (ví dụ `hunt_area` hoặc `combo_bar`) được dùng trong `VisionEngine.match_templates(frame, roi=combo_bar_roi)`.
Bởi vì `frame` nhận được là ảnh chụp của **client area** của cửa sổ (đã loại bỏ border/title bar), các tọa độ ROI này là **tọa độ tương đối (relative) so với góc trên-trái (top-left) của client area (frame)**, không phải tọa độ tuyệt đối của màn hình.

### 4. Kiểm tra `run_scan()` của `ScanController`: capture trước hay detect trước?
Luồng thực thi trong `worker` của `run_scan`:
1. Xác định `window_info` (lấy từ UI hoặc tự động).
2. Kiểm tra Vision Engine & Database.
3. Nếu `scanner.screen_capture` chưa gán đúng window thì gọi `start(title)`.
4. Gọi `get_frame()` để **capture ảnh trước**.
5. Cắt 4 bounding boxes từ ảnh để lưu template (nếu có).
6. Gọi `scanner.run_scan()` truyền vào config. Bên trong `scan_screen()`, nó lại tiếp tục lấy frame (nếu cần) và gọi `detect_monster_pipeline` / `match_templates` để **detect sau**.

=> Trình tự là **Capture trước, Detect sau**.

### 5. Kiểm tra có cache ảnh không, có thread-safe không.
- **Cache ảnh:** `ScreenCapture` duy trì một `queue.Queue` với kích thước tối đa `max_frames=2`. Vòng lặp `_capture_loop` liên tục thêm frame mới và bỏ frame cũ (nếu đầy). Do đó nó giữ các frame mới nhất.
- **Thread-safe:**
  - `ScreenCapture`: Dùng `queue.Queue` nên `get_frame` là thread-safe. Thread chạy nền `_capture_loop` tự cập nhật lại `window_rect` nếu client size thay đổi.
  - `VisionEngine`: Có dùng `self.snapshot_lock` để bảo vệ khi cập nhật `latest_frame` và `latest_detections`.
  - `ScanController`: Chạy toàn bộ logic trong `worker()` thread. Các callback UI (`show_results`, `set_status_text`) được gửi vào luồng chính qua Tkinter `after` hoặc đôi khi gọi trực tiếp (có nguy cơ nhỏ nếu gọi trực tiếp tk APIs).

## Kết luận & Kiến nghị
- **Nguyên nhân cốt lõi (Root Cause) của mismatch:** `ScreenCapture.start(title)` không nhận trực tiếp HWND mà tìm kiếm lại bằng `title`. Nếu có nhiều cửa sổ cùng tên (multi-client), `ScreenCapture` có thể bắt nhầm cửa sổ khác.
- **Giải pháp:** Cần sửa `ScreenCapture.start()` để nhận `hwnd` thay vì (hoặc cùng với) `window_title`, để đảm bảo nó chụp đúng `selected_window`.
