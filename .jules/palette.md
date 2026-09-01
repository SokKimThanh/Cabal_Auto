2025-08-18 - Singleton Dialogs & Duplicate Name Resolution UX
Learning: Opening multiple instances of a modal editing window leads to state collision and user confusion in desktop Tkinter apps. Enforcing a Singleton pattern using `lift()` and `focus_force()` brings existing edit windows to the front cleanly. Furthermore, validating item name uniqueness with a non-blocking prompt that offers automatic index suffixing (e.g., "Quái Mới (1)") prevents accidental overwrites while maintaining continuous workflow.
Action: Always track active dialog references on parent controllers to bring existing modal dialogs to front when requested, and provide clear index suffixing when handling user-accepted duplicate entries.

2025-10-25 - Standardized Icon Buttons & Multi-Tk Root Cache Pruning
Learning: Standardizing UI buttons across forms and toolbars via unified factory functions (`create_icon_button`, `create_save_button`, `create_cancel_button`, etc.) guarantees visual consistency, height alignment (`variant='compact'` vs `variant='medium'`), and mandatory multi-language tooltips (`tooltip_key`). When running unit tests that create and destroy sequential `tk.Tk()` root instances, cached `PhotoImage` objects or global image reference lists (`_ICON_REFS`) holding dead `Tk` handles will throw `_tkinter.TclError: image "pyimage1" doesn't exist`. Pruning stale references by checking `root.tk.call('image', 'height', ...)` prevents cross-test image leaks.
Action: Always instantiate buttons via `ui.components.create_icon_button` or its helper methods, and prune stale `PhotoImage` references when caching across isolated Tk root instances.

## Button & UI Standards

1. **Nút HÌNH VUÔNG (Square Button):**
   - Chỉ dành riêng cho loại nút CHỈ CÓ ICON (Icon-only).
   - Tuyệt đối không để text/chữ bên trong nút hình vuông.

2. **Nút HÌNH CHỮ NHẬT (Rectangular Button):**
   - Dùng cho nút CÓ CẢ ICON + TEXT (Ví dụ: "Thêm", "Sửa", "Xóa").
   - Kích thước chiều rộng: Tự động dãn theo nội dung (Auto / Fit-content), không cố định `width` dạng vuông.
   - Độ đệm (Padding): Luôn có horizontal padding (`padx`) tối thiểu 10px - 15px để văn bản và icon không bị xén viền.

Lưu ý: Từ nay về sau, mỗi khi chỉnh sửa hoặc tạo mới bất kỳ thành phần UI nào, bạn MUST đọc và tuân thủ các quy tắc trong `palette.md`.

2025-10-26 - Tkinter Button Accessibility
Learning: In a Tkinter Python application, standard HTML ARIA attributes like `aria-label` do not apply and setting them raises a `TclError`. To implement accessibility and clarity for icon buttons that may lack clear context, we must utilize the existing i18n tooltip system by providing `tooltip_key` and `tooltip_ns` arguments to button creation helper functions like `create_icon_button`.
Action: Always attach a tooltip using `tooltip_key` to all icon buttons to ensure functionality is accessible and discoverable.
