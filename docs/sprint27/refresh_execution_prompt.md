Dưới đây là một prompt thực thi (execution prompt) chi tiết dựa trên báo cáo lỗi về chức năng Refresh danh sách cửa sổ (Window Detection), được thiết kế để bạn có thể copy/paste trực tiếp cho một AI Agent tiến hành sửa lỗi trong mã nguồn:

---

**PROMPT THỰC THI (Copy phần bên dưới)**

"Bạn đóng vai trò là một kỹ sư phần mềm hệ thống chuyên về Tkinter/Python và Windows API. Dựa trên đánh giá chức năng Refresh danh sách cửa sổ (`Window Detection`) của ứng dụng, hãy thực hiện các bước refactor sau đây để khắc phục tình trạng UI bị đơ (blocking), lỗi API, và logic reset trạng thái cứng nhắc. Hãy sửa trực tiếp vào mã nguồn của ứng dụng.

**Bối cảnh (Context):**
Quá trình liệt kê cửa sổ đang chạy đồng bộ trên luồng chính (Main Thread) của Tkinter thông qua `ui/components/compact_window_selector.py` và sử dụng wrapper `win32gui` có nguy cơ gây lỗi ngầm trong `lib/system/window_manager.py`.

**Nhiệm vụ cụ thể (Tasks):**

1.  **Chuyển đổi sang API WinAPI trực tiếp (Robust Window Enumeration):**
    *   **File:** `lib/system/window_manager.py`.
    *   **Hành động:** Sửa đổi phương thức `list_windows`. Loại bỏ `win32gui.EnumWindows(callback, None)` và thay thế bằng `ctypes.windll.user32.EnumWindows(EnumWindowsProc, 0)`.
    *   **Cụ thể:** Bạn cần định nghĩa `EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int))` và truyền hàm callback tương ứng. Trong callback, sử dụng `ctypes.windll.user32.IsWindowVisible` và `ctypes.windll.user32.GetWindowTextW` để kiểm tra và lấy tiêu đề thay vì phụ thuộc hoàn toàn vào `win32gui`.

2.  **Khử Blocking (Asynchronous Execution) & Sửa logic UI Reset:**
    *   **File:** `ui/components/compact_window_selector.py`.
    *   **Hành động:** Cập nhật logic trong `_on_refresh_clicked` và `_on_refresh` để chúng không block UI.
    *   **Cụ thể:**
        - Khi nút refresh được click (`_on_refresh_clicked`), thiết lập nút sang trạng thái đang tải (Loading state, vd: `state='disabled'`, text `⟳`).
        - Khởi tạo một thread chạy ngầm (`threading.Thread`) để gọi `self.window_controller._list_windows()`.
        - Thay vì dùng hardcode `self.refresh_btn.after(300, reset_btn)`, hãy dùng `self.root.after(0, update_ui_callback, windows)` để đẩy kết quả từ thread ngầm trở lại Main Thread sau khi hàm `_list_windows` trả về kết quả.
        - Trong `update_ui_callback` (tương đương phần thân cũ của `_on_refresh`), thực hiện cập nhật danh sách `self.win_items`, cập nhật nhãn (`info_label`), gọi `_update_listbox()`, và sau đó khôi phục nút refresh về trạng thái hoạt động bình thường (text `🔄`).

**Nguyên tắc thực hiện:**
*   **Luôn Verify:** Sau mỗi thay đổi, hãy chạy `python3 run_tests.py` và chạy thử (headless hoặc GUI) để đảm bảo không sinh ra lỗi cú pháp hay `_tkinter.TclError`, và việc liệt kê cửa sổ thực sự hoạt động, kết quả được nạp vào Listbox.
*   Hãy chú ý đến luồng dữ liệu (Thread Safety): Không cập nhật Tkinter widget (như `listbox.insert` hoặc `info_label.config`) từ bên trong luồng background; luôn dùng `after(0, ...)` để thực hiện ở Main Thread."