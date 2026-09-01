Markdown# Session Prompt UX1: Standardize Quick Action Bar (Zone A)

Timebox: 25–30 minutes.
Priority: High – Streamline top-level game window selection, primary controls, and robust recovery.

---

## Objective
Gộp toàn bộ thanh Header và công cụ trên cùng thành Vùng A (Quick Action Bar) kích thước 1920 x 80 px. Tích hợp chọn cửa sổ, nút refresh kèm logic khôi phục cửa sổ ẩn/minimize, widget hiển thị trạng thái Bounds, nút Start/Stop có cơ chế Debounce chống double-click và bộ chuyển đổi ngôn ngữ động không mất trạng thái.

## Target Files
- Modify: `ui/action_bar.py` (hoặc frame Vùng A trong `app_gui.py`)
- Modify: `lib/ui_style.py`
- Modify: `lib/features/hunt/window_selection_service.py`
- Reference: `lib/system/window_manager.py`

---

## Implementation Details

### 1. Bố Cục Vùng A & DPI Scaling Guard (100% – 200%)
- Kích thước chuẩn: Chiều cao 80 px, chia cột bằng `grid()` với `sticky="ew"`.
  * `Window Selector Combobox`: Chiều rộng tối thiểu 380 px - 420 px.
  * `Refresh / Restore Button`: 44 x 36 px (Icon xoay đồng bộ).
  * `Bounds Readiness Widget`: Tối thiểu 260 x 36 px.
  * `Start / Stop Button`: 160 x 44 px (tối thiểu không co dưới 140 x 40 px).
  * `Language Selector`: Combobox `vi / en` đặt góc phải (80 x 36 px).
- DPI Fallback: Khi Windows DPI ≥ 175%, tự động rút gọn text tiêu đề thành dạng Icon + Tooltip để chống tràn khung hình.

### 2. Xử Lý Trạng Thái Bounds & Recovery Logic
- Khi `resolve_bounds()` phát hiện cửa sổ bị minimize (tọa độ ≤ -32000):
  * Widget Bounds chuyển sang trạng thái `STATE_ERROR` (Màu đỏ/cam) với thông báo `[!] Cửa sổ bị thu nhỏ`.
  * Nhấp vào nút Refresh sẽ tự động gọi chuỗi phục hồi: `WindowManager.restore(hwnd)` → `WindowManager.set_foreground(hwnd)` → quét lại toạ độ.
  * **Retry không được block Main Thread**: triển khai retry (tối đa 3 lần, delay 300ms giữa các lần) bằng chuỗi lịch trình bất đồng bộ (`self.after(300, self._retry_resolve_bounds)`), tuyệt đối không dùng `time.sleep()` trong handler của nút Refresh — vì đó là code chạy trên Main Thread, `sleep` sẽ đơ toàn bộ UI trong lúc retry.
  * Nếu cả 3 lần retry đều thất bại: chuyển `STATE_ERROR` sang thông báo cụ thể hơn, ví dụ `[!] Không thể khôi phục cửa sổ — vui lòng thao tác thủ công (Alt+Tab / click cửa sổ game)`, thay vì giữ nguyên thông báo minimize ban đầu hoặc để trạng thái mơ hồ.
- Khi tọa độ hợp lệ: Chuyển sang `STATE_READY` (Xanh lá) với thông báo động theo kích thước thực tế vừa quét được, ví dụ `f"[✓] Sẵn sàng ({width}x{height})"` — không hard-code `1920x1080`, vì cửa sổ game có thể ở bất kỳ độ phân giải/kích thước nào.

### 3. Nút Start/Stop Chống Double-Click (Debounce & State Lock)
- Nút hoạt động theo state machine rõ ràng, không phải một hành động cố định:
  ```python
  def on_start_stop_clicked(self):
      self.start_stop_btn.configure(state="disabled")
      is_running = self.hunt_state == "RUNNING"
      if is_running:
          self._request_stop_hunt()   # đi qua SingleInstanceLock / stop luồng
      else:
          self._request_start_hunt()  # đi qua SingleInstanceLock / start luồng
      self.after(500, self._reenable_start_stop_btn)

  def _reenable_start_stop_btn(self):
      self.start_stop_btn.configure(state="normal")
      # Màu và text phải phản ánh TRẠNG THÁI MỚI sau khi start/stop đã xử lý xong,
      # không phải trạng thái trước khi bấm.
      self._refresh_start_stop_visual()
  ```
  - Debounce 500ms ở tầng UI (`disabled` state) chỉ để chống double-click gây khó chịu trải nghiệm; đây **không phải** cơ chế đảm bảo an toàn logic duy nhất — `SingleInstanceLock` ở tầng khởi động luồng vẫn phải được giữ nguyên như lớp bảo vệ thực sự chống khởi động trùng, hai cơ chế bổ trợ nhau, không thay thế nhau.
  - Màu sắc: `UIStyle.BTN_START_BG` (Xanh lá) khi rảnh và `UIStyle.BTN_STOP_BG` (Đỏ) khi bot đang chạy, cập nhật qua `_refresh_start_stop_visual()` dựa trên `self.hunt_state` thực tế tại thời điểm gọi, không suy đoán từ hành động vừa bấm.

### 4. Chuyển Đổi Ngôn Ngữ Động (Dynamic i18n)
- Khi người dùng đổi `vi ↔ en`, gọi hàm `self.refresh_translations()`:
  - Cập nhật trực tiếp text trên các widget và `values` trên combobox qua `GLOBAL_TRANSLATIONS`.
  - Tuyệt đối không hủy widget hay reload lại toàn bộ app để tránh mất trạng thái đã chọn.
  - **Binding lựa chọn phải dựa trên key/id ổn định, không dựa trên chuỗi hiển thị**: Window Selector Combobox và bất kỳ combobox nào khác có lựa chọn cần được lưu trữ (map nội bộ) theo giá trị định danh không đổi (VD: `hwnd`, hoặc mã ngôn ngữ), rồi mới render label hiển thị theo ngôn ngữ hiện tại. Nếu combobox map lựa chọn theo text hiển thị, đổi ngôn ngữ sẽ làm mất khớp lựa chọn hiện tại dù `refresh_translations()` không reload widget.

## Validation & Testing

### 1. Automated Tests (`tests/unit/test_action_bar.py`)
- Test Debounce Click: Click nút Start liên tục 5 lần trong 200ms → Assert chỉ có duy nhất 1 luồng săn được kích hoạt.
- Test Minimize Recovery: Giả lập hwnd có tọa độ `[-32000, -32000]` → Nhấn Refresh → Assert hàm `WindowManager.restore` được gọi và cập nhật lại bounds, và assert quá trình retry không dùng blocking sleep (verify qua `self.after` được gọi thay vì `time.sleep`).
- (Added) Test Retry Exhausted: Giả lập cả 3 lần retry đều thất bại → Assert UI hiển thị thông báo "không thể khôi phục" cụ thể, không giữ nguyên thông báo minimize ban đầu, và không tiếp tục retry vô hạn.
- Test Dynamic i18n: Đổi ngôn ngữ từ `vi` sang `en` → Assert text trên nút Start chuyển thành "Start Hunt" mà không làm thay đổi cửa sổ game đang được chọn (verify bằng `hwnd`/id nội bộ không đổi, không chỉ verify text).
- (Added) Test Start/Stop State Correctness: Bấm Start khi đang `IDLE` → assert chuyển sang `RUNNING` và màu/text nút cập nhật đúng sau khi debounce hết hạn; lặp lại cho bấm Stop khi đang `RUNNING`.

### 2. Visual & DPI Check
- Kiểm tra bố cục không bị tràn/đè chữ ở các mức DPI: 100%, 125%, 150%, 175%, 200%.
- Kiểm tra thông báo `STATE_READY` hiển thị đúng kích thước thực tế của cửa sổ được chọn (không phải giá trị cố định).

## Session Boundary Gate

**PASSED nếu:**
- Vùng A hiển thị chuẩn xác, xử lý khôi phục cửa sổ minimize mượt mà, không block UI trong lúc retry.
- Nút Start/Stop có debounce an toàn, không sinh tiến trình rác, và luôn phản ánh đúng trạng thái thực tế sau khi xử lý.
- Đổi ngôn ngữ chuyển text ngay lập tức mà không mất trạng thái cửa sổ (verify theo id, không theo text).
- Retry khi mất cửa sổ có giới hạn rõ ràng (3 lần) và có thông báo dứt khoát khi thất bại hoàn toàn.

**REVERTED nếu:**
- Vỡ layout ở DPI cao hoặc mất liên kết binding cửa sổ game.
- Retry recovery làm đơ UI (dùng blocking sleep trên Main Thread).
- Báo cáo kết quả PASSED/REVERTED ở phút thứ 25.