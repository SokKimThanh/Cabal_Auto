# Đặc Tả Kỹ Thuật: Hệ Thống Quản Lý UI Components (UI Component Management System)

## 1. Tổng Quan & Mục Tiêu

Hệ thống Quản lý UI Components (Button, Toggle Button, Combobox, Label) được thiết kế nhằm chuẩn hóa, quản lý tập trung và đồng bộ hóa toàn bộ các thành phần giao diện tương tác trong ứng dụng. Hệ thống này giải quyết triệt để vấn đề chuyển đổi ngôn ngữ (i18n), thay đổi trạng thái icon (Icon Management System) và áp dụng giao diện nhất quán (UI Style V2) mà không gây giật lag hay phá vỡ layout.

**Mục tiêu chính:**
- **Quản lý tập trung:** Đưa toàn bộ cấu hình của các UI Component (nút bấm, nhãn, combobox) vào cơ sở dữ liệu (SQLite), có giao diện quản lý UI (CRUD) dành cho Admin/Developer.
- **Tích hợp sâu i18n & Icon:** Đảm bảo khi người dùng chuyển ngôn ngữ hoặc cập nhật icon, toàn bộ component liên quan tự động cập nhật mượt mà.
- **Quản lý Tooltip đồng bộ:** Quản lý nội dung tooltip qua i18n, áp dụng UI Style V2 cho tooltip (không dùng tooltip mặc định của HĐH).
- **Kiểm soát vị trí chính xác:** Định vị rõ ràng mỗi component nằm ở không gian nào trong ứng dụng (Grid Zone: A, B, C1...).
- **Phân loại đa dạng:** Quản lý được nhiều loại component (nút chỉ có chữ, nút chỉ có icon, nút có cả hai, toggle button, combobox...).

---

## 2. Kiến Trúc Không Gian & Vị Trí (Zoning & Grid System)

Ứng dụng được chia thành các phân khu (Zone) chính trong `app_gui.py`:
- **Zone A (`shell_zone_a`):** Action Bar / Thanh công cụ trên cùng (Chứa nút Global Apply, Start/Stop, Language Toggle).
- **Zone B (`shell_zone_b`):** Vùng làm việc chính / Workspaces (Chứa các View như Hunt, Setup, Managers...).
- **Zone C1 (`shell_zone_c1`):** Sidebar / Thanh điều hướng bên trái (Chứa các nút chuyển View).

Mỗi component trong DB sẽ được map với một thuộc tính `zone_id` và `parent_frame` để hệ thống biết chính xác nó được "gắn vô đâu".

---

## 3. Thiết Kế Cơ Sở Dữ Liệu (Database Schema)

Hệ thống sử dụng SQLite làm "Single Source of Truth".

**Bảng `ui_components`:**

| Cột | Kiểu Dữ Liệu | Ràng Buộc | Mô Tả |
| :--- | :--- | :--- | :--- |
| `component_id` | TEXT | PRIMARY KEY | Định danh duy nhất của component (VD: `btn_lang_toggle`, `btn_global_apply`). |
| `component_type` | TEXT | NOT NULL | Loại thành phần (VD: `button`, `toggle_button`, `combobox`, `label`, `icon_button`). |
| `zone_id` | TEXT | NOT NULL | Vị trí Zone gốc (VD: `zone_a`, `zone_b`, `zone_c1`). |
| `parent_frame` | TEXT | NOT NULL | Tên Frame hoặc Container chứa (VD: `col2_frame`, `sidebar`). |
| `i18n_text_key` | TEXT | | Key đa ngôn ngữ cho văn bản hiển thị trên nút (VD: `language`). Rỗng nếu chỉ có Icon. |
| `icon_key` | TEXT | | Mã định danh icon từ Icon Management System (VD: `icon_language`). Rỗng nếu chỉ có Text. |
| `style_role` | TEXT | NOT NULL | Semantic Role theo UI Style V2 (VD: `primary`, `danger`, `info`, `neutral`, `icon`). |
| `tooltip_i18n_key` | TEXT | | Key đa ngôn ngữ cho Tooltip. |
| `tooltip_style` | TEXT | DEFAULT 'default' | Loại style cho tooltip (VD: `default`, `danger`, `info`) sử dụng font/color từ UI Style V2. |
| `is_active` | INTEGER | DEFAULT 1 | Cờ kích hoạt (1: Hiển thị, 0: Ẩn). |
| `metadata` | TEXT | | JSON lưu cấu hình phụ (VD: danh sách giá trị cho Combobox, padding `{"padx": 20, "pady": 6}`). |

---

## 4. Giao Diện Quản Lý (UI Component Manager)

Giao diện quản lý (tương tự như Icon Manager) sẽ được thêm vào `Zone B` dưới dạng một View mới (VD: `ui_component_manager`).

**Tính năng chính:**
1. **Treeview/Danh sách:** Nhóm các component theo `zone_id` và `component_type`.
2. **Form Chi Tiết (CRUD):**
   - Cho phép chọn/đổi `icon_key` (liên kết với Icon Manager).
   - Chọn/đổi `i18n_text_key` và `tooltip_i18n_key`.
   - Chỉnh sửa `style_role` (Dropdown: primary, danger, info...).
   - Xác định vị trí (`zone_id`, `parent_frame`).
3. **Live Preview:** Một ô nhỏ hiển thị component thực tế dựa trên cấu hình đang chỉnh sửa.

---

## 5. Đặc Tả Chi Tiết Các Loại Nút & Đồng Bộ

### 5.1. Phân Loại Nút
Hệ thống sẽ render component dựa trên cột `component_type` kết hợp với dữ liệu cấu hình:
- **Button (Chữ):** Có `i18n_text_key`, không có `icon_key`.
- **Icon Button (Chỉ Icon):** Có `icon_key`, không có `i18n_text_key`. (Style role thường là `icon`).
- **Button (Icon + Chữ):** Có cả `icon_key` và `i18n_text_key`.
- **Toggle Button:** Tương tự nút thường nhưng có hai trạng thái nội tại (metadata quy định 2 icon/text key chuyển đổi qua lại, VD: `start` <-> `stop`, `en` <-> `vi`).
- **Combobox:** Cần cấu hình mảng dữ liệu trong `metadata` (VD: `["en", "vi"]`).

### 5.2. Đồng Bộ i18n & Trải Nghiệm Mượt Mà
- Ứng dụng sử dụng cơ chế **Event Bus / Observer** (tương tự `on_bot_state_changed` hoặc thông qua `TranslationBinder`).
- Khi người dùng nhấn nút chuyển ngôn ngữ, hệ thống không hủy (destroy) và tạo lại (recreate) các widget để tránh giật hình (flickering). Thay vào đó, nó lặp qua danh sách các component đã đăng ký trong `TranslationBinder` hoặc đọc từ DB và gọi `config(text=new_text, image=new_image)`.

### 5.3. Quản Lý Tooltip
- Tooltip không sử dụng mặc định của HĐH mà được custom qua một component riêng (VD: kế thừa `ui/helpers/tooltip.py`).
- Tooltip phải tuân thủ UI Style V2: viền `THEME_BORDER_DEFAULT`, nền `THEME_BG_PANEL`, chữ `THEME_TEXT_PRIMARY`, font `FONT_BODY`.
- Nội dung được tự động dịch qua `tooltip_i18n_key` khi chuyển ngữ.

### 5.4. Áp Dụng UI Style V2
- Tất cả các nút được render phải sử dụng thư viện ttk/Tkinter đã gắn theme token từ `UIStyleV2`.
- Tham chiếu theo cột `style_role` liên kết với `ROLE_STYLES` trong `button_styles.py` (Primary.TButton, Danger.TButton...).

---

## 6. Các Lưu Ý Cốt Lõi (Pitfalls & Notes)

- **Garbage Collection (GC) của Image:** Khi cập nhật icon động, phải luôn giữ tham chiếu mạnh (`widget.image = new_photoimage`) để tránh ảnh bị mất, hiển thị vùng trắng.
- **Cấu hình Nút Ngôn Ngữ Cụ Thể (Language Toggle):** Đối với nút chuyển ngữ, đây là một dạng Toggle Button đặc biệt. Nó sẽ nằm ở `Zone A` -> `col2_frame`. Cần đảm bảo hàm callback của nút cập nhật state vào cấu hình `hunt_cfg` và phát ra sự kiện chuyển ngữ toàn cục. Nút có thể vừa có icon (Icon trái đất) vừa hiện text (EN/VI).
- **Tránh Xung Đột Database:** Khi load lúc khởi động, phải cache dữ liệu UI Component vào bộ nhớ (Dict) để vẽ giao diện, không query DB liên tục trong quá trình render.
- **Gắn Event Tooltip đúng cách:** Ràng buộc (bind) các sự kiện `<Enter>`, `<Leave>`, `<Button>` phải được dọn dẹp cẩn thận khi cập nhật trạng thái nút (VD: Disabled state) để tooltip không bị kẹt trên màn hình.