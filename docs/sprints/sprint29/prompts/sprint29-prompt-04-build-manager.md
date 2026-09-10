# Sprint 29 - Prompt 04: Tạo Build Manager UI

## Mục tiêu
Cung cấp giao diện để người dùng có thể tạo và quản lý các cách nâng cấp/chọn kỹ năng (Builds) cho từng nhân vật (Class). Đảm bảo rằng mỗi Build phải được liên kết hợp lệ với một Class hiện có.

## Phạm vi (Scope)
- Tạo file mới: `ui/views/build_manager_frame.py`
- Sửa đổi: `ui/app_gui.py`

## Chi tiết yêu cầu

1. **Xây dựng `BuildManagerFrame`**
   - Kế thừa `ResponsiveGridBase`.
   - Top Bar: Chứa nút "Add New Build", thanh Search, và quan trọng nhất là **một Dropdown (Combobox) để Filter theo Class**. Dropdown này phải load danh sách từ `self.app.db_class_service.get_all_classes()`.
   - Body: `ttk.Treeview` liệt kê các bảng ghi từ `builds` table (Cột: Build ID, Class Name, Author, Description, Upvotes).
   - Footer: Phân trang chuẩn (Prev / Next).
   - Logic kết nối: Gọi `self.app.db_build_service.get_builds_by_filter()` (hoặc tương tự, tùy service có sẵn). Nếu service thiếu logic filter theo class_id, hãy tự filter trên UI tạm thời, hoặc bổ sung vào `lib/db/services/build_service.py`.

2. **Dialog thêm/sửa Build**
   - Tạo một `tk.Toplevel` hoặc viết ngay trong frame.
   - Bắt buộc phải có Dropdown `Class` (tương tự Prompt 02) để người dùng chọn Class khi tạo Build. Khóa ngoại `class_id` không được phép Null.
   - Các trường khác: `author`, `description`.

3. **Gắn vào Application (Sidebar)**
   - Cập nhật `ui/app_gui.py` để thêm View "Build Manager" vào navigation, tương tự như đã làm với Class Manager.

4. **Kiểm tra (Verification)**
   - Chọn bộ lọc Class trên Top Bar -> Bảng cập nhật tương ứng.
   - Nút "Add Build" hiển thị Dropdown Class đầy đủ dữ liệu. Thêm mới thành công vào DB mà không vi phạm Foreign Key constraint.

## Lưu ý (Memory Guidelines)
- Do not mix `pack` and `grid` geometry managers within the same parent frame (ví dụ filter_frame).
- Vẫn dùng class style `UIStyleV2` để đảm bảo theme thống nhất.