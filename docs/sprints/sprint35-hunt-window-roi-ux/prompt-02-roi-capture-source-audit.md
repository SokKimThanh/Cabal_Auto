# Prompt 02 — Audit nguồn ảnh của ROI Scanner

## Mục tiêu
Xác định ROI Scanner lấy ảnh từ đâu: cửa sổ đã chọn, cửa sổ active, hay toàn màn hình.

## Root Cause
Nghi ngờ ROI dùng `active_window` hoặc screenshot toàn màn hình thay vì `selected_window`.

## Phạm vi
- CHỈ ĐỌC.
- Đọc: `lib/features/hunt/scanner.py`, `lib/system/screen_capture.py`, `lib/vision/vision_engine.py`, `lib/features/hunt/scan_controller.py`.

## Công việc
1. Grep:
   ```bash
   grep -rn "screenshot\|grab\|capture\|ImageGrab\|BitBlt\|mss\|window_rect\|client_rect" lib/vision/ lib/system/ lib/features/hunt/
   ```
2. Xác định:
   - Hàm capture nào được ROI dùng?
   - Nguồn ảnh: full screen / active window / selected window?
   - Tọa độ ROI tính theo origin nào?
3. Kiểm tra `run_scan()` của `ScanController`: capture trước hay detect trước?
4. Kiểm tra có cache ảnh không, có thread-safe không.

## Output
- Bảng: `Hàm capture | Nguồn ảnh | Origin tọa độ | Thread-safe?`
- Xác định mismatch (nếu có) giữa window selection và ROI capture.
- Lưu tại: `docs/sprints/sprint35-hunt-window-roi-ux/audit-02-roi-source.md`

## Commit
```
docs(sprint35): audit roi scanner image source and coordinate origin
```
