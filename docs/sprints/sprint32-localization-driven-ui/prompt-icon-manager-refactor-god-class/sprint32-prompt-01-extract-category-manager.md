# Prompt 01: Tách CategoryManagerComponent từ IconManagerFrame

**Thời gian dự kiến:** < 30 phút

## Mục tiêu
Tách rời toàn bộ logic và giao diện liên quan đến "Quản lý Danh mục Icon" (Category) ra khỏi `IconManagerFrame` (God Class hiện tại) thành một UI component độc lập.

## Yêu cầu thực hiện
1. **Tạo file mới:** Tạo file `ui/components/category_manager_component.py`.
2. **Khai báo Class:** Tạo class `CategoryManagerComponent(tk.Frame)`.
3. **Di chuyển giao diện (View):** Chuyển hàm `_build_categories_panel` từ `icon_manager_frame.py` sang class mới (có thể đổi tên thành `_setup_ui`).
4. **Di chuyển trạng thái và sự kiện (Logic):** Di chuyển các hàm liên quan đến Category:
   - `_load_categories_tree`
   - `_set_cat_form_state`
   - `_on_cat_tree_select`
   - `_on_cat_add`
   - `_on_cat_save`
   - `_on_cat_cancel`
   - `_on_cat_delete`
   - `_on_cat_tree_interaction`
5. **Giao tiếp (Callback/EventBus):** Khi thêm/sửa/xoá Category thành công, component mới cần gọi một callback hoặc EventBus để báo cho `IconManagerFrame` (hoặc Controller) biết nhằm cập nhật lại danh sách Filter (combobox) bên phần Icon.
6. **Cập nhật IconManagerFrame:** Thay thế toàn bộ code cũ trong `_build_categories_panel` bằng việc khởi tạo và gắn `CategoryManagerComponent` vào giao diện. Đảm bảo xóa các code cũ đã chuyển đi.

## Điều kiện hoàn thành (DoD)
- Giao diện tab "Quản lý Danh mục" vẫn hoạt động bình thường (Thêm/Sửa/Xóa).
- `IconManagerFrame` giảm bớt được khoảng 200-300 dòng code liên quan.
- Không phát sinh lỗi `UnboundLocalError` hay mất liên kết tham chiếu.
