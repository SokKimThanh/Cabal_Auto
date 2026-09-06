Dưới đây là một prompt thực thi (execution prompt) chi tiết dựa trên báo cáo lỗi UI, được thiết kế để bạn có thể copy/paste trực tiếp cho một AI Agent (như Cursor, GitHub Copilot, hoặc Jules) để tiến hành sửa lỗi trong mã nguồn:

---

**PROMPT THỰC THI (Copy phần bên dưới)**

"Bạn đóng vai trò là một kỹ sư phần mềm chuyên về UI/UX và Tkinter/Python. Dựa trên đánh giá giao diện hiện tại của ứng dụng (sử dụng Dark Theme), hãy thực hiện các bước refactor và styling sau đây để khắc phục các lỗi về độ tương phản, bố cục và widget mặc định. Hãy sửa trực tiếp vào mã nguồn của ứng dụng.

**Bối cảnh (Context):**
Ứng dụng đang sử dụng hệ thống thiết kế Phase 2 (`UIStyleV2` trong `lib/ui_style_v2.py`). Hãy ưu tiên sử dụng các biến màu và style token từ class này (ví dụ: `UI.BG_BASE`, `UI.BG_SURFACE`, `UI.TEXT_PRIMARY`, `UI.ACCENT_GREEN`) thay vì hardcode mã màu hex hoặc dùng các constant `THEME_` cũ.

**Nhiệm vụ cụ thể (Tasks):**

1.  **Sửa lỗi Độ tương phản & Màu nền rò rỉ:**
    *   **"0 windows"**: Trong `ui/components/compact_window_selector.py` (tìm chuỗi `"✗ 0 windows"`). Thay đổi màu chữ từ đỏ sẫm sang một màu đỏ sáng hơn (light red / pastel red) để dễ đọc trên nền tối.
    *   **Tab "Săn" ở Sidebar**: Trong `app_gui.py` (vòng lặp tạo `tk.Button` cho `sidebar_items`). Đảm bảo chữ bên trong tab có màu sáng (ví dụ: `TEXT_PRIMARY`) để nổi bật trên nền/viền xanh lá.
    *   **Nhãn trạng thái**: Trong `ui/panels/target_status_panel.py` (các nhãn như `hunt_status_badge` dùng `StatusBadge`). Thay đổi sang màu sáng hơn hoặc áp dụng màu nền (background/badge) tương phản tốt.
    *   **Lỗi nền trắng**:
        *   Nhãn "Nhấp chuột phải để xóa từng quái..." trong `ui/panels/monster_target_panel.py` (biến `monster_rotation_delete_hint`). Ép sử dụng nền tối (`BG_SURFACE`) và chữ sáng (`TEXT_PRIMARY`).
        *   Nhãn "Mục tiêu: Trống" trong `ui/panels/target_status_panel.py` (`hunt_target_info_label`). Ép sử dụng nền tối và chữ sáng.

2.  **Style các Widget Mặc định (Unstyled Components):**
    *   **Thanh cuộn (Scrollbar)**: Trong `ui/panels/monster_target_panel.py` (các `tk.Scrollbar` cho `monster_rotation_listbox` và `detected_monsters_listbox`) và `ui/panels/skill_stats_panel.py` (`tk.Scrollbar`). Cập nhật để chúng không dùng giao diện mặc định (trắng/xám sáng) của Windows.
    *   **Nút điều khiển danh sách**: Trong `ui/panels/monster_target_panel.py` (các nút dùng `_create_icon_button` như `btn_add_monster`, `btn_move_up`, v.v.). Xóa style native và áp dụng thiết kế phẳng phù hợp với giao diện.
    *   **Thanh điều hướng Tabs**: Trong `ui/panels/monster_target_panel.py` (hiện tại dùng `ttk.Radiobutton` nhưng đóng vai trò như tabs điều hướng cho policy). Style lại để phân biệt rõ tab nào đang được chọn và tăng padding.
    *   **Checkbox**: Trong `ui/panels/skill_panel.py` (tìm `tk.Checkbutton` của biến Auto Combo). Đảm bảo không bị viền nổi trắng bao quanh, sử dụng `selectcolor` phù hợp.

3.  **Sửa Bố cục & Căn chỉnh (Layout & Alignment):**
    *   **Khung viền Buff Lane**: Trong `ui/panels/skill_panel.py` (tìm `skill_strip.buff_lane`). Sửa lỗi đường viền cắt ngang chữ tiêu đề bằng cách thêm padding dọc, hoặc sử dụng `tk.Frame` với `tk.Label` rời thay vì `LabelFrame`.
    *   **Khoảng cách nút công cụ**: Trong `ui/components/compact_window_selector.py` (khu vực gần chữ "0 windows"). Thêm padding ngang cho các nút công cụ nhỏ và căn giữa theo chiều dọc.
    *   **Khoảng cách Dropdown/Entry**: Trong `ui/panels/skill_panel.py` (khu vực Combo Chain / Dropdown). Tăng không gian và padding để giao diện bớt chật chội.

**Nguyên tắc thực hiện:**
*   **Luôn Verify:** Sau mỗi thay đổi, hãy đọc lại file hoặc chạy thử nghiệm headless UI để đảm bảo không sinh ra lỗi cú pháp hay `_tkinter.TclError`.
*   Chỉ sử dụng token từ `lib/ui_style_v2.py` (nếu có import), không hardcode màu sắc."
