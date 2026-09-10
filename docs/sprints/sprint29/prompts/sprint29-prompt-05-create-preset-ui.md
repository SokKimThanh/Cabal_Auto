# Sprint 29 - Prompt 05: Thêm chức năng Create Preset từ SkillPanel

## Mục tiêu
Cho phép người dùng lưu nhanh cấu hình kỹ năng hiện tại trên `SkillPanel` thành một Preset lưu vào cơ sở dữ liệu (`skill_presets` và `preset_skills`).

## Phạm vi (Scope)
- Sửa đổi file: `ui/panels/skill_panel.py`
- Tạo file mới: `ui/dialogs/create_preset_dialog.py`

## Chi tiết yêu cầu

1. **Thêm nút "Save as Preset"**
   - Trong `ui/panels/skill_panel.py`, tại khu vực controls_frame (cùng chỗ với nút Combo), thêm một `tk.Button` tên "Save as Preset" (có thể để icon 💾).
   - Gắn command gọi đến hàm `_on_save_preset_click()`.

2. **Xây dựng `CreatePresetDialog`**
   - Tạo file `ui/dialogs/create_preset_dialog.py` kế thừa từ `tk.Toplevel`.
   - Giao diện gồm:
     - Input Text: Tên của Preset (Bắt buộc).
     - Label: Hiển thị Class ID (hoặc Name) mà preset này thuộc về (lấy từ `self.app_state._current_class_id`). Không cho phép đổi.
     - Frame: Một vùng nhỏ List ra tóm tắt (ReadOnly) các skill ID hoặc Name đang chuẩn bị được lưu.
     - Nút Save và Cancel.
   - Khi ấn Save, dialog thu thập dữ liệu và gọi hàm callback truyền lại cho `SkillPanel`.

3. **Xử lý lưu trữ xuống Database**
   - Khi dialog trả về dữ liệu (Tên Preset), trong `SkillPanel`, hãy đọc cấu trúc kỹ năng hiện tại từ `self.app_state.skill_slots` (bằng cách tương tự như trong `on_skill_slots_changed`).
   - Khởi tạo service (nếu app_state chưa có sẵn hàm save, hãy dùng `self.app.db_skill_service` hoặc tương đương). Gọi API Database để:
     1. Insert vào bảng `skill_presets` (name, class_id).
     2. Lặp qua các skill trong `skill_slots` (vd: attack_combo, buff_lane) và insert vào bảng `preset_skills`.

4. **Kiểm tra (Verification)**
   - Mở app, chỉnh sửa các dropdown skill trên Skill Panel.
   - Nhấn "Save as Preset", đặt tên.
   - Dùng SQLite Viewer kiểm tra bảng `skill_presets` và `preset_skills` xem dữ liệu đã được sinh ra chưa. Không được lỗi Null ForeignKey.

## Lưu ý (Memory Guidelines)
- Khi gọi Toplevel từ Tkinter, hãy disable nút "Save as Preset" tạm thời để tránh click nhiều lần tạo ra nhiều hộp thoại (debounce/lock).