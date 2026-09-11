# Prompt 01: Thiết lập Database Schema & Migrations cho Hệ thống Icon Management

## Mục tiêu
Khởi tạo cấu trúc cơ sở dữ liệu (SQLite) cho hệ thống quản lý Icon, bao gồm 2 bảng `icons` và `icon_usages` nhằm làm nguồn dữ liệu chân lý (Source of Truth). Hỗ trợ quá trình khởi chạy (migration) mà không làm ảnh hưởng đến dữ liệu hiện có.

## Ngữ cảnh & Yêu cầu từ Đặc tả
Theo phần "2. Thiết Kế Cơ Sở Dữ Liệu", chúng ta cần 2 bảng:
1.  **Bảng `icons`:** Lưu thông tin định nghĩa Icon (`icon_key`, `name`, `filepath`, `fallback_emoji`, `tooltip_translation_key`, `category`, `description`, `created_at`).
2.  **Bảng `icon_usages`:** Lưu lịch sử/vị trí sử dụng của Icon để hỗ trợ Real-time Refresh (`icon_key`, `module_name`, `ui_component_type`, `ui_element_id`, `description`).

## Các bước triển khai chi tiết dành cho Người/AI

### Bước 1: Định nghĩa Script tạo bảng
- **Vị trí:** Mở file cấu hình schema SQL (VD: `lib/db/schema.sql` hoặc file tương tự chuyên quản lý tạo bảng).
- **Hành động:** Viết các câu lệnh `CREATE TABLE IF NOT EXISTS` cho 2 bảng:
  - Bảng `icons`: Cần đảm bảo `icon_key` là `UNIQUE NOT NULL`. Cột `created_at` nên dùng `DEFAULT CURRENT_TIMESTAMP`.
  - Bảng `icon_usages`: Cần thiết lập `FOREIGN KEY (icon_key) REFERENCES icons(icon_key)` (nếu có dùng Pragma Foreign Keys).

### Bước 2: Thiết lập Migration/Initialization
- **Vị trí:** Mở logic khởi tạo database (VD: `lib/db/database.py` hoặc `database_service.py` ở hàm `init_db()`).
- **Hành động:**
  - Đảm bảo các lệnh SQL tạo bảng ở Bước 1 được thực thi mỗi khi khởi động hệ thống.
  - Sử dụng `try...except` để bắt và ghi log nếu có lỗi SQLite, tránh crash app (VD: lỗi schema không hợp lệ).

### Bước 3: Viết Unit Test cho Database Schema
- **Vị trí:** Tạo file test mới (VD: `tests/unit/test_db_icon_schema.py`).
- **Hành động:**
  - Setup một in-memory SQLite database (`:memory:`).
  - Khởi chạy script tạo bảng.
  - Viết 2 test cases:
    1.  Test insert thành công vào bảng `icons` và `icon_usages`.
    2.  Test vi phạm ràng buộc UNIQUE của `icon_key` trong bảng `icons` (chắc chắn sẽ văng lỗi `sqlite3.IntegrityError`).

## Tiêu chí hoàn thành (Definition of Done)
- [ ] Các bảng `icons` và `icon_usages` được tạo tự động nếu chưa tồn tại khi chạy ứng dụng.
- [ ] Không làm gián đoạn hoặc hỏng hóc các bảng hiện có trong DB `monsters.db`.
- [ ] Chạy Unit Test thành công 100%.

## Thời gian dự kiến: ~15-20 phút
