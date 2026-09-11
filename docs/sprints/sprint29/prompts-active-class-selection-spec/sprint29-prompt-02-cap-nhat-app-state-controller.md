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
- **Bước 1: Kiểm tra thay đổi chưa lưu (Unsaved Changes).**
  - Kiểm tra trạng thái lưu bằng cách đọc cờ `self.root.has_unsaved_changes`.
  - Nếu cờ này là `True` (CÓ thay đổi chưa lưu), gọi `tkinter.messagebox.askyesno` để hiển thị hộp thoại xác nhận. Sử dụng `i18n_t("warning_title", ns=I18N_GLOBAL)` cho tiêu đề và text lấy từ `i18n_t("msg_unsaved_class_change", ns=I18N_GLOBAL)` cho nội dung thông báo.
  - Nếu người dùng chọn "No" (Không), lập tức `return False` để từ chối đổi class.
- **Bước 2: Cập nhật biến trạng thái.**
  - Nếu người dùng đồng ý (chọn "Yes") hoặc không có unsaved changes:
  - Gán `self.root._current_class_id = class_id`.
- **Bước 3: Đặt lại trạng thái Unsaved.**
  - Gọi phương thức `self._clear_unsaved_changes()` để xóa cờ unsaved changes, tránh việc UI tiếp tục báo có thay đổi chưa lưu mặc dù đã load dữ liệu mới sạch từ DB.
- **Bước 4: Tự động load Preset.**
  - Gọi phương thức `self.load_preset_for_class(class_id)` để tải lại preset mặc định cho class mới.
- **Bước 5: Trả kết quả.**
  - `return True` để báo hiệu cho UI biết là đổi class thành công để update giao diện.

## 5. Tiêu chí Hoàn thành (Acceptance Criteria / Verification)
1. Thêm hàm thành công mà không gây lỗi syntax.
2. Có thể mô phỏng gọi `app_state.set_current_class(2)` và quan sát biến `_current_class_id` thay đổi, `load_preset_for_class` được gọi.
3. Nếu giả lập trạng thái `self.root.has_unsaved_changes = True`, sẽ hiện popup `askyesno` hỏi xác nhận bằng đúng ngôn ngữ i18n và xử lý đúng logic khi người dùng chọn Yes/No.
4. Đảm bảo `self._clear_unsaved_changes()` được gọi đúng lúc.
