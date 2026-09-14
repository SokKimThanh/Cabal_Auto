# Sprint 30: Refactor `app_gui.py` - Giai đoạn 2

**Mã số:** 02
**Tên công việc:** MVC/MVVM & Event Bus (Gỡ rối Luồng xử lý)
**Thời gian dự kiến:** 9 - 12 giờ

## 1. Bối cảnh
Sau khi hoàn thành Giai đoạn 1 (Gỡ rối Dữ liệu), lớp `App` đã nhận các Dependencies từ bên ngoài và tách biệt phần dữ liệu. Tuy nhiên, nó vẫn còn chứa trực tiếp các hàm xử lý logic nghiệp vụ rắc rối như tính toán luồng chạy của quái vật (`promote_detected_monster`) hay tính toán thời gian, điều khiển Bot (HuntRunner/Orchestrator).
Bên cạnh đó, luồng giao tiếp giữa UI và các background service đang phụ thuộc vào vô số hàm callback ẩn danh (lambda) lồng nhau, gây khó khăn cho việc truy vết lỗi và dễ dẫn đến memory leak ở Tkinter.

## 2. Mục tiêu
Thực hiện "Bước 2 (Gỡ rối Luồng xử lý)" của lộ trình refactor:
1.  **Tách MVC/MVVM:** Di chuyển các logic tính toán, xử lý nghiệp vụ ra khỏi View (lớp `App`) sang các Controller chuyên biệt.
2.  **Áp dụng Event Bus:** Loại bỏ mô hình truyền callback nối tiếp, thay thế bằng cơ chế phát (emit) và đăng ký (subscribe) sự kiện đồng bộ trạng thái UI.

## 3. Các bước thực thi chi tiết

### 3.1. Phân rã MVC/MVVM
*   **Tạo mới `HuntController`:**
    *   Vị trí: `lib/ui/controllers/hunt_controller.py`.
    *   Trách nhiệm: Nhận các tương tác liên quan đến Hunt từ View (Start, Stop, cấu hình Hunt). Điều phối với `HuntOrchestrator` và cập nhật `HuntConfigStore` (đã tạo ở Giai đoạn 1).
    *   Di dời các hàm như: logic chuẩn bị săn, validate cửa sổ, start/stop vào đây.
*   **Tạo mới `MonsterRotationController`:**
    *   Vị trí: `lib/ui/controllers/monster_rotation_controller.py`.
    *   Trách nhiệm: Nhận các hành động như thêm/bớt/đẩy ưu tiên (promote) quái vật.
    *   Di dời các hàm xử lý logic nghiệp vụ của quái vật (ví dụ: `promote_detected_monster`) khỏi `App`.
*   **View (`App`):** View lúc này chỉ làm nhiệm vụ: `button_click -> controller.do_action()`. Tuyệt đối không chứa logic `if/else` nghiệp vụ bên trong View.

### 3.2. Chuyển đổi sang Event Bus
*   Rà soát lại sự kết nối giữa `HuntRunner`, `HuntOrchestrator` và UI.
*   **Loại bỏ Callback:** Các tham số như `on_status_update`, `set_status`, `schedule_ui_task` (thường là các lambda truyền vào constructor của service) phải được dọn dẹp.
*   **Phát sự kiện (Emit):** Các service chạy nền chỉ cần gọi `EventBus.emit("HUNT_STATUS_CHANGED", new_status)`.
*   **Đăng ký sự kiện (Subscribe):** Tại các Controller hoặc View (cụ thể là `App` hiện tại), sử dụng `EventBus.bind()` để lắng nghe sự kiện và cập nhật lên UI widget tương ứng. Chú ý xử lý thread-safe bằng `after()` nếu cần để tránh đóng băng Tkinter.

## 4. Yêu cầu nghiệm thu (Acceptance Criteria)
*   Không còn các hàm chứa logic tính toán phức tạp (như xử lý mảng quái vật, tính giây) trong `app_gui.py`.
*   Không còn các callback UI truyền sâu vào trong background service.
*   Log, trạng thái (status bar) và giao diện cập nhật chính xác, mượt mà khi chạy luồng săn quái mô phỏng.
*   **Kiểm thử rò rỉ:** Chuyển đổi qua lại giữa các tính năng mà ứng dụng không bị tăng RAM bất thường (do event không được unbind).

> **Lưu ý cho AI Assistant:** Hãy chú ý đến việc bind/unbind event của EventBus trong vòng đời của Tkinter để tránh hiện tượng gọi cập nhật UI khi widget đã bị phá hủy.