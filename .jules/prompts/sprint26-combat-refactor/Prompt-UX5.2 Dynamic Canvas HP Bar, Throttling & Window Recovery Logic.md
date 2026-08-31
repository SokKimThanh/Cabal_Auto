# Session Prompt UX5.2: Dynamic Step-Fill HP Canvas, Throttling & Resilient Recovery Controller

Timebox: 25–30 minutes.  
Priority: High – Implements high-performance target HP tracking, event throttling, and fail-safe window recovery.

---

## Objective
Tích hợp thanh máu Canvas tự co giãn với hiệu năng vẽ tối ưu (Segmented Step-Fill), bộ điều tiết tần suất (HP Throttling) chống nghẽn Main Thread, cơ chế dọn dẹp thẻ quái chết (Graceful Delay Reset), khung cảnh báo phục hồi cửa sổ game có Retry UX 3 bước và hỗ trợ DPI 100% – 200%.

## Target Files
- Create: `lib/vision/target_hp_reader.py` (thuật toán tính % máu từ Target Bar)
- Modify: `ui/tabs/hunt_tab.py`
- Modify: `lib/features/hunt/hunt_orchestrator.py`
- Modify: `lib/system/i18n.py`
- Reference: `lib/system/window_manager.py`, `lib/ui_style.py`

---

## Implementation Details

### 1. Thanh Máu Canvas Động Tối Ưu & HP Throttling
- **Vẽ Canvas Hiệu Năng Cao (Segmented Step-Fill):**
  * Chiều cao cố định 24 px, co giãn ngang theo sự kiện `<Configure>`.
  * Khởi tạo sẵn 2 đối tượng Canvas ID: `self.hp_bg` (nền xám `#27272A`) và `self.hp_fill` (thanh máu).
  * Khi cập nhật: Chỉ gọi `canvas.coords(self.hp_fill, 0, 0, fill_width, 24)` và đổi màu fill theo mốc: Xanh lá (`> 60%`), Vàng cam (`30% - 60%`), Đỏ tươi (`< 30%`). Tuyệt đối không gọi `canvas.delete("all")`.
  * Nhãn text HP: Vẽ tại tâm `(width / 2, 12)` với `anchor="center"`, tự động cập nhật chuỗi `f"{current_hp:,} / {max_hp:,} ({percent:.1f}%)"`.
- **Bộ Điều Tiết Tần Suất (HP Throttling):**
  * Giới hạn cập nhật UI tối đa **10 FPS (100ms / tick)** hoặc khi $|\Delta \text{HP}| \ge 0.5\%$.
- **Graceful Death Reset:**
  * Khi HP = 0%: Đổi màu `hp_fill` sang xám mờ `#52525B`, hiển thị text `[ Đã Tiêu Diệt ]`, sau đó gọi `self.after(200, self._clear_target_card)` để xóa thẻ và trả UI về `Idle`.

### 2. Bộ Điều Khiển Phục Hồi Cửa Sổ (Fail-Safe Recovery UX)
- Khi `WindowSelectionService` phát hiện tọa độ $\le -32000$:
  * Dashboard hiển thị khung màu cam `UIStyle.STATE_WARN` kèm nút `[ Khôi Phục Cửa Sổ Game ]`.
- **Hành vi Nút Bấm & Retry Logic:**
  * Khi click: Khóa nút (`state="disabled"`), hiển thị text tiến trình `⏳ Đang thử lại (1/3)...` $\rightarrow$ `(2/3)...` $\rightarrow$ `(3/3)...` (mỗi lần cách nhau 500ms).
  * Gọi `WindowManager.restore(hwnd)` và `WindowManager.set_foreground(hwnd)`.
  * **Nếu thất bại sau 3 lần:** Đổi nhãn cảnh báo sang màu đỏ `UIStyle.STATE_ERROR`, kích hoạt Toast: `target_card.recovery_failed` ("Không thể khôi phục game. Vui lòng mở lại game bằng tay") và mở lại trạng thái nút.

### 3. Đa Ngôn Ngữ (i18n)
- Đăng ký đầy đủ các key dịch song ngữ:
  * `target_card.status_approaching`, `target_card.status_attacking`, `target_card.status_idle`, `target_card.target_dead`, `target_card.recovery_btn`, `target_card.recovery_retry`, `target_card.recovery_failed`.

---

## Validation & Testing (`tests/unit/test_target_hp_recovery.py`)

### 1. Automated Tests
- **Stress Test HP Throttling:** Bắn $2.000$ sự kiện cập nhật HP trong vòng 5 giây -> Assert giao diện chỉ kích hoạt vẽ lại tối đa 50 lần, Main Thread phản hồi mượt mà.
- **Test Graceful Death Delay:** Cập nhật HP = 0% -> Assert nhãn đổi thành `[ Đã Tiêu Diệt ]` và thẻ mục tiêu được reset sạch sẽ sau 200ms.
- **Test 3-Step Recovery Retry & Failure Fallback:** Giả lập hàm `WindowManager.restore()` luôn trả về `False` -> Assert nút bấm cập nhật đủ 3 bước retry và kích hoạt thông báo lỗi thất bại.

### 2. Visual & High-DPI Check
- Kiểm tra thanh Canvas HP và nhãn số hiển thị sắc nét, canh giữa hoàn hảo ở các mức DPI 100%, 125%, 150%, 175%, 200%.
- Kiểm tra chuyển đổi ngôn ngữ `vi` <-> `en` cập nhật tức thì toàn bộ trạng thái và tooltip.

---

## Session Boundary Gate
- **PASSED nếu:**
  * Thanh máu cập nhật mượt mà (Segmented step-fill), không gây nghẽn CPU khi bị spam dữ liệu.
  * Cơ chế Retry khôi phục cửa sổ hoạt động chính xác kèm thông báo thất bại an toàn.
  * Vượt qua toàn bộ automated unit tests.
- **REVERTED nếu:**
  * Gây treo giao diện khi spam HP hoặc lỗi crash khi quái chết.
  * Báo cáo kết quả PASSED/REVERTED ở phút thứ 25.