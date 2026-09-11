# Prompt 08: Ráp nối Luồng (Workflows) & Tính năng Real-time UI Refresh

## Mục tiêu
Kết nối toàn bộ giao diện đã xây (ở Prompt 5, 6, 7) với tầng Service (Prompt 2, 3, 4) để tạo thành luồng thao tác hoàn chỉnh: Thêm, Sửa, Xóa ảnh. Cài đặt lắng nghe EventBus để thực thi Real-time UI Refresh và giải quyết vấn đề Self-Management Paradox.

## Ngữ cảnh & Yêu cầu từ Đặc tả
- **Workflow Thêm/Sửa (Import File):** Bấm nút Browse -> Chọn file `.png/.ico` -> Hệ thống tự copy (qua `FileManager`) -> Bấm Lưu (qua `Service`) -> Gọi hàm Event Trigger.
- **Workflow Xóa (Khôi phục Fallback):** Xóa đường dẫn file hoặc xóa hẳn Icon.
- **Real-time Refresh & Paradox:** Khi Event phát ra, các giao diện (bao gồm Sidebar của chính app và nút Icon Manager) phải thay đổi icon lập tức.

## Các bước triển khai chi tiết dành cho Người/AI

### Bước 1: Ráp nối luồng Chọn File (Browse)
- **Hành động:**
  - Gắn command cho nút `btn_browse` (trong Detail Form).
  - Viết hàm `self._on_browse_file()`:
    - Mở `filedialog.askopenfilename(filetypes=[("Image files", "*.png *.ico")])`.
    - Gọi `IconFileManager.import_icon_file()` để copy file vào kho.
    - Lấy tên file trả về, điền tự động vào trường `filepath` entry trên Form.
    - Cập nhật tạm thời Khung Preview bằng file vừa chọn.

### Bước 2: Ráp nối luồng Lưu (Save)
- **Hành động:**
  - Gắn command cho nút `btn_save`.
  - Viết hàm `self._on_save()`:
    - Thu thập dữ liệu từ các Entry (Key, Name, Category, Fallback, Filepath...).
    - Gọi `IconService.upsert_icon(data)`. (Lưu ý: Service này ở Prompt 3 đã tích hợp tự động trigger event và export json).
    - Thoát chế độ Edit/Add, tải lại Treeview (`self.load_tree_data()`) để update Status (Mã màu).

### Bước 3: Ráp nối luồng Xóa (Delete)
- **Hành động:**
  - Gắn command cho nút `btn_delete`.
  - Viết hàm `self._on_delete()`:
    - Hiện cảnh báo `messagebox.askyesno`.
    - Nếu đồng ý, gọi `IconService.delete_icon()`.
    - (Khoan xóa file vật lý vội, sẽ xử lý ở Prompt 9 - Orphaned Files).
    - Clear form, reload Treeview.

### Bước 4: Xử lý Event & Real-time Refresh
- **Hành động:**
  - Tại App Controller (VD: `app.py` hoặc `WorkspacePanel` - nơi quản lý các view):
    - Đăng ký listener: `event_bus.subscribe(IconUpdatedEvent, self.on_icon_updated)`.
  - Hàm `on_icon_updated(event)`:
    - Nhận `event.icon_key`.
    - Truy vấn `IconService.get_usages(icon_key)`.
    - Duyệt qua kết quả, xác định widget nào đang dùng icon này.
    - Gọi `IconHelper` tải lại image và gán vào thuộc tính `.image` (phải giữ tham chiếu mạnh để không bị GC) và thuộc tính UI (ví dụ `widget.config(image=new_img)`).

### Bước 5: Cấu hình Self-Management Paradox
- **Hành động:**
  - Mở `app_gui.py` (nơi định nghĩa Sidebar).
  - Khai báo nút Icon Manager bằng `SidebarWidgetDef` chuẩn: `SidebarWidgetDef(..., key="btn_icon_manager", view_target="icon_manager", icon="icon_manager_icon")`.
  - Đảm bảo trong database seed script (hoặc chèn tay lần đầu), bảng `icons` có `icon_manager_icon` và bảng `icon_usages` có tracking cho nó. Để khi thử đổi ảnh `icon_manager_icon` qua chính công cụ này, Sidebar sẽ tự động đổi.

## Tiêu chí hoàn thành (Definition of Done)
- [ ] Chọn file từ máy tính, file tự động copy vào thư mục `assets/images/icon/`.
- [ ] Lưu thành công, dữ liệu được ghi vào DB và xuất ra `icons.json`.
- [ ] Xóa thành công Icon (cần xác nhận).
- [ ] Thay đổi hình ảnh của 1 icon, toàn bộ những nơi đang hiển thị nó (bao gồm cả Sidebar Icon của chính tool) tự động cập nhật mà không cần reset app.

## Thời gian dự kiến: ~30-40 phút
