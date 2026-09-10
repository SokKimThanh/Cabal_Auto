# Sprint 29 - Prompt 06: Cập nhật Preset Dialog hiển thị và lưu Active State

## Mục tiêu
Cải thiện `PresetDialog` hiện tại để người dùng dễ dàng biết được Preset nào đang được kích hoạt (Active) và đảm bảo khi Apply một Preset mới, trạng thái này được lưu vào bảng `user_preset_state` trong DB.

## Phạm vi (Scope)
- Sửa đổi file: `ui/dialogs/preset_dialog.py`
- Sửa đổi hàm Apply preset ở AppStateController (nếu cần).

## Chi tiết yêu cầu

1. **Hiển thị chỉ báo Active trên Giao diện**
   - Trong `ui/dialogs/preset_dialog.py`, tìm phương thức load danh sách presets (`_load_presets`).
   - Cần query (hoặc lấy từ `app_state`) ID của preset đang active hiện tại cho `self.class_id`.
   - Trong giao diện Listbox (hoặc Treeview nếu bạn có ý định đổi), bên cạnh tên của Preset đang active, hãy thêm một hậu tố ` [Active]`, hoặc dùng màu sắc (nếu listbox hỗ trợ) để bôi đậm/hiển thị màu khác.

2. **Cập nhật Logic khi nhấn nút Apply**
   - Trong hàm `on_apply()` của `PresetDialog` (hoặc nơi nó gọi tới Controller).
   - Đảm bảo rằng ngoài việc set skill slots in-memory, cần phải thực hiện một lệnh Upsert vào bảng `user_preset_state`.
   - Cập nhật record với `class_id = self.class_id` và `active_preset_id = selected_preset_id`.

3. **Kiểm tra (Verification)**
   - Mở PresetDialog, chọn một Preset và nhấn Apply.
   - Đóng Dialog, sau đó mở lại. Preset vừa chọn phải có chữ `[Active]` bên cạnh.
   - Kiểm tra DB, bảng `user_preset_state` phải có record (class_id, active_preset_id) tương ứng.

## Lưu ý (Memory Guidelines)
- Chú ý bảng `user_preset_state` sử dụng UNIQUE cho `class_id`, nên khi insert phải dùng UPSERT (`ON CONFLICT(class_id) DO UPDATE...`).
- Nếu listbox không hỗ trợ màu text riêng lẻ, cách đơn giản nhất là đổi text thành f"{preset_name} [ACTIVE]".