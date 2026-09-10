# Sprint 29 - Prompt 03: Tạo Class Manager UI

## Mục tiêu
Tạo ra một giao diện mới `ClassManagerFrame` (dựa trên chuẩn thiết kế `ResponsiveGridBase` của project) để quản lý danh sách các nghề nghiệp (Classes), lấp đầy dữ liệu vào bảng `classes` đang trống.

## Phạm vi (Scope)
- Tạo file mới: `ui/views/class_manager_frame.py`
- Sửa đổi: `ui/app_gui.py` (để gắn vào sidebar)

## Chi tiết yêu cầu

1. **Xây dựng `ClassManagerFrame`**
   - Kế thừa class `ResponsiveGridBase` từ thư mục `ui/mixins/` (hoặc cấu trúc chuẩn của dự án).
   - Thiết kế Top Bar: Thanh công cụ với nút "Add New Class" và một Search bar đơn giản (tìm theo tên class).
   - Thiết kế Body: Khởi tạo một `ttk.Treeview` hiển thị cột (ID, Name, Description, STR, INT, DEX).
   - Footer: Thêm phân trang (Prev / Next buttons).
   - Logic kết nối: Gọi `self.app.db_class_service.get_all_classes()` để nạp vào Treeview. *(Note: ClassService trong `lib.db.services` hiện có cung cấp `get_all_classes`, bạn cần implement logic phân trang nếu cần, hoặc giả lập phân trang ở layer UI).*

2. **Implement Dialog thêm/sửa Class**
   - Có thể thiết kế ngay trong file bằng một `tk.Toplevel` đơn giản (tương tự `SkillEditDialog`), gồm các trường nhập: `name` (bắt buộc), `description`, `str_base`, `int_base`, `dex_base`.
   - Kết nối với `self.app.db_class_service.create_class()` và `update_class()`.

3. **Gắn vào Application (Sidebar)**
   - Mở `ui/app_gui.py`.
   - Thêm nút cho `Class Manager` vào Sidebar, ngay cạnh các view `Monster Manager` và `Skill Manager`.
   - Khai báo mapping view (ví dụ: chuỗi `"class_manager"`).
   - Inject `self.app.db_class_service` vào `App` instance nếu nó chưa được khởi tạo.

4. **Kiểm tra (Verification)**
   - Ứng dụng chạy lên có Sidebar item mới.
   - Click vào mở ra view quản lý Class chuẩn UI/UX của app.
   - Thêm/Sửa/Xóa thành công một bản ghi Class.

## Lưu ý (Memory Guidelines)
- *"The `ResponsiveGridBase` component is the standard architecture for responsive, zero-occlusion layouts... It exposes a `get_content_frame()` method which must be used as the parent for child widgets."*
- Phân trang: dùng "Prev", "Next" buttons bên cạnh Label chỉ trang số mấy ở dưới thanh Action bar.