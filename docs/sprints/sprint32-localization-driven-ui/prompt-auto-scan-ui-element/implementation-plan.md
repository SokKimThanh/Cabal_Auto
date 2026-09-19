# Implementation Plan: Auto-Scan UI Elements (Runtime Discovery)

Dựa trên Proposal kiến trúc "Runtime UI Element Registry", dưới đây là bản thiết kế Implementation Plan chi tiết dành cho lập trình viên để triển khai Sprint này một cách an toàn và dứt điểm.

## 1. Danh sách file cần tạo/chỉnh sửa

### File tạo mới (New Files)
- `lib/events/ui_element_registry.py`: Chứa lõi kiến trúc bao gồm Data classes, Enum và Singleton Registry.
- `tests/unit/events/test_ui_element_registry.py`: Chứa các unit tests cho Registry.

### File cần chỉnh sửa (Modified Files)
- `ui/components/icon_button.py`: Sửa đổi helper `create_icon_button` để thu thập metadata runtime.
- `ui/views/icon_manager_frame.py`: Tích hợp Registry vào giao diện Icon Manager (load data & save data).
- `ui/views/build_manager_frame.py` (và 1-2 frames mẫu khác): Thêm các class attributes `MODULE_NAME`, `SCREEN_NAME` và áp dụng Enum để làm form chuẩn (Reference Template).

## 2. Các Class / Structure cần tạo

Trong file `lib/events/ui_element_registry.py`:

**1. `UIElementDescriptor` (Dataclass):**
```python
@dataclass
class UIElementDescriptor:
    element_id: str
    module: str
    screen: str
    element_type: str
```

**2. `CommonUI` (Enum):**
```python
class CommonUI(str, Enum):
    BTN_SAVE = "btn_save"
    BTN_CANCEL = "btn_cancel"
    BTN_ADD = "btn_add"
    BTN_DELETE = "btn_delete"
    # ...
```

**3. `UIElementRegistry` (Singleton Class):**
- Biến: `_instance`, `_elements: dict[tuple[str, str, str], UIElementDescriptor]`.
- Phương thức:
  - `register(descriptor: UIElementDescriptor)`: Thêm vào dict. Log warning nếu key đã tồn tại.
  - `get_all() -> list[UIElementDescriptor]`: Trả về toàn bộ data.
  - `clear()`: Xóa sạch dict (dùng cho Unit tests).

## 3. Interfaces / API thay đổi

### UI Helper
- Hàm `create_icon_button(parent, icon_name, ...)`:
  - **Thay đổi ngầm (Implicit):** Tự động truy xuất `getattr(parent, "MODULE_NAME", "unknown")` và `getattr(parent, "SCREEN_NAME", "unknown")`.
  - Không phá vỡ (Break) API cũ. Bất kỳ Form nào chưa có 2 biến này sẽ rơi vào giá trị default `"unknown"` và bỏ qua việc thu thập (backward compatibility).

### Icon Manager Controller / Frame
- Combobox `combo_usage_element`:
  - **Dữ liệu hiển thị (Display Data):** Trước đây chỉ hiển thị `element_id`. Nay hiển thị dạng `{module}/{screen}/{element_id}` để có context rành mạch.
  - **Hành vi Save:** Khi user chọn string dài `build_manager/settings/btn_save` và bấm "Save", hàm `_on_add_usage()` **phải** chẻ (split) chuỗi này, lấy phần tử cuối cùng (`btn_save`) để gửi xuống Database. Database vẫn giữ nguyên schema (chỉ lưu Element ID gốc).

## 4. Unit Tests cần bổ sung

Trong file `tests/unit/events/test_ui_element_registry.py`:

- `test_registry_is_singleton`: Kiểm tra `UIElementRegistry.instance()` luôn trả về cùng 1 bộ nhớ.
- `test_registry_idempotent_registration`: Đăng ký 2 lần cùng một ID. Kiểm tra số lượng item không bị nhân đôi, không xảy ra Exception crash.
- `test_registry_metadata_only`: Đăng ký thành công, lấy ra giá trị trả về đúng kiểu dữ liệu nguyên thủy (thỏa mãn quy định Architectural Decision - tuyệt đối không lưu Widget state).
- `test_registry_clear`: Test hàm `clear()` hoạt động đúng để các test case khác không bị rò rỉ dữ liệu chéo (data cross-pollution).

## 5. Rủi ro khi Rollout (Risks & Mitigations)

1. **Rủi ro rò rỉ bộ nhớ (Memory Leak):**
   - **Tác động:** Nếu ai đó sửa code Registry và lưu `widget=ttk.Button`, Tkinter sẽ không giải phóng được widget khi đóng màn hình, app càng xài càng nặng.
   - **Phòng ngừa:** Được giới hạn chặt chẽ trong Proposal. Team Lead lúc Code Review phải soi kỹ không cho bất kỳ reference nào của Tkinter đi vào file `ui_element_registry.py`.

2. **Rủi ro Database lưu sai định dạng (Mismatch Format):**
   - **Tác động:** Nếu Combobox hiển thị `a/b/btn_save` mà lúc Save lại bê nguyên chuỗi đó xuống DB. Hệ thống EventBus lúc render sẽ đi tìm nút có tên `a/b/btn_save` thay vì `btn_save` => Mapping hỏng toàn tập.
   - **Phòng ngừa:** Tại hàm `_on_add_usage()` của Icon Manager, phải có logic `element_id = selected_string.split("/")[-1]` (hoặc parser tương tự) trước khi gọi API lưu xuống database.

3. **Rủi ro gãy build hàng loạt (Backward Compatibility Issue):**
   - **Tác động:** Việc gắn thêm mandatory param vào UI Helper sẽ làm hỏng hàng trăm file giao diện cũ.
   - **Phòng ngừa:** Sử dụng `parent` đã có sẵn trong helper. Dùng `getattr` với giá trị mặc định ("unknown"). Nếu giá trị là "unknown" thì âm thầm bypass qua, không bắt buộc đăng ký vào Registry. Các Form được refactor dần dần về sau.

## 6. Acceptance Criteria (Tiêu chí hoàn thành)

✅ **AC1:** Có class `UIElementRegistry` hoạt động theo mô hình Singleton, có unit tests cover đầy đủ tính idempotent và clear.
✅ **AC2:** Component `create_icon_button` tự động đăng ký ID, Module, Screen vào Registry khi Widget được vẽ lên (nếu Parent có cung cấp metadata). Không làm gãy build các form cũ.
✅ **AC3:** Nếu form đăng ký cùng một button 2 lần, Terminal in ra Warning Log nhưng UI không bị crash.
✅ **AC4:** Trong form Icon Manager, Combobox hiển thị danh sách từ cả DB lẫn Registry gộp lại. Khi chọn và Save, hệ thống parse và chỉ lưu ID gốc xuống Database thành công.
✅ **AC5:** Ít nhất 1 form chính (VD: `BuildManagerFrame`) được refactor để sử dụng `MODULE_NAME`, `SCREEN_NAME` và áp dụng Enum `CommonUI`.