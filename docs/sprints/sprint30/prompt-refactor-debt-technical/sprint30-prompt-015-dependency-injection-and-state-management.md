# Sprint 30: Refactor `app_gui.py` - Giai đoạn 1

**Mã số:** 01
**Tên công việc:** Dependency Injection & State Management (Gỡ rối Dữ liệu)
**Thời gian dự kiến:** 5 - 8 giờ

## 1. Bối cảnh
Hiện tại, lớp `App` (trong `lib/app_gui.py`) đang đóng vai trò là một God Class. Bên trong hàm `__init__`, nó đang tự khởi tạo một lượng lớn các Service (ví dụ: `HuntOrchestrator`, `IconService`, `ConfigManager`...) dẫn đến Tight Coupling, gây khó khăn cho việc viết Unit Test và mở rộng.
Đồng thời, nó cũng đang ôm đồm việc lưu trữ các trạng thái (State) như danh sách cấu hình, dữ liệu rotation quái vật, v.v...

## 2. Mục tiêu
Thực hiện "Bước 1 (Gỡ rối Dữ liệu)" của lộ trình refactor:
1.  **State Management:** Bóc tách các biến trạng thái cục bộ đang lưu lộn xộn trong `App` ra các Store chuyên dụng.
2.  **Dependency Injection (DI):** Loại bỏ việc tự khởi tạo Service bên trong `App.__init__`. Thay vào đó, thiết lập các DI Container ở tầng khởi chạy ứng dụng (`main.py` hoặc file tương đương) và truyền vào `App` thông qua tham số.

## 3. Các bước thực thi chi tiết

### 3.1. Thiết lập State Management
*   **Tạo mới `HuntConfigStore`:**
    *   Vị trí: `lib/ui/stores/hunt_config_store.py` (hoặc thư mục quản lý state tương ứng).
    *   Trách nhiệm: Đọc, ghi và lưu trữ bộ đệm cấu hình săn quái (chuyển đổi `self.hunt_cfg` từ `app_gui.py` sang đây).
*   **Tạo mới `MonsterSessionManager`:**
    *   Vị trí: `lib/ui/stores/monster_session_manager.py`.
    *   Trách nhiệm: Quản lý danh sách `monster_rotation`, `skills`, và `_monster_metadata_cache` đang nằm trong `App`.
*   **Tích hợp vào UI:** Cập nhật file `app_gui.py` để sử dụng các Store/Manager mới này thông qua phương thức truy xuất (getter/setter) hoặc đăng ký theo dõi thay vì truy cập trực tiếp `self.*`. (Hãy chú ý giữ tương thích với `AppStateController` hiện tại nếu chúng có giao thoa).

### 3.2. Áp dụng Dependency Injection
*   **Cấu trúc lại `App.__init__`:**
    *   Thay đổi signature của hàm khởi tạo (ví dụ: `def __init__(self, di_container: AppContainer)`).
    *   Xóa các đoạn mã tự gọi hàm khởi tạo lớp service (như `HuntOrchestrator(...)`).
*   **Thiết lập Container tại file khởi chạy (`main.py` / `run.py`):**
    *   Khởi tạo toàn bộ các Service tại đây.
    *   Truyền các instance này vào lớp `App` (Ví dụ: thông qua một đối tượng Data Class tên là `AppContainer`).

## 4. Yêu cầu nghiệm thu (Acceptance Criteria)
*   Lớp `App` không còn tự khởi tạo (gọi trực tiếp constructor) của các lớp Service cốt lõi (HuntOrchestrator, v.v...).
*   Các biến `hunt_cfg`, `monster_rotation` đã được chuyển hẳn khỏi thuộc tính cá nhân của `App`.
*   Ứng dụng (Tkinter) vẫn khởi chạy bình thường. Chạy thử các tính năng tải cấu hình và xem danh sách quái để đảm bảo dữ liệu được hiển thị đầy đủ mà không bị lỗi.
*   **Nguyên tắc an toàn:** Sau mỗi file được sửa đổi, hãy dùng tool đọc lại file để đảm bảo code không bị mất hoặc sai thụt lề.

> **Lưu ý cho AI Assistant:** Vui lòng áp dụng nguyên lý sửa đổi code một cách cẩn thận (sử dụng merge_diff). Giao tiếp với người dùng khi cần làm rõ cách phân định ranh giới giữa `AppStateController` hiện có và các Store mới.