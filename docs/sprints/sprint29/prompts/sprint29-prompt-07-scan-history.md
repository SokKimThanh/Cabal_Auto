# Sprint 29 - Prompt 07: Tạo Scan History UI

## Mục tiêu
Tạo giao diện hiển thị lịch sử quét (Scans) từ bảng `scans`, đồng thời hỗ trợ bộ lọc và giao diện Empty State đẹp mắt khi chưa có dữ liệu.

## Phạm vi (Scope)
- Tạo file mới: `ui/views/scan_history_frame.py`
- Sửa đổi: `ui/app_gui.py`

## Chi tiết yêu cầu

1. **Xây dựng `ScanHistoryFrame`**
   - Kế thừa `ResponsiveGridBase`.
   - Top Bar: Chứa các bộ lọc:
     - Dropdown chọn Class (lấy dữ liệu từ db_class_service).
     - Dropdown chọn Monster (lấy dữ liệu từ db_monster_service hoặc danh sách ID đơn giản, tùy data thực tế).
     - Nút "Refresh".
   - Body: `ttk.Treeview` hiển thị cột: Scan ID, Thời gian (Timestamp), Tên Class, Tên Kỹ Năng (Skill), Tên Quái (Monster), Status.
   - Footer: Phân trang (Prev / Next).

2. **Truy vấn Dữ liệu (JOIN)**
   - Do bảng `scans` chỉ lưu ID, bạn cần viết (hoặc sửa đổi) service `ScanService` trong `lib/db/services/scan_service.py`.
   - Query cần JOIN với bảng `classes`, `skills`, và `monsters` (nếu có, bảng `monsters` dùng ID kiểu TEXT) để lấy ra `class_name`, `skill_name`, `monster_name` phục vụ cho việc hiển thị trên Treeview.

3. **Implement Empty State**
   - Import `EmptyState` (nếu có sẵn component trong `ui/components/`, ví dụ: `from ui.components.empty_state import EmptyState`).
   - Nếu dữ liệu scan trả về bằng 0 (khi vừa khởi tạo app hoặc filter ra rỗng), ẩn `Treeview` và pack `EmptyState` lên hiển thị thông báo "Chưa có dữ liệu scan nào."

4. **Gắn vào Application (Sidebar)**
   - Cập nhật `ui/app_gui.py` để thêm View "Scan History" vào navigation, tương tự như đã làm với Class Manager, Build Manager.

5. **Kiểm tra (Verification)**
   - Khởi động app, chọn tab Scan History.
   - Nếu Database trắng, màn hình hiển thị Empty State.
   - Insert tay 1 bản ghi vào bảng `scans` qua sqlite viewer, nhấn Refresh trên UI, Treeview sẽ hiện ra bản ghi đó với tên đầy đủ nhờ lệnh JOIN.

## Lưu ý (Memory Guidelines)
- Chú ý kiểu dữ liệu: `scans.monster_id` tham chiếu tới `monsters(id)` và hiện tại kiểu dữ liệu của `monsters.id` có thể là TEXT.
- Treeview chỉ Read-only, không cung cấp tính năng Edit/Delete (trừ khi có nút Clear All nếu muốn).