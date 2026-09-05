# Session Prompt UX5.2: Dynamic Step-Fill HP Canvas, Throttling & Resilient Recovery Controller

Timebox: 25–30 minutes.
Priority: High – Implements high-performance target HP tracking, event throttling, and fail-safe window recovery.

---

## ⚠ Xác nhận trước khi bắt đầu

1. **Quan hệ với `target_hp_reader.py` (CB4A):** CB4A đã tạo file này và quy định `calculate_target_hp_percent()` phải tái sử dụng `TargetBarDetector.get_hp_percentage()` (CB1) làm nguồn duy nhất, không viết lại thuật toán đọc pixel. Target Files bên dưới ghi "Modify" (không phải "Create") cho file này — session này chỉ bổ sung phần Canvas rendering/throttling ở tầng UI, **không** viết lại thuật toán tính % HP.
2. **Quan hệ với cơ chế Recovery ở UX1 (Action Bar):** Nếu nút "Khôi Phục Cửa Sổ Game" ở Target Card và nút Refresh ở Action Bar (UX1) cùng tồn tại, cả hai **phải gọi chung một hàm retry-logic duy nhất** ở tầng service (đặt trong `window_selection_service.py`), dùng chung state (đang retry lần mấy, đã thất bại hay chưa) — không viết 2 state machine retry độc lập cho 2 nút khác nhau.

## Objective
Tích hợp thanh máu Canvas tự co giãn với hiệu năng vẽ tối ưu (Segmented Step-Fill), bộ điều tiết tần suất (HP Throttling) chống nghẽn Main Thread, cơ chế dọn dẹp thẻ quái chết (Graceful Delay Reset, kế thừa race-condition guard từ CB4A), khung cảnh báo phục hồi cửa sổ game có Retry UX 3 bước (bất đồng bộ, dùng chung logic với UX1) và hỗ trợ DPI 100% – 200%.

## Target Files
- Modify: `lib/vision/target_hp_reader.py` (chỉ bổ sung phần cần thiết cho Canvas rendering ở UI, thuật toán % HP giữ nguyên từ CB4A/CB1)
- Modify: `ui/tabs/hunt_tab.py`
- Modify: `lib/features/hunt/hunt_orchestrator.py`
- Modify: `lib/features/hunt/window_selection_service.py` (hàm retry dùng chung với UX1)
- Modify: `lib/i18n/translations.py`
- Reference: `lib/system/window_manager.py`, `lib/ui_style.py`

---

## Implementation Details

### 1. Thanh Máu Canvas Động Tối Ưu & HP Throttling
- **Vẽ Canvas Hiệu Năng Cao (Segmented Step-Fill):**
  * Chiều cao cố định 24 px, co giãn ngang theo sự kiện `<Configure>`.
  * Khởi tạo sẵn 2 đối tượng Canvas ID: `self.hp_bg` (nền xám `#27272A`) và `self.hp_fill` (thanh máu).
  * Khi cập nhật: Chỉ gọi `canvas.coords(self.hp_fill, 0, 0, fill_width, 24)` và đổi màu fill theo mốc: Xanh lá (`> 60%`), Vàng cam (`30% - 60%`), Đỏ tươi (`< 30%`). Tuyệt đối không gọi `canvas.delete("all")`.
  * Nhãn text HP: Vẽ tại tâm `(width / 2, 12)` với `anchor="center"`, tự động cập nhật chuỗi `f"{current_hp:,} / {max_hp:,} ({percent:.1f}%)"`.
- **Bộ Điều Tiết Tần Suất (HP Throttling) — công thức chính xác (thay thế cách diễn đạt "hoặc" mơ hồ):**
  * Giới hạn cứng: không bao giờ vẽ lại UI nhanh hơn mỗi **100ms** (10 FPS là trần tuyệt đối, không có ngoại lệ vượt trần dù HP thay đổi đột ngột).
  * Điều kiện rõ ràng cho phép vẽ lại:
    ```python
    if (current_time - last_draw_time >= 100) and (abs(new_percent - last_drawn_percent) >= 0.5):
        # Draw to canvas and update last_draw_time
    ```
  * Trong mỗi chu kỳ đã đủ 100ms kể từ lần vẽ trước: chỉ thực sự vẽ lại nếu `abs(new_percent - last_drawn_percent) >= 0.5`; nếu thay đổi nhỏ hơn ngưỡng này, bỏ qua lần vẽ đó (giữ nguyên canvas) để giảm vẽ thừa khi HP gần như không đổi.
  * Đây là điều kiện **AND** giữa "đã đủ 100ms" và "delta ≥ 0.5%", không phải OR — không cho phép vẽ sớm hơn 100ms dù delta lớn tới đâu, vì điều đó sẽ phá vỡ trần 10 FPS.
- **Graceful Death Reset (kế thừa race-condition guard từ CB4A):**
  * Khi HP = 0%: Đổi màu `hp_fill` sang xám mờ `#52525B`, hiển thị text `[ Đã Tiêu Diệt ]`, sau đó gọi `self.after(200, self._clear_target_card)` để xóa thẻ và trả UI về `Idle`.
  * **Bắt buộc giữ lại cơ chế đã chốt ở CB4A**: nếu một mục tiêu mới được khoá trong vòng 200ms kể từ khi lịch xoá này được đặt (kill liên tiếp nhanh), phải gọi `self.after_cancel(pending_clear_id)` trước khi hiển thị card mới, tránh xoá nhầm card của mục tiêu mới. Không được bỏ sót yêu cầu này khi viết lại phần Canvas.

### 2. Bộ Điều Khiển Phục Hồi Cửa Sổ (Fail-Safe Recovery UX)
- Khi `WindowSelectionService` phát hiện tọa độ ≤ -32000:
  * Dashboard hiển thị khung màu cam `UIStyle.STATE_WARN` kèm nút `[ Khôi Phục Cửa Sổ Game ]`.
- **Hành vi Nút Bấm & Retry Logic (dùng chung service với UX1, bất đồng bộ bắt buộc):**
  * Khi click: khóa nút (`state="disabled"`), gọi vào hàm retry dùng chung ở `window_selection_service.py` (cùng hàm mà nút Refresh của UX1 gọi), triển khai bằng chuỗi lịch trình `self.after(500, self._retry_step)` — **tuyệt đối không dùng `time.sleep()`** giữa các bước retry, vì đây là code chạy trên Main Thread.
  * Hiển thị text tiến trình `⏳ Đang thử lại (1/3)...` → `(2/3)...` → `(3/3)...` (mỗi bước cách nhau 500ms qua `self.after`, không chặn UI).
  * Gọi `WindowManager.restore(hwnd)` và `WindowManager.set_foreground(hwnd)` ở mỗi bước.
  * **Nếu thất bại sau 3 lần:** Đổi nhãn cảnh báo sang màu đỏ `UIStyle.STATE_ERROR`, kích hoạt Toast: `target_card.recovery_failed` ("Không thể khôi phục game. Vui lòng mở lại game bằng tay") và mở lại trạng thái nút.
  * Nếu nút Refresh (UX1, Action Bar) đang retry đồng thời với nút này (người dùng bấm cả hai gần nhau), hàm dùng chung phải khoá lẫn nhau (chỉ một chuỗi retry chạy tại một thời điểm) để tránh 2 chuỗi retry chồng chéo cùng thao tác trên `hwnd`.

### 3. Đa Ngôn Ngữ (i18n)
- Đăng ký đầy đủ các key dịch song ngữ: `target_card.status_approaching`, `target_card.status_attacking`, `target_card.status_idle`, `target_card.target_dead`, `target_card.recovery_btn`, `target_card.recovery_retry`, `target_card.recovery_failed` — kiểm tra trước các key `status_*` đã đăng ký ở CB4A/UX5.1 để tái sử dụng, không tạo bộ key trùng cho cùng khái niệm.

---

## Validation & Testing (`tests/unit/test_target_hp_recovery.py`)

### 1. Automated Tests
- **Stress Test HP Throttling:** Bắn 2.000 sự kiện cập nhật HP trong vòng 5 giây → Assert giao diện chỉ kích hoạt vẽ lại **tối đa đúng 50 lần** (khớp chính xác trần 10 FPS × 5s, không có ngoại lệ vượt trần do delta lớn), Main Thread phản hồi mượt mà.
- (Added) **Test Delta Threshold Skip:** Trong cùng một cửa sổ 100ms đã đủ điều kiện vẽ, gửi một thay đổi HP nhỏ hơn 0.5% → Assert không có lệnh vẽ lại nào được gọi cho tới khi delta tích luỹ đạt ngưỡng.
- **Test Graceful Death Delay:** Cập nhật HP = 0% → Assert nhãn đổi thành `[ Đã Tiêu Diệt ]` và thẻ mục tiêu được reset sạch sẽ sau 200ms.
- (Added) **Test Rapid Re-target Cancels Pending Clear:** Cập nhật HP = 0% rồi khoá mục tiêu mới trong vòng 200ms → Assert `after_cancel` được gọi và card mới không bị xoá nhầm (đúng theo yêu cầu kế thừa từ CB4A).
- **Test 3-Step Recovery Retry & Failure Fallback:** Giả lập hàm `WindowManager.restore()` luôn trả về `False` → Assert nút bấm cập nhật đủ 3 bước retry (qua `self.after`, không phải `time.sleep`) và kích hoạt thông báo lỗi thất bại.
- (Added) **Test Shared Retry Lock With UX1:** Giả lập cả nút Refresh (UX1) và nút Recovery (Target Card) được bấm gần như đồng thời → Assert chỉ một chuỗi retry chạy, không có 2 chuỗi retry chồng chéo cùng gọi `WindowManager.restore(hwnd)` song song.

### 2. Visual & High-DPI Check
- Kiểm tra thanh Canvas HP và nhãn số hiển thị sắc nét, canh giữa hoàn hảo ở các mức DPI 100%, 125%, 150%, 175%, 200%.
- Kiểm tra chuyển đổi ngôn ngữ `vi` <-> `en` cập nhật tức thì toàn bộ trạng thái và tooltip.

---

## Session Boundary Gate
- **PASSED nếu:**
  * Thanh máu cập nhật mượt mà (Segmented step-fill), không gây nghẽn CPU khi bị spam dữ liệu, đúng trần 10 FPS tuyệt đối.
  * Cơ chế Retry khôi phục cửa sổ hoạt động chính xác, bất đồng bộ hoàn toàn, kèm thông báo thất bại an toàn, và dùng chung logic với UX1 (không có 2 state machine độc lập).
  * `target_hp_reader.py` không viết lại thuật toán tính % HP đã có từ CB1/CB4A.
  * Race-condition guard cho Graceful Death Reset (kế thừa CB4A) được giữ nguyên.
  * Vượt qua toàn bộ automated unit tests.
- **REVERTED nếu:**
  * Gây treo giao diện khi spam HP hoặc lỗi crash khi quái chết.
  * Retry dùng `time.sleep()` chặn Main Thread, hoặc tồn tại 2 luồng retry độc lập giữa UX1 và Target Card.
  * Báo cáo kết quả PASSED/REVERTED ở phút thứ 25.