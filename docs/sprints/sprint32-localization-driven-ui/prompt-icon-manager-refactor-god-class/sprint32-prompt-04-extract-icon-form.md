# Prompt 04: Tách IconFormComponent và Quản lý State

**Thời gian dự kiến:** < 30 phút

## Mục tiêu
Tách khu vực Form nhập liệu chi tiết (Tên, Icon Key, Tooltip, Danh mục) và cơ chế quản lý trạng thái tĩnh (View/Add/Edit) ra khỏi `IconManagerFrame`.

## Yêu cầu thực hiện
1. **Tạo file mới:** Tạo file `ui/components/icon_form_component.py`.
2. **Khai báo Class:** Tạo class `IconFormComponent(tk.Frame)`.
3. **Di chuyển giao diện:** Chuyển `_build_detail_form` vào class này.
4. **Quản lý dữ liệu:** Giữ nguyên các `tk.StringVar` (như `var_name`, `var_icon_key`, ...) ở trong Form này. Form sẽ cung cấp hàm `get_form_data() -> dict` để trả về cục dữ liệu thô, và hàm `set_form_data(dict)` để fill dữ liệu.
5. **Di chuyển Logic Autocomplete Tooltip:** Di chuyển `_load_i18n_keys`, `_validate_tooltip_key`, `_autocomplete_tooltip` đi kèm form.
6. **Chuyển đổi hàm `set_form_state`:** Thay vì một hàm `set_form_state` khổng lồ, chia nó thành các phương thức trong `IconFormComponent`: `enter_view_mode()`, `enter_add_mode()`, `enter_edit_mode()`.
7. **Cập nhật IconManagerFrame:** Thay vì chỉnh sửa trực tiếp từng entry, `IconManagerFrame` sẽ gọi các hàm điều khiển State của `IconFormComponent`. (Lưu ý: Các nút Add/Edit/Save có thể được nhóm lại trong một `ActionToolBarComponent` ở prompt sau, hiện tại để `IconManagerFrame` gọi hàm của Form để tắt mở form).

## Điều kiện hoàn thành (DoD)
- Form nhập liệu hoạt động trơn tru (enable/disable đúng lúc).
- Cơ chế gợi ý và kiểm tra (validate) tooltip_key chạy bình thường.
- `IconManagerFrame` hoàn toàn không còn biết về giao diện chi tiết của Form.
