# Palette & UI Standards

## Button & UI Standards

1. **Nút HÌNH VUÔNG (Square Button):**
   - Chỉ dành riêng cho loại nút CHỈ CÓ ICON (Icon-only).
   - Tuyệt đối không để text/chữ bên trong nút hình vuông.

2. **Nút HÌNH CHỮ NHẬT (Rectangular Button):**
   - Dùng cho nút CÓ CẢ ICON + TEXT (Ví dụ: "Thêm", "Sửa", "Xóa").
   - Kích thước chiều rộng: Tự động dãn theo nội dung (Auto / Fit-content), không cố định `width` dạng vuông.
   - Độ đệm (Padding): Luôn có horizontal padding (`padx`) tối thiểu 10px - 15px để văn bản và icon không bị xén viền.

Lưu ý: Từ nay về sau, mỗi khi chỉnh sửa hoặc tạo mới bất kỳ thành phần UI nào, bạn MUST đọc và tuân thủ các quy tắc trong `palette.md`.
