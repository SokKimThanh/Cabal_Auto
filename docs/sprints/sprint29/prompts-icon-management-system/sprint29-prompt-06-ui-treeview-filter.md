# Prompt 06: UI - Master List (Treeview) & Tính năng Lọc (Filter/Search)

## Mục tiêu
Đổ dữ liệu giao diện cho khu vực Left Sidebar và Top Filter Bar của `IconManagerFrame`. Tạo một Treeview có khả năng gom nhóm theo Category (như tài liệu đã mô tả: không hiện list phẳng) và một thanh tìm kiếm tự động lọc với độ trễ (debounce) 500ms.

## Ngữ cảnh & Yêu cầu từ Đặc tả
- **Treeview (Left Sidebar):** Cấu trúc cây `Category -> Icons`. Cột hiển thị: ID, Icon Key, Status (Mã màu).
- **Search (Top Filter):** Tìm kiếm theo tên hoặc key với auto-filter (debounce 500ms, không cần nút Search thủ công). Dùng `ttk.Entry` thay vì `tk.Entry`.
- **Dropdown Filter (Top Filter):** Lọc theo Status (Xanh, Vàng, Đỏ) và Category.

## Các bước triển khai chi tiết dành cho Người/AI

### Bước 1: Xây dựng khu vực Top Filter
- **Vị trí:** Trong `IconManagerFrame`, tại `self.top_filter_frame`.
- **Hành động:**
  - Thêm một `ttk.Entry` (Search Box). Gán biến `self.search_var`.
  - Bind sự kiện `<KeyRelease>` cho `ttk.Entry` vào một hàm xử lý debounce (ví dụ gọi `self.after(500, self.apply_filters)`).
  - Thêm 2 `ttk.Combobox`: Một cho "Status Filter", một cho "Category Filter". Bind sự kiện `<<ComboboxSelected>>` gọi thẳng `self.apply_filters`.

### Bước 2: Thiết lập Tkinter Treeview
- **Vị trí:** Tại `self.left_master_frame`.
- **Hành động:**
  - Tạo `ttk.Treeview`. Khai báo các cột: `col_id`, `col_key`, `col_status`.
  - Thiết lập tiêu đề cột (Heading). (Chú ý dùng key i18n nếu có thể, tạm thời có thể hardcode text chuẩn bị cho i18n sau).
  - Gắn Scrollbar dọc (và ngang nếu cần) cho Treeview. Sử dụng `grid` cho cả Treeview và Scrollbar (như memory chỉ định: "dùng grid để implement auto-hiding scrollbar nếu cần, không dùng pack").
  - Bind sự kiện `<<TreeviewSelect>>` để chuẩn bị bắt hành động người dùng click vào Icon.

### Bước 3: Đổ dữ liệu vào Treeview (Group by Category)
- **Hành động:**
  - Viết hàm `self.load_tree_data()`. Hàm này gọi `IconService.get_all_icons()`.
  - Phân tích dữ liệu, nhóm các icon lại theo thuộc tính `category`.
  - Lặp qua dictionary đã nhóm:
    - Insert Node cha (Category Folder). VD: `tree.insert('', 'end', iid=f"cat_{cat_name}", text=f"📁 {cat_name}")`.
    - Lặp qua các icon trong category, insert Node con. VD: `tree.insert(f"cat_{cat_name}", 'end', iid=icon['icon_key'], text=icon['name'], values=(icon['id'], icon['icon_key'], status_color))`.

### Bước 4: Viết logic lọc dữ liệu (Apply Filters)
- **Hành động:**
  - Hàm `self.apply_filters()` lấy giá trị từ search box, status dropdown, category dropdown.
  - Xóa toàn bộ node hiện tại trên Treeview (`tree.delete(*tree.get_children())`).
  - Lọc dữ liệu thô (từ bộ nhớ tạm hoặc gọi lại Service với params) và chạy lại logic đổ dữ liệu ở Bước 3.

## Tiêu chí hoàn thành (Definition of Done)
- [ ] Treeview hiển thị đúng cấu trúc Cây (Cha: Category, Con: Các icon thuộc category đó).
- [ ] Gõ chữ vào Search Box, dừng tay 0.5s thì danh sách tự động lọc (chữ hoa/thường không phân biệt). Không cần bấm Enter.
- [ ] Cột Treeview hiển thị đủ thông tin ID, Key, Status.
- [ ] Bấm vào dropdown trạng thái thì danh sách cập nhật ngay.

## Thời gian dự kiến: ~25-30 phút
