# Tích hợp Registry vào Icon Manager (Phase 3/4)

## Mục tiêu
Trích xuất danh sách metadata từ Registry và hợp nhất (merge) với dữ liệu lịch sử từ Database để hiển thị vào Combobox trong Form `Icon Manager`.

## Khối lượng công việc ước tính
< 30 phút

## Yêu cầu chi tiết

### 1. Cập nhật `IconManagerFrame._load_all_usage_ids()`
- Hàm này hiện đang gọi DB: `SELECT DISTINCT ui_element_id FROM icon_usages`.
- Hãy gọi thêm: `registry_items = UIElementRegistry.instance().get_all()`.
- Chuyển đổi các object `UIElementDescriptor` thành chuỗi hiển thị theo format: `f"{desc.module}/{desc.screen}/{desc.element_id}"`.
- Hợp nhất (Merge) 2 danh sách lại với nhau. Sử dụng `set` để loại bỏ các phần tử trùng lặp (ví dụ một ID đã lưu trong DB và đồng thời cũng đang có mặt trên UI qua Registry).

### 2. Điều chỉnh UX của Combobox
- Vì danh sách hiển thị giờ là `module/screen/element_id`, khi người dùng chọn một item và nhấn Save, đảm bảo rằng giá trị được lưu xuống CSDL **chỉ là phần `element_id`**.
- Tại hàm `_on_add_usage()` của `IconManagerFrame`, bắt buộc phải có logic parse (VD: `element_id = selected_string.split("/")[-1]`) để trích xuất ID gốc trước khi gọi hàm controller lưu xuống DB.

## Rủi ro tiềm ẩn (Cần tránh)
- **Database Format Mismatch (Lưu rác vào Database):** Nếu Combobox hiển thị `a/b/btn_save` mà lúc Save lại bê nguyên chuỗi đó xuống DB. Hệ thống EventBus lúc render sẽ đi tìm nút có tên `a/b/btn_save` thay vì `btn_save` dẫn đến chức năng map icon hỏng toàn tập. Việc split chuỗi lấy Element ID gốc là **bắt buộc**.
- **Race Condition / Duplicate Display:** Dữ liệu cũ trong DB đang là `btn_save`. Dữ liệu từ Registry đưa lên là `build_manager/settings/btn_save`. Hãy cẩn thận khi merge hai danh sách này để tránh Combobox hiển thị trùng lặp về mặt ý nghĩa (nếu cần, chỉ hiển thị format dài cho những ID đến từ Registry, ID rác không hợp lệ trong DB có thể bỏ qua hoặc chuẩn hóa).
