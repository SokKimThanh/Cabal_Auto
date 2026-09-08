# Sprint 29: Refactor Popups into Workspace Shell Zone

## Mục Tiêu (Objective)
Đưa các chức năng quản lý từ dạng cửa sổ phụ (popup) trực tiếp vào không gian làm việc chính (Workspace/Shell Zone B). Điều này giúp:
- Nâng cao tính nhất quán của UX/UI.
- Tránh tình trạng phân mảnh khi người dùng đang thực hiện một luồng công việc liền mạch (hunt).
- Đưa các chức năng Quản lý Kỹ năng (Skill Manager) và Quản lý Quái vật (Monster Manager) vào tiêu chuẩn kỹ thuật mới (Grid layout, `UIStyleV2`, i18n).

## Thành Quả (Accomplishments)
1. **Loại bỏ hệ thống Popup Lỗi Thời:** Xóa hoàn toàn `ui/windows/library_manager.py` (chứa 3 tab lỗi thời) và `ui/windows/monster_manager_win.py` cùng các Controller đi kèm (Library, Monster, Skill Controllers).
2. **Skill Manager Workspace:** Đã tạo mới `ui/views/skill_manager_frame.py` với trạng thái `EmptyState` ("Đang phát triển"), sử dụng `ResponsiveGridBase` chuẩn form để chừa chỗ cho việc phát triển CRUD về sau.
3. **Monster Manager Workspace:**
   - Kế thừa toàn bộ giao diện/chức năng cốt lõi (Treeview, form CRUD, tính năng sắp xếp/tìm kiếm) từ `MonsterManagerWin` sang `ui/views/monster_manager_frame.py`.
   - Ứng dụng thành công `ResponsiveGridBase` giúp form tự tạo thanh cuộn mượt mà thay vì bị nén/vỡ hình khi thu hẹp kích thước ứng dụng (Zero-occlusion).
   - Tái sử dụng hoàn toàn hệ thống dịch `self.app._t` và tokens màu/khoảng cách từ `UIStyleV2`.
4. **App GUI Routing:** Chuyển đổi định tuyến trên Sidebar (C1) sang việc gọi `switch_view("skill_manager")` và `switch_view("monster_manager")` ngay trong `app_gui.py`.

## Phân Tích Kỹ Thuật & Cạm Bẫy Đã Tránh (Pitfalls Avoided)
- **Xung đột Layout Manager:** Không trộn lẫn `pack` và `grid` cùng một cấp bên trong các Frame con. Nhờ dùng `ResponsiveGridBase`, việc quy hoạch được phân chia rõ ràng hơn (outer là pack/grid, content frame là lưới độc lập).
- **Tránh việc viết lại CRUD từ đầu:** Sử dụng lại toàn bộ API thao tác Database/State (`self.db.execute_query` và `ensure_unique_monster_id`), giữ nguyên logic thêm/sửa/xóa đã được kiểm chứng ở bản cũ.
- **Vấn đề Binding và Rò rỉ Bộ Nhớ:** Loại bỏ triệt để các cửa sổ TopLevel giúp dẹp bỏ bài toán phức tạp về `WM_DELETE_WINDOW` và Focus Stealing thường gặp ở Tkinter trên Windows/Linux.

## Hướng Tới (Next Steps)
- Tiến hành thực thi hệ thống CRUD đầy đủ trên Workspace `skill_manager_frame.py`.
- Xem xét lại Timing Calculator (phần bị bỏ lại từ LibraryManagerWindow cũ) để quyết định sẽ được đưa vào Setup View, hay một Modal chuyên dụng mới.
