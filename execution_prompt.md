Dưới đây là một prompt thực thi (execution prompt) chi tiết dựa trên báo cáo lỗi UI, được thiết kế để bạn có thể copy/paste trực tiếp cho một AI Agent (như Cursor, GitHub Copilot, hoặc Jules) để tiến hành sửa lỗi trong mã nguồn:

---

**PROMPT THỰC THI (Copy phần bên dưới)**

"Bạn đóng vai trò là một kỹ sư phần mềm chuyên về UI/UX và Tkinter/Python. Dựa trên đánh giá giao diện hiện tại của ứng dụng (sử dụng Dark Theme), hãy thực hiện các bước refactor và styling sau đây để khắc phục các lỗi về độ tương phản, bố cục và widget mặc định. Hãy sửa trực tiếp vào mã nguồn của ứng dụng.

**Bối cảnh (Context):**
Ứng dụng đang sử dụng hệ thống thiết kế Phase 2 (`UIStyleV2` trong `lib/ui_style_v2.py`). Hãy ưu tiên sử dụng các biến màu và style token từ class này (ví dụ: `UI.BG_BASE`, `UI.BG_SURFACE`, `UI.TEXT_PRIMARY`, `UI.ACCENT_GREEN`) thay vì hardcode mã màu hex hoặc dùng các constant `THEME_` cũ.

**Nhiệm vụ cụ thể (Tasks):**

1.  **Sửa lỗi Độ tương phản & Màu nền rò rỉ:**
    *   Tìm khu vực hiển thị số lượng cửa sổ (chữ '0 windows' góc trên bên trái). Thay đổi màu chữ từ đỏ sẫm sang một màu đỏ sáng hơn (light red / pastel red) để dễ đọc trên nền tối.
    *   Sửa màu chữ cho tab 'Săn' ở Sidebar (Menu trái). Đảm bảo chữ bên trong tab có màu sáng (ví dụ: `TEXT_PRIMARY`) để nổi bật trên nền/viền xanh lá.
    *   Tìm các nhãn hiển thị trạng thái như 'Đã lưu tất cả thay đổi' (màu xanh lá đậm) và 'CHỜ' (ở phần Current Target). Thay đổi sang màu sáng hơn hoặc áp dụng màu nền (background/badge) tương phản tốt.
    *   **Lỗi nền trắng:** Tìm Label chứa dòng chữ 'Nhấp chuột phải để xóa từng quái...' (dưới danh sách quái) và Label 'Mục tiêu: Trống' (góc trên phải). Ép các thành phần này sử dụng nền tối (`BG_SURFACE` hoặc `bg` tương ứng) và chữ sáng (`TEXT_PRIMARY`) thay vì để rò rỉ nền trắng của hệ thống.

2.  **Style các Widget Mặc định (Unstyled Components):**
    *   Tìm các Listbox/Treeview ở phần 'Current Target' và 'Skill Performance'. Thiết lập lại màu nền (background) và màu chữ (foreground) cho Listbox/Treeview và các Scrollbar đi kèm để phù hợp với giao diện tối. Tránh dùng Scrollbar mặc định màu trắng/xám sáng của Windows.
    *   Định kiểu lại các nút điều khiển danh sách (+, ^, v, x ở bên phải danh sách quái). Xóa style native (mặc định) và áp dụng thiết kế phẳng phù hợp với nút của ứng dụng (ví dụ: dùng `tk.Button` với `relief='flat'`, set `bg` và `fg`).
    *   Cập nhật style cho thanh điều hướng Tabs (Notebook) 'Quái đã chọn', 'Tự nhận diện', 'Mọi mục tiêu'. Tăng padding và style lại `TNotebook.Tab` để rõ ràng tab nào đang được chọn.
    *   Tìm các Checkbox ('Bật Auto Combo', '0 skills valid') và đảm bảo chúng có style dark mode (không bị viền nổi trắng bao quanh). Sử dụng `selectcolor` phù hợp.

3.  **Sửa Bố cục & Căn chỉnh (Layout & Alignment):**
    *   Tìm khung `LabelFrame` chứa 'Buff Lane'. Sửa lỗi đường viền cắt ngang chữ tiêu đề bằng cách thêm padding dọc (ví dụ `pady=(12, 8)`) để tiêu đề có không gian, hoặc thay thế bằng một Frame thông thường có thẻ tiêu đề (Label) riêng biệt.
    *   Căn chỉnh lại các nút công cụ nhỏ kế bên chữ '0 windows' cho cách xa nhau một chút (thêm padding ngang) và căn giữa theo chiều dọc (vertical alignment) với đoạn text.
    *   Điều chỉnh khoảng cách/padding bên trong các trường nhập liệu (Dropdown, Entry) của phần 'Combo Chain' để giao diện bớt chật chội.
    *   Mở rộng kích thước (width) hoặc thêm padding cho Dropdown ngôn ngữ ('vi') ở góc trên phải để dễ click hơn.

**Nguyên tắc thực hiện:**
*   Sử dụng công cụ tìm kiếm (`grep`, `read_file`) để xác định đúng file chứa UI (thường nằm trong thư mục `ui/panels/`, `ui/components/` hoặc `app_gui.py`).
*   **Luôn Verify:** Sau mỗi thay đổi, hãy đọc lại file hoặc chạy thử nghiệm headless UI để đảm bảo không sinh ra lỗi cú pháp hay `_tkinter.TclError`.
*   Chỉ sử dụng token từ `lib/ui_style_v2.py` (nếu có import), không hardcode màu sắc."
