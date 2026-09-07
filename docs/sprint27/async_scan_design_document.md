# Async Scan & Template Storage System - Design Document

## Mục tiêu (Objective)
Tự động trích xuất các template hình ảnh từ luồng quét (scan) của màn hình game mà không làm đơ giao diện người dùng (non-blocking UI). Các ảnh này được lưu vào thư mục có kiểm soát dung lượng (xoay vòng ở mức 5MB) để chuẩn bị dữ liệu đầu vào cho hệ thống nhận diện tự động sau này. Đồng thời, hiển thị phản hồi trực quan (thumbnail) lên giao diện để người dùng tin tưởng rằng phần mềm vẫn đang hoạt động.

## Các thành phần đã thiết kế & triển khai

### 1. `TemplateStorageManager` (Quản lý lưu trữ & Xoay vòng)
**File:** `lib/utils/template_storage.py`
- **Mô tả:** Đóng vai trò như một kho chứa bất đồng bộ.
- **Tính năng cốt lõi:**
  - **Thread-safe Queue:** Sử dụng `queue.Queue` và một Background Worker Thread (`_worker_loop`) để nhận các mảng ảnh (Numpy arrays) đẩy vào.
  - **Non-blocking Write:** Khi gọi `save_templates_async(images_list)`, hàm lập tức trả về (tránh giật lag ứng dụng chính). Luồng nền sẽ làm nhiệm vụ lưu file ra đĩa với định dạng `template_{timestamp}_{index}.png`.
  - **Disk Rotation (5MB Limit):** Hàm `_enforce_size_limit()` chạy sau mỗi lần ghi file. Nếu tổng dung lượng thư mục `data/captured_templates` vượt quá 5MB, hệ thống sẽ xóa các file cũ nhất (dựa trên `mtime`) cho đến khi dung lượng thỏa mãn.

### 2. Tích hợp trích xuất ảnh vào `ScanController`
**File:** `lib/features/hunt/scan_controller.py`
- **Mô tả:** Nơi luồng điều phối (Controller) gọi quét ảnh.
- **Tính năng cốt lõi:**
  - Sau khi `scanner.run_scan()` hoàn thành, bộ điều khiển sẽ phân tích `frame` (hình ảnh màn hình hiện tại).
  - Tạm thời cắt 4 vùng nhỏ quanh trung tâm màn hình (4 bounding boxes 100x100). Trong tương lai, các tọa độ này sẽ được thay bằng tọa độ thực của quái vật phát hiện được.
  - Đẩy 4 mảng ảnh vào `storage_manager.save_templates_async`.
  - Dùng OpenCV (`cv2`) và `PIL` để thay đổi kích thước (resize) một trong các ảnh này thành dạng thumbnail siêu nhỏ (48x36).
  - Đóng gói thumbnail này vào đối tượng `results` để đẩy lên UI.

### 3. Phản hồi giao diện qua `ScreenStatePanel`
**Files:** `app_gui.py` và `ui/panels/screen_state_panel.py`
- **Mô tả:** Cập nhật UI để người dùng thấy hệ thống đang quét.
- **Tính năng cốt lõi:**
  - **app_gui.py:** Bắt lấy trường hợp `results` trả về có chứa key `thumbnail`. Sau đó, kích hoạt hàm `update_thumbnail()` của `ScreenStatePanel`.
  - **screen_state_panel.py:**
    - Bổ sung thêm 2 thành phần (widgets): Một nhãn văn bản `lbl_scan_status` để thông báo "⏳ Đang theo dõi..." và "✅ Đã cập nhật scan".
    - Một nhãn hình ảnh `lbl_thumbnail` để hiển thị ảnh PIL Thumbnail thu được từ luồng nền (giúp người dùng theo dõi và yên tâm là quá trình auto vẫn bám sát tình hình game thực tế).

## Tóm tắt Luồng thực thi (Execution Flow)
1. User nhấn `Nút Quét` (hoặc Timer tự động gọi).
2. `ScanController` chạy trong Thread ngầm, bắt `frame` và quét dữ liệu.
3. Cắt 4 mảng hình (Numpy) từ `frame`. Đẩy 4 ảnh này vào `TemplateStorageManager`.
4. `TemplateStorageManager` (Thread riêng) từ từ ghi ảnh xuống đĩa và xóa ảnh cũ nếu > 5MB.
5. `ScanController` thu nhỏ ảnh đầu tiên, tạo `ImageTk.PhotoImage`.
6. Thông qua hàm `root.after(0)`, đẩy ảnh lên `app_gui.py` trên Main UI Thread.
7. `ScreenStatePanel` hiển thị ảnh và đổi trạng thái thành "Đã cập nhật".
