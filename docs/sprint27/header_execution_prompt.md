Dưới đây là một prompt thực thi (execution prompt) chi tiết dựa trên báo cáo đánh giá Header Bar & Sidebar Layout, được thiết kế để bạn có thể copy/paste trực tiếp cho một AI Agent tiến hành sửa lỗi trong mã nguồn `app_gui.py`:

---

**PROMPT THỰC THI (Copy phần bên dưới)**

"Bạn đóng vai trò là một kỹ sư phần mềm chuyên về Tkinter UI/UX. Dựa trên đánh giá cấu trúc giao diện hiện tại của file `app_gui.py`, hãy thực hiện các bước refactor sau đây để khắc phục lỗi co giãn Sidebar và tái thiết kế Header Bar thành 3 cột có thanh cuộn (scrollbar). Hãy sửa trực tiếp vào mã nguồn của ứng dụng.

**Bối cảnh (Context):**
Ứng dụng sử dụng Grid layout trên `main_shell`. Hiện tại đang xảy ra xung đột `weight` khiến chiều cao Sidebar (`shell_zone_c1`) không ổn định khi đổi tab, và Header Bar (`action_bar_frame`) đang bị nhồi nhét quá nhiều vào một hàng 6 cột.

**Nhiệm vụ cụ thể (Tasks):**

1.  **Sửa lỗi co giãn (Scaling Bug) của Sidebar & Workspace:**
    *   **Vị trí:** Trong file `app_gui.py`, hàm `_build_ui()`.
    *   **Hành động:**
        - Tìm phần "Ensure main_shell fills root window". Hãy xóa dòng `self.main_shell.grid_rowconfigure(0, weight=1)` để đảm bảo Hàng 0 (Header Bar) giữ kích thước tĩnh tĩnh (`weight=0`), không tranh giành chiều cao với Hàng 1 (Workspace, giữ nguyên `weight=1`).
        - Ngay dưới đoạn khởi tạo `self.shell_zone_a`, thêm dòng `self.shell_zone_a.grid_propagate(False)` để khóa cứng chiều cao của Header.

2.  **Thiết kế lại Header Bar (3 Cột + Scrollbar):**
    *   **Vị trí:** Trong file `app_gui.py`, phần khởi tạo `self.action_bar_frame` bên trong `shell_zone_a`.
    *   **Hành động:**
        - **Bọc Scroll:** Tạo một `tk.Canvas` trong `shell_zone_a` (set `height=100` hoặc tương đương) và gắn `ttk.Scrollbar` ngang/dọc cho nó nếu cần thiết (ưu tiên thanh cuộn ngang nếu thiếu diện tích ngang, hoặc cuộn dọc nếu component rớt dòng). Tạo `self.action_bar_frame` bên trong Canvas này (sử dụng `create_window`).
        - **Cấu hình Lưới (Grid):** Sửa cấu hình `.columnconfigure` của `action_bar_frame` từ 6 cột xuống còn đúng 3 cột. Đặt weight phù hợp (vd: Cột 0 `weight=1`, Cột 1 `weight=1`, Cột 2 `weight=1`).
        - **Phân bổ Component:** Gán lại giá trị `column` trong các hàm `.grid()` của các widget con:
            - **Cột 0 (Trái):** Đặt `compact_window_selector` và nút `btn_manual_scan`. Bạn có thể cần tạo một Frame phụ trợ (sub-frame) ở Cột 0 để chứa hai widget này bằng `pack(side="left")`.
            - **Cột 1 (Giữa):** Đặt `bounds_placeholder` (chứa `screen_state_panel`). Set `column=1`.
            - **Cột 2 (Phải):** Đặt nút `start_stop_btn` và `lang_cmb` (Language Selector). Tạo một Frame phụ trợ ở Cột 2 để chứa chúng.

**Nguyên tắc thực hiện:**
*   **Luôn Verify:** Sau mỗi thay đổi, hãy chạy `python3 run_tests.py` và chạy thử giao diện để đảm bảo việc di chuyển widget không gây ra lỗi `_tkinter.TclError` (như lỗi bad window path).
*   Đảm bảo việc gán scrollbar vào canvas được cấu hình đúng lệnh (vd: `canvas.configure(scrollregion=canvas.bbox("all"))`)."
