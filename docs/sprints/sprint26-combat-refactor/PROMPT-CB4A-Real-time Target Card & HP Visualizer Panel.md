# Session Prompt CB4A: Real-time Target Card & Safe Target Info Visualizer

Timebox: 25-30 minutes.
Priority: High – Target monitoring and HP tracking.

---

## Objective
Xây dựng khung hiển thị thông tin mục tiêu (Target Card Dashboard) tại vùng "Mục Tiêu & Trạng Thái". Hiển thị tên quái, ảnh đại diện từ CSDL hoặc fallback icon, máy trạng thái di chuyển/tấn công và thanh máu % thời gian thực mà không làm vỡ kiến trúc JSON/DB và không gọi Tkinter ngoài Main Thread.

## Target Files
- Modify: `ui/tabs/hunt_tab.py` (hoặc frame Target Status trong `app_gui.py`)
- Create: `lib/vision/target_hp_reader.py`
- Modify: `lib/features/monsters/monster_repo.py` (hoặc helper tra cứu quái an toàn)
- Reference: `lib/ui_style.py`, `lib/vision/target_bar_detector.py` (CB1)

---

## Implementation Details

### 1. Hàm Tra cứu Quái An toàn 2 Tầng (Safe Fallback Reader)
- Triển khai `get_target_monster_info(name_or_id: str) -> Dict[str, Any]`:
  - **Tầng 1:** Tra cứu SQLite `monsters.db` để lấy nhanh các chỉ số (`hp`, `level`, `defense`, `image_path`).
  - **Tầng 2 (Fallback):** Nếu DB không có kết quả, gọi `load_monster_library()` đọc từ `lib/data/monsters.json`.
  - Nếu cả 2 đều không có: Trả về dict mặc định với `name: name_or_id`, `hp: 10000`, `image_path: None`, kèm flag `"is_placeholder": True` để không bao giờ gây crash app. **Bất kỳ consumer nào khác** (timing calculator, ước lượng thời gian hạ gục, logic quyết định) phải kiểm tra `is_placeholder` và không dùng `hp: 10000` cho tính toán thực — giá trị này chỉ để UI có gì đó hiển thị, không phải HP thật của quái.

### 2. Đọc % HP thời gian thực (`lib/vision/target_hp_reader.py`)
- Không cài lại thuật toán đọc HP từ đầu. `calculate_target_hp_percent(frame)` phải gọi/tái sử dụng `TargetBarDetector.get_hp_percentage()` (đã cài ở CB1) làm nguồn tính toán duy nhất, để tránh hai nơi trong code base tính % HP theo hai công thức có thể lệch nhau. Nếu cần logic bổ sung riêng cho panel này (VD: làm mượt số liệu để progressbar không giật — xem bên dưới), bọc quanh kết quả của CB1 thay vì viết lại phần đọc pixel.
- Throttle tần suất tính toán: không tính HP% mỗi khi có frame mới không giới hạn. Dùng chung nhịp với vòng lặp worker (hoặc một interval UI riêng, VD 150-200ms) để tránh tốn CPU lặp lại vấn đề đã nêu ở CB1/CB2B.
- Làm mượt hiển thị (tuỳ chọn nhưng khuyến nghị): áp dụng nội suy/giảm dao động nhỏ (VD: chỉ cập nhật progressbar khi % thay đổi ≥ 1 đơn vị) để thanh máu không giật do nhiễu detector, dùng debounce tương tự cơ chế đã áp dụng cho `have_target` ở CB2.

### 3. Giao diện Target Card (`ui/tabs/hunt_tab.py`)
- Header Bar:
  - Label trạng thái: `🏃 Đang tiếp cận...` (vàng/cam), `⚔️ Đang tấn công...` (xanh lá), hoặc `Sẵn sàng săn` (xám).
  - Badge ID: `Target: #<id>`.
- Container Thẻ Quái (Ẩn khi không có mục tiêu):
  - Cột trái: Ảnh quái vật (Dùng `PIL.ImageTk`). Nếu file ảnh không tồn tại hoặc lỗi đường dẫn, tự động load icon mặc định `assets/icons/default_monster.png`.
    - **Thread-safety cho ảnh:** đọc/giải mã file ảnh (PIL `Image.open`, resize, v.v.) có thể thực hiện ở background thread, nhưng việc khởi tạo `ImageTk.PhotoImage(...)` **bắt buộc phải chạy trên Main Thread** (giới hạn nội tại của Tkinter — PhotoImage không an toàn khi tạo ngoài main loop). Thực hiện bước này bên trong `schedule_ui_task`.
    - Giữ một reference mạnh tới mỗi `PhotoImage` đang hiển thị (VD: gán vào `self._current_target_image = photo_image` trên widget/controller), để tránh bug garbage-collection kinh điển của Tkinter khiến ảnh tự biến mất dù code không lỗi.
  - Cột phải: Tên, Cấp độ, Máu tối đa, Chỉ số thủ.
  - Thanh máu thời gian thực: `ttk.Progressbar` hoặc Canvas, được cập nhật từ giá trị % đã tính sẵn ở background thread (theo mục 2) — bản thân widget update chỉ nhận một con số float đã tính xong, không tự gọi `calculate_target_hp_percent()`/OpenCV bên trong lambda UI.

### 4. Đồng bộ Trạng thái & Main Thread Gate
- Trong `HuntOrchestrator`:
  - Khi khóa mục tiêu mới nhưng máu chưa giảm: Bắn trạng thái `APPROACHING` lên UI.
  - Khi máu bắt đầu giảm hoặc cast skill: Bắn trạng thái `ATTACKING` và cập nhật % thanh máu.
  - Khi máu = 0%: Bắn trạng thái `TARGET_DEAD`, lên lịch xóa Target Card sau 0.2s và reset về `Idle`.
    - **Race condition khi đổi mục tiêu nhanh:** nếu một mục tiêu mới được khóa trong vòng 0.2s kể từ khi lên lịch xóa (kill liên tiếp), phải huỷ lịch xóa cũ (`self.after_cancel(pending_clear_id)`) trước khi hiển thị card mới, để không xóa nhầm card của mục tiêu mới vừa khóa.
  - Đảm bảo thứ tự các lệnh cập nhật trạng thái (`APPROACHING` → `ATTACKING` → `TARGET_DEAD`) tới UI theo đúng thứ tự phát sinh — đẩy qua một hàng đợi tuần tự duy nhất (hoặc dùng `schedule_ui_task` theo đúng thứ tự gọi, không chạy song song), tránh trường hợp `ATTACKING` hiển thị sau `TARGET_DEAD` do interleaving giữa các luồng.
- **Bắt buộc:** Mọi thao tác cập nhật Label/Progressbar/Ảnh phải gọi qua `self.schedule_ui_task(lambda: ...)` hoặc `self.after(0, ...)`, và các lambda này chỉ nhận dữ liệu đã tính toán xong (số %, đường dẫn ảnh đã resolve, text trạng thái) — không thực hiện I/O hay xử lý ảnh/OpenCV bên trong lambda.

---

## Validation & Testing
- Test Case 1 (Valid Monster): Khóa mục tiêu quái có trong DB -> Assert hiển thị đúng ảnh, tên, chỉ số HP.
- Test Case 2 (Missing Asset / Unlisted Mob): Khóa mục tiêu quái không có ảnh hoặc quái lạ -> Assert load fallback icon an toàn, không ném exception, và `is_placeholder: True` được set đúng khi dùng dict mặc định.
- Test Case 3 (Combat Transition): Giả lập HP giảm từ 100% -> 50% -> 0% -> Assert thanh máu trượt mượt và thẻ quái tự dọn dẹp khi chết.
- (Added) Test Case 4 (Rapid Re-target Race): Giả lập `TARGET_DEAD` rồi khóa mục tiêu mới trong vòng 0.2s -> Assert lịch xóa card cũ bị huỷ và card mới không bị xóa nhầm.
- (Added) Test Case 5 (Placeholder HP not leaking into logic): Giả lập quái không có trong DB/JSON -> Assert bất kỳ module tiêu thụ `get_target_monster_info()` khác (nếu có trong scope test) bỏ qua giá trị `hp: 10000` khi `is_placeholder == True`.
- (Added) Test Case 6 (No duplicate HP-reading logic): Assert `calculate_target_hp_percent()` gọi vào `TargetBarDetector.get_hp_percentage()` (VD: qua mock/spy) thay vì chứa logic đọc pixel độc lập.

## Session Boundary Gate
- **PASSED nếu:**
  * Thẻ mục tiêu hiển thị mượt mà ở các mức DPI 100%-150%.
  * Dùng đúng bảng màu `UIStyle` (không dùng mã màu hex cố định).
  * Không gọi bất kỳ phương thức widget Tkinter nào từ background thread, kể cả khởi tạo `PhotoImage`.
  * `calculate_target_hp_percent()` tái sử dụng logic CB1, không trùng lặp thuật toán.
- **REVERTED nếu:**
  * Lỗi crash do missing file ảnh hoặc truy vấn DB thất bại.
  * Ảnh Target Card biến mất do lỗi garbage-collection của `PhotoImage`.
  * Báo cáo kết quả PASSED/REVERTED ở phút thứ 25.