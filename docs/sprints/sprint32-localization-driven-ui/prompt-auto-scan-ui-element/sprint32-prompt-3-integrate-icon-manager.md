# Prompt 3: Tích hợp Registry vào Icon Manager (Combobox Usages)

**Mục tiêu:**
Đưa danh sách các Element ID đang nằm trong Registry lên giao diện `IconManagerFrame` để người dùng có thể chọn. Task này mất khoảng 20-30 phút.

**Các bước thực hiện:**
1. Mở file `ui/views/icon_manager_frame.py`.
2. Tìm hàm `_load_all_usage_ids(self)`.
3. Hiện tại hàm này đang query DB: `SELECT DISTINCT ui_element_id FROM icon_usages...`
4. Cập nhật hàm:
   - Truy vấn DB để lấy danh sách (như cũ).
   - Lấy danh sách ID từ Runtime Registry: `UIElementRegistry.get_all()`.
   - Gộp (merge) hai danh sách này lại, loại bỏ các mục trùng lặp, `None` hoặc chuỗi rỗng.
   - Sắp xếp (sort) lại mảng gộp được và gán cho `self._available_usage_ids`.
   - Cập nhật combobox: `self.combo_usage_element['values'] = self._available_usage_ids`.
5. Kiểm tra tính năng Auto-complete (`_autocomplete_usage_element`): Chắc chắn rằng nó vẫn chạy đúng trên danh sách mới gộp này.
6. (Tùy chọn test nhanh): Tìm một màn hình bất kỳ trong app, thêm tham số `element_id="test_runtime_btn"` vào một `create_icon_button`. Chạy app, mở màn hình đó, sau đó mở Icon Manager xem Combobox đã hiện `test_runtime_btn` chưa.

**Ràng buộc (Memory):**
- Theo memory: *UI components must not directly execute file system operations or direct DB queries*. Tuy nhiên `IconManagerFrame` hiện đang chứa một số query trực tiếp. Bạn chỉ cần điều chỉnh phần merge In-memory List, không cần thiết phải refactor toàn bộ class này trừ khi thật sự cần thiết.
- Đảm bảo combobox auto-complete không bị set `validate="key"` làm hỏng gõ phím.
