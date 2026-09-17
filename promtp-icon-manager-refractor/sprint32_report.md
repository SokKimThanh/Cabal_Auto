# Báo cáo Cải tiến (Refactor) - Sprint 32: Icon Manager UI Decoupling

## 1. Tổng quan
Trong Sprint 32, mục tiêu cốt lõi là cấu trúc lại (refactor) module `IconManagerFrame` để tách biệt rõ ràng giữa **Giao diện (UI)** và **Logic xử lý dữ liệu (Business Logic)**. Quá trình này giúp đưa màn hình quản lý Icon về đúng vai trò Controller/View, giao toàn bộ trách nhiệm thao tác tệp tin, dữ liệu và trạng thái cho các Model tương ứng (`ImageLibraryModel` và `IconTreeModel`). Ngoài ra, Sprint còn bao gồm việc sửa một lỗi nghiêm trọng liên quan đến luồng đồng bộ UI (real-time refresh) dựa trên bảng `icon_usages`.

## 2. Chi tiết các hạng mục thực hiện

### 2.1. Prompt 01: Refactor Import Logic (Xử lý Import File)
- **Vấn đề cũ:** Hàm `_on_browse_clicked` chứa quá nhiều logic xử lý trực tiếp với hệ điều hành (`os.path`, `shutil`), tự kiểm tra tồn tại, tự xử lý ghi đè và sinh tên file.
- **Giải pháp:** Xóa hoàn toàn các thư viện thao tác file khỏi UI. Uỷ quyền (delegate) việc kiểm tra file trùng lặp (`check_name_collision`) và copy file (`import_image`) sang `ImageLibraryModel`.
- **Kết quả:** Code UI gọn gàng hơn, các cảnh báo ghi đè hoặc đổi tên được thống nhất chuẩn xác với hành vi của nút "Import Image".

### 2.2. Prompt 02: Refactor Scan & Search Logic (Quét thư mục và Tìm kiếm)
- **Vấn đề cũ:** UI vẫn còn sót đoạn code tự dùng vòng lặp (`iterdir()`) để dò tìm xem file ảnh có tồn tại thật trong ổ cứng hay không khi người dùng nhấn Save.
- **Giải pháp:** Chuyển giao logic kiểm tra file tồn tại vào hàm `evaluate_icon_status()` của `IconHelper`. Cập nhật thanh tìm kiếm (Search Icon) để thuần tuý gọi `self.tree_model.set_filters(...)` thay vì tự duyệt qua danh sách.
- **Kết quả:** Tránh được tình trạng treo giao diện (UI freezing) khi phải đọc ổ đĩa liên tục trong luồng chính (Main Thread).

### 2.3. Prompt 03: Refactor Tree Logic (Xây dựng Cây dữ liệu Icon)
- **Vấn đề cũ:** Hàm `load_tree_data()` thực hiện việc lọc, sắp xếp, duyệt qua danh sách và khởi tạo cấu trúc cho Tkinter Treeview (`_render_queue`) - ôm đồm cả Data Builder và UI Renderer.
- **Giải pháp:**
  - Đưa nhiệm vụ trả về dữ liệu đã lọc (filtered_data) cho `IconTreeModel.get_filtered_tree_data()`.
  - Tách riêng vòng lặp tạo cấu trúc Tkinter thành hàm mới `_render_tree(filtered_data, ...)`.
- **Kết quả:** Hàm `load_tree_data` giờ đây chỉ làm đúng vai trò điều phối: Lấy filter từ UI -> Gọi Model -> Đẩy kết quả vào Renderer.

### 2.4. Prompt 04: Refactor Preview Logic (Hiển thị ảnh thu nhỏ và Tooltip)
- **Vấn đề cũ:** Logic hiển thị/ẩn ảnh thu nhỏ, bật tắt giao diện trống (Empty State) và gắn tooltip bị rải rác ở nhiều nơi (trong lúc khởi tạo, lúc chọn Icon, lúc xóa).
- **Giải pháp:** Gộp tất cả lệnh cập nhật hình ảnh, text, và tháo lắp tooltip (unbind `_i18n_tooltip`) vào duy nhất một hàm `_render_preview(icon_data)`.
- **Kết quả:** Ngăn chặn tuyệt đối các bug liên quan đến hiển thị rác hoặc sai trạng thái tooltip khi chuyển đổi giữa các Icon.

### 2.5. Prompt 05: Refactor Form State (Trạng thái Form)
- **Vấn đề cũ:** Trạng thái của Form quản lý bằng một hàm `set_form_state(state)` khổng lồ chứa hàng loạt vòng `if state == "ADD"` lồng nhau phức tạp.
- **Giải pháp:** Xóa bỏ hàm monolithic này. Thay bằng các hàm chuyển trạng thái tường minh: `_enter_add_mode()`, `_enter_edit_mode()`, và `_enter_view_mode()`.
- **Kết quả:** Code dễ đọc hơn, dễ bảo trì và mở rộng sau này nếu có thêm các mode xử lý khác.

### 2.6. Bugfix: Real-time Sidebar Refresh bằng `icon_usages`
- **Vấn đề cũ:** Khi đổi ảnh của Icon quản lý Sidebar (ví dụ đổi icon của nút "Monster Manager"), Sidebar có cập nhật nhưng lập tức bị ghi đè lại ảnh cũ khi rê chuột (hover). Nguyên nhân là hàm cập nhật tự ghi đè UI một cách lỏng lẻo thay vì reload lại bộ nhớ. Việc đếm `icon_usages` hoàn toàn bị vô tác dụng đối với Runtime UI.
- **Giải pháp:** Sửa đổi `app_gui.py`:
  1. Yêu cầu `IconHelper` tải lại (`reload_icon_map()`) từ JSON vào RAM.
  2. Xóa Cache ảnh cũ của Tkinter.
  3. Lặp qua `icon_usages`, nếu phát hiện sử dụng tại `sidebar_button`, gọi tự nhiên lệnh `self.sidebar.set_active_tab()` để Sidebar tự động vẽ lại các nút dựa trên bộ nhớ đệm vừa được làm mới.
  4. Sửa `sidebar_component.py` để không bị phụ thuộc vào trạng thái khởi tạo (image vs emoji).
- **Kết quả:** Cập nhật bất kỳ Icon nào được khai báo trong `icon_usages` sẽ lập tức đồng bộ lên toàn bộ ứng dụng một cách hoàn hảo và kiên định.

## 3. Tổng kết kiến trúc
- **Tách biệt Model-View-Controller (MVC):** `IconManagerFrame` hiện tại hoàn thành xuất sắc vai trò Controller/View, không còn chứa logic thao tác file hay xử lý dữ liệu sâu.
- **Tăng tính ổn định của Tkinter:** Việc đưa các logic khởi tạo UI nặng (heavy I/O) ra khỏi luồng chính và sử dụng `_render_queue` giúp ứng dụng mượt mà, không giật lag.
- **Runtime Tracking:** Bảng `icon_usages` chính thức trở thành "Bản đồ nguồn (Source of Truth)" định hướng cho EventBus trong việc cập nhật giao diện thời gian thực.
