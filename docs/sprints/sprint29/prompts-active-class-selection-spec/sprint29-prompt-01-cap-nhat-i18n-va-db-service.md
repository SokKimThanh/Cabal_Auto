# Session 1: Cập nhật i18n và DB Service cho Tính năng Chọn Class

## 1. Tiêu đề & Mục tiêu
- **Tiêu đề:** Khai báo Translations (i18n) và Viết Service Truy xuất Danh sách Class.
- **Mục tiêu:** Đảm bảo ứng dụng có đủ bản dịch chuẩn quốc tế hóa cho UI chọn Class sắp tới và cung cấp phương thức truy vấn danh sách Class từ SQLite (`monsters.db`) để nạp vào Combobox. Task này cần hoàn thành dưới 30 phút.

## 2. Ngữ cảnh (Context)
Dựa theo tài liệu đặc tả `active_class_selection_spec.md`:
> Thiết kế Giao diện: Nhãn "Class:".
> Thiết kế Logic: Khởi tạo - Đọc danh sách classes thông qua `ClassService` và đưa vào Dropdown (Ví dụ: `1 - Blader`).
> Tránh Điểm Yếu (Pitfalls): Thiếu tiêu chuẩn Quốc tế hóa (i18n). Bắt buộc phải khai báo và sử dụng translation keys (ví dụ: `lbl_class_select`, `msg_unsaved_class_change`) theo chuẩn của `lib/i18n`.

## 3. Các file cần thay đổi
1. `lib/i18n/translations.py` (hoặc file lưu dictionary translation của dự án).
2. `lib/db/services/class_service.py` (nếu chưa có thì tạo mới, hoặc thêm vào service chung quản lý class).

## 4. Hướng dẫn thực hiện chi tiết

### 4.1. Cập nhật `translations.py`
- Mở file quản lý translation toàn cục.
- Thêm các key mới (hỗ trợ ít nhất tiếng Anh và tiếng Việt):
  - `lbl_class_select`: "Class:" / "Lớp nhân vật:"
  - `msg_unsaved_class_change`: "You have unsaved changes. Change class anyway?" / "Bạn có thay đổi chưa lưu. Vẫn tiếp tục đổi lớp nhân vật?"
  - `msg_class_scan_mismatch`: "Scanned class differs from selected class. Update?" / "Lớp nhân vật quét được khác với lựa chọn. Cập nhật?"
- **Lưu ý:** Nếu file sử dụng cơ chế `register_bulk`, hãy chắc chắn không xoá lệnh register ở cuối file. Sau khi thêm, hãy dùng script `python3 scripts/migrate_translations_to_db.py` nếu cần thiết để đồng bộ.

### 4.2. Viết hàm lấy danh sách Class trong DB Service
- Mở `lib/db/services/class_service.py` (nếu không có, hãy tạo mới theo chuẩn của project hoặc đặt vào file db tương ứng quản lý class).
- Viết phương thức: `def get_all_classes(self) -> List[Dict]:`
  - Hàm này sử dụng kết nối SQLite (thông qua Database connection pool hiện có của project).
  - Thực thi câu lệnh SQL: `SELECT id, name FROM classes ORDER BY id ASC;`
  - Trả về list dạng dict hoặc tuple để UI dễ dàng format thành string `"ID - Name"`.

## 5. Tiêu chí Hoàn thành (Acceptance Criteria / Verification)
1. Chạy app không bị crash.
2. Kiểm tra log/DB không có lỗi cú pháp.
3. Nếu mở Python console trong project:
   - `from lib.i18n import t; print(t("lbl_class_select"))` in ra đúng chuỗi mong muốn.
   - Gọi thử instance của `ClassService.get_all_classes()` trả về danh sách class (ví dụ ID 1 là Blader).
