# Khởi tạo Cấu trúc Dữ liệu và Registry (Phase 1/4)

## Mục tiêu
Xây dựng nền tảng dữ liệu (`UIElementDescriptor`, `CommonUI`) và Singleton Registry để lưu trữ siêu dữ liệu (metadata) của các thành phần giao diện.

## Khối lượng công việc ước tính
< 30 phút

## Yêu cầu chi tiết

### 1. Định nghĩa Data Structures
Tạo file (hoặc đặt ở vị trí phù hợp trong `lib/events/`):
- `UIElementDescriptor`: Là một `@dataclass` chứa 4 trường: `element_id` (str), `module` (str), `screen` (str), `element_type` (str).
- `CommonUI`: Là một `Enum` kế thừa từ `str` chứa các ID dùng chung để tránh hardcode (VD: `BTN_SAVE = "btn_save"`, `BTN_CANCEL = "btn_cancel"`).

### 2. Xây dựng UIElementRegistry (Singleton)
- Tạo class `UIElementRegistry` đóng vai trò là một Singleton.
- **Cấu trúc lưu trữ:** Sử dụng một dictionary: `_elements: dict[tuple[str, str, str], UIElementDescriptor]`. Khóa (Key) là tuple `(module, screen, element_id)`.
- **Phương thức `register(descriptor: UIElementDescriptor)`:**
  - Lấy key từ descriptor.
  - Gán vào dictionary `_elements[key] = descriptor`.
  - **Lưu ý Idempotent:** Cố tình ghi đè nếu key đã tồn tại. Không sử dụng mảng (`list`) và không raise Exception để tránh lỗi crash khi UI bị render lại nhiều lần.
- **Phương thức `get_all() -> list[UIElementDescriptor]`:** Trả về toàn bộ values của dictionary.
- **Phương thức `clear()`:** Xóa toàn bộ dictionary (dành cho Unit tests).

## Rủi ro tiềm ẩn (Cần tránh)
- **Memory Leak:** Tuyệt đối không lưu trữ object `Widget` (như `ttk.Button`) vào Registry. Chỉ lưu `UIElementDescriptor` (dạng string/primitive).
- **Lỗi Singleton State:** Quên viết hàm `clear()` sẽ làm các test case phía sau bị rò rỉ trạng thái, dẫn đến false positives.
