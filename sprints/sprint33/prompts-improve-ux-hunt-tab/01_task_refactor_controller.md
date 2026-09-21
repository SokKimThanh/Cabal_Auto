# Task 1: Nâng cấp Data Layer cho Skill Panel

## Bối cảnh (Context)
Hiện tại `SkillPanelController` và cấu hình quản lý kỹ năng đang gắn liền với khái niệm 4 slot combo và 2 slot buff cứng ngắc. Để phục vụ cho thiết kế dạng thanh thời gian (Timeline Strip) linh hoạt, Controller cần hỗ trợ trả về và cập nhật danh sách kỹ năng dưới dạng mảng (list) không giới hạn số lượng (mặc định vẫn khởi tạo 4-2 nhưng cho phép mở rộng/thêm bớt dễ dàng).

## Yêu cầu (Requirements)
1. Chỉnh sửa `ui/controllers/skill_panel_controller.py`.
2. Tạo các phương thức mới: `get_combo_sequence() -> list` và `get_buff_sequence() -> list` thay cho việc gọi từng slot.
3. Đảm bảo luồng lưu trữ (save) vẫn tương thích với cấu trúc của `hunt_config.json` hoặc tự động migration sang cấu trúc mảng nếu cần thiết.

## Rủi ro (Risks & Pitfalls)
- **Tương thích ngược:** Các panel khác hoặc logic core (như `SkillRuntimeService`) có thể đang đọc trực tiếp dữ liệu theo kiểu cũ. Phải kiểm tra kỹ các lời gọi API.
- Cần chú ý đến việc bind dữ liệu (Data binding) trong Tkinter.

## Unit Tests Cần Thêm (Unit Tests to Add)
- Thêm test trong `tests/ui/controllers/test_skill_panel_controller.py` để verify việc trả về chuỗi sequence mảng.
- Test khả năng thêm mới hoặc xóa một kỹ năng khỏi chuỗi (Sequence mutation).
## Phụ lục (Important Note from Review):
- Hệ thống `SkillPresetController` (hàm `set_skill_slot`) bản chất đã là mảng mở rộng (`while len(...) <= position`). Do đó Task 1 này khá đơn giản, chủ yếu là bạn chỉ cần viết các hàm `get_combo_slots()` và `get_buff_slots()` ở `SkillPanelController` để Timeline Strip gọi và render ra vòng lặp thay vì fix cứng `range(4)`.
