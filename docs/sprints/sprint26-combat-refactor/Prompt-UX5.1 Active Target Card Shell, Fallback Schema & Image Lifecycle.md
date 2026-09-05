# Session Prompt UX5.1: Active Target Card Shell, Multi-Tier Fallback & Image Lifecycle
## **PHASE 1 of 2-Phase Feature Implementation**

**Timebox:** 40–50 minutes  
**Priority:** High – Establishes resilient monster metadata presentation with zero memory leaks  
**Status:** Foundational phase (CB4A Phase 2 depends on this)

---

## 📌 Quan Hệ với Session CB4A: **PHASE 1 → PHASE 2**

**Xác nhận rõ ràng:** Sau khi kiểm tra chi tiết, UX5.1 và CB4A là **hai phase của cùng một tính năng**:

- **UX5.1 (Phase 1 - Hiện tại):** Shell nền tảng, fallback schema an toàn, quản lý bộ nhớ ảnh
  - Triển khai: `get_target_monster_info()` (2-tầng fallback DB→JSON)
  - Triển khai: Target Card Panel UI (776x552px, PhotoImage lifecycle)
  - Triển khai: i18n keys + DPI scaling
  - **Gate:** PASSED = Shell hoạt động, zero memory leaks, 100%-200% DPI tested

- **CB4A (Phase 2 - Dependency):** Nâng cấp tính năng, thêm HP real-time + status FSM
  - **ĐIỀU KIỆN:** Chỉ bắt đầu **khi UX5.1 PASSED hoàn toàn**
  - Triển khai: `target_hp_reader.py` (HP% real-time + throttling)
  - Triển khai: Status FSM (APPROACHING → ATTACKING → DEAD)
  - Triển khai: Race condition handler (rapid re-target)
  - Tái sử dụng: `get_target_monster_info()` từ UX5.1 (không viết lại)
  - Tái sử dụng: Target Card Panel từ UX5.1 (chỉ thêm methods)
  - Tái sử dụng: i18n keys từ UX5.1 (cùng namespace `target_card.*`)

**🚫 Quan trọng:** Không định nghĩa hai schema fallback độc lập. Hàm `get_target_monster_info()` trong UX5.1 **là đội sự thực duy nhất** cho cả Phase 1 và Phase 2. Cờ `is_placeholder` được thiết lập một lần ở UX5.1, tái sử dụng ở CB4A.

## Objective
**Phase 1 Goal:** Xây dựng shell nền tảng cho Thẻ Mục Tiêu (Active Target Card) tại Panel 2 bên phải Vùng B (kích thước chuẩn 776 x 552 px) với:
- Hàm tra cứu quái an toàn 2-tầng (`get_target_monster_info()`) dùng chung cho Phase 1 & Phase 2
- Cơ chế Fallback an toàn 3 tầng (kể cả khi mất sạch file ảnh)
- Giải phóng bộ nhớ hình ảnh Tkinter triệt để, hỗ trợ DPI 100% – 200%, song ngữ i18n

**Tái sử dụng ở Phase 2 (CB4A):** Panel UI này không sửa; CB4A chỉ thêm methods như `update_status()` và `update_hp_display()` lên trên nền tảng hiện có.

## Target Files
- **Create:** `lib/features/monsters/monster_repo.py` → `get_target_monster_info()` function (2-tầng fallback, dùng chung Phase 1 & 2)
- **Modify:** `ui/tabs/hunt_tab.py` → Target Card Panel UI (776x552px) + lifecycle methods
- **Modify:** `lib/i18n/translations.py` → `target_card.*` i18n keys (shared with CB4A Phase 2)
- **Reference:** `lib/ui_style.py` (colors, fonts, DPI scaling)

---

## Implementation Details

### 1. Fallback Toàn Diện Cho CSDL (Full Schema Fallback Adapter) - **UNIFIED FUNCTION FOR PHASE 1 & 2**
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
- Triển khai `get_target_monster_info(name_or_id: str) -> Dict[str, Any]` (**SINGLE SOURCE OF TRUTH cho Phase 1 & 2**):
  - Sử dụng fallback cho từng trường nếu dữ liệu từ `monsters.db` bị `None` hoặc sai kiểu.
  - **Tầng 1:** Tra cứu SQLite `monsters.db` để lấy nhanh các chỉ số (`hp`, `level`, `defense`, `image_path`).
  - **Tầng 2:** Nếu DB không có kết quả, gọi `load_monster_library()` đọc từ `lib/data/monsters.json`.
  - **Tầng 3 (Default):** Nếu cả 2 đều không có: Trả về dict mặc định với `name: name_or_id`, `hp: 10000`, `image_path: None`, kèm flag `"is_placeholder": True`.
  - **Không phải là function riêng ở Phase 2:** CB4A sẽ gọi trực tiếp `get_target_monster_info()` này, không viết lại hay tạo hàm thay thế tên khác.

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

## Session Boundary Gate: **PHASE 1 COMPLETION CRITERIA**
- **PASSED nếu:**
  * Hàm `get_target_monster_info(name_or_id: str)` triển khai đúng 2-tầng fallback + `is_placeholder` flag
  * Thẻ mục tiêu hiển thị sắc nét, cơ chế giải phóng ảnh Tkinter hoạt động hoàn hảo không rò rỉ RAM (theo ngưỡng đo cụ thể ở trên)
  * Xử lý an toàn 100% các trường hợp mất file ảnh (kể cả zero-asset), dùng một `Label` duy nhất không churn loại widget
  * Vượt qua toàn bộ automated unit tests (8 tests từ Validation & Testing)
  * **Xác nhận:** Quan hệ với CB4A rõ ràng (schema fallback dùng chung, không trùng lặp)

- **🔴 GATE: CHỈ CÓ THỂ CHUYỂN SANG CB4A (PHASE 2) SAU KHI UX5.1 PASSED HOÀN TOÀN**
  * Nếu UX5.1 chưa sẵn sàng, CB4A không thể bắt đầu
  * Nếu UX5.1 bị REVERTED, CB4A cũng bị REVERTED

- **REVERTED nếu:**
  * Tràn bộ nhớ khi chuyển đổi ảnh liên tục hoặc lỗi layout ở DPI cao
  * Tồn tại 2 schema fallback độc lập không đồng bộ với CB4A
  * Hàm `get_target_monster_info()` không implement 2-tầng fallback đầy đủ
  * Báo cáo kết quả PASSED/REVERTED ở phút thứ 20.