# Sprint 29 - Prompt 02: Cập nhật Skill Edit Dialog (Ràng buộc Class)

## Mục tiêu
Đảm bảo khi thêm/sửa một Skill, người dùng không phải tự nhập tay `class_id` một cách mù quáng, tránh việc gây lỗi toàn vẹn dữ liệu. Giao diện cần hiển thị danh sách các Class thực tế từ Database dưới dạng Dropdown (Combobox).

## Phạm vi (Scope)
- Sửa file `ui/dialogs/skill_edit_dialog.py`.

## Chi tiết yêu cầu

1. **Khởi tạo và gọi dữ liệu Classes**
   - Trong `_build_ui()` của `SkillEditDialog`, tại phần render `class_frame` (Label: `Class ID:`).
   - Hãy dùng `self.app.db_class_service.get_all_classes()` (giả định service có sẵn trong `self.app`, nếu chưa, hãy fetch giống như cách làm trong `SkillManagerFrame`).
   - Xây dựng một danh sách dictionary/map giữa `class_id` và `name` (VD: `"1 - Warrior"`, `"2 - Mage"`). Nếu không gọi được DB, fallback về danh sách rỗng hoặc default.

2. **Thay đổi Component**
   - Thay thế `tk.Spinbox` hiện tại của `var_class_id` bằng một `ttk.Combobox`.
   - Gắn `values` của combobox bằng danh sách các chuỗi `"ID - Name"` đã tạo ở trên.
   - Khi dialog mở lên để Edit, tìm xem `self.skill_data.get('class_id')` là số mấy, khớp với string nào trong combobox để gán giá trị mặc định cho `Combobox`.

3. **Cập nhật luồng Save (`_on_save_click`)**
   - Lấy giá trị chuỗi từ Combobox (vd: `"1 - Warrior"`).
   - Tách chuỗi để lấy phần ID (phần số nguyên ở đầu).
   - Truyền ID này vào dictionary `data` dưới khóa `class_id`.

4. **Kiểm tra (Verification)**
   - Mở giao diện Quản lý Kỹ Năng (`SkillManagerFrame`), nhấn Add/Edit, hộp thoại hiện lên cần có Dropdown chứa danh sách các class.
   - Nhấn Save thì `class_id` chuẩn xác phải được truyền xuống tầng Database mà không bị crash ép kiểu.
