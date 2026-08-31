# Session Prompt UX4.2: Smart Skill Routing, Key Conflict & Robust JSON Migration

Timebox: 25–30 minutes.  
Priority: High – Handles bidirectional skill routing, key conflict warnings, and resilient legacy config migration.

---

## Objective
Xử lý toàn bộ tầng logic dữ liệu cho Dải kỹ năng Dual-Lane: Điều hướng kỹ năng 2 chiều thông minh (Attack <-> Buff), thông báo Toast chống spam, phát hiện cảnh báo trùng phím mềm dẻo (Hover Tooltip), và nạp/lưu cấu hình tương thích ngược với mọi định dạng file `hunt_config.json` (kể cả file lỗi/rác).

## Target Files
- Modify: `ui/tabs/hunt_tab.py`
- Modify: `lib/features/skills/runtime.py`
- Modify: `lib/features/hunt/hunt_config.py`
- Create Test: `tests/unit/test_skill_strip_logic.py`

---

## Implementation Details

### 1. Điều Hướng Kỹ Năng 2 Chiều Thông Minh (Bidirectional Routing)
- Khi người dùng chọn skill từ dropdown:
  * **Trường hợp 1:** Chọn skill Buff vào Làn Combo -> Tìm ô trống đầu tiên của Làn Buff để chuyển sang.
  * **Trường hợp 2:** Chọn skill Attack vào Làn Buff -> Tìm ô trống đầu tiên của Làn Combo để chuyển sang.
  * **Trường hợp 3:** Nếu làn tương ứng đã kín chỗ -> Hủy lựa chọn, giữ nguyên skill cũ và bật Toast: *"Làn kỹ năng tương ứng đã đầy"*.
- **Debounced Toast Notification:**
  * Hiển thị thông báo dạng dải mờ nổi 2s ở góc dưới.
  * Tái sử dụng widget Toast duy nhất, reset timer `self.after(2000, ...)` khi có thông báo mới để chống spam đè chữ.

### 2. Bộ Cảnh Báo Trùng Phím Tắt (Key Conflict Soft Warning)
- Hàm `check_key_conflicts()` quét toàn bộ phím gán:
  * Nếu phát hiện trùng phím: Đổi viền ô sang màu vàng cam `UIStyle.STATE_WARN`, gắn Tooltip khi Hover: `[!] Cảnh báo: Phím này đang bị gán trùng lặp`.
  * Cho phép lưu cấu hình (không chặn cứng), nhưng ghi log cảnh báo ra hệ thống.

### 3. Tương Thích Ngược & Phục Hồi Dữ Liệu Rác (Resilient JSON Migration)
- Trong `hunt_config.py` / `load_hunt_config()`:
  * Khi nạp file legacy hoặc file rỗng `{}`:
    - Nếu skill thiếu `type` hoặc `type` không chuẩn: Tra cứu `SkillRepo` để lấy type chuẩn. Nếu không tìm thấy, fallback gán `type = "attack"`, `cast_time = 1.0`, `cooldown = 1.0`.
    - Tách chuẩn thành 2 mảng: `skill_slots` (chứa attacks) và `buff_slots` (chứa buffs).
  * Lưu an toàn xuống `lib/data/hunt_config.json`.

---

## Validation & Testing (`tests/unit/test_skill_strip_logic.py`)

### 1. Automated Logic Tests
- **Test Bidirectional Routing:**
  * Chọn `Regeneration` (Buff) vào Combo slot -> Assert tự động chuyển sang Buff slot.
  * Chọn `Dark Explosion` (Attack) vào Buff slot -> Assert tự động chuyển sang Combo slot.
- **Test Full Lane Boundary:**
  * Lấp đầy Buff slots, chọn tiếp 1 skill Buff vào Combo slot -> Assert chặn thành công và hiển thị Toast báo đầy.
- **Test Malformed Migration:**
  * Nạp file JSON chứa skill rác `{"name": "BrokenSkill"}` (không có type, không có cd) -> Assert nạp thành công với giá trị fallback an toàn, không ném exception.
- **Test Soft Conflict Warning:**
  * Gán 3 skill cùng phím `1` -> Assert toàn bộ 3 ô đều được đánh dấu viền cảnh báo `STATE_WARN`.

### 2. Visual & Interaction Check
- Rê chuột vào ô trùng phím -> Kiểm tra Tooltip xuất hiện đúng vị trí.
- Thử nghiệm thao tác đổi skill liên tục -> Kiểm tra Toast hoạt động mượt mà, không giật lag Main Thread.

---

## Session Boundary Gate
- **PASSED nếu:**
  * Điều hướng 2 chiều hoạt động chính xác, Toast chống spam tốt.
  * Migration thành công 100% các file config rác/cũ mà không crash.
  * Vượt qua toàn bộ automated unit tests.
- **REVERTED nếu:**
  * Gây mất dữ liệu cấu hình kỹ năng hoặc phát sinh vòng lặp vô tận khi auto-route.
  * Báo cáo kết quả PASSED/REVERTED ở phút thứ 25.