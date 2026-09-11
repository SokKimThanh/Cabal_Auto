# Session 2: Cập nhật AppStateController cho Thay đổi Class

## 1. Tiêu đề & Mục tiêu
- **Tiêu đề:** Phát triển API quản lý State Class trong AppStateController.
- **Mục tiêu:** Cung cấp một phương thức an toàn để UI yêu cầu thay đổi `class_id`, đồng thời xử lý logic ngăn chặn mất dữ liệu chưa lưu. Task này cần hoàn thành dưới 30 phút.

## 2. Ngữ cảnh (Context)
Dựa theo tài liệu đặc tả:
> Cập nhật `AppStateController`: Bổ sung phương thức `set_current_class(class_id)`.
> Rủi ro (Pitfalls): Xóa nhầm dữ liệu chưa lưu (Unsaved Changes). Cần kiểm tra cờ "unsaved changes" trước khi thực hiện đổi class, prompt người dùng nếu cần.

## 3. Các file cần thay đổi
1. `ui/controllers/app_state_controller.py`

## 4. Hướng dẫn thực hiện chi tiết

### 4.1. Thêm phương thức `set_current_class(class_id: int) -> bool`
- Bổ sung hàm này vào `AppStateController`.
- **Bước 1: Kiểm tra thay đổi.**
  - Đọc trạng thái lưu (có thể thông qua hàm kiểm tra unsaved trên `self.root` hoặc manager tương ứng).
  - Nếu CÓ thay đổi chưa lưu, gọi `messagebox.askyesno` (hoặc custom dialog) với text lấy từ `t("msg_unsaved_class_change")`.
  - Nếu người dùng chọn "No" (Không), lập tức `return False` để từ chối đổi class.
- **Bước 2: Cập nhật biến trạng thái.**
  - Nếu người dùng đồng ý hoặc không có unsaved changes:
  - Gán `self.root._current_class_id = class_id`.
- **Bước 3: Tự động load Preset.**
  - Gọi phương thức load preset mặc định cho class (vd: `self.load_preset_for_class(class_id)` hoặc phương thức tương đương quản lý reset state).
- **Bước 4: Trả kết quả.**
  - `return True` để báo hiệu cho UI biết là đổi class thành công để update giao diện.

## 5. Tiêu chí Hoàn thành (Acceptance Criteria / Verification)
1. Thêm hàm thành công mà không gây lỗi syntax.
2. Có thể mô phỏng gọi `app_state.set_current_class(2)` và quan sát biến `_current_class_id` thay đổi.
3. Nếu giả lập trạng thái "unsaved", sẽ hiện popup hỏi xác nhận (nếu chạy trong môi trường GUI) bằng đúng ngôn ngữ i18n.
