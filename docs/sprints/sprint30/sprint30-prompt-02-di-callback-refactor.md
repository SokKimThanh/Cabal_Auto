# Sprint 30: Refactor `app_gui.py` - Giai đoạn 2

**Mã số:** 02
**Tên công việc:** Dependency Injection & Lifecycle (Gỡ rối Callbacks)
**Thời gian dự kiến:** 4 - 6 giờ

## 1. Bối cảnh
Ở Giai đoạn 1, chúng ta đã tách công việc khởi tạo các Service nặng nề ra khỏi `App.__init__` và đưa xuống `main()`, sau đó tiêm (inject) vào bằng `AppContainer`.
Tuy nhiên, do các Service như `HuntOrchestrator` và `HuntRunner` phụ thuộc rất nhiều vào các hàm giao diện (callbacks) như `self.state_controller.set_ui_var`, `self.hunt_tab.update_status`, việc khởi tạo chúng ở `main()` buộc phải làm một bước khá cồng kềnh: Khởi tạo `app = App()`, sau đó tạo Service và chèn các callback từ `app` vào, rồi mới gán Service ngược lại cho `app`.
Cách này vẫn là "Service Locator" trá hình, làm giảm tính linh hoạt và khó viết Unit Test (Test Isolation).

## 2. Mục tiêu
Thực hiện "Bước 2 (Gỡ rối Callbacks)":
1. **Event-driven UI updates:** Thay thế các callback UI trực tiếp (như `on_status_update`, `update_target_hp`) truyền vào `HuntOrchestrator` và `HuntRunner` bằng cơ chế Event Bus (hoặc Observer Pattern).
2. **Trì hoãn liên kết (Late Binding):** Nếu không dùng Event Bus, thì tách logic tạo Service trong DI Container thành một lớp `ServiceLocator` hoặc sử dụng Decorator để truyền hàm khi UI đã sẵn sàng (Lifecycle hook).
3. **Mục tiêu cuối:** Hàm `main()` tạo một Container hoàn chỉnh, truyền duy nhất biến `container` vào `App(di_container=container)`, các Service tự phát ra Event khi có thay đổi trạng thái, UI tự lắng nghe Event đó để cập nhật trạng thái lên màn hình mà Service không cần biết `app` là ai.

## 3. Các bước thực thi chi tiết
- **Bước 3.1:** Thêm các định nghĩa Event vào `lib/events/event_bus.py` (ví dụ: `HuntStatusChangedEvent`, `HuntTargetHpChangedEvent`).
- **Bước 3.2:** Sửa `HuntOrchestrator` và `HuntRunner` để chúng gọi `EventBus.emit()` thay vì gọi hàm callback.
- **Bước 3.3:** Xóa các argument lambda phức tạp trong hàm `main()` khi tạo `HuntOrchestrator` và `HuntRunner`.
- **Bước 3.4:** Trong file `app_gui.py` hoặc ở từng Component (như `HuntTab`), đăng ký lắng nghe (subscribe) các Event này và thực thi hàm cập nhật giao diện tương ứng.

## 4. Yêu cầu nghiệm thu
- Không còn truyền `lambda v: app.state_controller.set_ui_var(...)` vào trong hàm khởi tạo của `HuntOrchestrator` hay `HuntRunner`.
- UI vẫn cập nhật đầy đủ (trạng thái, máu của quái vật) trong quá trình auto đánh quái.
