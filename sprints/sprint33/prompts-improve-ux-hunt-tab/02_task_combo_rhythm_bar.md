# Task 2: Phát triển Component `ComboRhythmBar`

## Bối cảnh (Context)
Cần một phản hồi thị giác (visual feedback) để báo cho người dùng biết thuật toán `CabalComboDetector` đang hoạt động (quét và đánh trúng điểm "sweet spot").

## Yêu cầu (Requirements)
1. Tạo file `ui/components/combo_rhythm_bar.py` định nghĩa class `ComboRhythmBar` kế thừa từ `tk.Canvas` hoặc `ttk.Frame`.
2. Component cần vẽ một thanh ngang (Bar), có hiển thị vùng "Sweet Spot" (hit-zone) ở khoảng tọa độ ~0.78 (78% chiều dài).
3. Hỗ trợ phương thức `trigger_hit()` để làm lóe sáng (flash) khu vực Sweet Spot (đổi màu sang `UI.ACCENT_AMBER` rồi mờ dần về bình thường trong khoảng 200ms).

## Rủi ro (Risks & Pitfalls)
- **Tkinter After Loop:** Không dùng `time.sleep()` trong logic đổi màu. Bắt buộc gọi Centralized UIAnimationManager để thực hiện hiệu ứng mờ (fade) để không block luồng UI chính.
- **Tần suất gọi lớn:** Nếu backend gọi `trigger_hit()` liên tục, cần có cơ chế debounce hoặc bỏ qua animation mới nếu animation cũ chưa kết thúc để tránh tạo ra hàng ngàn callback `after()`.

## Unit Tests Cần Thêm (Unit Tests to Add)
- Khởi tạo headless `ComboRhythmBar` và gọi `trigger_hit()`. Đảm bảo không ném ra exception và màu sắc thay đổi đúng.