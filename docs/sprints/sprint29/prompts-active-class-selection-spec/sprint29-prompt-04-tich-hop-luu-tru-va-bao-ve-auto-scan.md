# Session 4: Tích hợp Lưu trữ và Bảo vệ Khỏi Auto-scan

## 1. Tiêu đề & Mục tiêu
- **Tiêu đề:** Đồng bộ State Chọn Class với Cấu hình hệ thống và Thread Auto-scan.
- **Mục tiêu:** Lưu trạng thái class mà người dùng đã chọn để lần sau mở ứng dụng vẫn giữ nguyên, đồng thời khóa giao diện (combobox) khi bot đang chạy để tránh xung đột dữ liệu. Task này cần hoàn thành dưới 30 phút.

## 2. Ngữ cảnh (Context)
Dựa theo tài liệu đặc tả:
> Cập nhật cấu hình lưu trữ (`hunt_cfg`) để ghi nhớ `class_id` cuối cùng người dùng đã chọn để lần sau mở app không bị reset về 1.
> Xung đột State với Auto-Scan: Khóa (Disable) dropdown chọn class nếu Bot/Auto-hunt đang ở trạng thái chạy (Active). Chỉ cập nhật class_id từ hệ thống auto-scan nếu bot chưa chạy, hoặc đưa ra cảnh báo (Soft warning).

## 3. Các file cần thay đổi
1. `ui/controllers/app_state_controller.py` (hoặc file config manager tương ứng).
2. `ui/panels/skill_panel.py` (cập nhật state cho combobox).

## 4. Hướng dẫn thực hiện chi tiết

### 4.1. Lưu trữ `class_id` vào Config
- Khi `AppStateController.set_current_class(class_id)` thành công, hãy đảm bảo giá trị này được lưu vào file config (thường thông qua một service như `ConfigManager` hoặc dictionary `hunt_cfg`).
- Ví dụ: `config.set("hunt_settings", "last_active_class_id", class_id)` và lưu ra đĩa (JSON/ini).
- Tại hàm khởi tạo của `AppStateController`, thay vì fix cứng `self.root._current_class_id = 1`, hãy đọc từ config. Nếu không có thì mới gán mặc định là 1.

### 4.2. Khóa UI trong quá trình Bot chạy (Auto-scan)
- Ứng dụng hiện có biến trạng thái kiểm tra bot chạy (vd: `app.hunt_thread` is not None hoặc `app.click_running`).
- Đăng ký một event hoặc bổ sung vào hàm tick loop (nếu có) trên `SkillPanel`:
  - `if app_state.is_bot_running():`
    - `class_combobox.configure(state="disabled")`
  - `else:`
    - `class_combobox.configure(state="readonly")` (chế độ chọn bình thường).
- Điều này loại bỏ hoàn toàn khả năng người dùng nhấn đổi class giữa lúc auto-bot đang tính toán combo.

### 4.3. Xử lý Warning khi Auto-scan trả về Class Mismatched
- Ở module quản lý scan màn hình (nơi nhận kết quả class_id từ ảnh):
  - Trước khi ghi đè, kiểm tra: `if scanned_class_id != app_state.get_current_class():`
  - Ghi log cảnh báo hoặc push notification nhẹ (tuỳ thuộc framework log UI đang có), thay vì ngầm ngầm ép đổi class.
  - Sử dụng chuỗi translation `t("msg_class_scan_mismatch")`.

## 5. Tiêu chí Hoàn thành (Acceptance Criteria / Verification)
1. Đóng app mở lại, `class_id` được giữ nguyên giá trị cuối cùng.
2. Bấm nút "Start" bot (chạy auto-hunt), Combobox chọn Class bị làm mờ (disabled), không cho phép click vào.
3. Khi bot nhận diện ra một class khác thực tế, log/thông báo cảnh báo i18n sẽ xuất hiện mà không làm sập ứng dụng.
