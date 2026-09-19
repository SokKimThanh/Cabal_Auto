# Proposal: Đăng ký UI Element ID Runtime (Runtime UI Element Registry)

## Bối cảnh và Vấn đề
Hiện tại, trong form **Quản lý Nơi Dùng (Usages)** của Icon Manager, khi người dùng muốn Gắn (Map) một icon vào một button trên giao diện, họ cần nhập chính xác **Element ID** của component đó (VD: `btn_settings`, `btn_build_manager`).
Để hỗ trợ UX, hệ thống hiện dùng Combobox hiển thị danh sách các ID **đã từng được map** trong cơ sở dữ liệu (`icon_usages` table).
Tuy nhiên, nếu một button mới được thêm vào UI (chưa được map icon bao giờ), Element ID đó sẽ không xuất hiện trong Combobox. Người dùng sẽ phải tự mở code ra để đọc ID và gõ tay, rất dễ dẫn đến lỗi sai chính tả (typo), làm hỏng ánh xạ của icon.

## Mục tiêu (Runtime Discovery)
- Giải quyết bài toán **Discovery**: "Hệ thống hiển thị đúng những gì đang thực sự tồn tại trên UI". Nếu một component ẩn do phân quyền, nó không nên xuất hiện.
- Cung cấp cơ chế **Runtime Registry** để tự động thu thập Element ID và Metadata khi các thành phần giao diện (UI widget) thực sự được render.
- Đặt nền móng dữ liệu đủ tốt (UIElementDescriptor) để mở đường cho các phân hệ tương lai (Localization, Permission, Audit) mà không over-engineering.

## Giải pháp Đề xuất: Runtime Discovery + UIElementDescriptor

Đây là giải pháp cân bằng nhất giữa giá trị và chi phí (Plan B) - giải quyết dứt điểm pain point hiện tại mà không biến thành một framework quá phức tạp.

### 1. Định nghĩa UIElementDescriptor
Lưu trữ thông tin chi tiết thay vì chuỗi string phẳng để dễ dàng phân loại và tránh trùng lặp:
```python
from dataclasses import dataclass

@dataclass
class UIElementDescriptor:
    element_id: str
    module: str
    screen: str
    element_type: str
```

### 2. Sửa đổi UI Helpers để thu thập Metadata (Lúc Runtime)
Các hàm tạo UI (như `create_icon_button`) sẽ nhận tham số `parent` và `element_id`. Helper sẽ tự động đọc `MODULE_NAME` và `SCREEN_NAME` từ `parent` để tránh việc lặp code (DRY), giúp code sạch hơn và ít typo hơn:

```python
class SettingsFrame(ttk.Frame):
    MODULE_NAME = "build_manager"
    SCREEN_NAME = "settings"

    def _create_ui(self):
        # Hàm create_icon_button tự đọc parent.MODULE_NAME và parent.SCREEN_NAME
        self.btn_save = create_icon_button(
            parent=self,
            element_id="btn_save" # Xem phần 3 để tối ưu hardcode
        )
```

### 3. Chuẩn hóa ID (Strong Typing)
Khuyến nghị **bắt buộc** đối với các shared/common IDs phải được định nghĩa dưới dạng Enum để tránh typo và hỗ trợ Automation:
```python
class CommonUI(str, Enum):
    BTN_SAVE = "btn_save"
    BTN_CANCEL = "btn_cancel"
    # Lập trình viên sẽ gọi: element_id=CommonUI.BTN_SAVE
```
Tuy nhiên, đối với các ID đặc thù (specific IDs) như `build_mgr_btn_generate_report`, vẫn có thể sử dụng string để tránh việc maintain một file Enum khổng lồ cho toàn bộ project (1000+ buttons).

### 4. Xây dựng Singleton Registry
Tạo một lớp quản lý danh sách in-memory:
- **Vị trí:** `lib/events/ui_element_registry.py`.
- **Cấu trúc lưu trữ:** `dict[tuple[str, str, str], UIElementDescriptor]`. Key sẽ là Tuple `(module, screen, element_id)`.
- **Hành vi Idempotent (An toàn với Lifecycle):** Khi hàm `register()` được gọi, nếu Tuple key đã tồn tại, hệ thống sẽ **log warning** thay vì im lặng ignore:
  ```
  [UIRegistry] Duplicate registration: build_manager/settings/btn_save
  ```
  Điều này giúp hệ thống không bị crash (Fail-Fast) hay rò rỉ bộ nhớ khi UI Tkinter render lại nhiều lần, đồng thời developer vẫn biết chuyện gì đang xảy ra.

### 5. Architectural Decision: Metadata Registry (State Classification)
**UIElementRegistry là Metadata Registry.**
Nó chỉ lưu mô tả của UI Element. Nó **tuyệt đối không lưu**:
- Widget references
- Widget state
- Runtime values
- Visibility status

Nếu lưu state tại đây (VD: `descriptor.widget = button` hoặc `descriptor.visible = True`), Registry sẽ biến thành nơi chứa state, và đó là con đường dẫn tới memory leak thật sự.

### 6. Tích hợp vào Icon Manager
Tại class `IconManagerFrame`:
- Lấy danh sách từ Registry và hiển thị Combobox dưới dạng format có ngữ cảnh: `f"{desc.module}/{desc.screen}/{desc.element_id}"`.

## Rủi ro và Điểm yếu

1. **Phụ thuộc vào User Journey:**
   - Vì là "Runtime Discovery", một button chỉ được thu thập nếu User/Admin **đã mở màn hình đó ra**.
   - *Đánh giá:* Đây là trade-off chấp nhận được. Trải nghiệm thực tế của Admin là họ luôn nhìn thấy nút bấm trên UI rồi mới quay sang Icon Manager để gán icon. Nếu dùng "Static Discovery" (quét toàn bộ file) thì sẽ thu thập cả những nút mà user hiện tại không có quyền truy cập, gây nhiễu loạn thông tin.

2. **Vấn đề Kế thừa (Inheritance):**
   - Nếu `AdvancedSettingsFrame` kế thừa `SettingsFrame` (có chung nút save), nút save có thể bị đăng ký 2 lần dưới 2 screen name khác nhau.
   - *Khắc phục:* Trong cấu trúc `dict` của Registry, Tuple key khác nhau sẽ sinh ra 2 entry. Trong phạm vi Icon Manager, điều này vô hại. Sẽ cần xử lý ở Phase xây dựng Audit Tree sau này.

## So sánh Combobox vs Tree Component (Khẳng định lại)

- **Search vs Audit:** Thao tác map icon là "Tìm kiếm" (Tôi cần nút Save của Build Manager -> gõ Combobox). Nó không phải là "Khám phá" (Tìm xem hệ thống có bao nhiêu module/nút).
- **Kết luận:** Giữ nguyên **Combobox + Auto-complete** cho màn hình nhập liệu. Nhường Tree Component cho màn hình "UI Explorer / Audit" trong tương lai.

## Lộ trình Thực thi & Ước lượng (Roadmap & Estimates)

Dự án được bóc tách thành các giai đoạn rõ ràng để kiểm soát khối lượng công việc và rủi ro over-engineering.

### 🟢 Sprint Hiện tại: Runtime Registry + UIElementDescriptor (Plan B)
- **Công việc:** Tạo `UIElementDescriptor`, class `UIElementRegistry` (dict), sửa các hàm helper truyền metadata, tích hợp Combobox Icon Manager và viết unit test.
- **Giá trị:** Giải quyết ngay lập tức pain point Typo của Icon Manager và thiết lập metadata chuẩn mực.
- **Ước lượng thời gian:** **~3 ngày làm việc** (± 1 ngày).

### 🟡 Sprint Tiếp theo: UI Audit Tree
- **Công việc:** Xây dựng màn hình UI Explorer dạng Tree (Module -> Screen -> Element). Hỗ trợ audit Missing Icon, Missing Translation, Usage Count.
- **Giá trị:** Cung cấp công cụ quản trị (Governance) mạnh mẽ cho Admin.
- **Ước lượng thời gian:** **1 - 2 tuần**.

### 🔴 Tương lai xa (6-12 tháng tới): Application UI Metadata Platform (Plan C)
- **Công việc:** Khi nhu cầu Automation, Permission phức tạp tăng cao, tiến hành nghiên cứu Framework Reflection, Class Decorators (`@ui_screen`, `@ui_element`), Auto-discovery tĩnh lúc startup.
- **Đánh giá:** Đây là một thay đổi kiến trúc lớn, mang tính chất "Governance Framework" chứ không còn là "Discovery". Không nên nhồi nhét vào giai đoạn hiện tại.
- **Ước lượng thời gian:** **2 - 4 tuần**.
