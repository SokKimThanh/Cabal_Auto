# Đặc Tả Kỹ Thuật: Hệ Thống Quản Lý Icon (Icon Management System)

## 1. Tổng Quan & Mục Tiêu
Hệ thống Quản lý Icon được thiết kế để cung cấp cho người dùng (đặc biệt là Designer và Admin) một giao diện trực quan nhằm thực hiện các thao tác CRUD (Thêm, Sửa, Xóa, Xem) đối với các hình ảnh biểu tượng trong ứng dụng.

**Mục tiêu chính:**
- Loại bỏ việc thao tác thủ công với file hệ thống (copy/paste file hình).
- Đảm bảo tính đồng bộ tuyệt đối giữa cấu hình hệ thống (JSON), Cơ sở dữ liệu (SQLite) và các file vật lý thực tế.
- Cung cấp cơ chế an toàn (Fallback Priority) để tránh lỗi văng ứng dụng khi mất file hình.
- Tích hợp chuẩn xác với hệ thống đa ngôn ngữ (i18n) thông qua Translation Tooltip.

---

## 2. Thiết Kế Cơ Sở Dữ Liệu (Database Schema)
Hệ thống sẽ lưu trữ toàn bộ dữ liệu cấu hình Icon làm "Single Source of Truth" (Nguồn chân lý duy nhất).

**Bảng `icons`:**

| Cột | Kiểu dữ liệu | Ràng buộc | Mô tả |
| :--- | :--- | :--- | :--- |
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Khóa chính |
| `icon_key` | TEXT | UNIQUE, NOT NULL | Mã định danh duy nhất (VD: `icon_sword`, `btn_save`). Dùng để liên kết trong code. |
| `name` | TEXT | NOT NULL | Tên hiển thị gợi nhớ (VD: "Kiếm Sắt", "Nút Lưu"). |
| `filepath` | TEXT | | Tên file hình ảnh (VD: `sword.png`). Hệ thống ngầm định lưu trong `assets/images/icon/`. |
| `fallback_emoji` | TEXT | | Ký tự Emoji/Unicode dự phòng khi không có ảnh (VD: ⚔️, 🛡️). |
| `tooltip_translation_key` | TEXT | | Key đa ngôn ngữ dùng hiển thị tooltip khi người dùng hover chuột (VD: `tooltip_save_icon`). |
| `category` | TEXT | | Phân loại icon để filter (VD: `skill`, `monster`, `ui`, `item`). |
| `description` | TEXT | | Mô tả chi tiết (Tùy chọn). |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Thời gian tạo. |

**Bảng `icon_usages` (Theo dõi vị trí sử dụng):**

Bảng này lưu trữ mối liên hệ giữa các icon và vị trí sử dụng của chúng trên toàn bộ ứng dụng. Điều này cho phép hệ thống theo dõi chính xác những thành phần UI nào (như button, label, shell zone...) đang sử dụng icon nào để thực hiện cập nhật theo thời gian thực khi có thay đổi (ví dụ: chuyển từ emoji sang ảnh thực tế).

| Cột | Kiểu dữ liệu | Ràng buộc | Mô tả |
| :--- | :--- | :--- | :--- |
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Khóa chính |
| `icon_key` | TEXT | FOREIGN KEY, NOT NULL | Liên kết tới `icons.icon_key`. Xác định icon đang được sử dụng. |
| `module_name` | TEXT | NOT NULL | Tên module, frame hoặc màn hình chứa icon (VD: `WorkspacePanel`, `SkillManagerFrame`, `Dialog_MonsterEdit`). |
| `ui_component_type` | TEXT | NOT NULL | Loại thành phần giao diện (VD: `button`, `label`, `shell_zone`, `treeview_column`). |
| `ui_element_id` | TEXT | NOT NULL | Tên biến hoặc định danh duy nhất của thành phần UI trong code (VD: `btn_save`, `lbl_monster_icon`). |
| `description` | TEXT | | Mô tả chi tiết về vị trí và mục đích sử dụng (Tùy chọn). |

---

## 3. Cơ Chế Hiển Thị & Thứ Tự Ưu Tiên (Fallback Priority)
Hệ thống xử lý hình ảnh (kế thừa logic của `IconHelper`) sẽ tuân thủ nghiêm ngặt 3 cấp độ ưu tiên khi render Icon lên giao diện. Cơ chế này đảm bảo UI luôn ổn định.

- **Ưu tiên 1 (Highest) - Định dạng `.png`:** Hệ thống kiểm tra trong thư mục `assets/images/icon/` xem có tồn tại file `filepath` với đuôi `.png` hay không. Nếu có, dùng file này (hỗ trợ nền trong suốt tốt nhất).
- **Ưu tiên 2 (Secondary) - Định dạng `.ico`:** Nếu file `.png` không tồn tại, hệ thống tự động tìm kiếm file trùng tên nhưng có đuôi `.ico`. Nếu tìm thấy, render file `.ico`.
- **Ưu tiên 3 (Fallback cuối cùng) - Ký tự Emoji/Unicode:** Nếu cả `.png` và `.ico` đều không tồn tại (hoặc trường `filepath` bị bỏ trống có chủ đích), ứng dụng sẽ tự động chuyển sang sử dụng `fallback_emoji` làm biểu tượng thay thế. Điều này ngăn chặn tình trạng crash ứng dụng hoặc hiển thị các ô vuông lỗi.

---

## 4. Quản Lý Trạng Thái Icon Trực Quan (UI Status Indicators)
Trên giao diện quản lý, để giúp người dùng nhận biết ngay tình trạng của từng Icon, hệ thống sẽ sử dụng các mã màu cảnh báo trực quan:

*   🟢 **Trạng Thái Xanh (Hoạt động tốt):** Icon có khai báo `icon_key`, có `filepath`, và file vật lý (`.png` hoặc `.ico`) **tồn tại** thực sự trong thư mục `assets/images/icon/`.
*   🟡 **Trạng Thái Vàng (Chủ đích dùng Fallback):** Hệ thống có `icon_key`, tuy nhiên trường `filepath` đang trống, và hệ thống đang hiển thị bằng `fallback_emoji`. Đây là trạng thái an toàn có chủ đích (ví dụ: các icon tạm thời chưa có thiết kế).
*   🔴 **Trạng Thái Đỏ (Lỗi thất lạc file):** Dữ liệu có khai báo tên file trong trường `filepath`, nhưng hệ thống kiểm tra và **không tìm thấy** file vật lý này (có thể đã bị xóa nhầm). Hệ thống phải ép dùng `fallback_emoji` để chống cháy.
*   ⚪ **Trạng Thái Xám (Chưa đồng bộ JSON):** Dữ liệu có trong DB nhưng kiểm tra mã băm/trạng thái thấy chưa được ghi đè xuất ra file cấu hình JSON.

---

## 5. Cơ Chế Đồng Bộ Hệ Thống (Data Sync & File Management)

Để đảm bảo DB, File JSON và File Vật lý luôn khớp nhau:

1.  **Lúc khởi động (Startup Auto-Sync):**
    *   Hệ thống đọc danh sách cấu hình Icon (từ file `icons.json` hoặc dictionary config gốc).
    *   Sử dụng lệnh `INSERT ... ON CONFLICT DO NOTHING` để chèn những cấu hình chưa có vào DB. Đảm bảo những khai báo mới từ tầng Code được đưa vào DB an toàn.
2.  **Quản lý File tự động khi Thêm mới (Create/Import):**
    *   Người dùng bấm **"Thêm mới từ máy"**, mở hộp thoại File Dialog.
    *   Sau khi chọn ảnh (đuôi `.png`, `.ico`), hệ thống tự động **sao chép (copy)** file đó vào `assets/images/icon/`.
    *   Không yêu cầu người dùng phải tự mở thư mục và copy tay.
3.  **Xuất dữ liệu lúc Lưu (CRUD Sync):**
    *   Mỗi khi người dùng Thêm/Sửa/Xóa Icon trên UI (thực hiện gọi lệnh cập nhật Database), hệ thống lập tức gọi trigger (ví dụ `IconService.export_to_json()`) để xuất dữ liệu mới nhất đè lên file JSON. Đảm bảo Database luôn là Source of Truth.
4.  **Tự động cập nhật giao diện (Real-time UI Refresh):**
    *   Khi thông tin hoặc trạng thái của một Icon thay đổi (ví dụ: người dùng mới thêm một file ảnh design thay thế cho Emoji trước đó), hệ thống cần cập nhật giao diện ngay lập tức mà không yêu cầu khởi động lại ứng dụng.
    *   Sử dụng cơ chế Publish-Subscribe (Event Bus/Observer Pattern): Sau khi lưu Icon thành công, `IconService` phát ra một sự kiện (ví dụ: `IconUpdatedEvent(icon_key)`).
    *   Căn cứ vào bảng `icon_usages`, hệ thống xác định các module/thành phần giao diện đang active (có sử dụng `icon_key` này).
    *   Các Controller hoặc Frame tương ứng bắt sự kiện và gọi hàm refresh (VD: cấu hình lại thuộc tính `image` của widget bằng `IconHelper` mới) cho các `ui_element_id` đó, giúp chuyển đổi mượt mà từ Fallback Emoji sang ảnh vật lý mới tại mọi vị trí đang sử dụng trên app.

---

## 6. Thiết Kế Giao Diện (UI - IconManagerFrame)

Màn hình `IconManagerFrame` được thiết kế kế thừa Layout của màn hình `MonsterManagerFrame` để đảm bảo tính nhất quán (Consistent UX), được nhúng thẳng vào Workspace Panel.

**6.1. Bố cục chính:**
*   **Sidebar trái (Master List):**
    *   Danh sách dạng Treeview các Icon.
    *   Cột hiển thị: ID, Icon Key, Phân loại (Category), Trạng Thái (Status - Mã màu).
    *   Thanh tìm kiếm (Search Box) phía trên hỗ trợ **auto-filter** với 500ms debounce (Không dùng nút lọc thủ công).
*   **Khu vực phải (Detail & Preview Zone):**
    *   Hiển thị chi tiết thông tin của Icon được chọn.
    *   Có form để sửa các trường: Tên, Phân loại, Mô tả, Translation Tooltip Key.
    *   **Khung Preview Khổng Lồ:** Hiển thị hình ảnh thực tế của icon. Tại đây, khi người dùng rê chuột (hover) vào hình ảnh, hệ thống sẽ gọi hệ thống đa ngôn ngữ để render chữ từ `tooltip_translation_key`, giúp người quản trị dễ dàng test xem chuỗi dịch có hoạt động đúng không.
*   **Khu vực Action (Bottom Bar):**
    *   Chứa các nút hành động đồng nhất: `btn_add`, `btn_edit`, `btn_delete`, `btn_refresh`.

**6.2. Tích hợp Sidebar:**
*   Thêm một menu item trong App Sidebar: `SidebarWidgetDef(..., key="btn_icon_manager", view_target="IconManagerFrame", icon="icon_image.png")`.