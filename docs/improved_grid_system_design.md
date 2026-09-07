# Tài Liệu Thiết Kế: Hệ Thống Grid Cải Tiến (Improved Grid System Design)

## 1. Mục Tiêu (Objective)
Tài liệu này đề xuất một kiến trúc hệ thống Grid (lưới) mới, nhằm chuẩn hóa bố cục cho **toàn bộ các màn hình**. Mục tiêu cốt lõi:
- **Tính nhất quán**: Tuân thủ tuyệt đối các chuẩn thiết kế từ `UIStyleV2`.
- **Responsive & Chống che khuất (Zero-occlusion)**: Khắc phục nhược điểm của kiến trúc `ttk.PanedWindow` hiện tại (như đang dùng trong `HuntTab`), vốn có xu hướng ép nén (shrink) hoặc che lấp component khi không gian hiển thị bị thu hẹp. Giải pháp mới sẽ dùng cơ chế trượt (scroll) linh hoạt để đẩy component lên trên.
- **Component-based Architecture**: Tách biệt UI và Logic thành các component độc lập, có đầu vào (inputs/props) và đầu ra (outputs/callbacks/events) rõ ràng.
- **Theo dõi vòng đời**: Tích hợp cơ chế logging cho các sự kiện layout để dễ dàng debug.

## 2. Kiến Trúc Lõi: Component "ResponsiveGridBase"

Hệ thống sẽ được xây dựng xoay quanh một class gốc (base class) có tên `ResponsiveGridBase` kế thừa từ một khung cuộn (Scrollable Frame). Tất cả các Panel hiện có (như trong `ui/panels/`) sẽ kế thừa từ component này.

### 2.1. Giải pháp Responsive (Cuộn nội dung)
Để đảm bảo các component không bao giờ bị che mất khi kích thước cửa sổ thu hẹp:
- **Canvas + Scrollbar (ttk.Scrollbar)**: `ResponsiveGridBase` sẽ đóng gói một `tk.Canvas` bên ngoài một `tk.Frame` chứa nội dung thực sự.
- **Động lực học Kích thước (Dynamic Resizing)**: Bắt sự kiện `<Configure>` của Canvas để tự động điều chỉnh `width` của Frame bên trong, đảm bảo chiều ngang luôn phủ đầy, nhưng cho phép chiều dọc kích hoạt thanh cuộn (Scrollbar) nếu `reqheight` của Frame vượt quá chiều cao thực tế của Canvas.

### 2.2. Tích hợp UIStyleV2
Mọi chỉ số trong Grid phải được ánh xạ từ `UIStyleV2`:
- `padx`, `pady` sử dụng `UIStyleV2.SPACING_MD`, `SPACING_LG`.
- Backgrounds phải kế thừa từ `UIStyleV2.BG_BASE` hoặc `UIStyleV2.BG_SURFACE`.

### 2.3. Cơ chế Logging Vòng Đời Layout
Base component sẽ tự động ghi log (thông qua thư viện `logging`) khi các sự kiện quan trọng xảy ra:
- `_on_mount`: Log khi component lần đầu tiên được gắn vào lưới.
- `_on_resize`: Log sự thay đổi kích thước đột ngột kèm theo thông tin kích thước không gian mới.
- Khuyến nghị: Log mức độ `DEBUG` để tránh làm nhiễu console trong môi trường Production.

## 3. Kiến Trúc Component Độc Lập (Componentization)

Mặc dù ứng dụng hiện tại đã bắt đầu quá trình mô-đun hóa (ví dụ: chia `HuntTab` thành `MonsterTargetPanel`, `SkillPanel`, v.v. nằm trong `ui/panels/`), kiến trúc mới yêu cầu nâng cấp cách thức truyền dữ liệu:

### 3.1. Cấu trúc một Component tiêu chuẩn
- **Inputs (Đầu vào)**: Nhận thông qua constructor (ví dụ: `initial_data`) và các phương thức `update_state(data: dict)`.
- **Outputs (Đầu ra)**: Truyền các hàm callback thông qua constructor (ví dụ: `on_action_click=self.handle_action`) để Component không cần gọi ngược (tightly-couple) trực tiếp đến `self.app` hoặc các dịch vụ lõi bên dưới nếu không cần thiết.
- **Tách biệt Logic**: Component chỉ chịu trách nhiệm render UI dựa trên Inputs và phát ra sự kiện (Outputs). Logic xử lý (ví dụ: truy vấn DB, gọi API quét màn hình) phải nằm ở lớp Service/Controller.

### 3.2. Cấu trúc Thư mục Đề nghị
Bảo lưu cấu trúc `ui/panels/` hiện có, nhưng bổ sung thêm `ResponsiveGridBase`:
```text
ui/
  components/
    base/
      responsive_grid_base.py  # Chứa Base Class (Canvas + Scrollbar + Logging)
  panels/
    monster_target_panel.py    # Kế thừa ResponsiveGridBase thay vì ttk.LabelFrame
    skill_panel.py             # Kế thừa ResponsiveGridBase
    ...
```

## 4. Nguyên Tắc Cập Nhật & Di Dời (Migration Strategy)
1. **Bước 1**: Tạo `ResponsiveGridBase` hoàn chỉnh với tính năng scroll và logging.
2. **Bước 2**: Chuyển đổi các Panel hiện có trong `ui/panels/` (ví dụ `ScreenStatePanel`, `SkillStatsPanel`, `MonsterTargetPanel`) để kế thừa từ `ResponsiveGridBase` thay vì `tk.Frame` hay `ttk.LabelFrame`.
3. **Bước 3**: Loại bỏ các layout cứng ngắc gây che lấp như `ttk.PanedWindow` trong các Workspace (`ui/tabs/hunt_tab.py`) và thay thế bằng việc xếp các `ResponsiveGridBase` vào một luồng (flow) tự động scroll.
4. **Bước 4**: Tinh chỉnh lại luồng dữ liệu một chiều (One-way data flow: Controller -> Component -> Action).
