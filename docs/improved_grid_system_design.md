# Tài Liệu Thiết Kế: Hệ Thống Grid Cải Tiến (Improved Grid System Design)

## 1. Mục Tiêu (Objective)
Dựa trên tài liệu `layout_review.md` và tình trạng hiện tại của ứng dụng, tài liệu này đề xuất một kiến trúc hệ thống Grid (lưới) mới, nhằm chuẩn hóa bố cục cho **toàn bộ các màn hình**. Mục tiêu cốt lõi:
- **Tính nhất quán**: Tuân thủ tuyệt đối các chuẩn thiết kế từ `UIStyleV2`.
- **Responsive & Chống che khuất**: Giải quyết bài toán thiếu không gian hiển thị bằng cơ chế trượt (scroll) linh hoạt, đẩy component lên trên thay vì che lấp hoặc cắt xén.
- **Component-based Architecture**: Tách biệt UI và Logic thành các component độc lập, có đầu vào (inputs/props) và đầu ra (outputs/callbacks/events) rõ ràng.
- **Theo dõi vòng đời**: Tích hợp cơ chế logging cho các sự kiện layout để dễ dàng debug.

## 2. Kiến Trúc Lõi: Component "ResponsiveGridBase"

Hệ thống sẽ được xây dựng xoay quanh một class gốc (base class) có tên `ResponsiveGridBase` kế thừa từ một khung cuộn (Scrollable Frame). Tất cả các Panel hoặc Tab mới sẽ kế thừa từ component này.

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

Thay vì thiết kế giao diện liền khối (monolithic UI) như `HuntTab` cũ, mọi thành phần UX/UI mới sẽ được mô-đun hóa:

### 3.1. Cấu trúc một Component tiêu chuẩn
Mỗi giao diện (VD: `TargetStatusPanel`) sẽ được viết lại thành một Class với đặc tả sau:
- **Inputs (Đầu vào)**: Nhận thông qua constructor (ví dụ: `initial_data`) và các phương thức `update_state(data: dict)`.
- **Outputs (Đầu ra)**: Truyền các hàm callback thông qua constructor (ví dụ: `on_action_click=self.handle_action`) để Component không cần biết đến Logic hoặc Database.
- **Tách biệt Logic**: Component chỉ chịu trách nhiệm render UI dựa trên Inputs và phát ra sự kiện (Outputs). Logic xử lý (ví dụ: truy vấn DB, gọi API quét màn hình) phải nằm ở lớp Service/Controller.

### 3.2. Cấu trúc Thư mục Đề nghị
```text
ui/
  components/
    base/
      responsive_grid_base.py  # Chứa Base Class
    panels/
      ...                      # Các Component cụ thể kế thừa từ base
```

## 4. Nguyên Tắc Cập Nhật & Di Dời (Migration Strategy)
1. **Bước 1**: Tạo `ResponsiveGridBase` hoàn chỉnh với tính năng scroll và logging.
2. **Bước 2**: Đóng gói các panel nhỏ lẻ (như `ScreenStatePanel`, `SkillStatsPanel`) vào base mới.
3. **Bước 3**: Lắp ráp các panel này lại vào các Zone (như `shell_zone_b`) trong `app_gui.py` thông qua Grid.
4. **Bước 4**: Loại bỏ dần code giao diện liền khối cũ và chuyển giao toàn bộ qua cơ chế quản lý trạng thái luồng dữ liệu một chiều (One-way data flow: Controller -> Component -> Action).
