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
- DPI Fallback: Khi Windows DPI $\ge 175\%$, tự động rút gọn text tiêu đề thành dạng Icon + Tooltip để chống tràn khung hình.

### 2. Xử Lý Trạng Thái Bounds & Recovery Logic
- Khi `resolve_bounds()` phát hiện cửa sổ bị minimize (tọa độ $\le -32000$):
  * Widget Bounds chuyển sang trạng thái `STATE_ERROR` (Màu đỏ/cam) với thông báo `[!] Cửa sổ bị thu nhỏ`.
  * Nhấp vào nút Refresh sẽ tự động gọi chuỗi phục hồi: `WindowManager.restore(hwnd)` $\rightarrow$ `WindowManager.set_foreground(hwnd)` $\rightarrow$ quét lại toạ độ (Retry tối đa 3 lần với delay 300ms).
- Khi tọa độ hợp lệ: Chuyển sang `STATE_READY` (Xanh lá) với thông báo `[✓] Sẵn sàng (1920x1080)`.

### 3. Nút Start/Stop Chống Double-Click (Debounce & State Lock)
- Bổ sung cơ chế Debounce $500\text{ms}$:
  ```python
  def on_start_stop_clicked(self):
      self.start_stop_btn.configure(state="disabled")
      self.after(500, lambda: self.start_stop_btn.configure(state="normal"))
      # Kích hoạt / Dừng luồng săn qua SingleInstanceLock
Màu sắc: UIStyle.BTN_START_BG (Xanh lá) khi rảnh và UIStyle.BTN_STOP_BG (Đỏ) khi bot đang chạy.4. Chuyển Đổi Ngôn Ngữ Động (Dynamic i18n)Khi người dùng đổi vi $\leftrightarrow$ en, gọi hàm self.refresh_translations():Cập nhật trực tiếp text trên các widget và values trên combobox qua GLOBAL_TRANSLATIONS.Tuyệt đối không hủy widget hay reload lại toàn bộ app để tránh mất trạng thái đã chọn.Validation & Testing1. Automated Tests (tests/unit/test_action_bar.py)Test Debounce Click: Click nút Start liên tục 5 lần trong 200ms -> Assert chỉ có duy nhất 1 luồng săn được kích hoạt.Test Minimize Recovery: Giả lập hwnd có tọa độ [-32000, -32000] -> Nhấn Refresh -> Assert hàm WindowManager.restore được gọi và cập nhật lại bounds.Test Dynamic i18n: Đổi ngôn ngữ từ vi sang en -> Assert text trên nút Start chuyển thành "Start Hunt" mà không làm thay đổi cửa sổ game đang được chọn.2. Visual & DPI CheckKiểm tra bố cục không bị tràn/đè chữ ở các mức DPI: 100%, 125%, 150%, 175%, 200%.Session Boundary GatePASSED nếu:Vùng A hiển thị chuẩn xác, xử lý khôi phục cửa sổ minimize mượt mà.Nút Start/Stop có debounce an toàn, không sinh tiến trình rác.Đổi ngôn ngữ chuyển text ngay lập tức mà không mất trạng thái cửa sổ.REVERTED nếu:Vỡ layout ở DPI cao hoặc mất liên kết binding cửa sổ game.Báo cáo kết quả PASSED/REVERTED ở phút thứ 25.