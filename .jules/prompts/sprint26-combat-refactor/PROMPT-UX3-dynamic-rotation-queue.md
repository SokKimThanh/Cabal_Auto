# Session Prompt UX3: Implement Dynamic Monster Rotation Queue Panel (Zone B Left)

Timebox: 25–30 minutes.  
Priority: High – Modernizes monster list into an interactive, high-performance priority queue.

---

## Objective
Tái cấu trúc Panel 1 bên trái của Vùng B (kích thước 776 x 552 px) thành bảng danh sách Luân Chuyển Quái dạng Hàng đợi động (Dynamic Queue). Tích hợp cơ chế phân biệt trực quan quái thật/fallback, hiển thị khoảng cách thời gian thực (rate-limited), đồng bộ an toàn luồng với `hunt_config.json`, hỗ trợ DPI 100% – 200% và song ngữ i18n đầy đủ.

## Target Files
- Modify: `ui/tabs/hunt_tab.py` (Panel Monster Rotation)
- Modify: `lib/features/monsters/monster_repo.py`
- Modify: `lib/features/hunt/hunt_config.py`
- Reference: `lib/ui_style.py`, `lib/system/i18n.py`

---

## Implementation Details

### 1. Bố Cục Panel & DPI Scaling Guard (776 x 552 px)
- Container: `tk.Frame` nằm ở cột 0 của Vùng B với `sticky="nsew"`, `minwidth=360px`.
- Header Bar:
  * Dropdown chọn chế độ: `Sequence` (Tuần tự) / `Priority` (Ưu tiên khoảng cách gần).
  * Bộ công cụ thao tác: Nút thêm quái `[+]`, Nút đẩy lên `[▲]`, Nút đẩy xuống `[▼]`, Nút gỡ `[Xóa]`.
- Bảng danh sách cuộn độc lập:
  * Tùy biến Listbox/Canvas phẳng với viền 1px `UIStyle.BORDER_COLOR`.
  * Hỗ trợ tự động scale padding và font chữ khi Windows DPI đạt 150%, 175%, 200%.

### 2. Định Dạng Dòng Hiển Thị & Phân Biệt Record
- **Dữ liệu chuẩn từ DB:**
  * Format: `☑ [#<id>] <Tên Quái> - Lv.<Level> | HP: <Max_HP> [d: <Range>m]`
  * Màu sắc: Text chính `UIStyle.TEXT_MAIN`, Badge ID màu xanh dương/cyan.
- **Dữ liệu Fallback / Chưa nhận diện:**
  * Format: `⚠ [#0 - Chưa rõ] <Tên Gốc> - Lv.N/A | HP: 10000`
  * Màu sắc: Badge màu cam `UIStyle.STATE_WARN`, Text phụ màu xám mờ `UIStyle.TEXT_MUTED`.

### 3. State Management & Thread-Safe Config Sync
- Tạo lớp `MonsterQueueController`:
  * Lưu trữ danh sách mục tiêu hiện tại trong RAM.
  * Khi người dùng thêm/xóa/đổi thứ tự trên UI: Cập nhật ngay danh sách hiển thị và lên lịch ghi đè an toàn xuống `hunt_config.json` sau $300\text{ms}$ (Debounced save).
- Cập nhật từ luồng Săn (Hunt Thread):
  * Khi quét thấy quái mới: Tự động chèn vào hàng đợi và tính khoảng cách (Cập nhật UI tối đa 5 FPS / mỗi 200ms).
  * Khi quái chết: Xóa ngay lập tức khỏi UI qua `schedule_ui_task()` và tự động kích hoạt target con tiếp theo.

### 4. Đa Ngôn Ngữ (i18n)
- Đăng ký đầy đủ key dịch song ngữ (`vi`/`en`) trong namespace `monster_rotation`:
  * `monster_rotation.title`, `monster_rotation.mode_sequence`, `monster_rotation.mode_priority`, `monster_rotation.add_btn`, `monster_rotation.remove_btn`, `monster_rotation.unknown_badge`.

---

## Validation & Testing

### 1. Automated Tests (`tests/unit/test_monster_rotation_queue.py`)
- **Test Debounced JSON Sync:**
  * Thực hiện liên tiếp 5 thao tác đổi vị trí và xóa quái trong 100ms -> Assert file `hunt_config.json` chỉ được ghi đúng 1 lần sau 300ms và lưu đúng mảng `monster_rotation`.
- **Test Dynamic Death Queue:**
  * Khởi tạo hàng đợi gồm 3 quái -> Giả lập tín hiệu báo quái chết liên tiếp -> Assert UI gỡ bỏ chính xác từng dòng mà không bị lỗi `IndexError` hay vỡ Listbox.
- **Test Fallback Record Display:**
  * Nạp record khuyết thiếu `{"name": "Unknown Mob"}` -> Assert danh sách hiển thị đúng badge `[#0 - Chưa rõ]` và cấp độ `Lv.N/A`.

### 2. Visual & DPI Check
- Kiểm tra danh sách hiển thị sắc nét, không bị mất icon/chữ ở các mức DPI: 100%, 125%, 150%, 175%, 200%.
- Kiểm tra chuyển đổi ngôn ngữ `vi` <-> `en` làm mới text toàn bộ panel ngay lập tức.

---

## Session Boundary Gate
- **PASSED nếu:**
  * Panel hiển thị chuẩn kích thước, thanh cuộn hoạt động mượt mà, danh sách cập nhật động theo thời gian thực.
  * Phân biệt rõ ràng quái thật và quái fallback.
  * Vượt qua toàn bộ automated tests đồng bộ file JSON.
- **REVERTED nếu:**
  * Lỗi văng `IndexError` khi quái chết nhanh hoặc làm hỏng cấu trúc `hunt_config.json`.
  * Báo cáo kết quả PASSED/REVERTED ở phút thứ 25.