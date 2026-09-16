# Sprint 32 - Prompt 005: Kiểm tra tích hợp TranslationBinder

**Vai trò:** QA Engineer & Tech Lead

**Ngữ cảnh:**
Các text đã được refactor. Bước cuối là đảm bảo cơ chế thay đổi ngôn ngữ hoạt động ổn định trên toàn bộ UI vừa sửa.

**Yêu cầu công việc:**
1. Kích hoạt tính năng chuyển đổi ngôn ngữ (Event `LanguageChangedEvent`).
2. Rà soát các vùng vừa được refactor (Manager Frames, Panels, Treeviews) xem có thành phần nào không chịu tự cập nhật (Refresh) khi đổi ngôn ngữ không.
3. Fix lỗi cho các widget chưa được bind qua `TranslationBinder.bind_text()`. (Đặc biệt lưu ý các Treeview headings).

**Ràng buộc:**
- Hoạt động ổn định, không gây crash hoặc Memory Leak qua WeakRef.

**Kết quả mong đợi:**
- Ứng dụng tự động thay đổi ngôn ngữ mượt mà không cần restart lại.
