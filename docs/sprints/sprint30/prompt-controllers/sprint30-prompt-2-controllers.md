# Sprint 30 - Bước 2: Tạo Controllers (Hunt & MonsterRotation)

**Mục tiêu:** Tách logic tính toán nghiệp vụ (business logic) ra khỏi `App` class trong `app_gui.py` và chuyển vào các Controllers chuyên biệt. Đảm bảo tuân thủ mô hình MVC/MVVM.

**Các bước thực hiện:**
1. **Tạo `MonsterRotationController`:**
   - Tạo file `lib/ui/controllers/monster_rotation_controller.py`.
   - Lớp Controller nhận `state_controller` (để truy cập/cập nhật dữ liệu quái vật, unsaved changes) thông qua constructor (hoặc Dependency Injection).
   - Di chuyển hàm `promote_detected_monster` từ `app_gui.py` vào đây. Chú ý refactor để hàm này không trực tiếp gọi UI (ví dụ như `_update_detected_monsters_list` hay `_refresh_monster_rotation_list` trong View), mà thay vào đó sẽ trigger các Event (ví dụ: `EventBus.trigger(MonsterRotationUpdatedEvent())`).
   - Xử lý việc tính toán độ ưu tiên (priority), kiểm tra trùng lặp (duplicate) độc lập với View.
2. **Tạo `HuntController`:**
   - Tạo file `lib/ui/controllers/hunt_controller.py`.
   - Controller này chịu trách nhiệm: Validate cửa sổ (`WindowSelectionService.validate_prerequisites`), xây dựng `hunt_cfg`, lưu cấu hình, và gọi lệnh tới `HuntOrchestrator` (`start_hunt` / `stop_hunt`).
   - Di dời logic của các hàm như `_request_start_hunt` và `_request_stop_hunt` từ `app_gui.py` sang Controller này.
3. **Đăng ký Services/Controllers trong `app_container.py` (nếu cần thiết):**
   - Đảm bảo các Controller mới được khởi tạo đúng vòng đời và tiêm (inject) vào View hoặc Container nếu đang dùng DI.
