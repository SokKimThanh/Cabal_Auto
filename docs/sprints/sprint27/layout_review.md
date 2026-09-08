# Tài Liệu Review Bố Cục Màn Hình Ứng Dụng (Application Layout Review)

## Tổng Quan (Overview)
Bố cục chính của ứng dụng được xây dựng dựa trên lưới (grid) Tkinter trong `app_gui.py`, chia làm 3 vùng chính để đảm bảo khả năng đáp ứng và trải nghiệm người dùng tối ưu:

### 1. Khu Vực Hành Động Phía Trên (Top Action Bar) - `shell_zone_a`
- **Vị trí**: Nằm ở hàng trên cùng của giao diện.
- **Thuộc tính Layout**: Cố định chiều cao (vd: `height=80`), `weight=0` (không giãn nở theo chiều dọc), và sử dụng `grid_propagate(False)` để tránh bị xô lệch khi thay đổi kích thước nội dung bên trong.
- **Thành phần chính**:
  - Chứa các nút chức năng tổng quan hoặc thông tin trạng thái màn hình (ví dụ: `ScreenStatePanel`).
  - Nơi hiển thị thông báo theo thời gian thực như trạng thái Scan, Thumbnail quét màn hình.

### 2. Khu Vực Thanh Bên (Sidebar) - `shell_zone_c1`
- **Vị trí**: Nằm bên trái giao diện, kéo dài từ trên xuống dưới (sử dụng `rowspan`).
- **Thành phần chính**:
  - Chứa hệ thống điều hướng (Navigation Sidebar).
  - Bao gồm các nút chuyển tab chính yếu như: **Hunt** (Bố cục 4-panel), **Setup**, v.v.

### 3. Khu Vực Không Gian Làm Việc (Active Workspace) - `shell_zone_b`
- **Vị trí**: Nằm ở phần trung tâm/bên phải, chiếm phần lớn diện tích màn hình.
- **Thuộc tính Layout**: Có `weight=1` để mở rộng tối đa (co giãn theo kích thước cửa sổ).
- **Thành phần chính**:
  - Đây là nơi hiển thị nội dung chi tiết tương ứng với tab được chọn ở thanh bên.
  - **Ví dụ nổi bật (Hunt Tab)**: Sử dụng một hệ thống lưới 2x2 cân bằng (4-panel layout) thông qua `ttk.PanedWindow`:
    - `MonsterTargetPanel`: Hiển thị HP, cấp độ, thông tin quái mục tiêu và chiến lược xoay vòng mục tiêu.
    - `SkillPanel`: Khu vực hiển thị các ô kỹ năng.
    - `TargetStatusPanel`: Hiển thị tình trạng chi tiết.
    - `SkillStatsPanel`: Hiển thị chỉ số liên quan đến kỹ năng.

## Điểm Mạnh Của Kiến Trúc Hiện Tại
1. **Quản lý Vùng Rõ Ràng**: Các zone được chia cắt chức năng cụ thể giúp dễ bảo trì mã nguồn, khi cập nhật không làm vỡ giao diện chung.
2. **Khả Năng Chống Gãy Đổ (Layout Stability)**: Áp dụng fixed height (`weight=0`) cho Top Action Bar, ngăn lỗi giao diện giật nhấp nháy khi chuyển Workspace.
3. **Mở Rộng Dễ Dàng**: Không gian `shell_zone_b` là vùng chứa (container) linh hoạt, có thể chèn các giao diện màn hình mới độc lập mà không cần phải viết lại khung sườn chính.
