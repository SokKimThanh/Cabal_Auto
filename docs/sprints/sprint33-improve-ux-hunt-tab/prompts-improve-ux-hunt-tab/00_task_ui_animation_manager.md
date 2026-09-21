# Task 0: Xây dựng nền tảng `UIAnimationManager`

## Bối cảnh (Context)
Trước khi nâng cấp các UI component (như Thanh HP chạy mượt, Thanh Combo nháy sáng), chúng ta phải giải quyết vấn nạn phân mảnh Animation Loop. Nếu mỗi Widget tự gọi `self.after(16)` sẽ gây tranh chấp tài nguyên (Resource Contention) của Tkinter Main Thread, dẫn tới UI bị giật lag và lỗi tính toán máu.

## Yêu cầu (Requirements)
1. Tạo class `UIAnimationManager` (Singleton) tại `lib/ui/animation_manager.py`.
2. Lớp này chỉ duy trì **1 vòng lặp `.after(16)` duy nhất** (tương đương ~60fps) cho toàn bộ ứng dụng.
3. Cung cấp API `register_tween(target_id: str, widget, start_val, end_val, duration_ms, update_func)`:
   - `target_id`: Identifier duy nhất cho đối tượng cần hiệu ứng (VD: `hp_bar_canvas`).
   - Nếu `target_id` đã tồn tại đang chạy, hệ thống PHẢI tự động **Override/Cancel** tiến trình cũ và bắt đầu tiến trình mới từ giá trị hiện hành (chống lỗi thanh HP chạy giật lùi).
4. Cung cấp API `cancel_tween(target_id: str)`.
5. Đảm bảo kiểm tra `widget.winfo_exists()` bên trong update loop để không throw `_tkinter.TclError` khi UI bị tắt.

## Unit Tests Cần Thêm
- Test: Gọi `register_tween` 2 lần liên tiếp với cùng một `target_id`. Đảm bảo mảng queue chỉ chứa 1 job duy nhất (Override thành công).
- Test: Gọi khi widget giả lập đã bị destroy, đảm bảo loop không crash.