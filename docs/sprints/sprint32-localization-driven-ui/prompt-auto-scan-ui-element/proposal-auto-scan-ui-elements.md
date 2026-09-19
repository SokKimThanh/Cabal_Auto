# Proposal: Đăng ký UI Element ID Runtime (Runtime UI Element Registry)

## Bối cảnh và Vấn đề
Hiện tại, trong form **Quản lý Nơi Dùng (Usages)** của Icon Manager, khi người dùng muốn Gắn (Map) một icon vào một button trên giao diện, họ cần nhập chính xác **Element ID** của component đó (VD: `btn_settings`, `btn_build_manager`).
Để hỗ trợ UX, hệ thống hiện dùng Combobox hiển thị danh sách các ID **đã từng được map** trong cơ sở dữ liệu (`icon_usages` table).
Tuy nhiên, nếu một button mới được thêm vào UI (chưa được map icon bao giờ), Element ID đó sẽ không xuất hiện trong Combobox. Người dùng sẽ phải tự mở code ra để đọc ID và gõ tay, rất dễ dẫn đến lỗi sai chính tả (typo), làm hỏng ánh xạ của icon.

## Mục tiêu
- Cung cấp một cơ chế **Runtime Registry** để tự động thu thập các Element ID khi các thành phần giao diện (UI widget) được khởi tạo.
- Tích hợp Registry này vào màn hình Icon Manager, giúp Combobox chứa được danh sách đầy đủ các UI Elements (bao gồm cả những element chưa lưu vào CSDL) để người dùng có thể chọn thay vì gõ tay.

## Giải pháp Đề xuất: Runtime Memory Registry

### 1. Sửa đổi các UI Helpers (Thêm tham số `element_id`)
Các hàm tạo UI trong `ui/components/icon_button.py` (như `create_icon_button`, `create_add_button`, `create_icon_label`...) hiện tại chưa hỗ trợ tham số `element_id`.
**Thực thi:**
- Thêm tham số `element_id: Optional[str] = None` vào signature của các hàm này.
- Khi tạo widget, lưu trữ ID đó vào một thuộc tính ẩn: `widget._element_id = element_id` (tương tự như cách ta đang lưu `text_key` và `tooltip_key`).

### 2. Xây dựng Singleton Registry
Tạo một lớp quản lý danh sách các Element ID in-memory:
- **Vị trí:** `lib/events/ui_element_registry.py` (hoặc bên trong `ui/helpers/`).
- **Chức năng:** Sử dụng `set` để lưu trữ các ID không trùng lặp.
- **Phương thức:** `register(element_id: str)` và `get_all() -> list[str]`.

### 3. Đăng ký Element khi khởi tạo
Bên trong hàm `create_icon_button` (và các helper liên quan), sau khi widget được tạo, nếu có truyền `element_id`, hệ thống sẽ tự động gọi:
`UIElementRegistry.instance().register(element_id)`

### 4. Tích hợp vào Icon Manager
Tại class `IconManagerFrame` (trong `ui/views/icon_manager_frame.py`):
- Phương thức `_load_all_usage_ids()` hiện đang truy vấn trực tiếp từ CSDL (`SELECT DISTINCT ui_element_id FROM icon_usages...`).
- Sửa đổi phương thức này: Lấy danh sách ID từ cơ sở dữ liệu, sau đó **merge (kết hợp)** với danh sách từ `UIElementRegistry.instance().get_all()`.
- Loại bỏ các ID rỗng (`None` hoặc `""`).
- Sắp xếp (sort) lại và nạp vào biến `self._available_usage_ids`.

## So sánh các phương pháp (Tại sao lại chọn Runtime Registry)

| Tiêu chí | Runtime Registry (Đề xuất) | Quét tĩnh AST (Tùy chọn cũ bị loại bỏ) |
| :--- | :--- | :--- |
| **Độ phức tạp** | Rất thấp (chỉ là in-memory set). | Rất cao (cần viết script phân tích code Python). |
| **Bảo trì** | Code Python đơn giản, gắn liền với UI Helpers. | Nếu cấu trúc code thay đổi, script AST dễ bị vỡ. |
| **Khuyết điểm** | Chỉ đăng ký các màn hình đã được render (nghĩa là user phải mở màn hình đó rồi thì ID mới vào Registry). | Đòi hỏi phải chạy script build ra JSON thủ công trước khi commit, dễ quên. |

*(Tuy Runtime Registry chỉ thu thập được các ID của các UI đã render lên màn hình, nhưng xét trên luồng sử dụng thông thường của Admin/Dev, họ thường nhìn thấy button trên UI rồi mới quay sang Icon Manager để cấu hình. Do đó, trade-off này là hoàn toàn hợp lý).*

## Kế hoạch Thực thi Kỹ thuật (Cho các Sprint sau)
1. Thêm class `UIElementRegistry` (Singleton).
2. Sửa `create_icon_button` và các hàm helper liên quan (thêm `element_id`).
3. Sửa `IconManagerFrame._load_all_usage_ids()` để merge dữ liệu từ Registry.
4. (Tùy chọn) Rà soát lại một số màn hình quan trọng, truyền `element_id` cho các button chính để kiểm thử.

## Rủi ro và Điểm yếu cần chú ý

Khi triển khai giải pháp Runtime Registry này, đội ngũ cần đặc biệt lưu ý các điểm sau:

1. **Vấn đề rò rỉ bộ nhớ (Memory Leak):**
   - Registry **tuyệt đối không được** lưu trữ tham chiếu (reference) đến đối tượng Widget thực tế. Nó chỉ được phép lưu chuỗi ký tự (`str`) của `element_id`. Nếu lưu widget, Garbage Collector của Python sẽ không thể giải phóng bộ nhớ khi các cửa sổ/tab UI bị đóng.

2. **Xung đột định danh (ID Collision):**
   - Vì danh sách được gộp chung thành một mảng phẳng (phục vụ Combobox), nếu hai module khác nhau vô tình gán cùng một ID (VD: `btn_save`), người dùng sẽ không phân biệt được ID nào thuộc màn hình nào.
   - **Quy tắc:** Lập trình viên phải sử dụng tiền tố (prefix) theo namespace khi khai báo ID (VD: `icon_mgr_btn_save`, `build_mgr_btn_save`).

3. **Vấn đề Isolated Testing:**
   - Việc sử dụng Singleton (hoặc class attributes) lưu trạng thái toàn cục sẽ khiến các unit test bị rò rỉ state sang nhau.
   - Bắt buộc phải xây dựng hàm `UIElementRegistry.clear()` và gọi nó trong quá trình `teardown` của các kịch bản test.

4. **Hạn chế Lazy-Load:**
   - Những widget nằm trong các module lười tải (lazy load) hoặc ở các màn hình chưa từng được mở ra sẽ không được đẩy vào Registry. Do đó, người dùng (Admin) cần phải "lướt qua" màn hình đó ít nhất một lần để khởi tạo widget trước khi vào Icon Manager để gán Icon. Đây là một trade-off có chủ đích và có thể chấp nhận được so với sự phức tạp của quét tĩnh AST.
