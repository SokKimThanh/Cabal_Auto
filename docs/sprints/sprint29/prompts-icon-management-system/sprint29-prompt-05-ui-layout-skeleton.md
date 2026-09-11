# Prompt 05: Khởi tạo UI Layout Skeleton cho IconManagerFrame

## Mục tiêu
Tạo bộ khung (skeleton) giao diện cơ bản cho `IconManagerFrame` bằng Tkinter theo đúng bố cục 3 khu vực + 1 bottom bar đã định nghĩa trong mục "6.1. Bố cục không gian làm việc". Đảm bảo layout scale tốt khi phóng to/thu nhỏ.

## Ngữ cảnh & Yêu cầu từ Đặc tả
Bố cục được chia thành:
- **Top Filter Bar:** Dành cho ô tìm kiếm và các dropdown lọc.
- **Left Sidebar:** Danh sách Master List dạng cây.
- **Right Zone:** Khung chi tiết và form nhập liệu.
- **Bottom Action Bar:** Khu vực cố định dưới cùng chứa các nút hệ thống.
Tất cả các khu vực này chỉ cần DỰNG KHUNG, chưa cần đắp logic hay widget chi tiết bên trong.

## Các bước triển khai chi tiết dành cho Người/AI

### Bước 1: Khởi tạo class IconManagerFrame
- **Vị trí:** Tạo file `ui/panels/icon_manager_frame.py` (hoặc `ui/frames/...`).
- **Hành động:**
  - Khai báo class `IconManagerFrame` kế thừa từ `tk.Frame` (hoặc `ttk.Frame`).
  - Trong `__init__`, nhận các biến cần thiết (VD: `parent`, `app_state`, ...).
  - Đặt màu nền bằng `UIStyle.BG_BASE` hoặc màu tương tự của dự án (Lưu ý: Không dùng các token cũ như `THEME_BG_APP`).

### Bước 2: Xây dựng Layout Grid (Bộ xương chính)
- **Hành động:** Sử dụng `pack` hoặc `grid` manager (ưu tiên `grid` vì dễ chia cột/hàng) cho chính `IconManagerFrame`:
  - `row 0`: Top Bar (chiếm hết chiều ngang).
  - `row 1`: Vùng Content chính (chiếm hết không gian còn lại).
  - `row 2`: Bottom Bar (chiếm hết chiều ngang, bám đáy).

### Bước 3: Định hình vùng Content (Phân chia Left - Right)
- **Hành động:**
  - Tại `row 1`, tạo một PanedWindow (hoặc Frame chia 2 cột bằng `grid`):
    - Cột 1 (Left Sidebar): Dành cho Treeview sau này. Cấp một kích thước tối thiểu (VD: `width=250`). Đặt background khác màu chút để dễ phân biệt (lúc đang làm khung).
    - Cột 2 (Right Detail Zone): Dành cho Preview và Form. Thiết lập `weight=1` để chiếm toàn bộ phần diện tích mở rộng.

### Bước 4: Tạo Base Frames rỗng cho từng khu vực
- **Hành động:**
  - Tạo `self.top_filter_frame` (ở row 0). Đặt 1 label giữ chỗ: "Top Filter Bar Area".
  - Tạo `self.left_master_frame` (ở cột 1, content). Đặt 1 label: "Master List Area".
  - Tạo `self.right_detail_frame` (ở cột 2, content). Đặt 1 label: "Detail & Form Area".
  - Tạo `self.bottom_action_frame` (ở row 2). Đặt 1 label: "Bottom Action Bar Area".
  - **Lưu ý:** Đừng quên gán màu nền (bg) hợp lý để nhìn thấy rõ các khối trước khi đổ widget thật.

### Bước 5: Đăng ký Frame vào App Navigation
- **Hành động:**
  - Mở file điều hướng chính (VD: `app_gui.py` hoặc chỗ quản lý các View).
  - Khai báo và khởi tạo `IconManagerFrame`, đưa nó vào dictionary quản lý views (`self._views['icon_manager'] = IconManagerFrame(...)`).
  - (Tùy chọn) Thêm tạm 1 menu vào sidebar để có thể bấm vào test giao diện ngay (sẽ sửa chuẩn chỉnh lại sau ở phần tích hợp workflow).

## Tiêu chí hoàn thành (Definition of Done)
- [ ] Mở ứng dụng, điều hướng sang màn hình Icon Manager.
- [ ] Giao diện hiển thị đúng 4 khối (Top, Left, Right, Bottom).
- [ ] Khi resize cửa sổ, khối Right (Detail) phình to/thu nhỏ đúng tỷ lệ, khối Left giữ nguyên (hoặc thay đổi theo tỷ lệ nhẹ), Top/Bottom giữ nguyên chiều cao, bám lề.
- [ ] Code không dùng nhầm `grid` và `pack` trong cùng 1 cha (tránh `TclError`).

## Thời gian dự kiến: ~20 phút
