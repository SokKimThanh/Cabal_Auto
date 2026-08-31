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
## 2026-08-31 - Accessible Tkinter Collapsible Headers
**Learning:** Tkinter interactive frames (like a collapsible accordion header) do not naturally accept keyboard focus or events. When making them accessible, explicitly set `takefocus=1`, add a visible focus indicator using `highlightthickness` and `<FocusIn>` / `<FocusOut>` event bindings (safely guarded with try-except to avoid issues if the widget doesn't support `bg` config or is destroyed), and explicitly bind both `<Return>` and `<space>` keys for activation.
**Action:** Always apply this focus/keyboard pattern when using `Frame` or `Label` elements as interactive UI toggles in Tkinter.
