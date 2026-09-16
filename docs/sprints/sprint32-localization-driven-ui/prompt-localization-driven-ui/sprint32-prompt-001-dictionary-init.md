# Sprint 32 - Prompt 001: Khởi Tạo Từ Điển Chuẩn (Dictionary Init)

**Vai trò:** AI Tech Lead & Chuyên gia Localization

**Ngữ cảnh:**
Ứng dụng đang trong giai đoạn chuẩn hoá văn bản cứng sang `Metadata-Driven Localization UI`. Bước đầu tiên là phải liệt kê và tạo ra một cấu trúc JSON/Dictionary lưu trữ các key.

**Yêu cầu công việc:**
1. Rà soát nhanh các màn hình chính (`Manager Frames`, `Tabs`, `Panels`) để thu thập các từ khóa text đang hardcode.
2. Thiết kế và tạo mới file cấu trúc từ điển cơ sở (ví dụ `assets/i18n/en.json` và `vi.json` hoặc trong DB tùy kiến trúc hiện tại, chỉ cần đảm bảo định dạng) với bộ key được quy hoạch:
   - Các nút bấm: `btn.save`, `btn.cancel`, `btn.refresh`
   - Các nhãn: `lbl.class`, `lbl.author`, `lbl.target_setup`
   - Tiêu đề cột: `col.id`, `col.name`, `col.description`
3. Cập nhật `App` hoặc `LocalizationManager` (hoặc cấu trúc có sẵn) để đảm bảo có thể load bộ từ điển khởi tạo này thành công.

**Ràng buộc:**
- Không sửa giao diện trong prompt này, chỉ chuẩn bị bộ dữ liệu translation.
- Đảm bảo quy tắc đặt tên key nhất quán, chữ thường, dùng dấu chấm để phân cấp.

**Kết quả mong đợi:**
- Có script/code sinh ra file cấu hình từ điển cho tiếng Việt và tiếng Anh.
