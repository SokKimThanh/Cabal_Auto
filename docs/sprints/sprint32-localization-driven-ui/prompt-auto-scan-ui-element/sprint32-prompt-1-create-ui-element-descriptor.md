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
  - Nếu key đã tồn tại, tiến hành **log warning** (VD: `[UIRegistry] Duplicate registration: ...`). Không raise Exception để tránh lỗi crash (Fail-Fast) khi UI bị render lại nhiều lần.
  - Gán/ghi đè vào dictionary `_elements[key] = descriptor`.
- **Phương thức `get_all() -> list[UIElementDescriptor]`:** Trả về toàn bộ values của dictionary.
- **Phương thức `clear()`:** Xóa toàn bộ dictionary (dành cho Unit tests).

## Rủi ro tiềm ẩn (Cần tránh)
- **Vi phạm Kiến trúc (State Classification):** `UIElementRegistry` là **Metadata Registry**. Nó chỉ được lưu mô tả của UI Element (các trường dữ liệu nguyên thủy). Tuyệt đối **không** lưu trữ:
  - Widget references (như `ttk.Button`)
  - Widget state
  - Runtime values
  - Visibility status
  Nếu lưu các thông tin này, Registry sẽ bị biến thành nơi chứa state, gây ra memory leak.
- **Lỗi Singleton State:** Quên viết hàm `clear()` sẽ làm các test case phía sau bị rò rỉ trạng thái, dẫn đến false positives.
