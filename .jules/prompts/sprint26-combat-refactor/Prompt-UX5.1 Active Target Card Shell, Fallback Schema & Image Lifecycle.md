# Session Prompt UX5.1: Active Target Card Shell, Multi-Tier Fallback & Image Disposal

Timebox: 20–25 minutes.
Priority: High – Establishes resilient monster metadata presentation with zero memory leaks.

---

## ⚠ Xác nhận trước khi bắt đầu: Quan hệ với Session CB4A

Session **CB4A** ("Real-time Target Card & Safe Target Info Visualizer") đã mô tả một panel gần như trùng khớp: cùng vị trí (Panel 2 bên phải Vùng B / "Mục Tiêu & Trạng Thái"), cùng Status Badge 3 trạng thái, cùng cơ chế fallback ảnh 3 tầng, cùng giá trị fallback `hp: 10000`. Trước khi triển khai session này, cần xác nhận:

- **(a) UX5.1 là nền tảng/shell được xây trước, CB4A bổ sung phần đọc HP thời gian thực lên trên** — nếu vậy, `safe_get_monster_data()` ở đây và `get_target_monster_info()` ở CB4A **phải là cùng một hàm/cùng một schema fallback duy nhất** (bao gồm cờ `is_placeholder` đã dùng ở CB4A), không định nghĩa hai schema fallback độc lập dù có thể trùng giá trị.
- **(b) Đây là hai bản đặc tả khác nhau cho cùng một tính năng** (do thiết kế lại) — nếu vậy, cần chọn một bản làm chuẩn duy nhất trước khi code, tránh dựng 2 lần cùng một panel.

Mặc định trong tài liệu này: giả định trường hợp (a) — session này là shell nền tảng, và `safe_get_monster_data()` được viết theo cách để CB4A tái sử dụng lại (không phải viết lại). Nếu thực tế là trường hợp (b), điều chỉnh phạm vi trước khi bắt đầu.

## Objective
Xây dựng khung hiển thị Thẻ Mục Tiêu (Active Target Card) tại Panel 2 bên phải Vùng B (kích thước chuẩn 776 x 552 px). Tích hợp cơ chế Fallback an toàn 3 tầng (kể cả khi mất sạch file ảnh), giải phóng bộ nhớ hình ảnh Tkinter chuyên sâu, hỗ trợ DPI 100% – 200% và song ngữ i18n đầy đủ.

## Target Files
- Modify: `ui/tabs/hunt_tab.py` (Panel Mục Tiêu & Trạng Thái)
- Modify: `lib/features/monsters/monster_repo.py`
- Modify: `lib/system/i18n.py`
- Reference: `lib/ui_style.py`

---

## Implementation Details

### 1. Fallback Toàn Diện Cho CSDL (Full Schema Fallback Adapter)
- Khai báo schema chuẩn:
  ```python
  DEFAULT_MONSTER_SCHEMA = {
      "id": "0",
      "name": "Unknown Target",
      "level": "N/A",
      "hp": 10000,
      "defense": 0,
      "image_path": None,
      "is_placeholder": True,
  }
  ```
  (Trường `is_placeholder` được thêm vào để dùng chung với cờ đã thiết lập ở CB4A — không dùng cách suy luận riêng như so sánh `id == "0"` ở nơi khác trong code.)
- Triển khai `safe_get_monster_data(raw_data: Optional[dict]) -> dict`:
  - Sử dụng fallback cho từng trường nếu dữ liệu từ `monsters.db` bị `None` hoặc sai kiểu.
  - Nếu CB4A đã tồn tại `get_target_monster_info()`, hàm này nên **gọi vào/thay thế** nó thay vì tồn tại song song — xác nhận theo mục "Quan hệ với CB4A" ở trên.

### 2. Giao Diện Thẻ Mục Tiêu & Quản Lý Bộ Nhớ Ảnh (776 x 552 px)
- Header Bar:
  - Status Badge lớn (🏃 Đang tiếp cận... / ⚔️ Đang tấn công... / ✓ Sẵn sàng săn) kèm Target ID (`Target: #<id>`). Dùng chung namespace i18n với CB4A cho 3 trạng thái này nếu CB4A đã định nghĩa key tương ứng — không tạo bộ key dịch thứ hai cho cùng khái niệm.
  - Nếu dùng dữ liệu fallback (`is_placeholder == True`): Đổi màu badge sang `UIStyle.STATE_WARN` và gắn tooltip cảnh báo dữ liệu mặc định.
- Thẻ Quái Vật (Active Target Card Container):
  - Cột trái - Khung ảnh đại diện:
    - Co giãn theo DPI: Kích thước `int(120 * scale_factor)`.
    - Cơ chế Fallback 3 tầng: Nạp ảnh quái → Nạp `default_monster.png` → Hiển thị placeholder `[ NO IMAGE ]`.
    - **Dùng một `Label` duy nhất cho cả 3 tầng**, không chuyển đổi qua lại giữa `Label` và `Canvas` khi fallback — tránh churn loại widget (tạo/huỷ Canvas liên tục) có thể phát sinh widget rác nếu xử lý huỷ không triệt để. Khi ở tầng "no image", set `image_label.configure(image="", text="[ NO IMAGE ]", bg=UIStyle.BG_MUTED)`; khi có ảnh, set `image_label.configure(image=photo, text="")`.
    - **Thread-safety (nhắc lại từ CB4A):** đọc/giải mã file ảnh có thể ở background thread, nhưng khởi tạo `ImageTk.PhotoImage(...)` bắt buộc chạy trên Main Thread (qua `schedule_ui_task`), và phải giữ reference mạnh để tránh garbage-collection — áp dụng đúng quy tắc đã chốt ở CB4A, không cần thiết kế lại.
    - **Thứ tự giải phóng RAM triệt để**: gọi `clear_target_photo()` **trước** khi gán ảnh mới (không chỉ khi chuyển về trạng thái "không có mục tiêu"), để tránh khoảnh khắc giữ đồng thời cả reference ảnh cũ và ảnh mới khi đổi mục tiêu liên tục nhanh:
      ```python
      def clear_target_photo(self):
          if hasattr(self, 'image_label') and self.image_label:
              self.image_label.configure(image="")
          if hasattr(self, '_current_target_photo') and self._current_target_photo:
              del self._current_target_photo
              self._current_target_photo = None

      def set_target_photo(self, photo_image):
          self.clear_target_photo()  # luôn giải phóng ảnh cũ trước
          self._current_target_photo = photo_image
          self.image_label.configure(image=photo_image, text="")
      ```
  - Cột phải - Thông tin chỉ số: Tên quái vật (hỗ trợ `wraplength` tự xuống dòng khi DPI ≥ 175%), Cấp độ, Máu tối đa, Chỉ số thủ.

### 3. Đa Ngôn Ngữ Tường Minh (i18n Namespace)
- Đăng ký đầy đủ key trong `GLOBAL_TRANSLATIONS`: `target_card.level`, `target_card.max_hp`, `target_card.defense`, `target_card.status_idle`, `target_card.status_approaching`, `target_card.status_attacking`, `target_card.unknown_mob` — kiểm tra trước xem CB4A đã đăng ký các key `status_*` tương đương chưa để tái sử dụng thay vì tạo trùng.

## Validation & Testing (`tests/unit/test_target_card_shell.py`)

### 1. Automated Tests
- **Test Schema Fallback:** Truy vấn dữ liệu rỗng `{}` → Assert trả về đầy đủ các trường mặc định kèm `is_placeholder: True`, không ném `KeyError`.
- **Test Zero-Asset Fallback:** Giả lập xóa cả file ảnh quái lẫn file `default_monster.png` → Assert `image_label` chuyển sang hiển thị text `[ NO IMAGE ]` an toàn mà không crash app, và không có widget `Canvas` phụ nào được tạo thêm.
- **Test High-Load Memory Stability:** Giả lập tải liên tục 500 ảnh trong 30 giây → đo `psutil.Process().memory_info().rss` tại thời điểm bắt đầu (sau warmup 50 ảnh đầu) và tại thời điểm kết thúc → Assert mức tăng RSS giữa hai lần đo dưới một ngưỡng cụ thể (ví dụ < 20MB; điều chỉnh theo môi trường test thực tế), thay vì chỉ khẳng định chung chung "không tăng lũy tiến".
- (Added) **Test Clear-Before-Set Ordering:** Gọi `set_target_photo()` liên tiếp với 2 ảnh khác nhau mà không gọi `clear_target_photo()` thủ công ở giữa → Assert `clear_target_photo()` được gọi tự động trước khi ảnh thứ hai được gán (verify qua spy/mock), không có thời điểm nào 2 reference ảnh cùng tồn tại.
- (Added, nếu áp dụng trường hợp (a)) **Test Unified Fallback With CB4A:** Assert `safe_get_monster_data()` và `get_target_monster_info()` (CB4A) trả về cùng cấu trúc/giá trị cho cùng input, hoặc một hàm gọi trực tiếp vào hàm kia (không phải hai implementation độc lập).

### 2. Visual & DPI Check
- Kiểm tra hiển thị bố cục thẻ mục tiêu sắc nét ở các mức DPI: 100%, 125%, 150%, 175%, 200%.
- Kiểm tra chuyển đổi ngôn ngữ `vi` <-> `en` cập nhật tức thì toàn bộ nhãn.

---

## Session Boundary Gate
- **PASSED nếu:**
  * Thẻ mục tiêu hiển thị sắc nét, cơ chế giải phóng ảnh Tkinter hoạt động hoàn hảo không rò rỉ RAM (theo ngưỡng đo cụ thể ở trên).
  * Xử lý an toàn 100% các trường hợp mất file ảnh (kể cả zero-asset), dùng một `Label` duy nhất không churn loại widget.
  * Quan hệ với CB4A đã được xác nhận rõ ràng (schema fallback dùng chung, không trùng lặp).
  * Vượt qua toàn bộ automated unit tests.
- **REVERTED nếu:**
  * Tràn bộ nhớ khi chuyển đổi ảnh liên tục hoặc lỗi layout ở DPI cao.
  * Tồn tại 2 schema fallback độc lập không đồng bộ với CB4A.
  * Báo cáo kết quả PASSED/REVERTED ở phút thứ 20.