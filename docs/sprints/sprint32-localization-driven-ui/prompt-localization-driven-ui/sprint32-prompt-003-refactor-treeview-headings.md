# Sprint 32 - Prompt 003: Refactor Treeview Headings

**Vai trò:** UI/UX Developer

**Ngữ cảnh:**
Các thành phần hiển thị danh sách dạng bảng (Treeview) đang có các tiêu đề cột (Headings) bị hardcode.

**Yêu cầu công việc:**
1. Tìm tất cả các thành phần `ttk.Treeview` trong `ui/views/` và `ui/tabs/` (như `scan_history_frame.py`, `stats_tab.py`).
2. Thay thế text ở `self.tree.heading("ID", text="Build ID")` thành cách gọi lấy key từ dịch thuật, ví dụ: `text=self.app._t("col.build_id")`.
3. Kiểm tra xem `TranslationBinder` có hỗ trợ `tree.heading()` không. Nếu không, viết một custom binder function nhỏ hoặc chỉ gán tĩnh ở hàm khởi tạo tạm thời trong giai đoạn này (vì Treeview khó bind động hơn).

**Ràng buộc:**
- Đảm bảo ánh xạ các key đúng với ngữ cảnh bảng. (ví dụ `col.description` dùng cho cột Mô tả).

**Kết quả mong đợi:**
- Toàn bộ Headings của Treeview được nạp từ khóa Localization.
