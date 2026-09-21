# Kế Hoạch Triển Khai (Implementation Plan): UI Element Registry & Icon Manager Cải Tiến

Dựa trên đề xuất kiến trúc (UI_REGISTRY_PROPOSAL.md), dưới đây là kế hoạch chi tiết để triển khai hệ thống quản lý giao diện, bao gồm cơ sở dữ liệu mới và cải thiện các luồng người dùng trên `Icon Manager`. Kế hoạch được thiết kế cẩn thận để đảm bảo tính mở rộng, tránh lỗi rò rỉ bộ nhớ Tkinter và dễ dàng duy trì bảo trì về sau.

## 1. Files to Modify (Các tệp cần sửa đổi)
- `lib/db/database_setup.py`: Thêm script tạo bảng `ui_elements`.
- `lib/db/services/icon_service.py` (hoặc tạo một `UIElementService` mới): Thêm logic để truy xuất, tạo, và quản lý các `ui_elements`.
- `lib/db/services/icon_sync_manager.py`: Thêm logic đồng bộ tự động `UIElementRegistry` xuống bảng `ui_elements` vào thời điểm khởi chạy.
- `src/ui/screens/icon_manager/layout.py` (hoặc file chứa UI Icon Manager):
  - Di dời `btn_refresh` và `btn_sync` từ tab details lên Top Action Bar (vùng content cha).
  - Bổ sung thêm cột hiển thị trạng thái Độc Quyền (Exclusive Flags - 🔒/🌐) vào `ttk.Treeview`.
- `src/ui/screens/icon_manager/controller.py`: Cập nhật logic để hỗ trợ lưu và cập nhật trạng thái "Exclusive" khi render lên UI, nhận sự kiện từ top action bar.
- `lib/events/ui_element_registry.py`: (Tuỳ chọn) Bổ sung thuộc tính `is_exclusive` cho class `UIElementDescriptor` để hỗ trợ quét và lưu DB sau này.

## 2. Classes to Create (Các lớp cần tạo mới)
- `UIElementService` (tuỳ chọn nếu không gộp vào IconService): Class phụ trách CRUD dữ liệu trong bảng `ui_elements`.
- `IconPickerWindow` (kế thừa từ `tk.Toplevel`): Lớp xây dựng một Popup Dialog.
  - Giao diện gồm thanh tìm kiếm debounced (chống giật).
  - Khung Canvas lưới (Grid Layout) cuộn để hiển thị danh sách các biểu tượng thu nhỏ (thumbnails) với hiệu năng cao (lazy loading / caching).
- `ContextActionHelper`: Một class hoặc tập hợp các hàm helper tiện ích giúp gắn (bind) sự kiện Right-Click (Chuột phải) vào các Component (`CommonUI`) để gọi nhanh `IconPickerWindow`.

## 3. Interface Changes (Các thay đổi Giao diện)
- **Top Action Bar trong Icon Manager:** Giao diện quản lý Icon không còn giấu các tính năng Làm Mới và Đồng Bộ dưới các tab cụ thể. Chúng được đẩy lên một thanh nằm ngang phía trên Grid, độc lập với Tab.
- **TreeView Data Columns:** Bảng chọn UI Element (bên trái của Icon Manager) sẽ có thêm cột Icon/Text biểu thị mức độ Độc Quyền.
- **Fast-mapping Popup:** Màn hình popup nhỏ hiển thị các biểu tượng sẵn có trong thư viện. Popup cung cấp trải nghiệm nhấn lưu ngay, không cần chuyển tab.

## 4. Unit Tests to Add (Các kiểm thử cần bổ sung)
- **Database Tests (`test_ui_element_db.py`):**
  - Kiểm tra vi phạm Composite Unique Key (module, screen, element_id).
  - Kiểm tra tính tương thích khi join/map dữ liệu giữa `icon_usages` và `ui_elements` mới.
- **Service/Sync Tests (`test_sync_manager.py`):**
  - Giả lập việc một element mới được đăng ký thông qua `UIElementRegistry` trong thời gian chạy (runtime), sau đó kiểm tra xem dữ liệu có tự động điền (upsert) xuống cơ sở dữ liệu một cách an toàn không.
- **Headless UI Tests (`test_icon_picker_dialog.py`):**
  - Khởi tạo Mock Window và tạo một `IconPickerWindow` kiểm tra debounce search bar, và các callback nhận giá trị chọn.
  - Chú ý: Dùng `xvfb-run` hoặc biến môi trường `DISPLAY=:99` để chạy trên pipeline.

## 5. Rollout Risks (Các rủi ro triển khai)
- **Tkinter Memory Leaks:** Dialog `IconPickerWindow` cần phải có logic huỷ và quản lý tài nguyên Image (biến lưu giữ tham chiếu hình ảnh để chống GC của Python) hợp lý, nếu không người dùng mở và đóng liên tục có thể gây đầy RAM.
- **UI Thread Blocking:** Trong quá trình Đồng bộ từ Registry xuống DB lúc khởi động, nếu số lượng Element lớn (hàng trăm component), có thể dẫn tới độ trễ (delay) khi boot ứng dụng. Cần áp dụng Bulk Insert/Upsert thay vì for loop Insert.
- **Lỗi đệ quy (Infinite Recursion) ở Event loop:** Trong các màn hình Split-pane phức tạp, việc chọn một element ở bảng này tự động filter bảng kia có thể gây bắn event `<<TreeviewSelect>>` tuần hoàn. Cần sử dụng biến theo dõi trạng thái `_current_selection` thay vì gắn cờ boolean tạm thời.
- **Sự khác biệt Hệ điều hành:** Event chuột phải ở Windows thường là `<Button-3>`, còn MacOS/Linux cũ có thể là `<Button-2>` hoặc `<Button-3>`. Helper cần bind chuẩn xác đa nền tảng.

## 6. Acceptance Criteria (Tiêu chí nghiệm thu)
1. **Database Schema:** CSDL có bảng `ui_elements` với đầy đủ ràng buộc khóa ngoại/composite key và không vi phạm dữ liệu cũ của `icon_usages`.
2. **Layout Improvement:** `btn_sync` và `btn_refresh` đã nằm ngoài tab content và hoạt động ổn định bất kể người dùng đang chọn tab nào. Treeview có cột chỉ định Exclusive/Common.
3. **Fast-Mapping Flow:** Người dùng có thể click chuột phải vào một element (VD: `btn_save`), bảng `IconPickerWindow` hiển thị. Nhấp chọn một icon sẽ đóng Dialog, lưu thông tin vào DB, và tự động Refresh màn hình gốc để áp dụng icon mới ngay lập tức mà không gây gián đoạn công việc (crash hoặc mất focus các vùng khác).
4. **Code Quality:** Không tồn tại mix `pack()` và `grid()` trên cùng parent frame; Tất cả biến tham chiếu tới Tkinter Images trong Dialog phải được lưu lại (VD: `self._image_refs`) để tránh lỗi mất hình ảnh.