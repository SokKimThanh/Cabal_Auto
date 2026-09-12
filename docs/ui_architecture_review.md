# UI Architecture Review & Technical Debt Report

## 1. State Management (Quản lý trạng thái UI)

**Thực trạng:**
- Trạng thái hiện đang bị phân tán giữa `app_gui.py` (Lớp `App` đóng vai trò là một God Class quản lý hàng chục trạng thái như `self._detected_snapshot_items`, `self.hunt_selected`, v.v.), `AppStateController`, và bên trong các Panel/Frame.
- `AppStateController` hiện nay không thực sự bao bọc (encapsulate) State mà lại trực tiếp gán thuộc tính vào đối tượng `root` (ví dụ `app.click_running = False`, `app.win_items = []`).
- Nhiều Panel (như `SkillPanel`, `MonsterTargetPanel`, `TargetStatusPanel`) vẫn tự quản lý trạng thái hiển thị riêng rẽ và trực tiếp gọi các Service database từ trong UI thay vì thông qua một Controller/Manager thống nhất.
- Sự phụ thuộc mật thiết giữa UI và Business Logic, khiến việc tái sử dụng component hoặc unit test gặp nhiều khó khăn.

**Đề xuất kiến trúc mục tiêu:**
- **Tách bạch State Store:** Xây dựng một cơ chế Store (tương tự Vuex/Redux hoặc ViewModel) riêng biệt để lưu trữ App State. UI chỉ "observe" và cập nhật khi State thay đổi.
- **Loại bỏ trạng thái khỏi `App` root:** Lớp `App` chỉ nên chịu trách nhiệm bootstrap giao diện chính. Các trạng thái về Hunt, Scan, Window nên được đẩy về các State Manager chuyên dụng.
- Không để các UI Frame tự ý gọi DbService hoặc thao tác lưu file cấu hình trực tiếp mà phải thông qua một Event/Action gửi tới Controller/Service layer.

## 2. Component Lifecycle (Vòng đời đối tượng và __init__)

**Thực trạng:**
- Một số lượng rất lớn (gần 1400 trường hợp) thuộc tính (attributes) đang được khai báo và khởi tạo bên ngoài `__init__` (ví dụ trong các hàm `_build()`, `setup()`, hoặc khi một sự kiện xảy ra).
- Ví dụ trong `app_gui.py`, các biến như `self.has_unsaved_changes`, `self._btn_scan_ref`, `self._last_snapshot` được khai báo rải rác.
- Trong `ui/panels/skill_panel.py`, biến `self._class_list` và `self.skill_names` được tạo động trong các phương thức.
- Vi phạm này dẫn đến rủi ro lớn về lỗi `AttributeError` khi một phương thức truy cập thuộc tính trước khi nó được khởi tạo.

**Đề xuất cải thiện:**
- **Khai báo nghiêm ngặt trong `__init__`:** Mọi thuộc tính của Component phải được khai báo trong `__init__`. Nếu tại thời điểm khởi tạo chưa có giá trị, cần gán giá trị mặc định là `None`, `False`, `[]`, hoặc `{}`.
- Refactor các hàm `_build()` để chúng chỉ có nhiệm vụ khởi tạo widget và gán vào các thuộc tính đã được khai báo sẵn từ `__init__`.

## 3. Error Handling & Services

**Thực trạng:**
- **Timers:** Rất nhiều lời gọi `self.after(...)` (khoảng 60 chỗ) rải rác trong `app_gui.py`, `app_window_controller.py`, `hotkey_controller.py` để tạo loop, polling hoặc debounce. Thiếu cơ chế Timer Manager tập trung, dễ dẫn đến rò rỉ bộ nhớ (memory leak) hoặc lỗi Tcl/Tk khi Frame bị hủy nhưng timer vẫn chạy.
- **Dialog & Notification:** Lời gọi `messagebox.showinfo`, `messagebox.showerror` (khoảng 180 chỗ) được gọi trực tiếp bên trong `app_gui.py` và các hàm controller. Điều này khiến UI bị "khóa" cứng với hộp thoại mặc định của OS và rất khó để đổi sang custom modal, cũng như làm khó quá trình viết Unit Test.
- **Error Handling (Try/Except):** Rất nhiều block `try...except Exception:` (bare except) hoặc `try...except:` (chưa bắt cụ thể loại lỗi), khiến ứng dụng che giấu (swallow) các lỗi không lường trước. Việc xử lý lỗi và logging bị trộn lẫn với logic UI.
- **Background Tasks & Threads:** Thư viện `threading.Thread` được gọi thủ công (ví dụ ở `compact_window_selector.py`, `overlay_window.py`). UI thread bị phơi nhiễm rủi ro do tương tác chéo giữa các thread.

**Đề xuất kiến trúc mục tiêu:**
- **Timer/Task Service:** Chuyển các cơ chế polling và scheduling vào một `TaskScheduler` hoặc `TimerManager` (có quản lý lifecycle, tự động hủy khi component bị destroy).
- **Dialog/Notification Service:** Xây dựng một Dialog Service. Các Frame chỉ việc gọi `DialogService.show_error(msg)`. Service sẽ quyết định hiển thị qua `messagebox`, Custom UI, hay Toast Notification.
- **Xử lý lỗi tập trung:** Tránh bare except; phân loại exception rõ ràng. Các Frame nên chuyển lỗi về ErrorHandler chung để ghi log và thông báo.

## 4. Code Smells và Các Vấn Đề Khác

- **God Class:** `App` (trong `app_gui.py`, với hơn 3000 dòng code) đóng vai trò vừa là Window chứa (Container), vừa là trung tâm điều phối trạng thái, quản lý Controller, bắt sự kiện Window, xử lý Hunt... Cần tách `App` thành các View nhỏ và phân chia trách nhiệm.
- **Mức độ gắn kết cao (Coupling):** UI phụ thuộc trực tiếp vào các Service DB.
- **Thiếu kiểm soát luồng (Thread Management):** Việc xử lý bất đồng bộ hoặc gọi hàm định kỳ hiện tại dựa chủ yếu vào `.after` và `Thread` rải rác. Cần áp dụng một Worker/Task Queue thống nhất.

## 5. Kế hoạch hành động đề xuất

1. **Giai đoạn 1 (Lifecycle & Safety):** Khai báo toàn bộ thuộc tính (`self.x = None`) vào trong `__init__` của các UI Component để triệt tiêu lỗi `AttributeError`.
2. **Giai đoạn 2 (Service Extraction):** Tách Dialog, Notification, và Logging thành các Service độc lập có thể inject vào Controller. Thay thế toàn bộ `messagebox.*` bằng `DialogService`.
3. **Giai đoạn 3 (State Management & God Class):** Đưa trạng thái (State) ra khỏi `App` root. Biến `App` trở thành class mỏng chỉ có nhiệm vụ ráp nối các Module. Chuyển logic từ Frame sang các ViewModel/Controller tương ứng.
