# Sprint 30: Refactor `app_gui.py` - Giai đoạn 3

**Mã số:** 03
**Tên công việc:** UI Component Breakdown (Gỡ rối Giao diện)
**Thời gian dự kiến:** 4 - 6 giờ

## 1. Bối cảnh
Ở thời điểm này, lớp `App` (trong `lib/app_gui.py`) đã là một "Lớp rỗng" về mặt dữ liệu (DI/State Management - Giai đoạn 1) và mặt nghiệp vụ (MVC/Event Bus - Giai đoạn 2). Tuy nhiên, nó vẫn còn là một God Class về mặt Layout, chứa hàm `_build_ui` dài hàng trăm/ngàn dòng để khởi tạo tất cả các nút bấm, lưới, và khung của toàn bộ ứng dụng. Việc này làm giảm khả năng tái sử dụng (View Composition).

## 2. Mục tiêu
Thực hiện "Bước 3 (Gỡ rối Giao diện)" của lộ trình refactor:
1.  **Phân rã UI Component:** Tách các khối giao diện đang viết chung trong hàm `_build_ui` thành các class kế thừa từ `tk.Frame` chuyên biệt.
2.  **Biến `App` thành Layout Container:** Lớp `App` lúc này chỉ đóng vai trò là khung chứa (Root Container), thực hiện việc điều phối, gắn kết các View con (Components) lại với nhau dựa trên Grid System.

## 3. Các bước thực thi chi tiết

### 3.1. Xác định và Tách các vùng UI (Zone Breakdown)
Dựa theo kiến trúc lưới (Grid/Zone) của ứng dụng, hãy tiến hành tách code UI thành các class riêng. Ví dụ:
*   **`ActionBarView`:**
    *   Vị trí file: `lib/ui/components/action_bar_view.py`.
    *   Bao gồm: Các nút thao tác chung (Global Apply, Scan Manual, Settings menu...).
*   **`StatusBarView`:**
    *   Vị trí file: `lib/ui/components/status_bar_view.py`.
    *   Bao gồm: Thanh trạng thái bên dưới (Label trạng thái, Log metrics, Hotkey status...).
*   **Các Zone khác:** Tùy vào mức độ phức tạp hiện tại, có thể xem xét tách thêm các phần như MainContentZone hay Sidebar (nếu chưa tách).

### 3.2. Refactor `App._build_ui`
*   Rút gọn hoàn toàn hàm `_build_ui`.
*   Khởi tạo các View Component vừa tạo. Truyền các tham số cần thiết (ví dụ: Controller hoặc Dependency Injection Container) vào các View này.
*   Ví dụ:
    ```python
    self.action_bar = ActionBarView(self.shell_zone_a, controller=self.hunt_controller)
    self.action_bar.pack(fill="x")
    ```

## 4. Yêu cầu nghiệm thu (Acceptance Criteria)
*   Hàm `_build_ui` trong `app_gui.py` được rút gọn tối đa (khuyến nghị dưới 100 dòng), chỉ chứa cấu trúc layout tổng thể và khởi tạo component.
*   Mỗi vùng giao diện (ActionBar, StatusBar...) nằm trong một file và một Class `tk.Frame` riêng biệt.
*   Ứng dụng hiển thị không có sự thay đổi về mặt thiết kế (Pixel-perfect hoặc gần giống nhất có thể so với trước khi refactor). Cấu trúc Grid/Pack không bị vỡ.
*   Các tương tác (nhấn nút, xem trạng thái) vẫn hoạt động chính xác thông qua việc giao tiếp với Controller.

> **Lưu ý cho AI Assistant:** Khi di dời các đoạn mã tạo Widget của Tkinter sang Class mới, hãy chú ý đến biến `self` hoặc `parent` để đảm bảo widget được đặt đúng vào Frame chứa nó. Sử dụng `pack`, `grid`, `place` đồng nhất với kiến trúc cũ để tránh vỡ giao diện.