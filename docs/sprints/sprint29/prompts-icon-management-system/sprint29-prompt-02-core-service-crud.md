# Prompt 02: Xây dựng Core Service & CRUD Operations cho Icon Management

## Mục tiêu
Xây dựng một `IconService` (hoặc `IconRepository`) chịu trách nhiệm trung gian thao tác dữ liệu với SQLite (CRUD: Create, Read, Update, Delete) cho bảng `icons` và `icon_usages`. Lớp Service này đóng gói các logic truy vấn để tách biệt tầng Data và tầng UI.

## Ngữ cảnh & Yêu cầu từ Đặc tả
Theo phần "5. Cơ Chế Đồng Bộ Hệ Thống":
- Database được định nghĩa là Source of Truth. Mọi thao tác Thêm, Sửa, Xóa đều phải thông qua Database trước.
- Cần có chức năng Lấy danh sách Icon (có thể lọc theo Keyword, Category, Status). Tham số status sẽ được fetch all rồi thực hiện logic check file tồn tại ở lớp UI/Controller.
- Cần có hàm quản lý việc sử dụng icon (`icon_usages`).

## Các bước triển khai chi tiết dành cho Người/AI

### Bước 1: Khởi tạo IconService class
- **Vị trí:** Tạo file `lib/db/services/icon_service.py` (hoặc tương tự theo kiến trúc hiện tại).
- **Hành động:**
  - Khai báo class `IconService`. Truyền tham số nhận vào là `database_connection`.
  - Thiết lập logging cơ bản để trace lỗi (không in thẳng ra `print` mà dùng logger chuẩn của hệ thống, hoặc ít nhất log qua cơ chế quản lý an toàn).
  - Lưu ý: Không đưa logic ghi xuất file JSON (`export_to_json`) vào lớp này để tuân thủ SRP (Single Responsibility Principle). Ghi xuất JSON sẽ do lớp khác đảm nhận.

### Bước 2: Viết các hàm thao tác bảng `icons` (CRUD)
- **Hành động:** Viết các phương thức sau trong `IconService`:
  - `get_all_icons(self, search_term="", category="", status_filter="") -> List[Dict]`:
    - Truy vấn lấy danh sách lọc theo `search_term` và `category`.
    - Bỏ qua tham số `status_filter` trong truy vấn SQL vì logic này cần xác minh file ảnh tồn tại thật ở filesystem.
  - `get_icon_by_key(self, icon_key: str) -> Dict | None`: Truy xuất 1 record cụ thể.
  - `upsert_icon(self, icon_data: Dict) -> bool`: (Thêm mới/Cập nhật). Dùng lệnh `INSERT INTO ... ON CONFLICT(icon_key) DO UPDATE SET ...` để tiện việc save.
  - `delete_icon(self, icon_key: str) -> bool`: Xóa record dựa vào `icon_key`. Bắt buộc dùng `try...except` để chống văng lỗi SQLite.

### Bước 3: Viết các hàm thao tác bảng `icon_usages`
- **Hành động:** Viết thêm các phương thức:
  - `register_usage(self, icon_key, module_name, component_type, element_id) -> bool`: Thêm một usage vào DB.
  - `get_usages(self, icon_key: str) -> List[Dict]`: Lấy danh sách các UI element đang dùng icon này.
  - `clear_usages(self, icon_key: str) -> bool`: Xóa tất cả usages của 1 icon (cần thiết khi gỡ bỏ hoặc refactor).

### Bước 4: Viết Unit Test cho IconService
- **Vị trí:** Tạo file `tests/unit/test_icon_service.py`.
- **Hành động:**
  - Mock connection dùng `:memory:` DB cùng hàm `setup_icons_schema`.
  - Viết test:
    1. Insert 1 icon qua `upsert_icon` -> Verify đọc lại bằng `get_icon_by_key` trùng khớp.
    2. Cập nhật 1 icon -> Verify giá trị mới.
    3. Register 1 usage -> Lấy ra đúng record.
    4. Xóa icon -> Cần đảm bảo `get_icon_by_key` trả về None.

## Tiêu chí hoàn thành (Definition of Done)
- [ ] Lớp `IconService` bao bọc an toàn mọi lỗi SQL (không rò rỉ exception văng thẳng lên UI).
- [ ] Chạy thành công các bài Unit Test.
- [ ] Cấu trúc code tuân thủ Flake8, không có `bare except`.
