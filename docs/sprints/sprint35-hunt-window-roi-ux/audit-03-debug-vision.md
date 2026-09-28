# Audit Debug Vision

## Bảng Phân Tích Nguồn Ảnh

| Loại ảnh | Có hiển thị? | Widget | Nguồn dữ liệu |
| :--- | :---: | :--- | :--- |
| **Full frame** | Có | Main Canvas (Left Pane) | Lấy từ `vision_engine.get_latest_snapshot()` (`latest_frame`) |
| **ROI crop** | Có | System ROIs Panel (Right Pane) | Ảnh được crop (cắt) từ `latest_frame` theo toạ độ ROI trong `hunt_cfg['rois']` |
| **Ảnh đã tiền xử lý** (grayscale, v.v.) | Không | - | - |
| **Kết quả sau OCR/detect** | Có | Main Canvas (Left Pane) | Lấy từ `detections` của `vision_engine.get_latest_snapshot()` |

## Overlays & Window Source
- **Overlay ROI box**: Có, vẽ hình chữ nhật màu vàng (`(0, 255, 255)`) kèm theo tên ROI trên Main Canvas ở Left Pane (hàm `_render_main_canvas`).
- **Hiển thị window source**: Không có hiển thị thông tin về tên cửa sổ capture gốc (window title hay hwnd) trên UI của Debug Vision.

## Danh sách Gap so với kỳ vọng user

1. **Lỗi vẽ đè Bounding Box (Double Draw):**
   - Trong `vision_engine.py`, hàm `_process_frame` vẽ trực tiếp bounding box màu xanh lá lên frame (in-place) rồi lưu vào `latest_frame`.
   - Sau đó, khi `vision_snapshot_debugger.py` gọi hàm `get_latest_snapshot()` để lấy frame này, hàm `_render_main_canvas` lại lặp qua danh sách `detections` và vẽ đè thêm một lớp bounding box nữa lên trên.
2. **Không so sánh được Input vs Output (Mất ảnh gốc):**
   - Frame truyền cho Debugger đã là Output (đã bị vẽ bounding box ở backend). Người dùng không thể xem được Original Input (ảnh raw từ capture) để so sánh hay đối chiếu.
3. **Ảnh ROI bị vấy bẩn (Tainted ROI Crop):**
   - Hàm `_extract_and_render_rois` dùng mảng numpy cắt từ `frame` lấy từ engine. Vì `frame` này đã bị vẽ đè bounding box từ trước, ảnh hiển thị ở mục System ROIs (Right Pane) có thể sẽ dính các đường nét màu xanh lá nếu có detection lọt vào khu vực ROI.
4. **Không hiển thị ảnh tiền xử lý (Pre-processed Image):**
   - Không có tính năng (toggle hay view) để xem các bước trung gian của thuật toán nhận diện như Grayscale, Threshold, hay Canny Edge.
5. **Thiếu thông tin Window Source / Metadata:**
   - Debug Vision không cung cấp ngữ cảnh về cửa sổ đang bị quét, độ phân giải hiện tại, hay timestamp của frame, khiến việc đối chiếu ROI bị hạn chế khi thay đổi kích thước cửa sổ game.
