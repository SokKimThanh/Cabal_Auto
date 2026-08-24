# P0B - So Code Gốc Với Module Đã Tách Để Tìm Code Bị Mất

Paste `00-global-rules.md` first, then this prompt.

```text
Kiểm tra nguy cơ mất code sau khi tách module. Đây là session audit, ưu tiên đọc và báo cáo. Chỉ sửa code nếu phát hiện lỗi nhỏ, rõ ràng, có thể khôi phục an toàn trong phạm vi hẹp.

Nguồn so sánh:
- File gốc nếu có: .jules/prompts/app_gui_original.md
- File hiện tại: app_gui.py hoặc app_gui.md nếu repo đang dùng bản markdown để so sánh
- Các module đã tách liên quan: ui/tabs/*, ui/controllers/*, ui/windows/*, lib/features/*

Mục tiêu:
1. So các hàm/khối logic quan trọng trong file gốc với file hiện tại và module mới.
2. Tìm các phần có nguy cơ bị mất khi tách module.
3. Đánh giá cách viết mới có đơn giản hơn, rõ hơn, dễ test hơn, hoặc ít gây lỗi hơn không.
4. Nếu cách viết mới phức tạp hơn mà không có lợi ích rõ ràng, đề xuất cải thiện nhỏ, không refactor rộng.

Các nhóm phải rà kỹ:
- Callback của nút, menu, hotkey, combobox, listbox, bind phím/chuột.
- Public attributes trên App mà tab/window/module khác còn đọc hoặc ghi.
- Import bị xóa nhưng vẫn còn người gọi.
- Compatibility fallback cho config cũ, dữ liệu legacy, thiếu dependency, hoặc môi trường headless.
- Config migration và config validation.
- Close/destroy cleanup: hotkey, overlay, thread, window tracker, bot manager, setup wizard, library manager.
- Helper method cũ bị thay bằng `pass`, stub, placeholder, hoặc wrapper rỗng.

Báo cáo bắt buộc:
- Bảng `Gốc -> Hiện tại/module mới -> Trạng thái`.
- Trạng thái dùng một trong các nhãn: `kept`, `moved`, `replaced`, `missing-risk`, `intentionally-removed`.
- Với mọi `missing-risk`, nêu file/hàm liên quan và cách khôi phục đề xuất.
- Với mọi `intentionally-removed`, phải có bằng chứng search reference hoặc lý do rõ ràng.
- Danh sách chỗ code mới đang phức tạp hơn code cũ và đề xuất cách đơn giản hóa.

Không được:
- Không xóa code trong session audit nếu chưa có bằng chứng chắc chắn.
- Không thay thế logic thật bằng `pass` hoặc placeholder.
- Không sửa nhiều nhóm trách nhiệm cùng lúc.

Validation:
- Chạy search/reference checks phù hợp cho các hàm nghi ngờ bị mất.
- Chạy test hẹp nhất có liên quan nếu có sửa code.
- Nếu chỉ tạo báo cáo, không cần chạy test rộng; hãy ghi rõ đây là audit đọc/so sánh.
```
