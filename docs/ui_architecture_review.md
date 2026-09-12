# UI Architecture Review & Technical Debt Report

## 1. State Management (Quản lý trạng thái UI)

**Thực trạng:**
- Trạng thái hiện đang bị phân tán giữa `app_gui.py`, `AppStateController`, và bên trong các Panel/Frame.
- `AppStateController` hiện nay không thực sự bao bọc (encapsulate) State mà lại trực tiếp gán thuộc tính vào đối tượng `root` (ví dụ `app.click_running = False`, `app.win_items = []`).
- Nhiều Panel (như `SkillPanel`, `MonsterTargetPanel`, `TargetStatusPanel`) vẫn tự quản lý trạng thái hiển thị riêng rẽ và trực tiếp gọi các Service database từ trong UI thay vì thông qua một Controller/Manager thống nhất.
- Sự phụ thuộc mật thiết giữa UI và Business Logic, khiến việc tái sử dụng component hoặc unit test gặp nhiều khó khăn.

**Đề xuất kiến trúc mục tiêu:**
- **Tách bạch State Store:** Xây dựng một cơ chế Store riêng biệt. UI chỉ "observe" và cập nhật khi State thay đổi.
- Không để các UI Frame tự ý gọi DbService hoặc thao tác lưu file cấu hình trực tiếp mà phải thông qua một Event/Action gửi tới Controller/Service layer.

## 2. Code Smells và Các Vấn Đề Nghiêm Trọng Khác

**God Class (Lớp App trong app_gui.py)**
- Lớp `App` đang ôm đồm quá nhiều vai trò: quản lý window, quản lý state, tạo UI, điều hướng view, xử lý monster, skill, hunt, scan, dialog, i18n, icon cache... Nó đã vượt xa vai trò của một root window thông thường.
- Việc tập trung mọi thứ vào `App` khiến độ coupling cao và rất khó mở rộng.

**View Registry bị "Hardcoded"**
- Trong `_build_ui()`, tất cả các view đều được load và gán trực tiếp: `self._views["hunt"] = ...`.
- Hệ quả là `App` biết mọi View, Controller, Service, và State. Thiếu một `ViewRegistry` hoặc `NavigationService` để làm giảm độ kết dính (coupling).

**Service Locator Anti-Pattern (Lạm dụng hasattr/getattr)**
- Code chứa quá nhiều lời gọi `if hasattr(self, ...)` và `getattr(self, ...)`. Ví dụ: `if hasattr(self, "skill_service")`, `getattr(self, "hunt_selected", {})`.
- Điều này cho thấy "Object Contract" không rõ ràng; code không chắc chắn đối tượng đang giữ thuộc tính gì. Khi số lượng này tăng cao, đây là dấu hiệu kiến trúc đang mất kiểm soát và tiềm ẩn lỗi ngầm.

## 3. Error Handling, Timers & Services

**Thực trạng:**
- **Timers phân tán:** Hàng chục lời gọi `self.after(...)` (như `self.after(100, self._poll_log_queue)`) và `Thread()` nằm rải rác trong các Frame. Các hàm này tự đăng ký lại chính nó, dẫn đến nguy cơ lớn về timer orphan, memory leak, race condition hoặc chạy sau khi frame đã chết.
- **Dialog & Notification:** Gần 180 chỗ gọi trực tiếp `messagebox.showinfo` / `showerror` trong logic xử lý, làm UI bị "khóa cứng" vào hộp thoại OS và khó làm Unit Test.
- **Error Handling (Try/Except):** Rất nhiều block `try...except Exception:` che giấu (swallow) lỗi thực sự, trộn lẫn xử lý lỗi với UI logic.

**Đề xuất:**
- Tách ngay Timer và Task management thành các Manager (`TimerManager`, `TaskScheduler`) độc lập không phụ thuộc vào UI Frame.
- Đóng gói Dialog/Notification thành các interface thay vì gọi cứng thư viện OS.

## 4. Component Lifecycle (Vòng đời đối tượng và __init__)

**Thực trạng:**
- Có rất nhiều thuộc tính được tạo động bên ngoài `__init__`. Mặc dù gây ra lỗi pylint (`attribute-defined-outside-init`), đây là vấn đề ít nghiêm trọng hơn so với Timer rò rỉ hay God Class, nhưng vẫn tạo rủi ro truy cập thuộc tính trước khi nó tồn tại.

**Đề xuất:**
- Khai báo rõ ràng mọi thuộc tính (`self.xxx = None`) trong `__init__` để dễ dàng bảo trì và tránh bất ngờ.

---

## 5. Bảng Đánh Giá Mức Độ Nghiêm Trọng (Severity)

| Vấn đề | Mức độ | Nhận xét |
|---|---|---|
| **God Class App** | 🔴 Rất cao | Phải chia nhỏ để tránh phình to không kiểm soát. |
| **Timer/after phân tán** | 🔴 Rất cao | Nguy cơ memory leak, timer orphan và rủi ro luồng (race condition) cực cao. |
| **Service Locator Anti-Pattern** | 🔴 Rất cao | (hasattr/getattr) Phá vỡ contract, hệ thống mất kiểm soát. |
| **Hardcoded View Registry** | 🟠 Cao | Coupling cao, khó tái sử dụng hoặc mở rộng View mới. |
| **UI gọi Service trực tiếp** | 🟠 Cao | Mix logic và UI. |
| **State phân tán** | 🟠 Cao | Quản lý state chưa tốt, dễ sai lệch dữ liệu. |
| **Lifecycle (init)** | 🟡 Trung bình | Pylint issues; dễ sửa nhất nhưng không phải nguồn cơn gốc rễ. |

---

## 6. Kế Hoạch Hành Động Đề Xuất (Action Plan)

**Giai đoạn 1: God Class Decomposition (Ưu tiên số 1)**
- Tách `App` thành các phần tử chuyên trách: `AppShell`, `NavigationController`, `WindowStatusController`, `HuntWorkspaceController`, `ScanController`.
- Áp dụng `ViewRegistry` hoặc `NavigationService` để tháo gỡ việc hardcode các view.

**Giai đoạn 2: Timer/Task Management (Ưu tiên số 2)**
- Xây dựng `TimerManager`, `TaskScheduler`, và `WorkerQueue` tập trung.
- Thay thế toàn bộ các lời gọi `self.after(...)` và `Thread()` trực tiếp trong UI bằng các Service này, đảm bảo tự dọn dẹp khi UI bị destroy.

**Giai đoạn 3: State Management & Service Abstraction (Ưu tiên số 3)**
- Rút dần State (trạng thái) ra khỏi `App` gốc, đưa về State Store.
- Tách Dialog, Notification, và Logging thành các Service độc lập có thể inject. Loại bỏ Anti-pattern gọi `getattr/hasattr`.

**Giai đoạn 4: Lifecycle Cleanup (Ưu tiên số 4)**
- Rà soát toàn bộ project, chuyển các khởi tạo tạo động (dynamically defined attributes) về hàm `__init__` (gán `None` hoặc giá trị mặc định) để sạch Pylint và đảm bảo Object Contract.
