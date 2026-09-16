# Tổng hợp rủi ro & Thứ tự chạy lại dự kiến (Re-execute Order)

Tài liệu này dùng để hoạch định các chiến lược sửa sai (rollback hoặc re-execute) trong trường hợp quá trình chạy tự động các prompt (001 - 005) gặp sự cố.

## I. Phân Tích Rủi Ro Kỹ Thuật

1. **Rủi ro Dịch Thuật Cơ Sở (Prompt 001):**
   - **Mức độ:** Nghiêm trọng (Chặn mọi tiến trình sau).
   - **Mô tả:** Nếu file Dictionary lỗi syntax (JSON fail) hoặc cơ chế đọc biến/database fail, mọi component sử dụng key đều sẽ hiển thị rỗng hoặc báo lỗi.
2. **Rủi ro Tham Số Động (Prompt 004):**
   - **Mức độ:** Trung bình.
   - **Mô tả:** Truyền thiếu kwargs vào hàm dịch, ví dụ `{current} / {total}` nhưng code không cung cấp biến `{total}`, dẫn đến lỗi `KeyError` lúc render UI Panels.
3. **Rủi ro Binding Sự Kiện & Treeview (Prompt 003, 005):**
   - **Mức độ:** Thấp đến Trung bình.
   - **Mô tả:** Tkinter Treeview không hỗ trợ lưu `Variable` ở Headings. Việc gọi lại `tree.heading()` khi ngôn ngữ thay đổi thông qua Binder có thể gặp khó khăn hoặc crash nếu instance bị xóa.

## II. Thứ Tự Ưu Tiên Chạy Lại (Nếu có Lỗi Hồi Quy)

Trong quá trình thực thi, nếu các bài Review phát hiện lỗi, tiến trình re-execute (fix bug) phải tuân theo thứ tự chặt chẽ sau (từ mức nền tảng đi lên):

1. **Re-execute Prompt 001 (Từ Điển/Hạ Tầng)**
   - *Khi nào:* Nếu các view báo lỗi `KeyNotFound`, hoặc lỗi load config.
   - *Hành động:* Fix file từ điển và hàm khởi tạo.

2. **Re-execute Prompt 003 (Treeview)**
   - *Khi nào:* Bảng danh sách bị lỗi formating, mất cột, crash do truyền sai key vào `tree.heading()`.
   - *Hành động:* Cách ly lỗi treeview khỏi các thành phần label/button thuần.

3. **Re-execute Prompt 004 (Dynamic Panel)**
   - *Khi nào:* Lỗi `KeyError` ở Python Format String khi render trạng thái tĩnh/động.
   - *Hành động:* Kiểm tra lại cách truyền params `**kwargs` vào hàm Localization.

4. **Re-execute Prompt 005 (Binder / Leak Check)**
   - *Khi nào:* Ứng dụng chạy mượt nhưng khi đổi ngôn ngữ thì UI bị "đứng" hoặc lỗi WeakRef.
   - *Hành động:* Fix logic đăng ký sự kiện của `TranslationBinder` mà không đụng tới cấu trúc UI.

5. **Re-execute Prompt 002 (Labels/Buttons tĩnh)**
   - *Khi nào:* Thiếu hoặc sai typo hiển thị text tĩnh.
   - *Hành động:* Sửa typo đơn giản. (Ít ưu tiên nhất vì ít rủi ro sập app).
