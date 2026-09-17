# Prompt 05: Tách IconTreeComponent và Hoàn thiện Controller

**Thời gian dự kiến:** < 30 phút

## Mục tiêu
Bóc tách phần phức tạp nhất là "Cây danh sách Icon" (Treeview) cùng thuật toán nạp dữ liệu (Incremental Queue) thành một component độc lập, hoàn tất quá trình giải cứu "God Class".

## Yêu cầu thực hiện
1. **Tạo file mới:** Tạo file `ui/components/icon_tree_component.py`.
2. **Khai báo Class:** Tạo class `IconTreeComponent(tk.Frame)`.
3. **Di chuyển giao diện:** Chuyển phần tạo `ttk.Treeview`, thanh công cụ thu/phóng (Collapse/Expand All), và thanh Filter (Search, Status, Category) vào component này.
4. **Di chuyển Thuật toán Render:** Chuyển thuật toán rắc rối `_process_incremental_queue`, `load_tree_data` (phần build queue) vào component này.
5. **Thiết lập Giao tiếp:**
   - Component này cần một biến chứa instance của `IconTreeModel` để gọi dữ liệu.
   - Khi có sự kiện chọn node (`<<TreeviewSelect>>`), nó sẽ phát callback `on_node_selected(icon_key)`.
   - Khi có sự kiện thay đổi bộ lọc, nó báo cho Model và tự reload cây.
6. **Cập nhật IconManagerFrame:** Tại bước này, `IconManagerFrame` chỉ còn là cái vỏ (Mediator).
   - Nó sẽ khởi tạo `IconTreeComponent`, `IconFormComponent`, `ImageLibraryComponent`, v.v.
   - Nó sẽ nối dây (wiring): Lắng nghe `on_node_selected` từ Tree -> truyền dữ liệu xuống Form và Preview.
   - Khi Form báo Lưu thành công -> Gọi Tree tải lại dữ liệu.

## Điều kiện hoàn thành (DoD)
- Treeview hiển thị dữ liệu chính xác theo phân cấp Danh mục -> Icon.
- Hàng đợi render theo từng đợt (batch rendering) không bị vỡ, giao diện không giật lag.
- `IconManagerFrame` được tối giản xuống mức thấp nhất (< 300 dòng), thuần tuý làm nhiệm vụ liên kết các component với nhau.
