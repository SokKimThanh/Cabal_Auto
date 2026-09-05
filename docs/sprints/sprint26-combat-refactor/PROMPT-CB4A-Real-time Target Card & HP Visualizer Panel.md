# Session Prompt CB4A: Real-time Target Card & HP Visualizer Panel
## **PHASE 2 of 2-Phase Feature Implementation**

**Timebox:** 40–50 minutes  
**Priority:** High – Target monitoring and HP tracking  
**Status:** Enhancement phase (DEPENDS ON: UX5.1 Phase 1 PASSED)

---

## 🚫 CRITICAL: This Session is Phase 2 - Only Start After UX5.1 PASSED

**PREREQUISITE GATE:**
- ✅ UX5.1 Phase 1 must be **PASSED and MERGED** before this session starts
- ✅ `get_target_monster_info()` must be working in production
- ✅ Target Card Panel must be rendering at 100%-200% DPI
- ✅ PhotoImage lifecycle management must be proven stable (zero memory leaks)

**If UX5.1 is not PASSED:** Do not start this session. Wait for Phase 1 completion.

---

## Objective
**Phase 2 Enhancement:** Nâng cấp Thẻ Mục Tiêu (Target Card Dashboard) đã được xây dựng ở UX5.1 bằng cách thêm:
- Đọc % HP thời gian thực từ Target Bar trên màn hình
- Trạng thái quái vật (Đang tiếp cận / Đang tấn công / Chết) được cập nhật tự động
- Xử lý race condition khi đổi mục tiêu nhanh liên tiếp

**Tái sử dụng từ Phase 1 (UX5.1):**
- Hàm `get_target_monster_info()` (KHÔNG viết lại)
- Target Card Panel UI (KHÔNG thiết kế lại; chỉ thêm methods)
- i18n keys `target_card.*` (KHÔNG tạo trùng; dùng chung)

## Target Files (Building on UX5.1 Phase 1)
- **Modify:** `ui/tabs/hunt_tab.py` (Add methods to existing Target Card Panel: `update_status()`, `update_hp_display()`, `clear_target_card()`)
- **Create:** `lib/vision/target_hp_reader.py` (HP% calculation wrapping CB1)
- **Reuse:** `lib/features/monsters/monster_repo.py` → `get_target_monster_info()` from UX5.1 (NOT redefine)
- **Modify:** `lib/features/hunt/hunt_orchestrator.py` (State machine + race condition handler)
- **Reference:** `lib/ui_style.py`, `lib/vision/target_bar_detector.py` (CB1)

---

## Implementation Details

### 1. Hàm Tra cứu Quái An toàn 2 Tầng (Safe Fallback Reader) - **ALREADY IMPLEMENTED IN UX5.1**
✅ **REUSE:** Hàm `get_target_monster_info(name_or_id: str)` đã được UX5.1 triển khai đầy đủ:
  - **Tầng 1:** Tra cứu SQLite `monsters.db` để lấy nhanh các chỉ số (`hp`, `level`, `defense`, `image_path`)
  - **Tầng 2 (Fallback):** Nếu DB không có kết quả, gọi `load_monster_library()` đọc từ `lib/data/monsters.json`
  - **Tầng 3 (Default):** Nếu cả 2 đều không có: Trả về dict mặc định kèm flag `"is_placeholder": True`

🚫 **Không triển khai lại:** Không có `get_target_monster_info()` riêng ở CB4A. CB4A gọi trực tiếp hàm của UX5.1.

### 2. Đọc % HP thời gian thực (`lib/vision/target_hp_reader.py`)
- Không cài lại thuật toán đọc HP từ đầu. `calculate_target_hp_percent(frame)` phải gọi/tái sử dụng `TargetBarDetector.get_hp_percentage()` (đã cài ở CB1) làm nguồn tính toán duy nhất, để tránh hai nơi trong code base tính % HP theo hai công thức có thể lệch nhau. Nếu cần logic bổ sung riêng cho panel này (VD: làm mượt số liệu để progressbar không giật — xem bên dưới), bọc quanh kết quả của CB1 thay vì viết lại phần đọc pixel.
- Throttle tần suất tính toán: không tính HP% mỗi khi có frame mới không giới hạn. Dùng chung nhịp với vòng lặp worker (hoặc một interval UI riêng, VD 150-200ms) để tránh tốn CPU lặp lại vấn đề đã nêu ở CB1/CB2B.
- Làm mượt hiển thị (tuỳ chọn nhưng khuyến nghị): áp dụng nội suy/giảm dao động nhỏ (VD: chỉ cập nhật progressbar khi % thay đổi ≥ 1 đơn vị) để thanh máu không giật do nhiễu detector, dùng debounce tương tự cơ chế đã áp dụng cho `have_target` ở CB2.

### 3. Giao diện Target Card (`ui/tabs/hunt_tab.py`) - **EXTEND EXISTING FROM UX5.1**
✅ **Already Exists (from UX5.1 Phase 1):**
- Header Bar với Status Badge và Target ID
- Container Thẻ Quái với ảnh + thông tin chỉ số
- Thứ tự chiều `clear_target_photo()` → `set_target_photo()` → `clear_before_set pattern` đã sẵn

🔄 **ADD FOR PHASE 2:**
- Method `update_status(status_string)`: Cập nhật badge trạng thái (APPROACHING/ATTACKING/DEAD) từ background thread qua `schedule_ui_task`
  ```python
  def update_status(self, status_string):
      # Called from hunt_orchestrator via schedule_ui_task
      self.status_label.config(text=status_string)
      # Update badge color based on status
  ```
- Method `update_hp_display(hp_percent: float)`: Cập nhật Progressbar HP từ `target_hp_reader.py`
  ```python
  def update_hp_display(self, hp_percent):
      # Called from hunt_orchestrator via schedule_ui_task
      self.hp_progressbar.config(value=hp_percent)
      self.hp_label.config(text=f"HP: {hp_percent:.1f}%")
  ```
- Method `clear_target_card()`: Xóa card với delay (gọi từ orchestrator sau 0.2s TARGET_DEAD)

**Không thay đổi cấu trúc hiện có từ UX5.1.**

### 4. Đồng bộ Trạng thái & Main Thread Gate
- Trong `HuntOrchestrator`:
  - Khi khóa mục tiêu mới nhưng máu chưa giảm: Bắn trạng thái `APPROACHING` lên UI.
  - Khi máu bắt đầu giảm hoặc cast skill: Bắn trạng thái `ATTACKING` và cập nhật % thanh máu.
  - Khi máu = 0%: Bắn trạng thái `TARGET_DEAD`, lên lịch xóa Target Card sau 0.2s và reset về `Idle`.
    - **Race condition khi đổi mục tiêu nhanh:** nếu một mục tiêu mới được khóa trong vòng 0.2s kể từ khi lên lịch xóa (kill liên tiếp), phải huỷ lịch xóa cũ (`self.after_cancel(pending_clear_id)`) trước khi hiển thị card mới, để không xóa nhầm card của mục tiêu mới vừa khóa.
  - Đảm bảo thứ tự các lệnh cập nhật trạng thái (`APPROACHING` → `ATTACKING` → `TARGET_DEAD`) tới UI theo đúng thứ tự phát sinh — đẩy qua một hàng đợi tuần tự duy nhất (hoặc dùng `schedule_ui_task` theo đúng thứ tự gọi, không chạy song song), tránh trường hợp `ATTACKING` hiển thị sau `TARGET_DEAD` do interleaving giữa các luồng.
- **Bắt buộc:** Mọi thao tác cập nhật Label/Progressbar/Ảnh phải gọi qua `self.schedule_ui_task(lambda: ...)` hoặc `self.after(0, ...)`, và các lambda này chỉ nhận dữ liệu đã tính toán xong (số %, đường dẫn ảnh đã resolve, text trạng thái) — không thực hiện I/O hay xử lý ảnh/OpenCV bên trong lambda.

---

## Validation & Testing (Building on UX5.1 Test Suite)
**Assumption:** UX5.1 Phase 1 tests (8 tests) are PASSING. Do NOT re-test UX5.1 functionality.

**CB4A adds 6 new tests** (total test suite becomes 14 tests when merged):
- Test Case 1 (Valid Monster): Khóa mục tiêu quái có trong DB -> Assert hiển thị đúng ảnh, tên, chỉ số HP.
- Test Case 2 (Missing Asset / Unlisted Mob): Khóa mục tiêu quái không có ảnh hoặc quái lạ -> Assert load fallback icon an toàn, không ném exception, và `is_placeholder: True` được set đúng khi dùng dict mặc định.
- Test Case 3 (Combat Transition): Giả lập HP giảm từ 100% -> 50% -> 0% -> Assert thanh máu trượt mượt và thẻ quái tự dọn dẹp khi chết.
- (Added) Test Case 4 (Rapid Re-target Race): Giả lập `TARGET_DEAD` rồi khóa mục tiêu mới trong vòng 0.2s -> Assert lịch xóa card cũ bị huỷ và card mới không bị xóa nhầm.
- (Added) Test Case 5 (Placeholder HP not leaking into logic): Giả lập quái không có trong DB/JSON -> Assert bất kỳ module tiêu thụ `get_target_monster_info()` khác (nếu có trong scope test) bỏ qua giá trị `hp: 10000` khi `is_placeholder == True`.
- (Added) Test Case 6 (No duplicate HP-reading logic): Assert `calculate_target_hp_percent()` gọi vào `TargetBarDetector.get_hp_percentage()` (VD: qua mock/spy) thay vì chứa logic đọc pixel độc lập.

## Session Boundary Gate: **PHASE 2 COMPLETION CRITERIA**

**PREREQUISITE CHECK (before testing CB4A):**
- ✅ Confirm UX5.1 Phase 1 tests are all PASSING
- ✅ Confirm `get_target_monster_info()` is deployed and working
- ✅ Confirm Target Card Panel UI is rendering correctly at DPI 100%-200%
- 🚫 If UX5.1 not PASSED: Do NOT proceed to CB4A. REVERTED.

- **PASSED nếu:**
  * HP% updates smoothly (no jitter) with 150-200ms throttle
  * Status transitions (APPROACHING → ATTACKING → DEAD) occur in correct order
  * Race condition fixed: rapid re-target doesn't clear new card (verified via `after_cancel()`)
  * Không gọi bất kỳ phương thức widget Tkinter nào từ background thread
  * `calculate_target_hp_percent()` tái sử dụng logic CB1 (verified via spy/mock)
  * Vượt qua cả 6 test cases mới của CB4A
  * Merged test suite (UX5.1 8 tests + CB4A 6 tests = 14 total) all PASSING

- **REVERTED nếu:**
  * Lỗi crash do missing file ảnh hoặc truy vấn DB thất bại (should be handled by UX5.1)
  * Race condition: rapid re-target clears new card (pending_clear_id not cancelled properly)
  * HP đọc trùng lặp logic CB1 hoặc implement pixel-reading độc lập
  * UX5.1 Phase 1 tests fail after CB4A changes (regression)
  * Any UX5.1 functionality broken by CB4A modifications

---

## 📋 Summary: CB4A Phase 2 Inheritance from UX5.1 Phase 1

**Không viết lại/không định nghĩa lại:**
| Component | Status | Location | CB4A Action |
|-----------|--------|----------|-------------|
| `get_target_monster_info()` | ✅ Implemented | `lib/features/monsters/monster_repo.py` | **CALL, not redefine** |
| Target Card Panel UI | ✅ Implemented | `ui/tabs/hunt_tab.py` | **EXTEND with new methods** |
| PhotoImage lifecycle | ✅ Implemented | `ui/tabs/hunt_tab.py` | **Use existing pattern** |
| i18n keys `target_card.*` | ✅ Registered | `lib/i18n/translations.py` | **Use shared keys** |
| Schema + `is_placeholder` flag | ✅ Defined | `get_target_monster_info()` result | **Use as-is** |

**Riêng CB4A triển khai:**
| Component | Files | Purpose |
|-----------|-------|---------|
| `calculate_target_hp_percent()` | `lib/vision/target_hp_reader.py` | Wrap CB1, add throttle + smooth |
| Status FSM | `hunt_orchestrator.py` | Track APPROACHING/ATTACKING/DEAD |
| Race condition handler | `hunt_orchestrator.py` | Cancel pending clear on rapid re-target |
| New test suite | `tests/unit/test_target_card_cb4a.py` | 6 new tests for Phase 2 features |

**Merged Test Suite (Final):**
- UX5.1 tests: 8 tests (schema fallback, memory stability, DPI rendering)
- CB4A tests: 6 tests (HP transitions, rapid re-target, race condition handling)
- **Total: 14 tests passing = Feature complete**

**Decision:** Sequential 2-phase implementation is **SAFER** than parallel/combined:
- ✅ Phase 1 (UX5.1) risk: LOW (isolated foundation)
- ✅ Phase 2 (CB4A) risk: LOWER (builds on proven foundation)
- ❌ Combined risk: HIGHER (harder to isolate bugs)