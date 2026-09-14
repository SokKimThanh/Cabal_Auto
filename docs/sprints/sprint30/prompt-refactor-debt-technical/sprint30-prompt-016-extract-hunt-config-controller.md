# Sprint 30: Refactor Debt Technical - AppStateController

## Context & Motivation

Hiện tại, `AppStateController` đang chứa một hàm lớn tên là `build_hunt_config_from_state` và ôm luôn nhiệm vụ build config cho Auto Hunt. Không những thế, hàm này chứa hàng tá các cấu hình mặc định (delay `0.2`, `0.15`, phím tắt `"ctrl+shift+r"`) được hardcode thẳng vào logic mã. Việc này vi phạm Nguyên lý Đơn trách nhiệm (SRP) và gây khó khăn khi bảo trì (Magic numbers/strings).

**Title:** Tách HuntConfigController và loại bỏ cấu hình Hardcode
**Objective:** Tách toàn bộ logic tạo lập cấu hình săn (Hunt Config) ra một file controller chuyên biệt (hoặc service) là `HuntConfigController`, đồng thời đưa các hardcode defaults về dạng Constants tập trung.

## Execution Steps

### Step 1. Khởi tạo hằng số (Constants)
Tạo một file mới `lib/features/hunt/hunt_constants.py` (nếu chưa có hoặc đặt trong controller nếu thích hợp) để lưu các cấu hình mặc định, hoặc định nghĩa ngay tại đầu file `ui/controllers/hunt_config_controller.py`:
- `DEFAULT_TARGET_KEY = "TAB"`
- `DEFAULT_TARGET_CYCLE_DELAY = 0.2`
- `DEFAULT_SEARCH_INTERVAL = 0.25`
- `DEFAULT_ATTACK_INTERVAL = 0.15`
- `DEFAULT_LOST_TIMEOUT = 1.2`
- `DEFAULT_ATTACK_MIN_DURATION = 1.5`
- `DEFAULT_ATTACK_PRESS_MS = 60`
- `DEFAULT_START_HOTKEY = "ctrl+shift+r"`
- `DEFAULT_STOP_HOTKEY = "ctrl+shift+e"`
...

### Step 2. Tạo `HuntConfigController`
- Tạo file `ui/controllers/hunt_config_controller.py`.
- Tạo class `HuntConfigController` có thể nhận `app_state` (instance của `AppStateController`) để đọc UI vars và state thông qua các getter an toàn.
- Di chuyển hàm `build_hunt_config_from_state` từ `AppStateController` sang class mới này (đổi tên thành `build_config` hoặc giữ nguyên tùy chuẩn mực).

### Step 3. Loại bỏ Hardcode
- Cập nhật hàm vừa chuyển sang `HuntConfigController` để thay thế hoàn toàn các giá trị hardcode như `"TAB"`, `0.2`, `"ctrl+shift+r"` bằng các hằng số ở Bước 1.

### Step 4. Cập nhật nơi gọi (Consumers)
- Sửa những chỗ đang gọi `app.state_controller.build_hunt_config_from_state()` (như trong `hunt_controller.py` hoặc `app_gui.py`) để chúng khởi tạo/gọi đến `HuntConfigController().build_config(self.state_controller)` hoặc tiêm (inject) `HuntConfigController` phù hợp.
- Xóa hàm `build_hunt_config_from_state` ra khỏi `AppStateController`.

## Definition of Done (Checklist)
- [ ] `AppStateController` không còn chứa hàm `build_hunt_config_from_state`.
- [ ] File `hunt_config_controller.py` (hoặc module tương tự) được tạo và chứa logic build config.
- [ ] Các giá trị Magic Numbers, Magic Strings liên quan đến hotkey/delay mặc định được trừu tượng hóa qua Constants.
- [ ] Các consumer (ví dụ: `HuntController`) gọi đúng hàm build từ cấu trúc mới.