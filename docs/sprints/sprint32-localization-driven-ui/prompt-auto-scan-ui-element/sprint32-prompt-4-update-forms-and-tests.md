# Cập nhật Forms Mẫu và Unit Tests (Phase 4/4)

## Mục tiêu
Áp dụng cơ chế mới vào một số Form thực tế để chứng minh tính hiệu quả của Runtime Discovery, đồng thời viết Unit Test bảo vệ kiến trúc.

## Khối lượng công việc ước tính
< 30 phút

## Yêu cầu chi tiết

### 1. Cập nhật các UI Frame mẫu
Chọn 2-3 form quan trọng (Ví dụ: `SettingsFrame`, `BuildManagerFrame`).
- Thêm Class Attributes: `MODULE_NAME = "..."`, `SCREEN_NAME = "..."`.
- Đảm bảo các lệnh gọi `create_icon_button` đã được pass `parent=self` và `element_id=...` để helper tự động đọc 2 attribute trên.
- **Áp dụng Strong Typing:** Thay thế các chuỗi ID cứng (hardcode) thuộc nhóm shared/common (ví dụ: Save, Cancel, Add) bằng cách sử dụng bắt buộc Enum như `CommonUI.BTN_SAVE`. Đối với các ID mang tính chất đặc thù riêng biệt của màn hình (VD: `build_mgr_btn_generate_report`), tiếp tục sử dụng chuỗi string để tránh làm file Enum bị quá tải.

### 2. Viết Unit Test cho Registry
Tạo file `tests/events/test_ui_element_registry.py`:
- Viết test `test_registry_singleton`: Đảm bảo `instance()` luôn trả về cùng một object.
- Viết test `test_registry_idempotent`: Gọi `register()` 2 lần với cùng một tham số (cùng tuple key), đảm bảo `len(get_all()) == 1` (Không bị duplicate, không bị crash).
- Gọi `UIElementRegistry.instance().clear()` trong `setUp` và `tearDown` để chống rò rỉ state.

## Rủi ro tiềm ẩn (Cần tránh)
- **Thiếu Mocking trong UI Tests:** Nếu bạn viết thêm test cho Frame, việc khởi tạo UI có thể kích hoạt Registry. Đảm bảo các mock/patch hoạt động tốt để không làm hỏng các test case cũ.
- **Quên Cleanup:** Việc bỏ sót hàm `clear()` trong các bài test Registry sẽ dẫn đến hậu quả nghiêm trọng khi chạy toàn bộ test suite trên CI/CD, do các test sau sẽ nhận được metadata rác từ test trước.
