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
- **Chức năng:** Sử dụng `set` để lưu trữ các ID không trùng lặp (áp dụng cho Phase 1).
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
| **Khuyết điểm** | Phụ thuộc vào User Journey (Xem chi tiết ở phần Rủi ro). | Đòi hỏi phải chạy script build ra JSON thủ công trước khi commit, dễ quên. |

## Rủi ro và Điểm yếu cần chú ý

Khi triển khai giải pháp Runtime Registry này, đội ngũ cần đặc biệt lưu ý các điểm sau:

1. **Vấn đề rò rỉ bộ nhớ (Memory Leak):**
   - Registry **tuyệt đối không được** lưu trữ tham chiếu (reference) đến đối tượng Widget thực tế. Nó chỉ được phép lưu chuỗi ký tự (`str`) của `element_id`. Nếu lưu widget, Garbage Collector của Python sẽ không thể giải phóng bộ nhớ khi các cửa sổ/tab UI bị đóng.

2. **Xung đột định danh (ID Collision) & Quy tắc Namespace bắt buộc:**
   - Vì danh sách được gộp chung thành một mảng phẳng (phục vụ Combobox), nếu hai module khác nhau vô tình gán cùng một ID, người dùng sẽ không phân biệt được ID nào thuộc màn hình nào.
   - **Quy tắc bắt buộc:** Lập trình viên **bắt buộc** phải sử dụng tiền tố (prefix) theo namespace khi khai báo ID.
     - ❌ Sai: `btn_save`, `btn_cancel`
     - ✅ Đúng: `icon_mgr_btn_save`, `build_mgr_btn_save`, `settings_btn_save`
   - Nếu không làm chặt chẽ từ đầu, khi dự án phình to (vd 1500 elements), Registry sẽ chứa toàn ID trùng lặp vô nghĩa và mất hoàn toàn giá trị.

3. **Vấn đề Isolated Testing:**
   - Việc sử dụng Singleton (hoặc class attributes) lưu trạng thái toàn cục sẽ khiến các unit test bị rò rỉ state sang nhau.
   - Bắt buộc phải xây dựng hàm `UIElementRegistry.clear()` và gọi nó trong quá trình `teardown` của các kịch bản test.

4. **Sự phụ thuộc vào User Journey (Vấn đề UX lớn nhất):**
   - Hiện tại, Registry thu thập ID khi widget hoặc màn hình được render. Điều này dẫn đến trải nghiệm khó đoán:
     - VD: Admin mở Settings và Build Manager -> Registry có `settings_btn_save`, `build_btn_run`.
     - Tuy nhiên, Admin chưa mở Macro Manager -> Registry thiếu `macro_btn_run`.
     - Khi vào Icon Manager, Combobox hiển thị không đầy đủ. User sẽ bối rối: "Không thấy ID vì hệ thống không có hay vì mình chưa mở màn hình đó?".
   - **Giải pháp cải thiện:** Không nên đợi đến khi render widget mới đăng ký. Nên thiết kế việc gọi `register()` ngay trong phương thức `__init__` của các Frame (vd: `SettingsFrame.__init__`), hoặc tốt nhất là xây dựng cơ chế đăng ký toàn bộ `FrameRegistry` ngay lúc application startup để nạp sẵn danh sách ID, đảm bảo Registry luôn đầy đủ.

## Nghiên cứu mở rộng: Tree Component vs Combobox cho UI Element ID

Hiện tại, việc chọn `element_id` để map Icon đang được thực hiện qua **Combobox phẳng (Flat List) kết hợp Auto-complete (Search)**. Câu hỏi đặt ra là: *Có nên chuyển sang dùng Tree Component (dạng danh mục phân cấp) không?*

### Phân tích

**Phương án 1: Combobox (Hiện tại & Đề xuất)**
- **Bài toán:** Đây là một thao tác **Tìm kiếm (Search)**. User thường nghĩ: "Tôi cần gán icon cho button save của Build Manager" rồi gõ `build save`.
- **Ưu điểm:** Tốc độ chọn cực nhanh. Kết quả được lọc ngay lập tức sau vài giây gõ phím. Combobox chiến thắng tuyệt đối trong workflow nhập liệu (như Map Icon).

**Phương án 2: Tree Component (Phân cấp)**
- **Bài toán:** Đây là thao tác **Khám phá (Exploration) / Audit**. User nghĩ: "Hệ thống đang có những màn hình nào? Có bao nhiêu button? Button nào chưa được gán icon?".
- **Đặc điểm:** Cho cái nhìn tổng quan toàn hệ thống theo phân cấp (Module -> Screen -> Element). Tuy nhiên, thao tác chậm do phải click mở rộng từng node và tìm kiếm thủ công, không phù hợp cho form nhập liệu nhanh.

### Kết luận
- **Không nên thay Combobox bằng Tree** trong form Map Icon. Combobox + Search là công cụ phù hợp nhất cho bài toán tìm kiếm và nhập liệu.
- Tree Component rất mạnh, nhưng nên được dùng cho một màn hình **Audit UI / UI Explorer** riêng biệt thay vì đưa vào luồng cấu hình.

## Định hướng dài hạn: Sự tiến hóa thành UI Metadata Registry

Kiến trúc đề xuất hiện tại giải quyết tốt bài toán ngắn hạn (Sprint hiện tại) nhưng cũng mở đường cho sự phát triển dài hạn của hệ thống. Lộ trình tiến hóa dự kiến như sau:

- **Giai đoạn 1 (Hiện tại): Runtime Registry cơ bản**
  - Cấu trúc: `UIElementRegistry -> set[str]` (chỉ lưu chuỗi `element_id`).
  - Mục tiêu: Nhanh, nhỏ gọn, giải quyết trực tiếp pain point nhập liệu ID của Icon Manager.

- **Giai đoạn 2: Bổ sung Metadata (UIElementDescriptor)**
  - Cấu trúc: `UIElementRegistry -> dict[str, UIElementDescriptor]`
  - Mô tả: Thay vì lưu chuỗi phẳng, Registry sẽ lưu trữ các Object (`@dataclass`) chứa đầy đủ thông tin: `element_id`, `module`, `screen`, `element_type`.

- **Giai đoạn 3: Application UI Metadata Registry**
  - Mục tiêu: Tái sử dụng Registry làm nguồn dữ liệu "chân lý" (Source of Truth) cho nhiều phân hệ khác ngoài Icon:
    - **Localization:** `lang_manager.translate(element_id)`
    - **Permission:** `permission_service.hide(element_id)`
    - **Analytics:** `track_click(element_id)`
    - **Automation:** `click("btn_save")`

- **Giai đoạn 4: Màn hình UI Explorer (Audit Tool)**
  - Mục tiêu: Xây dựng một màn hình dạng Tree (Module -> Screen -> Element) độc lập.
  - Chức năng: Đọc dữ liệu từ `Application UI Metadata Registry` để cho phép quản trị viên khám phá, kiểm tra (audit) toàn bộ giao diện ứng dụng, xem trực quan phần tử nào đã có icon, phần tử nào đã được dịch thuật hay cấp quyền.
