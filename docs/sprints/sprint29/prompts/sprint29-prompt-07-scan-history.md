# Sprint 29 - Prompt 07: Tạo Scan History UI

## Mục tiêu
Tạo giao diện hiển thị lịch sử quét (Scans) từ bảng `scans`, đồng thời hỗ trợ bộ lọc và giao diện Empty State đẹp mắt khi chưa có dữ liệu.

## Phạm vi (Scope)
- Tạo file mới: `ui/views/scan_history_frame.py`
- Sửa đổi file: `ui/app_gui.py`
- Sửa đổi file: `lib/db/services/scan_service.py`

## Chi tiết yêu cầu

### 1. Xây dựng `ScanHistoryFrame` (`ui/views/scan_history_frame.py`)
- Kế thừa `ui.components.base.responsive_grid_base.ResponsiveGridBase`. Truyền `bg=UI.BG_BASE` khi gọi `super().__init__`.
- **Top Bar (Filter Zone)**: Chứa các bộ lọc:
  - Dropdown chọn Class (Combobox) lấy dữ liệu thông qua `self.app.db_class_service.get_all_classes()`. Format hiển thị: `ID - Name`. Fallback "0 - None".
  - Dropdown chọn Monster (Combobox). Để tối ưu hiệu năng, danh sách này chỉ nên chứa các Monster đã từng xuất hiện trong lịch sử scan (lấy thông qua hàm trong `ScanService`). Format hiển thị: `ID - Name` (lưu ý: `monster_id` là kiểu `TEXT`). Fallback " - All".
  - Nút "Refresh" (Sử dụng `btn_refresh` translation key).
- **Body**: `ttk.Treeview` hiển thị các cột: `Scan ID`, `Thời gian` (Timestamp), `Tên Class`, `Tên Kỹ Năng` (Skill), `Tên Quái` (Monster), `Status`.
  - Cấu hình grid cho Treeview và sử dụng thanh cuộn x, y tự động ẩn hiện (dùng `grid_remove()` và `grid()` dựa trên view range, không dùng `pack`).
  - Đảm bảo Treeview là Read-only (chỉ hiển thị, không Edit/Delete).
- **Footer**: Thanh phân trang (Prev / Next) cùng nhãn hiển thị số trang hiện tại.

### 2. Truy vấn Dữ liệu (JOIN) (`lib/db/services/scan_service.py`)
- Viết thêm method `get_scans_with_details(class_id, monster_id, page, page_size)` trong `ScanService`. Hàm này cần trả về tuple `(records, total_count)` để phục vụ phân trang và Empty State.
- Query cần thực hiện **LEFT JOIN** với các bảng `classes`, `skills`, và `monsters` để lấy ra `class_name`, `skill_name`, `monster_name` phục vụ cho Treeview.
- Viết thêm method `get_distinct_scanned_monsters()` để trả về danh sách các quái vật (ID và Name) đã có trong bảng `scans`, phục vụ cho Dropdown Monster Filter mà không cần load toàn bộ database quái vật.

### 3. Implement Empty State
- Import component: `from ui.components.empty_state import EmptyState`.
- Nếu API trả về tổng số scan bằng 0 (khi vừa khởi tạo app hoặc filter không có kết quả):
  - Gọi `grid_remove()` hoặc `pack_forget()` ẩn Treeview và Pagination.
  - Hiển thị `EmptyState` với cấu hình:
    - `message="Chưa có dữ liệu scan nào."` (sử dụng app._t() hoặc TranslationBinder).
    - `submessage="Hãy thực hiện quét vùng trên màn hình để lưu dữ liệu."`
    - `icon="🔍"` hoặc `🕒`
- Khi có dữ liệu, ẩn `EmptyState` và show lại `Treeview`.

### 4. Gắn vào Application (Sidebar) (`ui/app_gui.py`)
- Khởi tạo ScanService: Khai báo `self.db_scan_service = ScanService()` cùng với các db_service khác.
- Thêm View: Instantiate `ScanHistoryFrame` và thêm vào từ điển `self._views["scan_history"]`.
- Sidebar Navigation: Thêm một `SidebarWidgetDef` vào danh sách sidebar (trong hàm `_build_sidebar` hoặc danh sách `sidebar_items`), đặt ngay bên dưới "Class Manager".
  - Sử dụng translation key: `btn_scan_history` (cần thêm vào dictionaries trong `lib/i18n/translations.py` với nội dung "Scan History" | "Lịch sử quét").
  - Icon fallback: `🕒`
  - Command gọi `self.switch_view("scan_history")`.

### 5. Kiểm tra (Verification)
- Khởi động app, nhấp vào tab "Scan History" trên Sidebar.
- Kiểm tra hiển thị Empty State nếu Database trắng.
- Dùng SQLite Viewer chèn thử 1 bản ghi vào bảng `scans` (nhớ mapping tới `class_id`, `skill_id` và `monster_id` có tồn tại). Nhấn Refresh, bản ghi phải xuất hiện với tên hiển thị đầy đủ chứ không chỉ là ID.
- Đảm bảo khi switch qua lại giữa các view hoặc đổi ngôn ngữ (EN/VI) app không bị lỗi hoặc UI crash.

## Memory Guidelines (Lưu ý thực thi)
- **Geometry Managers**: Tuyệt đối không mix `pack` và `grid` trong cùng một container Frame để tránh `_tkinter.TclError`. Treeview auto-hiding scrollbars phải dùng `.grid()`.
- **Database Types**: Chú ý `scans.monster_id` tham chiếu tới `monsters(id)` và hiện tại kiểu dữ liệu của `monsters.id` là `TEXT`. Đừng cast ép sang `INT`.
- **Translation**: Các nút tiêu chuẩn sử dụng `btn_refresh`, `btn_prev`, `btn_next`. Giữ nguyên whitespace lúc gọi.
- **Background Color**: Khi subclassing `ResponsiveGridBase`, phải truyền explicitly `bg=UIStyle.BG_BASE` vào `super().__init__` để canvas bên trong không bị viền trắng.
