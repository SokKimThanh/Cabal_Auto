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
- **Động lực học Kích thước (Dynamic Resizing)**: Bắt sự kiện `<Configure>` của Canvas để tự động điều chỉnh `width` của Frame bên trong.
- **Cạm bẫy Runtime (Technical Gotchas)**:
  - Cần gọi `canvas.configure(scrollregion=canvas.bbox("all"))` ngay sau khi frame con thay đổi kích thước, nếu không sẽ xuất hiện lỗi scrollbar "ma" (chỉ báo sai vùng cuộn).
  - Binding sự kiện cuộn chuột (Mouse wheel) phải được xử lý cross-platform: Windows dùng `<MouseWheel>` với delta ±120, trong khi Linux/Mac dùng `<Button-4>` và `<Button-5>`.

### 2.1.a. Chiến lược Responsive cho Sidebar (`shell_zone_c1`)
Vùng Sidebar (Navigation) cũng phải kế thừa cơ chế cuộn tương tự `ResponsiveGridBase`. Khi số lượng tab điều hướng vượt quá chiều cao màn hình, thanh cuộn phải tự động xuất hiện để người dùng không bị mất quyền truy cập vào các tab bên dưới.

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
1. **Bước 1**: Tạo `ResponsiveGridBase` hoàn chỉnh với tính năng scroll và logging, đảm bảo chữ ký (constructor signature) tương thích ngược (hoặc có wrapper proxy) với `ttk.LabelFrame` để không phá vỡ logic khởi tạo hiện hành.
2. **Bước 2**: Xác định ưu tiên chuyển đổi (Priority Routing) - Bắt đầu từ các Panel ít phụ thuộc nhất (như `SkillStatsPanel`), kiểm thử hồi quy (regression test) trước khi di dời các Panel phức tạp hơn (như `MonsterTargetPanel`).
3. **Bước 3**: Loại bỏ các layout cứng ngắc gây che lấp như `ttk.PanedWindow` trong các Workspace (`ui/tabs/hunt_tab.py`) và thay thế bằng việc xếp các `ResponsiveGridBase` vào một luồng (flow) tự động scroll.
4. **Bước 4**: Tinh chỉnh lại luồng dữ liệu một chiều (One-way data flow: Controller -> Component -> Action).

## 5. Tiêu Chí Đo Lường Sự Thành Công (Measurable Criteria)
Để xác nhận quá trình migration sang hệ thống lưới mới thành công và đạt được mục tiêu "chống che khuất", hệ thống phải thỏa mãn các tiêu chí đo lường sau:

### 5.1. Kích thước cửa sổ (Window Dimensions)
- **Độ phân giải mục tiêu (Target Resolution)**: Giao diện phải hiển thị hoàn hảo, không có thanh cuộn (scrollbars) dư thừa ở độ phân giải tiêu chuẩn `1920x1080`.
- **Kích thước cửa sổ tối thiểu (Minimum Window Size)**: Giao diện phải duy trì được cấu trúc, không bị lỗi layout khi cửa sổ bị ép xuống kích thước tối thiểu là `800x600`. Dưới kích thước này, thanh cuộn phải xuất hiện để bao bọc toàn bộ nội dung.

### 5.2. Đo lường "Chống che khuất" và UX (Zero-occlusion & UX Metrics)
- **Kiểm tra thông số kỹ thuật (Technical Verification)**: Hệ thống test cần xác nhận: `widget.winfo_width() >= widget.winfo_reqwidth()` đối với tất cả các leaf-widgets.
- **Hạn chế phá vỡ UX (UX Fallback)**: Mặc dù giải pháp cuộn ngăn chặn việc che khuất dữ liệu, nhưng đối với `HuntTab` - nơi yêu cầu theo dõi thông tin real-time đồng thời (HP quái, skill, status) - việc phải cuộn có thể giấu đi thông tin sinh tử. Do đó:
  - Phải đặt một **Ngưỡng Kích Thước Tối Thiểu Tĩnh (Hard Minimum Constraint)** cho toàn bộ `HuntTab` (ví dụ: `800x600`), từ chối thu nhỏ cửa sổ nhỏ hơn ngưỡng này ở cấp độ OS window.
  - Trong trường hợp bắt buộc phải cuộn (do giới hạn phần cứng đặc biệt), cần có cơ chế **Ưu tiên Hiển thị (Stacking Priority)**: Panel Quái Mục Tiêu và Kỹ Năng Đang Dùng phải được ghim hoặc nằm ở vị trí ưu tiên cao nhất, các panel phụ trợ (như Skill Stats) sẽ bị đẩy xuống vùng cuộn phía dưới.
