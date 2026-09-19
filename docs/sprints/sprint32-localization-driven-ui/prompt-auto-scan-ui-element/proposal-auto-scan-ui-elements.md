# Proposal: Đăng ký UI Element ID Runtime (Runtime UI Element Registry)

## Bối cảnh và Vấn đề
Hiện tại, trong form **Quản lý Nơi Dùng (Usages)** của Icon Manager, khi người dùng muốn Gắn (Map) một icon vào một button trên giao diện, họ cần nhập chính xác **Element ID** của component đó (VD: `btn_settings`, `btn_build_manager`).
Để hỗ trợ UX, hệ thống hiện dùng Combobox hiển thị danh sách các ID **đã từng được map** trong cơ sở dữ liệu (`icon_usages` table).
Tuy nhiên, nếu một button mới được thêm vào UI (chưa được map icon bao giờ), Element ID đó sẽ không xuất hiện trong Combobox. Người dùng sẽ phải tự mở code ra để đọc ID và gõ tay, rất dễ dẫn đến lỗi sai chính tả (typo), làm hỏng ánh xạ của icon.

## Mục tiêu
- Cung cấp một cơ chế **Runtime Registry** để tự động thu thập các Element ID và Metadata khi các thành phần giao diện (UI widget) được khởi tạo.
- Tích hợp Registry này vào màn hình Icon Manager, giúp Combobox chứa được danh sách đầy đủ các UI Elements (bao gồm cả những element chưa lưu vào CSDL) để người dùng có thể chọn thay vì gõ tay.
- Đặt nền móng vững chắc từ ngày đầu tiên để Registry này trở thành **Source of Truth** (Nguồn chân lý) về UI Metadata cho các phân hệ khác (Localization, Permission, Analytics) trong tương lai.

## Giải pháp Đề xuất: Runtime Memory Registry với UIElementDescriptor

Thay vì chỉ lưu trữ các ID dưới dạng mảng chuỗi phẳng (có nguy cơ trùng lặp cao và nghèo nàn thông tin), hệ thống sẽ sử dụng Object để lưu trữ Metadata ngay từ Sprint đầu tiên. Điều này giúp ngăn chặn Technical Debt và định hình chuẩn mực code ngay từ đầu.

### 1. Định nghĩa UIElementDescriptor
```python
from dataclasses import dataclass

@dataclass
class UIElementDescriptor:
    element_id: str
    module: str
    screen: str
    element_type: str
```

### 2. Nguồn cung cấp Metadata và Tự động suy diễn (Auto-derivation)
Để đảm bảo Developer Experience (DX) tốt nhất và tuân thủ nguyên tắc DRY (Don't Repeat Yourself), metadata (`module`, `screen`) sẽ **không cần khai báo thủ công** mà được **suy diễn tự động (Auto-derived)** từ cấu trúc của Framework (thông qua Reflection/Inspect).

**Kiến trúc Đề xuất:**
- Một lớp `BaseFrame` sẽ tự động phân tích (parse) tên class (VD: `SettingsFrame` -> `settings`) và thư mục chứa file (VD: `ui/views/build_manager/` -> `build_manager`) trong phương thức `__init__` để tự động gán hai thuộc tính ẩn `self._module` và `self._screen`.
- Lập trình viên UI khi viết code layout **chỉ cần truyền ID** cho các hàm UI Helper. UI Helper sẽ tự động trích xuất metadata từ tham số `parent`.

```python
class SettingsFrame(BaseFrame):
    # Không cần khai báo MODULE_NAME hay SCREEN_NAME thủ công

    def _create_ui(self):
        # UI Helper tự động nhận diện module="build_manager" và screen="settings" từ 'self'
        self.btn_save = create_icon_button(
            parent=self,
            element_id="btn_save"
        )
```
- **Cơ chế ép buộc (Enforcement):** Nếu UI Helper nhận thấy tham số `parent` không cung cấp đủ metadata (ví dụ dùng `tk.Frame` thường thay vì `BaseFrame`), hàm Helper sẽ tự động quăng lỗi (Exception) để ép buộc Lập trình viên phải tuân thủ kiến trúc chuẩn.

### 3. Xây dựng Singleton Registry
Tạo một lớp quản lý danh sách in-memory:
- **Vị trí:** `lib/events/ui_element_registry.py`.
- **Cấu trúc lưu trữ:** `dict[tuple[str, str, str], UIElementDescriptor]`. Key sẽ là Tuple `(module, screen, element_id)` để đảm bảo tính duy nhất.
- **Phương thức:** `register(descriptor: UIElementDescriptor)` và `get_all() -> list[UIElementDescriptor]`.

### 4. Đăng ký Element khi khởi tạo
Bên trong hàm `create_icon_button` (và các helper liên quan), sau khi widget được tạo, hệ thống sẽ tự động gọi:
`UIElementRegistry.instance().register(UIElementDescriptor(element_id=..., module=..., screen=..., type="button"))`

### 5. Tích hợp vào Icon Manager
Tại class `IconManagerFrame`:
- Khi render dữ liệu cho Combobox, dữ liệu sẽ được format từ Descriptor: `f"{desc.module}/{desc.screen}/{desc.element_id}"`.
- Điều này cung cấp bối cảnh tuyệt vời cho người quản trị khi tìm kiếm.

## So sánh các phương pháp (Tại sao lại chọn Runtime Registry)

| Tiêu chí | Runtime Registry (Đề xuất) | Quét tĩnh AST (Tùy chọn cũ bị loại bỏ) |
| :--- | :--- | :--- |
| **Độ phức tạp** | Thấp (In-memory dict). | Rất cao (cần viết script phân tích code Python). |
| **Bảo trì** | Code Python đơn giản, IDE hỗ trợ auto-complete. | Nếu cấu trúc code thay đổi, script AST dễ bị vỡ. |
| **Khuyết điểm** | Phụ thuộc vào User Journey (Xem chi tiết ở phần Rủi ro). | Đòi hỏi phải chạy script build ra JSON thủ công trước khi commit, dễ quên. |

## Rủi ro và Điểm yếu cần chú ý

Khi triển khai giải pháp Runtime Registry này, đội ngũ cần đặc biệt lưu ý các điểm sau:

1. **Vấn đề rò rỉ bộ nhớ (Memory Leak):**
   - Registry **tuyệt đối không được** lưu trữ tham chiếu (reference) đến đối tượng Widget thực tế. Nó chỉ được phép lưu `UIElementDescriptor`. Nếu lưu widget, Garbage Collector của Python sẽ không thể giải phóng bộ nhớ.

2. **Xử lý Xung đột định danh (ID Collision) & Cơ chế Fail-Fast:**
   - Việc dùng khóa `(module, screen, element_id)` giải quyết được xung đột giữa các màn hình khác nhau (Ví dụ: 2 nút `btn_save` ở 2 màn hình).
   - **Đảm bảo Unique ID trong cùng một Screen:** Nếu Developer vô tình gán cùng một `element_id` cho 2 widget *bên trong cùng một màn hình*, hàm `register()` sẽ kiểm tra sự tồn tại của khóa này. Nếu trùng, hệ thống **bắt buộc quăng ra Exception (Fail-Fast)** (VD: `UIElementCollisionError`). Điều này sẽ làm crash ứng dụng ngay trong lúc Developer đang code/test màn hình đó, buộc họ phải sửa ID lập tức trước khi commit.

3. **Vấn đề Isolated Testing:**
   - Việc sử dụng Singleton lưu trạng thái toàn cục sẽ khiến các unit test bị rò rỉ state sang nhau.
   - Bắt buộc phải xây dựng hàm `UIElementRegistry.clear()` và gọi nó trong quá trình `teardown` của các kịch bản test.

4. **Sự phụ thuộc vào User Journey (Vấn đề UX lớn nhất):**
   - Hiện tại, Registry thu thập ID khi widget hoặc màn hình được render. Điều này dẫn đến trải nghiệm khó đoán.
     - VD: Admin chưa mở Macro Manager -> Registry thiếu `macro/main/btn_run`. Khi vào Icon Manager, Combobox sẽ không hiển thị nút này.
   - **Giải pháp:** Xây dựng cơ chế đăng ký tĩnh hoặc đăng ký toàn bộ danh sách `UIElementDescriptor` ngay lúc application startup (thông qua Application Bootstrapper hoặc `FrameRegistry`), đảm bảo Registry luôn đầy đủ dữ liệu ngay từ giây đầu tiên khởi động.

## Nghiên cứu mở rộng: Tree Component vs Combobox cho UI Element ID

Hiện tại, việc chọn Element ID đang được thực hiện qua **Combobox kết hợp Search**. Câu hỏi đặt ra là: *Có nên chuyển sang dùng Tree Component (dạng danh mục phân cấp) không?*

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

## Định hướng dài hạn: Sự tiến hóa thành Application UI Metadata Registry

Việc áp dụng ngay cấu trúc `UIElementDescriptor` từ Sprint đầu tiên đã đặt nền móng vững chắc cho lộ trình kiến trúc tương lai:

- **Giai đoạn 1 (Hiện tại): UX Enhancement & Metadata Foundation**
  - Registry đóng vai trò cung cấp gợi ý (Autocomplete) cho Combobox trong Icon Manager, cải thiện trải nghiệm người dùng, chống lỗi gõ sai.

- **Giai đoạn 2: Nâng cấp thành Source of Truth**
  - Registry trở thành Nguồn chân lý (Source of Truth) cho toàn bộ cấu trúc UI của ứng dụng.
  - Các hệ thống cốt lõi khác sẽ bắt đầu tiêu thụ dữ liệu từ Registry này:
    - **Localization:** `lang_manager.translate(module, screen, id)`
    - **Permission:** `permission_service.hide(module, screen, id)`
    - **Analytics:** `track_click(module, screen, id)`
    - **Automation:** Script auto-test có thể tra cứu Registry để biết chính xác UI nằm ở đâu.

- **Giai đoạn 3: Xây dựng UI Explorer (Audit Tool)**
  - Xây dựng một màn hình dạng Tree Component (Module -> Screen -> Element) độc lập.
  - Đọc dữ liệu từ Registry để cho phép quản trị viên khám phá, kiểm tra (audit) toàn bộ giao diện ứng dụng: xem trực quan phần tử nào đã có icon, phần tử nào đã được dịch thuật, phân quyền.
