# Sprint 30: Refactor Debt Technical - AppStateController

## Context & Motivation

Trong file `AppStateController`, hiện đang tồn tại hai hàm là `_refresh_slot_key_labels` và `_validate_slot_key_duplicates`. Hai hàm này trực tiếp duyệt qua một mảng chứa các Tkinter Label (Widget) và gọi hàm `.config(text=...)` hoặc `.config(fg=...)`. Điều này vi phạm nghiêm trọng mô hình MVC/MVVM: State Controller tuyệt đối không được điều khiển (manipulate) widget giao diện trực tiếp. Việc này rò rỉ (leak) UI logic vào Data layer.

**Title:** Xóa UI logic (.config) khỏi AppStateController và thay bằng Event Bus
**Objective:** Loại bỏ hoàn toàn các lời gọi `.config()` trong `AppStateController`. Thay vào đó, Controller chỉ đánh giá logic (ví dụ phát hiện trùng lặp) và phát đi (emit) Event; View sẽ lắng nghe Event này và tự cập nhật giao diện (`.config`).

## Execution Steps

### Step 1. Tái cấu trúc logic xác thực (Validation)
Trong `AppStateController` (hoặc Controller tương ứng quản lý Skill), chuyển đổi hàm `_validate_slot_key_duplicates`:
- Thay vì lấy danh sách labels ra và đổi màu, hàm này sẽ chỉ trả về hoặc tính toán một mảng (hoặc set) chứa các *chỉ số (index)* của những ô skill đang bị trùng lặp phím tắt.
- Sau khi tính toán xong danh sách `duplicate_indices`, gọi `self._emit_event("on_skill_key_duplicates_detected", duplicate_indices)`.

Tương tự cho `_refresh_slot_key_labels`:
- Logic ánh xạ (map) từ tên skill ra phím tắt có thể giữ lại như một hàm helper trả về danh sách các phím (keys array), sau đó phát ra event: `self._emit_event("on_skill_keys_updated", keys_list)`.

### Step 2. Xóa các hàm rò rỉ UI
- Xóa hoàn toàn việc gọi `label.config(...)` khỏi `AppStateController`.
- Controller sẽ không cần và không nên lưu/tham chiếu mảng `self.skill_slot_key_labels` nữa (có thể xóa khởi tạo này ở `__init__` nếu có ở Prompt 015).

### Step 3. Cập nhật View (Giao diện)
- Di chuyển mảng chứa các `tk.Label` về đúng file View (có thể là `ActionbarView` hoặc `SkillPanel` hoặc ngay trong `App` ở `app_gui.py` tùy thiết kế hiện tại).
- Bổ sung lệnh lắng nghe sự kiện (`register_callback` hoặc `EventBus.bind`) ngay tại View.
  Ví dụ: `self.state_controller.register_callback("on_skill_key_duplicates_detected", self._update_duplicate_colors)`
- Trong hàm `_update_duplicate_colors(duplicate_indices)` tại View, bạn mới thực sự vòng lặp qua mảng Label cục bộ của View và gọi `.config(fg=...)`.

## Definition of Done (Checklist)
- [ ] Hàm `_refresh_slot_key_labels` trong Controller không còn chứa bất kỳ hàm UI Tkinter nào (như `.config`).
- [ ] Hàm `_validate_slot_key_duplicates` trong Controller không còn chứa hàm UI Tkinter nào.
- [ ] `AppStateController` không còn cần giữ tham chiếu danh sách UI labels.
- [ ] View đã lắng nghe sự kiện thành công và UI đổi màu chữ đúng khi có sự thay đổi.