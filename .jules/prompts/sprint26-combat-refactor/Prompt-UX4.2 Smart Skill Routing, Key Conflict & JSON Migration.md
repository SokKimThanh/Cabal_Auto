# Session Prompt UX4.2: Smart Skill Routing, Key Conflict & Robust JSON Migration

Timebox: 25–30 minutes.
Priority: High – Handles bidirectional skill routing, key conflict warnings, and resilient legacy config migration.

---

## Objective
Xử lý toàn bộ tầng logic dữ liệu cho Dải kỹ năng Dual-Lane: Điều hướng kỹ năng 2 chiều thông minh (Attack <-> Buff), thông báo Toast chống spam, phát hiện cảnh báo trùng phím mềm dẻo (Hover Tooltip), và nạp/lưu cấu hình tương thích ngược với mọi định dạng file `hunt_config.json` (kể cả file lỗi/rác) — **tái sử dụng** cơ chế migration/ghi file an toàn đã xây ở CB4, không tạo luồng thứ hai độc lập.

## Target Files
- Modify: `ui/tabs/hunt_tab.py`
- Modify: `lib/features/skills/runtime.py`
- Modify: `lib/features/hunt/hunt_config.py`
- Modify: `lib/features/hunt/config_migrator.py` (bổ sung rule, không thay thế logic đã có ở CB4)
- Create Test: `tests/unit/test_skill_strip_logic.py`

---

## Implementation Details

### 1. Điều Hướng Kỹ Năng 2 Chiều Thông Minh (Bidirectional Routing)
- Khi người dùng chọn skill từ dropdown:
  * **Trường hợp 1:** Chọn skill Buff vào Làn Combo -> Tìm ô trống đầu tiên của Làn Buff để chuyển sang.
  * **Trường hợp 2:** Chọn skill Attack vào Làn Buff -> Tìm ô trống đầu tiên của Làn Combo để chuyển sang.
  * **Trường hợp 3:** Nếu làn tương ứng đã kín chỗ -> Hủy lựa chọn, giữ nguyên skill cũ **và revert giá trị hiển thị của dropdown về skill cũ** (không chỉ revert biến trạng thái nội bộ — combobox thường đã hiển thị giá trị mới ngay khi người dùng chọn, nên phải set lại giá trị hiển thị tường minh), bật Toast: *"Làn kỹ năng tương ứng đã đầy"*.
  * **Ràng buộc thiết kế quan trọng (chống vòng lặp vô tận):** Cơ chế routing chỉ thực hiện **đúng một bước nhảy** mỗi lần chọn — tìm ô trống đầu tiên của làn đối diện và dừng lại. Tuyệt đối không triển khai logic "dồn/đẩy dây chuyền" (di chuyển skill khác ra để nhường chỗ, rồi tiếp tục tìm chỗ cho skill bị đẩy ra, v.v.) — nếu làn đích đã đầy, xử lý theo case 3 (chặn + toast), không thử tự động sắp xếp lại toàn bộ layout.
- **Debounced Toast Notification:**
  * Hiển thị thông báo dạng dải mờ nổi 2s ở góc dưới.
  * Tái sử dụng widget Toast duy nhất, reset timer `self.after(2000, ...)` khi có thông báo mới để chống spam đè chữ.
  * Hành vi khi nhiều thông báo dồn dập: chỉ thông báo **mới nhất** được hiển thị, các thông báo trước đó (nếu chưa kịp hiển thị đủ 2s) bị thay thế ngay lập tức, không xếp hàng để hiển thị tuần tự — đây là hành vi "chống spam", không phải "không mất thông báo nào".

### 2. Bộ Cảnh Báo Trùng Phím Tắt (Key Conflict Soft Warning)
- Hàm `check_key_conflicts()` quét toàn bộ phím gán trên **cả hai làn** (Combo + Buff), **và đối chiếu thêm với `combo_start_key`** hiện tại (đã có ở CB3B/UX4.1) — dùng chung một hàm kiểm tra duy nhất cho cả hai chiều (skill-vs-skill và skill-vs-combo-start-key), thay vì để CB3B kiểm tra một chiều còn session này kiểm tra chiều khác một cách độc lập.
  * Nếu phát hiện trùng phím: Đổi viền ô sang màu vàng cam `UIStyle.STATE_WARN`, gắn Tooltip khi Hover: `[!] Cảnh báo: Phím này đang bị gán trùng lặp`. Nếu trùng với `combo_start_key`, ghi rõ trong tooltip: `[!] Cảnh báo: Phím này trùng với Combo Start Key`.
  * Cho phép lưu cấu hình (không chặn cứng), nhưng ghi log cảnh báo ra hệ thống.

### 3. Tương Thích Ngược & Phục Hồi Dữ Liệu Rác (Resilient JSON Migration)
- **Không tạo logic migration mới trong `load_hunt_config()`.** Bổ sung rule dưới đây vào `config_migrator.py` đã có từ CB4 (cùng `schema_version`, cùng cơ chế idempotency, cùng backup `.bak`, cùng atomic write temp-file + `os.replace()` đã chốt ở CB4):
  * Khi nạp file legacy hoặc file rỗng `{}`:
    - Nếu skill thiếu `type` hoặc `type` không chuẩn: Tra cứu `SkillRepo` để lấy type chuẩn. Nếu không tìm thấy, fallback gán `type = "attack"`, `cast_time = 1.0`, `cooldown = 1.0`, và log cảnh báo entry nào bị fallback (nhất quán với rule "skip + log" đã áp dụng cho entry hỏng ở CB4, chứ không âm thầm gán mặc định).
    - Tách chuẩn thành 2 mảng: `skill_slots` (chứa attacks) và `buff_slots` (chứa buffs), đúng theo schema đã định nghĩa ở CB4.
  * `load_hunt_config()` chỉ gọi vào `config_migrator.migrate()` (đã được mở rộng thêm rule trên) rồi đọc kết quả — không tự parse/fallback riêng.

---

## Validation & Testing (`tests/unit/test_skill_strip_logic.py`)

### 1. Automated Logic Tests
- **Test Bidirectional Routing:**
  * Chọn `Regeneration` (Buff) vào Combo slot -> Assert tự động chuyển sang Buff slot.
  * Chọn `Dark Explosion` (Attack) vào Buff slot -> Assert tự động chuyển sang Combo slot.
- **Test Full Lane Boundary:**
  * Lấp đầy Buff slots, chọn tiếp 1 skill Buff vào Combo slot -> Assert chặn thành công, hiển thị Toast báo đầy, **và assert giá trị hiển thị của dropdown đã revert về skill cũ** (không chỉ state nội bộ).
- (Added) **Test No Cascading Reassignment:** Lấp đầy cả hai làn, thực hiện một lựa chọn gây xung đột -> Assert không có skill nào khác trong layout bị di chuyển/dồn chỗ ngoài thao tác chặn đơn giản của case 3 (xác nhận không có hiệu ứng dây chuyền).
- **Test Malformed Migration:**
  * Nạp file JSON chứa skill rác `{"name": "BrokenSkill"}` (không có type, không có cd) -> Assert nạp thành công với giá trị fallback an toàn, không ném exception, và assert việc fallback được log lại.
- **Test Soft Conflict Warning:**
  * Gán 3 skill cùng phím `1` -> Assert toàn bộ 3 ô đều được đánh dấu viền cảnh báo `STATE_WARN`.
- (Added) **Test Conflict With Combo Start Key:** Gán một skill key trùng với `combo_start_key` hiện tại -> Assert ô skill đó được đánh dấu `STATE_WARN` với tooltip nêu rõ trùng combo-start-key.
- (Added) **Test Toast Latest-Only:** Kích hoạt 3 toast liên tiếp trong 500ms -> Assert chỉ nội dung của toast cuối cùng còn hiển thị, không có hàng đợi hiển thị tuần tự 3 thông báo.
- (Added) **Test Migration Dùng Chung Cơ Chế CB4:** Assert `load_hunt_config()` gọi vào `config_migrator.migrate()` (qua mock/spy) thay vì chứa logic parse/fallback song song, và assert file ghi ra tuân thủ atomic write + backup đã có từ CB4.

### 2. Visual & Interaction Check
- Rê chuột vào ô trùng phím -> Kiểm tra Tooltip xuất hiện đúng vị trí, đúng nội dung tuỳ loại xung đột (skill-skill hay skill-combo-key).
- Thử nghiệm thao tác đổi skill liên tục -> Kiểm tra Toast hoạt động mượt mà, không giật lag Main Thread.

---

## Session Boundary Gate
- **PASSED nếu:**
  * Điều hướng 2 chiều hoạt động chính xác (đúng một bước nhảy, không dây chuyền), Toast chống spam tốt (chỉ hiển thị mới nhất).
  * Migration thành công 100% các file config rác/cũ mà không crash, và tái sử dụng đúng `config_migrator.py`/atomic-write/backup đã có từ CB4 (không có luồng migration thứ hai).
  * Cảnh báo trùng phím bao phủ cả skill-vs-skill và skill-vs-combo-start-key.
  * Vượt qua toàn bộ automated unit tests.
- **REVERTED nếu:**
  * Gây mất dữ liệu cấu hình kỹ năng hoặc phát sinh vòng lặp vô tận/dây chuyền khi auto-route.
  * Tồn tại 2 luồng migration độc lập không đồng bộ với CB4.
  * Báo cáo kết quả PASSED/REVERTED ở phút thứ 25.