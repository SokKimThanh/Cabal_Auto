# Proposal: Đăng ký UI Element ID Runtime (Runtime UI Element Registry)

## Bối cảnh và Vấn đề
Hiện tại, trong form **Quản lý Nơi Dùng (Usages)** của Icon Manager, khi người dùng muốn Gắn (Map) một icon vào một button trên giao diện, họ cần nhập chính xác **Element ID** của component đó (VD: `btn_settings`, `btn_build_manager`).
Để hỗ trợ UX, hệ thống hiện dùng Combobox hiển thị danh sách các ID **đã từng được map** trong cơ sở dữ liệu (`icon_usages` table).
Tuy nhiên, nếu một button mới được thêm vào UI (chưa được map icon bao giờ), Element ID đó sẽ không xuất hiện trong Combobox. Người dùng sẽ phải tự mở code ra để đọc ID và gõ tay, rất dễ dẫn đến lỗi sai chính tả (typo), làm hỏng ánh xạ của icon.

## Mục tiêu Kiến trúc (Tầm nhìn dài hạn)
- Cung cấp một cơ chế **Registry** để thu thập tự động toàn bộ Element ID và Metadata của ứng dụng.
- Đảm bảo Registry hoạt động ổn định bất chấp vòng đời của UI (UI Lifecycle - tạo ra và hủy đi nhiều lần).
- Giải quyết triệt để sự phụ thuộc vào **User Journey** (không bắt buộc người dùng phải mở màn hình đó thì mới có dữ liệu).
- Xây dựng **Source of Truth** (Nguồn chân lý) về UI Metadata tĩnh cho toàn bộ hệ thống (Localization, Permission, Analytics, Automation).

## Giải pháp Đề xuất: Static Metadata Registry (Đăng ký tại thời điểm Load Module)

Nếu chúng ta đăng ký ID vào Registry bên trong các hàm render UI (ví dụ lúc gọi `create_icon_button`), hệ thống sẽ dính **Technical Debt nghiêm trọng**: Mỗi khi UI bị destroy và render lại (ví dụ đổi tab), hệ thống sẽ đăng ký lại ID đó, gây rò rỉ bộ nhớ hoặc lỗi Fail-Fast vô cớ.
Giải pháp triệt để là **tách bạch hoàn toàn Metadata (Tĩnh) khỏi Rendering (Động)** bằng cơ chế Static Registration (Decorators/Metaclasses) tại thời điểm Python nạp (load) module.

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

### 2. Sử dụng Decorator để khai báo Metadata tĩnh
Thay vì ép UI Helpers thực hiện đăng ký lúc chạy, chúng ta định nghĩa UI Elements ngay trên cấu trúc Class (Declarative) bằng Decorator. Việc đăng ký diễn ra ngay khi Python đọc file code (Import time).

```python
from lib.events.ui_element_registry import ui_screen, ui_element

@ui_screen(module="build_manager", screen="settings")
class SettingsFrame(BaseFrame):

    # Metadata được đăng ký tĩnh vào Registry ngay khi file này được import
    @ui_element(element_id="btn_save", type="button")
    def _create_save_btn(self):
        # UI Helper chỉ lo việc vẽ (render), không cần làm nhiệm vụ đăng ký nữa
        self.btn_save = create_icon_button(parent=self, element_id="btn_save")
```
- **Lợi ích:** Giải quyết 100% bài toán "Phụ thuộc User Journey". Chỉ cần ứng dụng khởi động (bootstrapper import các class UI), toàn bộ Metadata của ứng dụng đã nằm gọn trong Registry mà không cần bất kỳ màn hình nào phải thực sự render lên màn hình!

### 3. Chuẩn hóa ID bằng Enum (Chống Hardcode)
Để đảm bảo an toàn cho các tác vụ Auto-test hoặc Refactor diện rộng trong tương lai, các ID dùng chung không nên là String hardcode dễ gãy:
```python
class CommonUI(str, Enum):
    BTN_SAVE = "btn_save"
    BTN_CANCEL = "btn_cancel"

# Khai báo: @ui_element(element_id=CommonUI.BTN_SAVE, type="button")
```

### 4. Xây dựng Singleton Registry
Tạo một lớp quản lý danh sách in-memory:
- **Vị trí:** `lib/events/ui_element_registry.py`.
- **Cấu trúc lưu trữ:** `dict[tuple[str, str, str], UIElementDescriptor]`. Key sẽ là Tuple `(module, screen, element_id)` để đảm bảo tính duy nhất.
- **Phương thức:** `get_all() -> list[UIElementDescriptor]`.

### 5. Tích hợp vào Icon Manager
Tại class `IconManagerFrame`:
- Khi render dữ liệu cho Combobox, dữ liệu sẽ được lấy từ Singleton Registry và format: `f"{desc.module}/{desc.screen}/{desc.element_id}"`.

## Rủi ro và Điểm yếu (Đã được khắc phục bởi Static Registration)

1. **Vấn đề rò rỉ bộ nhớ & Lifecycle UI (Đã giải quyết):**
   - Bằng cách đăng ký qua Class Decorator (lúc load file code), việc tạo/hủy UI (destroy frame) hoàn toàn không ảnh hưởng đến Registry. Registry luôn sạch sẽ và ổn định.

2. **Xử lý Xung đột định danh (ID Collision) & Cơ chế Fail-Fast (Bảo vệ tuyệt đối):**
   - Khóa lưu trữ là `(module, screen, element_id)`. Nếu Developer vô tình khai báo 2 hàm có cùng `@ui_element(element_id="btn_save")` trong cùng một Class, Decorator sẽ quăng lỗi `UIElementCollisionError` **ngay lúc ứng dụng vừa bật lên** (Crash at startup). Lỗi được phát hiện ngay lập tức mà không cần đợi người dùng bấm vào màn hình đó.

3. **Sự phụ thuộc vào User Journey (Đã giải quyết):**
   - Combobox của Icon Manager sẽ luôn chứa 100% dữ liệu ngay từ giây đầu tiên ứng dụng khởi động, vì toàn bộ Decorator đã chạy trong lúc Import các Module.

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

Việc áp dụng kiến trúc **Static Metadata Registry** thông qua Decorators đã xây dựng một nền tảng chuẩn mực cho 3 năm tới:

- **Giai đoạn 1 (Hiện tại): UX Enhancement & Metadata Foundation**
  - Cung cấp dữ liệu hoàn chỉnh 100% (không sót do User Journey) cho Combobox trong Icon Manager.

- **Giai đoạn 2: Nâng cấp thành Source of Truth**
  - Registry trở thành Nguồn chân lý tĩnh (Static Source of Truth) cho toàn bộ cấu trúc UI của ứng dụng.
  - Các hệ thống cốt lõi sẽ tiêu thụ dữ liệu này cực kỳ an toàn:
    - **Localization:** `lang_manager.translate(module, screen, id)`
    - **Permission:** `permission_service.hide(module, screen, id)`
    - **Automation:** Script test dựa vào ID tĩnh để thao tác (không sợ gãy cấu trúc).

- **Giai đoạn 3: Xây dựng UI Explorer (Audit Tool)**
  - Đọc dữ liệu tĩnh từ Registry để dựng màn hình Tree Component (Module -> Screen -> Element) độc lập.
  - Cho phép Audit: màn hình nào đang thiếu localization, nút bấm nào đang chưa có icon, tất cả được báo cáo minh bạch ngay khi vừa mở app.
