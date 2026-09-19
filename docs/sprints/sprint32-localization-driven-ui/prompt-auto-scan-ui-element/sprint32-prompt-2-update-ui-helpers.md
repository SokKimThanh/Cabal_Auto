# Cập nhật UI Helpers để Hỗ trợ Discovery (Phase 2/4)

## Mục tiêu
Sửa đổi các hàm tạo UI (UI Helpers) để bắt buộc nhận metadata từ Frames và tiến hành đăng ký tự động (Runtime Discovery) vào Registry.

## Khối lượng công việc ước tính
< 30 phút

## Yêu cầu chi tiết

### 1. Sửa đổi `ui/components/icon_button.py`
- Cập nhật hàm `create_icon_button` (và các hàm tương tự như `create_add_button` nếu có).
- Cần có tham số `parent` (thường đã có sẵn) và tham số `element_id`.
- Helper sẽ được cập nhật để **tự động đọc** các thuộc tính `MODULE_NAME` và `SCREEN_NAME` từ đối tượng `parent` thay vì yêu cầu lập trình viên truyền thủ công mỗi lần gọi hàm.

### 2. Thực hiện Runtime Registration
Bên trong các hàm helper này, ngay sau khi tạo xong widget, thực thi đoạn code tương tự như sau (bạn cần điều chỉnh linh hoạt theo code thực tế):
```python
if element_id and parent:
    # Trích xuất từ parent
    module = getattr(parent, "MODULE_NAME", "unknown")
    screen = getattr(parent, "SCREEN_NAME", "unknown")

    if module != "unknown" and screen != "unknown":
        from lib.events.ui_element_registry import UIElementRegistry, UIElementDescriptor
        desc = UIElementDescriptor(
            element_id=element_id,
            module=module,
            screen=screen,
            element_type="button"
        )
        UIElementRegistry.instance().register(desc)
```
- Lưu metadata vào widget để tham chiếu sau này (nếu cần): `widget._element_id = element_id`.

## Rủi ro tiềm ẩn (Cần tránh)
- **Lỗi Circular Import:** Hãy cẩn thận khi import `UIElementRegistry` vào file UI component. Nếu xảy ra vòng lặp import, hãy import cục bộ (local import) bên trong thân hàm.
- **Xử lý thiếu thuộc tính ở Parent:** Đảm bảo sử dụng `getattr(parent, "MODULE_NAME", default)` an toàn. Hiện tại có hàng chục form cũ gọi hàm tạo UI mà class của chúng chưa định nghĩa 2 biến `MODULE_NAME` và `SCREEN_NAME`. Việc dùng `getattr` có default string ("unknown") giúp giữ **tương thích ngược**, không làm crash (gãy build) toàn bộ project. Hãy ưu tiên tính ổn định.
