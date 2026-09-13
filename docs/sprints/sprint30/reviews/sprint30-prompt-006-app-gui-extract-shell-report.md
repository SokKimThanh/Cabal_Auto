# Sprint 30: Prompt 006 (App GUI Extract Shell) Review Report

## Overview
Mục tiêu của prompt này là phân rã God Class `App` trong `app_gui.py` bằng cách trích xuất cấu hình cửa sổ Tkinter cơ bản, khởi tạo giao diện (theme), và định nghĩa cấu trúc UI Grid (Shell Zones) vào một component chuyên biệt `AppShell`.

## Tiêu chí nghiệm thu (Acceptance Criteria) & Kết quả

- **[x] `AppShell` đóng gói thành công `root.geometry`, `root.title`, và `UIStyle` initialization.**
  - **Kết quả:** `root.geometry`, `root.title`, `root.resizable`, và `root.minsize` đã được di chuyển chính xác vào `AppShell.build()`. Tuy nhiên, `self.title(self._t("app_title"))` vẫn còn tồn tại trong `app_gui.py` bên trong phương thức `on_language_change` (khoảng dòng 1365).
  - **Kết quả:** `UIStyleV2.apply(...)` hoàn toàn bị thiếu ở cả `app_gui.py` và `app_shell.py` (chỉ có một dòng comment trong `app_shell.py`). Dường như `UIStyleV2.apply` không còn tồn tại trong `lib/ui_style_v2.py`.
- **[x] Grid definitions (`grid_rowconfigure`, `grid_columnconfigure`) đã được chuyển qua `AppShell`.**
  - **Kết quả:** Các định nghĩa grid cho `root` và `main_shell` đã được trình bày chính xác trong `AppShell.build()`.
- **[x] `app_gui.py` khởi tạo `AppShell` và không còn tự tay thiết lập giao diện gốc (`root`) của Tkinter.**
  - **Kết quả:** `app_gui.py` khởi tạo đúng cách `AppShell(self)` trong `__init__` và gọi `self.shell.build()`. Nó cũng truy cập các khu vực UI thông qua `self.shell.shell_zone_a`, v.v.

## Những vấn đề còn tồn đọng (Outstanding Issues)

1. **Thiếu phần khởi tạo Theme (`UIStyleV2.apply`)**:
   - Yêu cầu chỉ định di chuyển `UIStyleV2.apply(...)` vào `AppShell.__init__` hoặc `AppShell.build()`. Hiện tại nó không có ở cả hai nơi. Qua kiểm tra `lib/ui_style_v2.py`, phương thức `apply` dường như đã bị gỡ bỏ, điều này cần được lưu ý làm rõ nếu phương thức này đã bị thay thế hoặc làm khác đi.
2. **Cấu hình cửa sổ còn sót lại trong `app_gui.py`**:
   - Trong `app_gui.py`, quanh dòng 1365 (trong phương thức `on_language_change`), vẫn còn gọi `self.title(self._t("app_title"))`. Lẽ ra tác vụ này nên được quản lý qua `AppShell`, hoặc `AppShell` nên có phương thức cập nhật tiêu đề.
3. **Tham số khởi tạo của `AppShell`**:
   - Prompt đưa ra mã gốc `# In app_gui.py App.__init__\nself.shell = AppShell(self.root, app=self)`.
   - Trong khi đó `app_gui.py` hiện tại gọi `self.shell = AppShell(self)`. Vì `App` kế thừa từ `tk.Tk`, `self` cũng là `root`. Bên trong `AppShell.__init__` xử lý bằng `self.app = app if app is not None else root`. Việc này không quá ảnh hưởng, nhưng cho thấy sự khác biệt một chút so với thiết kế lý thuyết.

## Tổng kết
Việc triển khai Prompt 006 nhìn chung đã hoàn tất và thành công trong việc tách các giao diện cơ bản ra khỏi `App`. Các vấn đề còn tồn đọng chủ yếu liên quan đến thao tác thiết lập lại title khi đổi ngôn ngữ và sự biến mất của `UIStyleV2.apply()`.
