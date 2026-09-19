# Cập nhật UI Helpers để Hỗ trợ Discovery (Phase 2/4)

## Mục tiêu
Sửa đổi các hàm tạo UI (UI Helpers) để bắt buộc nhận metadata từ Frames và tiến hành đăng ký tự động (Runtime Discovery) vào Registry.

## Khối lượng công việc ước tính
< 30 phút

## Yêu cầu chi tiết

### 1. Sửa đổi `ui/components/icon_button.py`
- Cập nhật hàm `create_icon_button` (và các hàm tương tự như `create_add_button` nếu có).
- Thêm 2 tham số **BẮT BUỘC** (không có giá trị default `None`):
  - `module: str`
  - `screen: str`
- Tham số `element_id` vẫn giữ nguyên.
- (Khuyến nghị dùng Type Hints rõ ràng để IDE có thể báo lỗi nếu lập trình viên quên truyền).

### 2. Thực hiện Runtime Registration
Bên trong các hàm helper này, ngay sau khi tạo xong widget, thực thi đoạn code sau:
```python
if element_id and module and screen:
    from lib.events.ui_element_registry import UIElementRegistry, UIElementDescriptor
    desc = UIElementDescriptor(
        element_id=element_id,
        module=module,
        screen=screen,
        element_type="button"
    )
    UIElementRegistry.instance().register(desc)
```
- Lưu metadata vào widget để tham chiếu sau này (nếu cần): `widget._element_id = element_id` (v.v..).

## Rủi ro tiềm ẩn (Cần tránh)
- **Lỗi Circular Import:** Hãy cẩn thận khi import `UIElementRegistry` vào file UI component. Nếu xảy ra vòng lặp import, hãy import cục bộ (local import) bên trong thân hàm.
- **Thiếu tương thích ngược (Backward Compatibility):** Hiện tại có hàng chục chỗ đang gọi `create_icon_button` mà chưa truyền `module` và `screen`. Tùy thuộc vào chiến lược của dự án, bạn có thể phải cấp giá trị default tạm thời (VD: `"unknown"`) và thêm `TODO` để refactor dần, HOẶC chủ động sửa các form hiện tại nếu lượng file ít. Hãy ưu tiên không làm gãy build của toàn dự án.
