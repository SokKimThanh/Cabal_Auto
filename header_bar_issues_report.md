# Đánh giá Layout Header Bar & Sidebar - Issues Report

Dựa trên yêu cầu và việc rà soát mã nguồn trong file `app_gui.py`, dưới đây là tổng hợp các vấn đề về tỷ lệ kích thước (scaling), phân bổ cột của Header Bar (Vùng A) và lỗi co giãn Sidebar.

## 1. Vấn đề Phân bổ Layout của Header Bar (Action Bar - `shell_zone_a`)
**Tình trạng hiện tại:**
- Khung `action_bar_frame` hiện đang sử dụng hệ thống lưới (`grid`) 6 cột với kích thước tối thiểu cứng (`minsize` cố định).
- Việc nhồi nhét tất cả các component (Compact Window Selector, Scan Button, Screen State Panel, Start/Stop Button, Language Dropdown) vào một hàng ngang khiến giao diện bị ép ngang và khó tương thích với các màn hình nhỏ, hoặc bị co cụm khi resize.
- Vùng Header chưa có giới hạn chiều cao tối đa thích hợp, hoặc cơ chế hiển thị scroll khi nội dung bị đẩy xuống.

**Giải pháp đề xuất (3 Cột + Scroll):**
- **Cấu trúc lại:** Thiết kế lại `action_bar_frame` thành một Container chính gồm 3 cột (Columns):
  - **Cột Trái (Left Column):** Chứa các công cụ chọn cửa sổ (`CompactWindowSelector`) và nút Scan.
  - **Cột Giữa (Center Column):** Dành riêng cho `ScreenStatePanel` (hiển thị trạng thái HP/MP, Level, Class).
  - **Cột Phải (Right Column):** Chứa các nút điều khiển chính (Start/Stop, Language Selector).
- **Cơ chế Scroll:** Bọc `action_bar_frame` trong một `tk.Canvas` kèm `ttk.Scrollbar` (hoặc custom scrollbar). Set chiều cao cố định cho Canvas này (ví dụ: `height=80` hoặc `100`). Nếu các component bên trong 3 cột tràn xuống khiến chiều cao frame lớn hơn Canvas, thanh cuộn sẽ xuất hiện để tiết kiệm diện tích thay vì đẩy toàn bộ app xuống.

## 2. Lỗi Tỷ lệ Chiều cao giữa Header Bar và Sidebar (`shell_zone_c1` & Workspace)
**Tình trạng hiện tại:**
- Lỗi: Khi click chuyển đổi giữa các menu trên Sidebar (gọi hàm `switch_view`), tỷ lệ chiều cao của Sidebar và Workspace (`shell_zone_b`) so với Header Bar bị thay đổi không ổn định, dẫn đến hiện tượng "giật" hoặc khung giao diện hàng thứ hai bị co giãn sai.
- Nguyên nhân kỹ thuật trong `app_gui.py`:
  - Lưới chính (`main_shell`) chia làm 2 hàng: Hàng 0 là `shell_zone_a` (Header), Hàng 1 là `shell_zone_b` (Workspace).
  - `shell_zone_c1` (Sidebar) được set `rowspan=2` (phủ qua cả Hàng 1 và Hàng 2 - footer log). Tuy nhiên, có sự xung đột về trọng số (`weight`): `rowconfigure(0, weight=0)` nhưng ngay bên dưới lại dùng `grid_rowconfigure(0, weight=1)`, khiến Hàng 0 (chứa Header) cố gắng co giãn tranh giành chiều cao với Hàng 1.
  - Mỗi khi `switch_view` được gọi, nội dung bên trong `shell_zone_b` thay đổi kích thước. Vì Hàng 0 không bị "khóa cứng" kích thước chiều cao, nó bị nội dung khổng lồ của Hàng 1 đẩy hoặc kéo lệch tỷ lệ.

**Giải pháp đề xuất:**
- Sửa lại cấu hình Grid của `main_shell`: Xóa bỏ dòng `self.main_shell.grid_rowconfigure(0, weight=1)` để đảm bảo Hàng 0 (Header Bar) hoàn toàn tĩnh (`weight=0`, giữ đúng `minsize`).
- Đặt `grid_propagate(False)` nghiêm ngặt cho `shell_zone_a` hoặc set kích thước chính xác cho Canvas bọc nó để đảm bảo việc thay đổi nội dung bên trong `shell_zone_b` không bao giờ tác động ngược lên chiều cao của Hàng 0.