# Báo cáo: Refactor IconManagerFrame sang IconManagerController

## 1. Mục tiêu
Tách toàn bộ nghiệp vụ xử lý dữ liệu khỏi `IconManagerFrame` để giải quyết vấn đề God Class. Giao diện (View) chỉ nên chịu trách nhiệm nhận sự kiện từ người dùng, gọi Controller và hiển thị kết quả, tuân thủ đúng mô hình MVC.

## 2. Các thay đổi chính

### 2.1 Tạo `IconManagerController` (`ui/controllers/icon_manager_controller.py`)
- Khởi tạo controller với các dependencies được inject từ View (`app`, `icon_service`, `tree_model`, `image_model`, `icon_helper`).
- Tách biệt hoàn toàn khỏi Tkinter, controller không nhận instance của View mà chỉ trả về các đối tượng mang thông tin kết quả.
- Các API chính của Controller:
  - `validate_icon_data(form_data)`: Kiểm tra tính hợp lệ của dữ liệu đầu vào.
  - `save_icon(form_data, old_filepath, just_imported_file)`: Thực hiện validate, lưu bản dịch (tooltip), cập nhật database (qua `icon_service`), cập nhật cache (qua `tree_model`), và xử lý rollback file ảnh nếu quá trình cập nhật DB thất bại.
  - `delete_icon(icon_key)`: Kiểm tra an toàn trước khi xóa (check safe delete) và thực hiện xóa trong database, sau đó invalidate cache.
  - `add_usage(...)` / `delete_usage(...)`: Quản lý các logic gán và gỡ Element ID khỏi Icon.
  - `sync_system_icons_async(on_complete, on_error)`: Chạy ngầm tiến trình đồng bộ system icons, nhận hai hàm callback từ View để gọi lại khi hoàn tất hay có lỗi.

### 2.2 Tạo Result Objects
- Tạo `OperationResult` và `SaveIconResult` (sử dụng `@dataclass`) để Controller trả về các thông tin trạng thái thành công/thất bại, thông điệp lỗi, và các dữ liệu cần thiết khác. Điều này giúp code trong sáng và dễ dàng bảo trì.

### 2.3 Refactor `IconManagerFrame` (`ui/views/icon_manager_frame.py`)
- Chuyển `_on_save`, `_on_delete`, `_on_add_usage`, `_on_del_usage` thành các hàm gọi đến `self.controller` tương ứng.
- View tiếp nhận `OperationResult` hoặc `SaveIconResult` từ Controller, sau đó chỉ thực hiện các thao tác UI (như show error messagebox, tkraise, request_load_tree_data).
- Đối với `_on_sync`, View cung cấp các hàm callback `on_complete` và `on_error`. Các callback này đảm bảo an toàn cho Tkinter bằng cách bọc logic trong `self.after(0, ...)`, giúp UI không bị đóng băng và an toàn về mặt luồng (thread-safe).
- Số dòng code của `IconManagerFrame` giảm đáng kể, tập trung hoàn toàn vào việc kết nối các component giao diện.

## 3. Kết quả
- Kiến trúc tuân thủ đúng MVC: View không còn chứa business logic (validate, gọi DB trực tiếp, tự handle rollback).
- Controller hoạt động độc lập, có thể dễ dàng viết Unit Test mà không cần mock giao diện Tkinter.
- Luồng xử lý bất đồng bộ (Sync) được đảm bảo an toàn và không gây treo ứng dụng.

## 4. Các bước tiếp theo (Khuyến nghị)
- Khi logic Save/Sync phát triển phức tạp hơn, có thể cân nhắc chia nhỏ `IconManagerController` thành các backend service chuyên biệt như `IconSaveService` và `IconSyncService` để giữ Controller ở đúng vai trò điều phối (Orchestrator).
- Triển khai Unit test toàn diện cho `IconManagerController`.