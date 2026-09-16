# Sprint 32 - Prompt 002: Refactor Labels và Buttons trên Manager Frames

**Vai trò:** UI/UX Developer

**Ngữ cảnh:**
Bộ dữ liệu Key dịch thuật đã được chuẩn bị (Prompt 001). Bây giờ chúng ta sẽ áp dụng các key này để thay thế văn bản cứng trên các khung quản lý.

**Yêu cầu công việc:**
1. Mở các file: `build_manager_frame.py`, `class_manager_frame.py`, `monster_manager_frame.py`, `skill_manager_frame.py`.
2. Thay thế toàn bộ text cứng (như `text="Class (*):"`, `text="Save"`, ...) của `tk.Label` và `tk.Button` bằng lời gọi hàm dịch (`self.app._t("lbl.class")`, `self.app._t("btn.save")`...).
3. Tích hợp với `TranslationBinder` (nếu kiến trúc hiện tại yêu cầu) bằng cách gọi `self.app.bind_text(widget, "btn.save")`.

**Ràng buộc:**
- Đảm bảo giữ nguyên các logic chức năng hiện tại của nút bấm, chỉ sửa phần hiển thị `text=`.
- Tránh thay thế các text mang tính biểu tượng (như `text="+"`) nếu chưa có cơ sở chuyển đổi sang icon.

**Kết quả mong đợi:**
- Không còn hardcoded text (Label, Button) trong thư mục `ui/views/`.
