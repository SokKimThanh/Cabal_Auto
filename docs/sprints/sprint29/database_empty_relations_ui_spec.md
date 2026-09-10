# Đặc Tả Giao Diện Cho Các Mối Quan Hệ Database Chưa Có Dữ Liệu

Tài liệu này phân tích các bảng và mối quan hệ (foreign keys) hiện đang trống dữ liệu trong cơ sở dữ liệu `monsters.db` của dự án Auto Bot. Từ đó, đánh giá sự phù hợp của giao diện (UI) hiện tại và đề xuất thiết kế các giao diện mới/cập nhật để đáp ứng các luồng dữ liệu này.

## 1. Phân Tích Hiện Trạng Dữ Liệu

Qua kiểm tra cơ sở dữ liệu, các mối quan hệ (foreign keys) sau hiện không có dữ liệu (do bảng con trống hoặc cột khoá ngoại hoàn toàn chứa `NULL`):

1. **Nhóm Skills & Classes (Kỹ năng và Nghề nghiệp)**
   - `skills.class_id` -> `classes.class_id`
   - `builds.class_id` -> `classes.class_id`

2. **Nhóm Presets (Bộ cài đặt Kỹ năng)**
   - `skill_presets.class_id` -> `classes.class_id`
   - `preset_skills.skill_id` -> `skills.skill_id`
   - `preset_skills.preset_id` -> `skill_presets.preset_id`
   - `user_preset_state.active_preset_id` -> `skill_presets.preset_id`
   - `user_preset_state.class_id` -> `classes.class_id`

3. **Nhóm Scans (Lịch sử Quét/Tương tác)**
   - `scans.class_id` -> `classes.class_id`
   - `scans.skill_id` -> `skills.skill_id`
   - `scans.monster_id` -> `monsters.id`

---

## 2. Đánh Giá Giao Diện Hiện Tại và Hướng Khắc Phục

### 2.1 Nhóm Skills & Classes

**Giao diện hiện tại:**
- Đã có `SkillManagerFrame` (`ui/views/skill_manager_frame.py`) để quản lý kỹ năng.
- Đã có `SkillEditDialog` (`ui/dialogs/skill_edit_dialog.py`) để thêm/sửa kỹ năng.

**Đánh giá:**
- **Chưa phù hợp:** Việc `skills.class_id` không có dữ liệu phần lớn do chưa có giao diện nào quản lý danh sách `classes`. Người dùng có thể không chọn được Class chuẩn khi tạo/sửa Skill, dẫn đến mối quan hệ này bị bỏ trống hoặc không toàn vẹn.
- Bảng `builds` hoàn toàn chưa có giao diện để tương tác.

**Đề xuất thiết kế lại:**
- Sửa đổi `SkillEditDialog`: Trường chọn `Class ID` phải là một Dropdown (Combobox) được đổ dữ liệu động trực tiếp từ bảng `classes`, thay vì nhập tay (nhằm đảm bảo ràng buộc foreign key).

### 2.2 Nhóm Presets

**Giao diện hiện tại:**
- Đã có `PresetDialog` (`ui/dialogs/preset_dialog.py`).

**Đánh giá:**
- **Chưa phù hợp:** Giao diện này chỉ hỗ trợ hiển thị danh sách (Listbox), Chọn (Apply) và Xoá (Delete) các presets đã có. Do cơ sở dữ liệu đang trống, mở màn hình này lên sẽ không có tác dụng. Hệ thống hiện thiếu luồng UX để **Tạo (Create)** hoặc **Lưu (Save)** một preset từ các kỹ năng đang được người dùng cấu hình.

**Đề xuất thiết kế lại:**
- Thêm cơ chế lưu tại màn hình `SkillPanel` (`ui/panels/skill_panel.py`).

### 2.3 Nhóm Scans

**Giao diện hiện tại:**
- Không tìm thấy bất kỳ giao diện nào (Dialog, Panel, hay Frame) hỗ trợ hiển thị dữ liệu lịch sử Scans trong thư mục `ui/`.

**Đánh giá:**
- Cần xây dựng mới hoàn toàn.

---

## 3. Đặc Tả Các Giao Diện Cần Làm Mới

Dưới đây là danh sách chi tiết các màn hình (screens) cần phát triển thêm để lấp đầy các khoảng trống về dữ liệu và hoàn thiện chức năng hệ thống, được chia theo từng nhóm.

### 3.1 Giao diện Nhóm Classes & Builds
*Các màn hình quản lý thông tin cốt lõi của nhân vật (Classes) và cách xây dựng nhân vật (Builds).*

#### A. Màn hình Class Manager (Mới)
- **Vị trí:** Tích hợp vào `shell_zone_b` dưới dạng tab điều hướng từ Sidebar (tương tự `MonsterManagerFrame`).
- **Thành phần UI:**
  - Kế thừa từ kiến trúc `ResponsiveGridBase` (chuẩn zero-occlusion).
  - Thanh công cụ (Top Bar): Nút "Add New Class", Thanh tìm kiếm nhanh.
  - Vùng dữ liệu (Body): Một `Treeview` hiển thị danh sách Classes (ID, Name, Description).
  - Phân trang (Pagination) ở dưới cùng.
- **Dữ liệu tương tác:** Thêm, Sửa, Xoá bản ghi trong bảng `classes`.

#### B. Màn hình Build Manager (Mới)
- **Vị trí:** Tích hợp tương tự Class Manager.
- **Thành phần UI:**
  - Bảng Treeview hiển thị các Builds.
  - Phải có bộ lọc (Filter) dạng Dropdown để lọc các Build theo `Class`.
- **Dữ liệu tương tác:** Thêm/Sửa/Xoá trong bảng `builds`. Ràng buộc bắt buộc phải chọn một `Class` hợp lệ khi tạo Build.

### 3.2 Giao diện Nhóm Presets
*Quản lý việc lưu trữ và nạp các bộ kỹ năng ưa thích (Skill Presets).*

#### A. Nút "Save as Preset" trong Skill Panel (Cập nhật)
- **Vị trí:** Màn hình `ui/panels/skill_panel.py` (nơi người dùng kéo thả/chọn kỹ năng hiện tại).
- **Thành phần UI:**
  - Thêm một nút `[Save as Preset]` ở góc trên/dưới của Panel.
  - Nút này sẽ gọi ra `CreatePresetDialog`.

#### B. Màn hình Create Preset Dialog (Mới)
- **Vị trí:** Một `tk.Toplevel` mới nằm trong `ui/dialogs/create_preset_dialog.py`.
- **Thành phần UI:**
  - Input: Tên Preset (`Preset Name`).
  - Dropdown: Chọn Class (`class_id`) muốn gán preset này (mặc định lấy class đang chọn hiện tại).
  - List danh sách tóm tắt các skills đang được lưu.
  - Nút `[Save]`, `[Cancel]`.
- **Dữ liệu tương tác:**
  - Tạo 1 bản ghi vào bảng `skill_presets`.
  - Lưu danh sách skill hiện hành vào bảng `preset_skills`.

#### C. Cập nhật Preset Dialog Hiện Tại
- **Vị trí:** `ui/dialogs/preset_dialog.py`.
- **Thành phần UI:**
  - Bổ sung hiển thị chỉ báo "Đang sử dụng" (Active) cho preset nào đang được kích hoạt.
- **Dữ liệu tương tác:** Khi nhấn `Apply`, ngoài việc gọi logic load skill, cần cập nhật/ghi đè bản ghi vào bảng `user_preset_state` để hệ thống nhớ preset đang dùng cho class đó.

### 3.3 Giao diện Nhóm Scans
*Lưu trữ và hiển thị lịch sử tương tác/quét (log).*

#### A. Màn hình Scan History (Mới)
- **Vị trí:** Một view mới (`scan_history_frame.py`) kế thừa `ResponsiveGridBase` để hiển thị ở Workspace.
- **Thành phần UI:**
  - Bộ lọc nâng cao: Combobox chọn `Class`, Combobox chọn `Monster`, Date range picker (nếu có).
  - Vùng dữ liệu (Body): `Treeview` dạng lưới rộng liệt kê lịch sử Scans.
    - Cột: Scan ID, Thời gian, Tên Class, Tên Kỹ Năng (Skill), Tên Quái (Monster), Kết quả.
  - Do tính chất log thường dài, cần có Empty State (`ui.components.empty_state.EmptyState`) đẹp mắt khi chưa có dữ liệu scan nào.
- **Dữ liệu tương tác:**
  - Đọc (Read-only) dữ liệu từ bảng `scans` kết hợp JOIN với các bảng `classes`, `skills`, và `monsters` để lấy tên hiển thị.
