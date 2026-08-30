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
- Reference: `lib/ui_style.py`

---

## Implementation Details

### 1. Hàm Tra cứu Quái An toàn 2 Tầng (Safe Fallback Reader)
- Triển khai `get_target_monster_info(name_or_id: str) -> Dict[str, Any]`:
  - **Tầng 1:** Tra cứu SQLite `monsters.db` để lấy nhanh các chỉ số (`hp`, `level`, `defense`, `image_path`).
  - **Tầng 2 (Fallback):** Nếu DB không có kết quả, gọi `load_monster_library()` đọc từ `lib/data/monsters.json`.
  - Nếu cả 2 đều không có: Trả về dict mặc định với `name: name_or_id`, `hp: 10000`, `image_path: None` để không bao giờ gây crash app.

### 2. Giao diện Target Card (`ui/tabs/hunt_tab.py`)
- Header Bar:
  - Label trạng thái: `🏃 Đang tiếp cận...` (vàng/cam), `⚔️ Đang tấn công...` (xanh lá), hoặc `Sẵn sàng săn` (xám).
  - Badge ID: `Target: #<id>`.
- Container Thẻ Quái (Ẩn khi không có mục tiêu):
  - Cột trái: Ảnh quái vật (Dùng `PIL.ImageTk`). Nếu file ảnh không tồn tại hoặc lỗi đường dẫn, tự động load icon mặc định `assets/icons/default_monster.png`.
  - Cột phải: Tên, Cấp độ, Máu tối đa, Chỉ số thủ.
  - Thanh máu thời gian thực: `ttk.Progressbar` hoặc Canvas bound trực tiếp với `target_hp_reader.calculate_target_hp_percent(frame)`.

### 3. Đồng bộ Trạng thái & Main Thread Gate
- Trong `HuntOrchestrator`:
  - Khi khóa mục tiêu mới nhưng máu chưa giảm: Bắn trạng thái `APPROACHING` lên UI.
  - Khi máu bắt đầu giảm hoặc cast skill: Bắn trạng thái `ATTACKING` và cập nhật % thanh máu.
  - Khi máu = 0%: Bắn trạng thái `TARGET_DEAD`, xóa Target Card sau 0.2s và reset về `Idle`.
- **Bắt buộc:** Mọi thao tác cập nhật Label/Progressbar/Ảnh phải gọi qua `self.schedule_ui_task(lambda: ...)` hoặc `self.after(0, ...)`.

---

## Validation & Testing
- Test Case 1 (Valid Monster): Khóa mục tiêu quái có trong DB -> Assert hiển thị đúng ảnh, tên, chỉ số HP.
- Test Case 2 (Missing Asset / Unlisted Mob): Khóa mục tiêu quái không có ảnh hoặc quái lạ -> Assert load fallback icon an toàn, không ném exception.
- Test Case 3 (Combat Transition): Giả lập HP giảm từ 100% -> 50% -> 0% -> Assert thanh máu trượt mượt và thẻ quái tự dọn dẹp khi chết.

## Session Boundary Gate
- **PASSED nếu:**
  * Thẻ mục tiêu hiển thị mượt mà ở các mức DPI 100%-150%.
  * Dùng đúng bảng màu `UIStyle` (không dùng mã màu hex cố định).
  * Không gọi bất kỳ phương thức widget Tkinter nào từ background thread.
- **REVERTED nếu:**
  * Lỗi crash do missing file ảnh hoặc truy vấn DB thất bại.
  * Báo cáo kết quả PASSED/REVERTED ở phút thứ 25.