# Kiến Trúc UI Element & Cải Tiến Icon Manager

## Bối Cảnh (Context)
Hiện tại, `Icon Manager` đã giải quyết bài toán ánh xạ (map) một Icon vào các `ui_element_id` thông qua bảng `icon_usages`. Tuy nhiên, các hạn chế đang gặp phải:
1. Giao diện UX của `Icon Manager` còn hơi rườm rà (Thêm/Sửa/Làm mới chưa nằm ngoài dễ thao tác).
2. Việc ánh xạ icon đang dựa vào `icon_usages` nhưng thiếu bảng `ui_elements` làm nguồn dữ liệu (Source of Truth) gốc.
3. Không có cờ (flag) phân định tính Độc quyền (Exclusive) của các phần tử (như `sidebar_button`) so với các phần tử Đại trà (như `common_button`).
4. Việc gắn icon cho nút Phổ thông đang thiếu luồng thao tác trực quan hơn.

## Mục Tiêu (Goals)
- Tạo bảng `ui_elements` lưu trữ thông tin (module, screen, element_id, tính độc quyền).
- Tách biệt UI Element Độc quyền vs Đại trà (Exclusive vs Common).
- Cải thiện Layout của Icon Manager: Di chuyển nút Làm mới / Đồng bộ ra thanh công cụ (Toolbar) phía trên hoặc khu vực độc lập dễ truy cập.
- Cải thiện luồng chọn Icon: Hỗ trợ một Popup/Dialog nhỏ gọn để user có thể click vào bất kỳ "nút phổ thông" nào trên UI và gọi dialog gắn Icon nhanh (Fast-mapping).

## Thiết Kế Cơ Sở Dữ Liệu (Database Schema)

### Bảng Mới: `ui_elements`
Bảng này sẽ là **Source of Truth** cho UI Element Registry.

| Column Name | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | INTEGER | PRIMARY KEY | ID định danh |
| `element_id` | TEXT | NOT NULL | Mã ID của component (vd: `btn_save`) |
| `module_name` | TEXT | NOT NULL | Tên module (vd: `App`) |
| `screen_name` | TEXT | NOT NULL | Tên màn hình (vd: `setup_tab`) |
| `component_type` | TEXT | NOT NULL | Loại component (vd: `button`, `sidebar_button`) |
| `is_exclusive` | BOOLEAN | DEFAULT 0 | 1 = Độc quyền (chỉ 1 icon được dùng cho 1 element, không chia sẻ), 0 = Đại trà |
| `description` | TEXT | | Mô tả chức năng của UI |

*Composite Unique Key:* `(module_name, screen_name, element_id)` để chống trùng lặp.

### Sửa đổi Bảng `icon_usages` (Tuỳ chọn)
Hiện tại `icon_usages` lưu cứng `module_name`, `ui_component_type`, `ui_element_id`. Sau khi có bảng `ui_elements`, ta có thể:
1. Tiếp tục giữ schema hiện tại cho tương thích ngược (Backward Compatibility), chỉ map logic trong Python.
2. Hoặc tạo khoá ngoại `ui_element_id_ref` trỏ tới bảng `ui_elements.id`. (Khuyến nghị dùng cách 1 để giảm rủi ro gián đoạn).

## Thiết Kế Giao Diện (UI Layout)

1. **Top Action Bar (Khu vực dùng chung):**
   - Chuyển `Làm mới (Refresh)` và `Đồng bộ (Sync)` lên một thanh công cụ nằm ở góc trên cùng của màn hình `Icon Manager` (trên cả lưới TreeView). Điều này giúp thao tác luôn truy cập được mà không cần quan tâm đang chọn tab nào.
2. **Ký Hiệu Độc Quyền (Exclusive Flags):**
   - Trên danh sách "Available Elements" (Thành phần cần gắn), thêm một cột (hoặc Icon) hiển thị trạng thái **Độc quyền** (vd: 🔒) hoặc **Đại trà** (vd: 🌐) dựa trên dữ liệu từ DB.
3. **Luồng Gắn Nút Phổ Thông (Common Fast-Map):**
   - Thiết kế một Dialog mới: `IconSelectorDialog`.
   - Bất cứ khi nào user đang ở chế độ "Chỉnh sửa giao diện" (nếu có), click chuột phải vào một nút (vd: `btn_save`), hệ thống mở `IconSelectorDialog`. User chỉ cần chọn Icon từ Library -> Bấm OK -> Hệ thống tự động insert vào `icon_usages` và reload.

## Kế Hoạch Thực Thi (Implementation Plan)

### Phase 1: Database Migration
1. Viết script tạo bảng `ui_elements`.
2. Tạo script migration quét (scan) tất cả `UIElementDescriptor` đang có trong `UIElementRegistry` để chèn vào bảng `ui_elements` (Định nghĩa sẵn `sidebar_button` là `is_exclusive = 1`).

### Phase 2: Cải tiến Icon Manager Layout
1. Tách `btn_refresh` và `btn_sync` ra khỏi `tab_details`. Đưa lên phần `content_frame` gốc ở góc trên cùng.
2. Hiển thị cột `Type (Exclusive)` trong bảng `available_elements_tree`.

### Phase 3: Fast-Mapping Dialog
1. Xây dựng lớp `IconPickerWindow` (Dialog hiển thị danh sách icons dạng lưới nhỏ).
2. Viết helper để gắn context menu (Chuột phải -> "Đổi Icon") cho các UI component cho phép thay đổi đại trà.
3. Liên kết Dialog với `IconManagerController` để thực thi lệnh lưu và cập nhật UI ngay lập tức.
