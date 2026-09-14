# Sprint 30: Refactor Debt Technical - AppStateController

## Context & Motivation

Hiện tại, `AppStateController` đang chứa nhiều logic quản lý bộ kỹ năng (Skill Presets) như `set_current_class`, `load_preset_for_class`, `set_skill_slot`, `apply_default_preset`, `set_custom_mode`, `save_custom_preset`, v.v. Việc ôm đồm logic của domain "Kỹ năng / Preset" khiến class này phình to (God Object anti-pattern). Rất may, trong dự án đã có sẵn file `ui/controllers/skill_preset_controller.py`. Chúng ta cần gộp logic từ `AppStateController` sang đó.

**Title:** Gộp logic Skill Preset vào SkillPresetController
**Objective:** Di chuyển toàn bộ các phương thức quản lý Skill Preset ra khỏi `AppStateController` và chuyển vào `SkillPresetController` để tuân thủ Single Responsibility Principle.

## Execution Steps

### Step 1. Di chuyển logic vào SkillPresetController
Mở `ui/controllers/skill_preset_controller.py` và di chuyển các hàm sau từ `AppStateController` sang:
- `set_current_class(self, class_id: int) -> bool`
- `load_preset_for_class(self, class_id: int, preset_id: Optional[int] = None)`
- `apply_default_preset(self, class_id: int)`
- `set_custom_mode(self)`
- `update_preset_state(self, preset_id: int, mode: str)`
- `save_custom_preset(self, preset_name: str)`
- `get_available_presets(self, class_id: int)`
- `set_skill_slot(self, lane: str, position: int, skill_id: int)`
- `set_skill_hotkey(self, lane: str, position: int, hotkey: str)`
- `update_skill_cooldown(self, lane: str, position: int, remaining: float)`

*Lưu ý:* `SkillPresetController` nhận vào `app_state`. Do đó, khi các hàm này cần update state (như `self._current_class_id`, `self.skill_slots`, `self._active_preset_id`), chúng sẽ cập nhật thông qua `self.app_state`. Đảm bảo `app_state` vẫn đóng vai trò là "Data Store" cho UI.

### Step 2. Tái cấu trúc State Data
Giữ lại các data fields (như `self.skill_slots`, `self._active_preset_id`, `self._preset_mode`) và logic Event (`self._emit_event`) bên trong `AppStateController`.
Trong `SkillPresetController`, thay đổi cách gọi để trigger event thông qua `self.app_state._emit_event(...)` (hoặc tạo một public method `emit` trên `app_state`).

### Step 3. Cập nhật các UI View gọi đến
Tìm tất cả các nơi đang gọi `self.state_controller.load_preset_for_class(...)` hoặc `self.state_controller.set_skill_slot(...)` (ví dụ: `app_gui.py`, `skill_panel.py`). Chuyển chúng sang gọi qua instance của `SkillPresetController`. Nếu view chưa có instance này, hãy thiết lập và tiêm (inject) `SkillPresetController` vào view đó.

## Definition of Done (Checklist)
- [ ] `AppStateController` không còn chứa các hàm logic như `load_preset_for_class`, `save_custom_preset`, `set_skill_slot`, v.v.
- [ ] `SkillPresetController` chứa toàn bộ logic xử lý preset và tương tác cập nhật dữ liệu với `app_state`.
- [ ] Các View/Tab gọi đúng phương thức từ `SkillPresetController` thay vì `state_controller`.
- [ ] Quá trình Load/Save preset vẫn hoạt động ổn định trên UI.