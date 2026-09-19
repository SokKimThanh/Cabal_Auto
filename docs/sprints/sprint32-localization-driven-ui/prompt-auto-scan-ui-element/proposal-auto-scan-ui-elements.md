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

## Kết quả đạt được (Expected Outcomes)
Sau khi triển khai thành công Runtime Registry, hệ thống sẽ đạt được:
1. **Trải nghiệm người dùng (UX) liền mạch:** Admin/Dev không cần phải mở IDE hay tra cứu mã nguồn để tìm `element_id` của các nút mới.
2. **Đảm bảo toàn vẹn dữ liệu:** Xóa bỏ hoàn toàn rủi ro lỗi chính tả (typo) khi nhập ID bằng tay, giúp các event (ví dụ như `IconUpdatedEvent`) gửi chính xác đến các UI element đang chờ.
3. **Mở rộng dễ dàng (Scalability):** Bất cứ khi nào một component mới được thêm vào ứng dụng thông qua các hàm Helper chuẩn, nó sẽ tự động được hệ thống Icon Manager nhận diện ngay lập tức.

## Nghiên cứu mở rộng: Có nên sử dụng Tree Component để chọn Element ID thay vì Combobox?

Hiện tại, việc chọn `element_id` để map Icon đang được thực hiện qua **Combobox phẳng (Flat List) kết hợp Auto-complete (Search)**. Câu hỏi đặt ra là: *Có nên chuyển sang dùng Tree Component (dạng danh mục phân cấp) không?*

### Phân tích

**Phương án 1: Combobox (Hiện tại & Đề xuất)**
- **Ưu điểm:** Tốc độ chọn cực nhanh. Người dùng chỉ cần gõ vài từ khóa (ví dụ "save", "build") là danh sách được lọc ngay lập tức. UX phù hợp với những người đã biết (hoặc nhớ mang máng) tên tính năng. Tốn ít không gian UI.
- **Nhược điểm:** Nếu không tuân thủ quy tắc đặt tên (`prefix`), danh sách sẽ trở nên lộn xộn. Người dùng không có cái nhìn tổng quan về hệ thống ("Màn hình này có bao nhiêu nút?").

**Phương án 2: Tree Component (Phân cấp)**
Giả sử ta cấu trúc ID theo dạng: `module_name` -> `screen_name` -> `element_id`.
- **Ưu điểm:** Cho cái nhìn tổng quan tuyệt vời. Người dùng có thể click mở rộng từng node (VD: *UI Module > Icon Manager > btn_save*) để khám phá các UI element mà không cần nhớ từ khóa. Quản lý cấu trúc rành mạch.
- **Nhược điểm:**
  - *Tốc độ chậm:* Phải thao tác nhiều click chuột (expand node, tìm, select).
  - *Độ phức tạp kỹ thuật (High Complexity):* Registry hiện tại chỉ nhận chuỗi phẳng. Để dựng được Tree, `create_icon_button` sẽ phải nhận cấu trúc phức tạp hơn (VD: truyền cả `module_name`, `screen_name` vào hàm helper), làm giảm sự tiện dụng khi lập trình UI.
  - *Tốn diện tích UI:* Treeview chiếm nhiều chỗ trên màn hình hơn so với một thanh Combobox nhỏ gọn.

### Kết luận & Đề xuất
- **Trong ngắn hạn và trung hạn:** **Không nên chuyển sang Tree Component** cho thao tác *Chọn/Map ID*. Việc dùng **Combobox + Auto-complete** kết hợp quy tắc đặt tên (Namespace ID) là sự cân bằng tốt nhất giữa tốc độ phát triển và UX.
- **Tương lai (Tính năng mở rộng):** Tree Component có thể được cân nhắc sử dụng trong một màn hình báo cáo "UI Element Audit" riêng biệt (để xem tổng quan toàn bộ UI của App), chứ không nên đặt ở form nhập liệu (Add Usage) vì sẽ làm chậm luồng thao tác (flow) của người quản trị.
