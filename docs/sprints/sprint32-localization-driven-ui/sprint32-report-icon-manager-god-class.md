# Báo cáo Phân tích và Đề xuất Refactor "God Class" - IconManagerFrame

## 1. Tổng quan
`IconManagerFrame` hiện tại trong file `ui/views/icon_manager_frame.py` đang có kích thước xấp xỉ **2000 dòng code** với hơn **60 phương thức (methods)**. Đây là một ví dụ điển hình của "God Class" (Anti-pattern).
Class này đang ôm đồm quá nhiều trách nhiệm, vi phạm nghiêm trọng nguyên tắc **Single Responsibility Principle (SRP)**, khiến việc bảo trì, mở rộng và tìm lỗi (debug) trở nên rất khó khăn.

## 2. Triệu chứng của "God Class" trong IconManagerFrame

1.  **Quá tải Trách nhiệm (Too Many Responsibilities):**
    *   Quản lý danh sách Icon (Treeview, Lọc, Tìm kiếm, Sắp xếp).
    *   Quản lý Form chi tiết Icon (Thêm, Sửa, Xóa, Validation).
    *   Quản lý Danh mục (Categories Treeview, Form, CRUD logic).
    *   Quản lý Thư viện Ảnh (Image Library Listbox, Search, File selection, Import).
    *   Hiển thị hình thu nhỏ (Preview Zone, Tooltips).
    *   Quản lý trạng thái giao diện (View, Add, Edit, Loading states).
    *   Xử lý bất đồng bộ, hàng đợi render (Incremental Queue cho Treeview).
    *   Xử lý logic Database cục bộ (Sync to DB, rollback).

2.  **Kích thước khổng lồ (Size & Complexity):**
    *   Gần 2000 dòng code. Các method UI building (`_build_icons_panel`, `_build_categories_panel`) rất dài và chứa nhiều widget lồng nhau phức tạp.
    *   Chứa hàng chục thuộc tính trạng thái nội bộ (`_is_dirty`, `_current_state`, `_cat_current_state`, các biến `_after_id` cho debounce, timer).

3.  **Mức độ kết dính thấp (Low Cohesion) và Phụ thuộc cao (High Coupling):**
    *   Logic của phần Danh mục (Category) hoàn toàn độc lập với phần Hình ảnh (Image Library) nhưng lại bị nhồi nhét chung vào một class.
    *   UI và Business Logic dính liền nhau (ví dụ: `_on_save`, `_on_sync`). Mặc dù trước đó đã có nỗ lực tách Model, Frame này vẫn tự xử lý form validation, kiểm tra sự tồn tại của file/node, và các quyết định rollback.

## 3. Đề xuất Hướng Refactor (Giải pháp tháo gỡ)

Mục tiêu chính là phân rã `IconManagerFrame` thành các Component (hoặc Sub-frame) nhỏ hơn, chuyên biệt hơn. `IconManagerFrame` sẽ chỉ đóng vai trò là một "Container" điều phối các thành phần con.

### Bước 1: Tách các Sub-Components (Giao diện)
*   **`IconTreeComponent`**: Quản lý riêng phần Left Master List (Cây Icon, thanh tìm kiếm, filter, phân trang/hàng đợi render).
*   **`IconFormComponent`**: Quản lý riêng phần nhập liệu chi tiết (Tên, Key, Tooltip, Nút Browse, Fallback).
*   **`CategoryManagerComponent`**: Tách toàn bộ logic và giao diện của tab "Quản lý Danh mục Icon" ra thành một class/file riêng biệt.
*   **`ImageLibraryComponent`**: Quản lý listbox hình ảnh, tìm kiếm ảnh và nút Import.
*   **`IconPreviewComponent`**: Quản lý khung hiển thị ảnh thu nhỏ, tooltip warning và empty state.
*   **`ActionToolBarComponent`**: (Tuỳ chọn) Quản lý dãy nút Add, Edit, Delete, Sync, Refresh.

### Bước 2: Tách Controller / State Manager (Logic)
*   Tạo một `IconManagerController` (nếu chưa có hoặc mở rộng từ Model hiện tại) để xử lý hoàn toàn các thao tác: Save, Delete, Sync, Validation.
*   UI Form sẽ không gọi trực tiếp `IconService` nữa mà gọi qua `Controller`.
*   Trạng thái của Form (`ADD`, `EDIT`, `VIEW`) nên được quản lý bởi một State Machine nhỏ, khi State thay đổi sẽ phát event (qua EventBus hoặc Callback) để các Component con tự bật/tắt (enable/disable) widget của mình, thay vì dùng hàm `set_form_state` khổng lồ đi chỉnh sửa từng ô text một.

### Bước 3: Tối ưu hoá luồng dữ liệu (Data Flow)
*   Sử dụng cơ chế Event-driven hoặc Pub/Sub giữa các component.
    *   *Ví dụ:* Khi click vào `IconTreeComponent`, component này phát ra sự kiện `OnIconSelected(icon_id)`.
    *   `IconManagerFrame` nhận sự kiện, ra lệnh cho Controller tải dữ liệu.
    *   Controller tải xong, phát dữ liệu cho `IconFormComponent` và `IconPreviewComponent` tự cập nhật hiển thị.

## 4. Lộ trình thực hiện (Gợi ý cho các Sprint tiếp theo)

*   **Prompt 1 (Sub-task 1):** Tách `CategoryManagerComponent`. Vì phần Danh mục hoạt động khá độc lập, tách nó ra sẽ lập tức giảm tải ~300 dòng code.
*   **Prompt 2 (Sub-task 2):** Tách `ImageLibraryComponent` và `IconPreviewComponent`.
*   **Prompt 3 (Sub-task 3):** Tách `IconTreeComponent` và thuật toán Incremental Queue ra file riêng.
*   **Prompt 4 (Sub-task 4):** Lắp ráp `IconFormComponent`, thiết lập Event/Callback để liên kết các component lại thông qua `IconManagerFrame` gọn nhẹ (Facade/Mediator).

## Kết luận
Việc refactor `IconManagerFrame` là cực kỳ cấp thiết để đảm bảo tính khả trì (maintainability). Quá trình này nên được chia nhỏ và test kỹ lưỡng từng component sau khi bóc tách để không làm gãy vỡ (break) luồng dữ liệu phức tạp hiện có.
