# Sprint 30: Refactor Debt Technical - AppStateController

## Context & Motivation

Trong `AppStateController`, có một tình trạng sử dụng `getattr()` và `hasattr()` rất nhiều đối với biến `self` (ví dụ `getattr(self, "skill_slot_key_labels", [])`, `if not hasattr(self, "_config_store"):`). Điều này cho thấy constructor (`__init__`) của Controller chưa khởi tạo đầy đủ các thuộc tính ngay từ đầu, khiến vòng đời đối tượng (Component Lifecycle) trở nên khó đoán, IDE khó hỗ trợ nhắc code, và mã nguồn vi phạm các quy tắc thiết kế cơ bản.

**Title:** Dọn dẹp `__init__` của AppStateController để loại bỏ `getattr` / `hasattr`
**Objective:** Khai báo toàn bộ các biến instance (bắt đầu bằng `self.`) bên trong hàm `__init__` của `AppStateController` và đảm bảo các properties không cần kiểm tra `hasattr(self, ...)` nữa.

## Execution Steps

### Step 1. Khai báo thuộc tính trong `__init__`
Mở `ui/controllers/app_state_controller.py` và cập nhật hàm `__init__`:
- Khởi tạo `self._config_store = HuntConfigStore()` và `self._monster_session_manager = MonsterSessionManager()` (hiện tại có thể đã khởi tạo, nhưng properties lại kiểm tra `hasattr`).
- Bổ sung định nghĩa các thuộc tính mà properties đang truy cập qua `getattr`:
  - `self._has_unsaved_changes = False`
  - `self._bounds_recovery_failed = False`
  - `self._win_items = []`
  - `self._hunt_selected = None`
  - `self._current_window_bounds = None`
  - `self.skill_slot_key_labels = []` (Nếu đang bị dùng qua `getattr(self, "skill_slot_key_labels", [])`)

### Step 2. Dọn dẹp Properties
Cập nhật các getter và setter trong `AppStateController` để sử dụng trực tiếp các biến `self._XXX` mà không cần dùng `getattr` hay `hasattr`.
- `hunt_cfg`: Trả về trực tiếp `self._config_store.get_config()`.
- `has_unsaved_changes`: Trả về trực tiếp `self._has_unsaved_changes`.
- `bounds_recovery_failed`: Trả về trực tiếp `self._bounds_recovery_failed`.
- `win_items`: Trả về trực tiếp `self._win_items`.
- `hunt_selected`: Trả về trực tiếp `self._hunt_selected`.
- `current_window_bounds`: Trả về trực tiếp `self._current_window_bounds`.
- `monster_rotation`: Trả về `self._monster_session_manager.get_rotation()`.

### Step 3. Dọn dẹp phương thức
- Tại các hàm `_refresh_slot_key_labels`, `_validate_slot_key_duplicates` và `build_hunt_config_from_state`: Loại bỏ việc sử dụng `getattr(self, ...)` và thay bằng việc truy cập trực tiếp `self.skill_slot_key_labels`, `self.skill_slot_vars`, `self.current_window_bounds`, v.v.

## Definition of Done (Checklist)
- [ ] Hàm `__init__` chứa đầy đủ tất cả các biến thuộc tính của class.
- [ ] Không còn bất kì sự xuất hiện nào của hàm `getattr(self, ...)` trong `AppStateController`.
- [ ] Không còn bất kì sự xuất hiện nào của hàm `hasattr(self, ...)` trong `AppStateController`.
- [ ] Code vẫn qua được các bài test đơn vị/tích hợp liên quan.