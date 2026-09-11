# Prompt 07: UI - Detail Form, Preview Zone & Action Buttons

## Mục tiêu
Hoàn thiện khu vực Detail (Bên phải) và Action Bar (Bên dưới) của `IconManagerFrame`. Tạo một form để hiển thị/chỉnh sửa thông tin Icon, một khu vực preview khổng lồ để xem trước ảnh (kèm test tooltip), và gắn các nút bấm thao tác chuẩn của hệ thống.

## Ngữ cảnh & Yêu cầu từ Đặc tả
- **Khung Preview Khổng Lồ:** Nửa trên khu vực detail. Phải hiển thị được ảnh (hoặc emoji to). Hover vào ảnh hiện tooltip theo mã `tooltip_translation_key` để test đa ngôn ngữ.
- **Form Thông Tin:** Nửa dưới khu vực detail. Các trường: ID (read-only), Tên, Icon Key, Phân Loại, Fallback Emoji, Filepath (kèm nút "Chọn file từ máy").
- **Bottom Bar Buttons:** Các nút: Thêm, Sửa, Xóa, Làm mới, Đồng bộ. (Sử dụng key i18n chuẩn như `btn_add`, `btn_edit`, `btn_delete`, v.v.).

## Các bước triển khai chi tiết dành cho Người/AI

### Bước 1: Xây dựng khu vực Preview Khổng Lồ
- **Vị trí:** Vùng nửa trên của `self.right_detail_frame`.
- **Hành động:**
  - Tạo `tk.Label` (hoặc `Canvas`) có kích thước lớn (VD: 128x128 hoặc 256x256). Đặt tên `self.lbl_preview`.
  - Thiết kế hàm `self._render_preview(icon_data)`: Gọi `IconHelper` lấy ảnh, resize (bằng PIL nếu cần), rồi gán vào `self.lbl_preview.image`.
  - Gắn Tooltip (nếu thư viện custom tooltip của project có sẵn) hoặc bind event `<Enter>` và `<Leave>` để hiển thị một label nổi nhỏ chứa kết quả dịch của trường `tooltip_translation_key`.

### Bước 2: Xây dựng Form Nhập Liệu (Detail Form)
- **Vị trí:** Vùng nửa dưới của `self.right_detail_frame`.
- **Hành động:** Tạo các Grid Label và Entry/Combobox tương ứng với cấu trúc Database:
  - `Icon Key` (tk.Entry) - Bắt buộc.
  - `Name` (tk.Entry) - Bắt buộc.
  - `Category` (ttk.Combobox) - Chứa list danh mục hiện tại.
  - `Fallback Emoji` (tk.Entry) - Text Unicode.
  - `Tooltip Key` (tk.Entry) - Text key cho i18n.
  - `Filepath`: Tạo một frame con gồm 1 `tk.Entry` (chỉ đọc hoặc cho phép sửa cẩn thận) và 1 Nút `btn_browse` (Chọn file). (Chỉ dựng UI, logic duyệt file sẽ nối ở Prompt 8).

### Bước 3: Đổ dữ liệu từ Treeview vào Form
- **Hành động:**
  - Tại hàm xử lý event `<<TreeviewSelect>>` (đã bind ở Prompt 6):
  - Lấy `icon_key` đang chọn, truy vấn `IconService.get_icon_by_key()`.
  - Cập nhật dữ liệu vào các Entry (xóa trắng -> insert chữ mới).
  - Gọi `self._render_preview` với data mới để thay hình.
  - Vô hiệu hóa/Kích hoạt các Entry dựa trên state (ví dụ chỉ cho sửa khi bấm nút "Edit").

### Bước 4: Xây dựng Bottom Action Bar
- **Vị trí:** `self.bottom_action_frame`.
- **Hành động:**
  - Tạo các nút bấm: `Thêm Mới` (`btn_add`), `Chỉnh Sửa` (`btn_edit`), `Xóa` (`btn_delete`), `Lưu` (`btn_save`), `Hủy` (`btn_cancel`).
  - *Lưu ý:* Sử dụng translation key chuẩn (VD: `self.btn_add = ttk.Button(..., text=get_text('btn_add'))`).
  - *Lưu ý:* Dùng `UIStyle.get_button_style('primary')` hoặc `danger` tương ứng (theo memory quy định về UIStyleV2).
  - Thiết lập trạng thái ban đầu: Nút Save/Cancel bị disable/ẩn. Bấm Add/Edit thì bật Save/Cancel, disable Add/Edit. (Quản lý State Form: Xem/Sửa/Thêm).

## Tiêu chí hoàn thành (Definition of Done)
- [ ] Khu vực Preview hiển thị được ảnh khổng lồ. Tooltip test hoạt động.
- [ ] Các trường thông tin hiển thị đúng dữ liệu khi click vào 1 icon bên Treeview.
- [ ] Khu vực Bottom Bar có đầy đủ các nút bấm với style chuẩn (primary, danger, v.v.).

## Thời gian dự kiến: ~30 phút
