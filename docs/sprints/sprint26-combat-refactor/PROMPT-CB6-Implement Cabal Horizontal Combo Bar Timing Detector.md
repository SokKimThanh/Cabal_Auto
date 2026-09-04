# Session Prompt CB6: Implement Cabal Horizontal Combo Bar Timing Detector

**Date**: 2026-09-04  
**Timebox**: 25–30 minutes  
**Priority**: High – Enables 20+ hit combo streak without breaking  

---

## Project Context Update

**Status as of 2026-09-04:**
- ✅ **Hunt Workspace Redesign Documentation COMPLETE**
  - WORKSPACE-REDESIGN-UI-DESIGN.md: 4-panel layout architecture (Monster Target, Skill Panel, Target & Status, Skill Stats)
  - WORKSPACE-REDESIGN-LOGIC-DESIGN.md: Data model, preset system, state management
  - **NEW Section 11**: Comprehensive 3-screen specification:
    - SCREEN 1: Combo Panel (Skill Panel in Hunt Tab) — 11.2
    - SCREEN 2: Skill Build Tab (Skill preset builder) — 11.3
    - SCREEN 3: CRUD Skill Tab (Skill management) — 11.4

- ⏳ **In-Progress Work**:
  - Build Skills Tab — NOT YET CREATED (Separate tab in notebook)
  - CRUD Skill Tab — NOT YET CREATED (Separate tab in notebook)
  - Skill Build Panel — NOT YET CREATED (Part of Build Skills Tab)
  - Combo Panel (Skill Panel) — EXISTS but needs enhancement per Section 11.2
  - Database schema: skill_presets, preset_skills, user_preset_state tables — DOCUMENTED
  - AppStateController: Enhanced with combo mode support — DOCUMENTED

- ✅ **Database Schema Ready**:
  - classes, skills, class_skill_assignments (existing)
  - skill_presets, preset_skills, user_preset_state (documented)
  - See: WORKSPACE-REDESIGN-LOGIC-DESIGN.md § 2 (Database Schema)

- ✅ **State Management Ready**:
  - AppStateController._combo_mode_active property
  - AppStateController.activate_combo_mode() / deactivate_combo_mode() methods
  - See: WORKSPACE-REDESIGN-LOGIC-DESIGN.md § 3.2 (AppStateController)

---

## Objective
Tạo module chuyên dụng `lib/features/combo/combo_timing_detector.py` để theo dõi thanh Combo Bar nằm ngang của Cabal (vị trí ngay dưới thanh máu Target Bar ở đỉnh giữa màn hình). Module phát hiện chính xác thời điểm vạch sáng di chuyển chạm vào vùng 2 vạch (hit-zone sweet spot) và kích hoạt phím kỹ năng, với độ trễ thực tế bị giới hạn bởi tần suất capture của `ScreenCapture` (xem mục 1) chứ không chỉ bởi `poll_interval_ms`, mà không gây nghẽn CPU hay spam phím đúp.

**NOTE**: CB6 phụ thuộc vào Combo Panel (Screen 1) trong Hunt Tab được cấu trúc lại theo WORKSPACE-REDESIGN-LOGIC-DESIGN.md § 11.2. Combo Panel cần có:
- Status indicator: 🔴 INACTIVE / 🟢 ACTIVE
- Start/Stop buttons: [▶️ START COMBO MODE] / [⏹️ STOP COMBO MODE]
- Hotkey assignment UI: Per-slot [Hotkey: X▼] dropdowns
- Cooldown display: "Skill (X.Xs)" or "Skill (Ready)"

## Target Files
- Create: `lib/features/combo/combo_timing_detector.py` — Detector module (NEW)
- Create: `lib/features/combo/__init__.py` — Package init (NEW)
- Modify: `lib/system/screen_capture.py` — Add `get_latest_frame()` method (EXISTING)
- Modify: `lib/features/hunt/hunt_orchestrator.py` — Integrate detector (EXISTING)
- Modify: `lib/data/hunt_config.json` — Add combo config section (EXISTING)
- Create Test: `tests/unit/test_combo_timing_detector.py` — Unit tests (NEW)

**Related Files** (Reference only, NOT modified by CB6):
- `ui/tabs/hunt_tab.py` — Combo Panel UI (will be enhanced in separate session)
- `lib/db/schema.py` — Database tables (already documented, not modified here)

---

## Implementation Details

### 1. Nâng cấp Bộ đệm `ScreenCapture` (`lib/system/screen_capture.py`)
- Thêm thuộc tính `self._latest_frame = None` được cập nhật mỗi khi chụp frame mới (từ `_capture_loop()`, đã có buffer-realloc/minimize-handling theo CB5).
- Thêm phương thức `get_latest_frame() -> Optional[np.ndarray]`:
  - Trả về **bản copy** (`self._latest_frame.copy()` nếu không `None`) của frame mới nhất đang có trong bộ đệm, không phải tham chiếu trực tiếp tới mảng đang được `_capture_loop()` ghi đè ở thread khác. Việc này tránh torn-read khi một thread khác đang ghi buffer đúng lúc `wait_for_hit_zone()` đang đọc. Copy một ROI nhỏ (không phải cả frame) là đủ rẻ để không ảnh hưởng tới ngân sách 4ms polling.
  - Không làm rỗng hàng đợi hoặc block, giúp vòng lặp tốc độ cao poll liên tục mà không tốn CPU.
  - Ghi chú giới hạn thực tế: độ chính xác thời điểm phát hiện hit-zone bị giới hạn bởi tần suất frame thực sự mới của `_capture_loop()` (ví dụ nếu capture chạy ~60fps thì frame mới chỉ xuất hiện mỗi ~16.6ms bất kể `poll_interval_ms` nhỏ tới đâu). Mục tiêu "<5ms" trong Objective là độ trễ *xử lý sau khi có frame mới*, không phải độ trễ tuyệt đối kể từ thời điểm vạch sáng thực sự chạm hit-zone.

### 2. Lớp `CabalComboDetector` (`lib/features/combo/combo_timing_detector.py`)
- Constructor:
  ```python
  def __init__(self, hwnd: int,
               y_ratio_range: tuple = (0.052, 0.062),
               x_ratio_range: tuple = (0.415, 0.585),
               hit_zone_x_ratio: float = 0.78,
               poll_interval_ms: int = 4,
               cooldown_guard_ms: int = 120,
               key_press_callback: callable = None):
  ```
  - `cooldown_guard_ms`: thời gian đóng băng sau khi bấm phím (mặc định 120ms) để chống bấm đúp khi vạch sáng lướt qua.

- Phương thức `wait_for_hit_zone(screen_capture, timeout_sec: float = None, is_target_alive_check: callable = None) -> bool`:
  - `timeout_sec`: nếu `None`, đọc từ `cfg["combo"]["hit_zone_timeout_sec"]` (mặc định `2.0`, đồng bộ với giá trị đã chốt ở CB3C — không dùng lại `2.5` như một bản nháp trước đó của file này).
  - Liên tục lấy frame qua `screen_capture.get_latest_frame()`. Nếu `frame is None`, sleep `poll_interval_ms` và tiếp tục.
  - Cắt ROI thanh Combo Bar, kiểm tra cột pixel tại tọa độ `hit_zone_x_ratio`.
  - Nếu phát hiện vạch sáng (HSV Value > 210 — giá trị khởi điểm cần hiệu chỉnh thực nghiệm theo theme UI/độ sáng màn hình của client, không coi là hằng số tuyệt đối đúng mọi cấu hình):
    - Gọi `key_press_callback()` để gửi phím skill và trả transport result (`SENT`/`FAILED`). Không coi callback không ném exception là game đã nhận skill.
    - Không gọi `mark_cast()` hoặc tăng rotation pointer ngay sau `SENT`. CB3D sở hữu bước hậu kiểm; chỉ acknowledgment `ACCEPTED` mới commit cooldown/pointer/stats. CB6 chỉ phát `TRIGGER_READY` và transport evidence.
    - Thay vì `time.sleep(cooldown_guard_ms / 1000.0)` một khối liền mạch, chia cooldown-guard thành các lát nhỏ (~20-30ms mỗi lát, tổng cộng đủ `cooldown_guard_ms`), và nếu có truyền `is_target_alive_check` (thường là `target_bar_detector.is_target_alive`), kiểm tra sau mỗi lát: nếu mục tiêu đã chết giữa lúc cooldown-guard đang chạy, thoát sớm khỏi cooldown-guard và trả về `True` ngay để nhường quyền cho luồng fast-break (CB3) xử lý, thay vì buộc chờ đủ 120ms mới được ngắt.
  - Trả về `False` khi chạm ngưỡng `timeout_sec`.

### 3. Cấu hình Schema (`lib/data/hunt_config.json`)
Thêm cấu hình trong phần `hunt_config` hoặc tạo section `combo` riêng:
```json
"combo": {
  "enabled": true,
  "combo_start_key": "alt+3",
  "hit_zone_x_ratio": 0.78,
  "hit_zone_timeout_sec": 2.0,
  "poll_interval_ms": 4,
  "cooldown_guard_ms": 120
}
```
(Lưu ý: `hit_zone_timeout_sec` là field đã được CB3C tham chiếu — session này chỉ hiện thực hoá, không đổi giá trị mặc định.)

### 4. Tích hợp vào Vòng lặp Chiến đấu (Hunt Loop)
Trong `HuntOrchestrator.worker()` / `HuntRunner._try_cast_skills()`:
- Nếu `combo.enabled` là `True`: nhấn `combo_start_key` **đúng một lần** khi Combo Mode bắt đầu cho một lượt mục tiêu mới (ví dụ tại thời điểm khoá mục tiêu mới hoặc khi combo mode vừa được bật) — không nhấn lại `combo_start_key` ở mỗi vòng lặp rotation bên trong cùng một lượt combo, tránh spam phím kích hoạt.
- Trước khi gửi phím skill tiếp theo trong chuỗi xoay tua, gọi `wait_for_hit_zone()` (truyền kèm `is_target_alive_check` để hỗ trợ ngắt sớm) để căn đúng nhịp vạch vào vùng 2 vạch. Trả trigger/transport evidence cho CB3D; không commit cast tại detector.
- Khi quái chết giữa chừng (Fast-Break qua `TargetBarDetector`, theo CB3): ngắt ngay vòng lặp chờ combo (kể cả nếu đang trong cooldown-guard, theo mục 2), nhấn phím `Z` để bắt mục tiêu mới.

### 5. Ghi chú Tích hợp với Preset System (WORKSPACE-REDESIGN)
- CB6 hoạt động **độc lập với preset system** (Screens 2-3 sẽ build/manage presets).
- CB6 chỉ cần biết:
  - Kỹ năng nào đang active trong combo: từ `AppStateController.skill_slots`
  - Phím tắt cho kỹ năng: từ `AppStateController.skill_slots[lane][position].user_hotkey`
  - Combo mode status: từ `AppStateController._combo_mode_active`
- CB6 không thay đổi `skill_slots` hoặc preset state, chỉ phát detect event cho orchestrator xử lý.

## Validation & Testing

Unit Test (`tests/unit/test_combo_timing_detector.py`):
- Đưa vào frame giả lập chứa cột pixel sáng: Assert callback chỉ được kích hoạt duy nhất 1 lần (nhờ Cooldown Guard).
- Test hiệu năng CPU: Chạy vòng lặp 4ms trong 10 giây với `get_latest_frame()` → Assert mức chiếm dụng CPU duy trì < 2%.
- (Added) Test `get_latest_frame()` trả về bản copy độc lập: sửa đổi mảng trả về, assert buffer nội bộ của `ScreenCapture` không bị ảnh hưởng (xác nhận không phải tham chiếu chung).
- (Added) Test ngắt sớm cooldown-guard khi target chết: giả lập `is_target_alive_check` trả `False` giữa lúc cooldown-guard đang chạy (sau lát thứ 2 trong ví dụ 120ms/~25ms mỗi lát), assert `wait_for_hit_zone()` thoát sớm thay vì chờ đủ 120ms.
- (Added) Test hit-zone chỉ phát một `TRIGGER_READY`; transport `SENT` không gọi `mark_cast()` hoặc tăng rotation index trước CB3D acknowledgment.
- (Added) Test `combo_start_key` chỉ được gửi một lần mỗi lượt mục tiêu mới, không lặp lại trong vòng rotation của cùng lượt combo đó.

## Dependencies & Prerequisites

- ✅ ScreenCapture class: Exists in `lib/system/screen_capture.py` (modify only)
- ✅ HuntOrchestrator class: Exists in `lib/features/hunt/hunt_orchestrator.py` (integrate only)
- ✅ Database schema: Documented in WORKSPACE-REDESIGN-LOGIC-DESIGN.md § 2
- ✅ AppStateController: Enhanced, documented in WORKSPACE-REDESIGN-LOGIC-DESIGN.md § 3.2
- ⏳ Combo Panel UI: Will be in `ui/tabs/hunt_tab.py` (separate session)
- ⏳ Build Skills Tab: Will be created in `ui/tabs/build_skills_tab.py` (separate session)
- ⏳ CRUD Skill Tab: Will be created in `ui/tabs/crud_skill_tab.py` (separate session)

**For detailed Combo Panel design reference**, see:
- WORKSPACE-REDESIGN-LOGIC-DESIGN.md § 11.2 — Combo Panel specification
- WORKSPACE-REDESIGN-UI-DESIGN.md § 13 — Cross-screen architecture reference

## Session Boundary Gate

**PASSED nếu:**
- Module import bình thường, vượt qua unit test không bị double-press.
- Tọa độ ROI khớp chính xác với thanh Combo Bar ở DPI 100%-150%.
- Không làm nghẽn Main Thread Tkinter.
- `hit_zone_timeout_sec` đọc từ config, khớp giá trị đã chốt ở CB3C (không có giá trị mặc định lệch trong code).
- Cooldown-guard có thể bị ngắt sớm khi target chết, không chặn fast-break tới 120ms.
- Detector không gọi `mark_cast()`; CB3D là nơi commit sau acknowledgment.
- Integration test: Orchestrator gọi `wait_for_hit_zone()` trước mỗi skill cast khi combo mode active.

**REVERTED nếu:**
- Xuất hiện tình trạng spam phím đúp hoặc tràn bộ nhớ GDI.
- `get_latest_frame()` trả về tham chiếu dùng chung gây torn-read.
- Báo cáo kết quả PASSED/REVERTED ở phút thứ 25.

---

## Implementation Details

### 1. Nâng cấp Bộ đệm `ScreenCapture` (`lib/system/screen_capture.py`)
- Thêm thuộc tính `self._latest_frame = None` được cập nhật mỗi khi chụp frame mới (từ `_capture_loop()`, đã có buffer-realloc/minimize-handling theo CB5).
- Thêm phương thức `get_latest_frame() -> Optional[np.ndarray]`:
  - Trả về **bản copy** (`self._latest_frame.copy()` nếu không `None`) của frame mới nhất đang có trong bộ đệm, không phải tham chiếu trực tiếp tới mảng đang được `_capture_loop()` ghi đè ở thread khác. Việc này tránh torn-read khi một thread khác đang ghi buffer đúng lúc `wait_for_hit_zone()` đang đọc. Copy một ROI nhỏ (không phải cả frame) là đủ rẻ để không ảnh hưởng tới ngân sách 4ms polling.
  - Không làm rỗng hàng đợi hoặc block, giúp vòng lặp tốc độ cao poll liên tục mà không tốn CPU.
  - Ghi chú giới hạn thực tế: độ chính xác thời điểm phát hiện hit-zone bị giới hạn bởi tần suất frame thực sự mới của `_capture_loop()` (ví dụ nếu capture chạy ~60fps thì frame mới chỉ xuất hiện mỗi ~16.6ms bất kể `poll_interval_ms` nhỏ tới đâu). Mục tiêu "<5ms" trong Objective là độ trễ *xử lý sau khi có frame mới*, không phải độ trễ tuyệt đối kể từ thời điểm vạch sáng thực sự chạm hit-zone.

### 2. Lớp `CabalComboDetector` (`lib/features/combo/combo_timing_detector.py`)
- Constructor:
  ```python
  def __init__(self, hwnd: int,
               y_ratio_range: tuple = (0.052, 0.062),
               x_ratio_range: tuple = (0.415, 0.585),
               hit_zone_x_ratio: float = 0.78,
               poll_interval_ms: int = 4,
               cooldown_guard_ms: int = 120,
               key_press_callback: callable = None):
  ```
  - `cooldown_guard_ms`: thời gian đóng băng sau khi bấm phím (mặc định 120ms) để chống bấm đúp khi vạch sáng lướt qua.

- Phương thức `wait_for_hit_zone(screen_capture, timeout_sec: float = None, is_target_alive_check: callable = None) -> bool`:
  - `timeout_sec`: nếu `None`, đọc từ `cfg["combo"]["hit_zone_timeout_sec"]` (mặc định `2.0`, đồng bộ với giá trị đã chốt ở CB3C — không dùng lại `2.5` như một bản nháp trước đó của file này).
  - Liên tục lấy frame qua `screen_capture.get_latest_frame()`. Nếu `frame is None`, sleep `poll_interval_ms` và tiếp tục.
  - Cắt ROI thanh Combo Bar, kiểm tra cột pixel tại tọa độ `hit_zone_x_ratio`.
  - Nếu phát hiện vạch sáng (HSV Value > 210 — giá trị khởi điểm cần hiệu chỉnh thực nghiệm theo theme UI/độ sáng màn hình của client, không coi là hằng số tuyệt đối đúng mọi cấu hình):
    - Gọi `key_press_callback()` để gửi phím skill và trả transport result (`SENT`/`FAILED`). Không coi callback không ném exception là game đã nhận skill.
    - Không gọi `mark_cast()` hoặc tăng rotation pointer ngay sau `SENT`. CB3D sở hữu bước hậu kiểm; chỉ acknowledgment `ACCEPTED` mới commit cooldown/pointer/stats. CB6 chỉ phát `TRIGGER_READY` và transport evidence.
    - Thay vì `time.sleep(cooldown_guard_ms / 1000.0)` một khối liền mạch, chia cooldown-guard thành các lát nhỏ (~20-30ms mỗi lát, tổng cộng đủ `cooldown_guard_ms`), và nếu có truyền `is_target_alive_check` (thường là `target_bar_detector.is_target_alive`), kiểm tra sau mỗi lát: nếu mục tiêu đã chết giữa lúc cooldown-guard đang chạy, thoát sớm khỏi cooldown-guard và trả về `True` ngay để nhường quyền cho luồng fast-break (CB3) xử lý, thay vì buộc chờ đủ 120ms mới được ngắt.
  - Trả về `False` khi chạm ngưỡng `timeout_sec`.

### 3. Cấu hình Schema (`lib/data/hunt_config.json`)
Thêm cấu hình:
```json
"combo": {
  "enabled": true,
  "combo_start_key": "alt+3",
  "hit_zone_x_ratio": 0.78,
  "hit_zone_timeout_sec": 2.0,
  "poll_interval_ms": 4,
  "cooldown_guard_ms": 120
}
```
(Lưu ý: `hit_zone_timeout_sec` là field đã được CB3C tham chiếu — session này chỉ hiện thực hoá, không đổi giá trị mặc định.)

### 4. Tích hợp vào Vòng lặp Chiến đấu (Hunt Loop)
Trong `HuntOrchestrator.worker()` / `HuntRunner._try_cast_skills()`:
- Nếu `combo.enabled` là `True`: nhấn `combo_start_key` **đúng một lần** khi Combo Mode bắt đầu cho một lượt mục tiêu mới (ví dụ tại thời điểm khoá mục tiêu mới hoặc khi combo mode vừa được bật) — không nhấn lại `combo_start_key` ở mỗi vòng lặp rotation bên trong cùng một lượt combo, tránh spam phím kích hoạt.
- Trước khi gửi phím skill tiếp theo trong chuỗi xoay tua, gọi `wait_for_hit_zone()` (truyền kèm `is_target_alive_check` để hỗ trợ ngắt sớm) để căn đúng nhịp vạch vào vùng 2 vạch. Trả trigger/transport evidence cho CB3D; không commit cast tại detector.
- Khi quái chết giữa chừng (Fast-Break qua `TargetBarDetector`, theo CB3): ngắt ngay vòng lặp chờ combo (kể cả nếu đang trong cooldown-guard, theo mục 2), nhấn phím `Z` để bắt mục tiêu mới.

## Validation & Testing

Unit Test (`tests/unit/test_combo_timing_detector.py`):
- Đưa vào frame giả lập chứa cột pixel sáng: Assert callback chỉ được kích hoạt duy nhất 1 lần (nhờ Cooldown Guard).
- Test hiệu năng CPU: Chạy vòng lặp 4ms trong 10 giây với `get_latest_frame()` → Assert mức chiếm dụng CPU duy trì < 2%.
- (Added) Test `get_latest_frame()` trả về bản copy độc lập: sửa đổi mảng trả về, assert buffer nội bộ của `ScreenCapture` không bị ảnh hưởng (xác nhận không phải tham chiếu chung).
- (Added) Test ngắt sớm cooldown-guard khi target chết: giả lập `is_target_alive_check` trả `False` giữa lúc cooldown-guard đang chạy (sau lát thứ 2 trong ví dụ 120ms/~25ms mỗi lát), assert `wait_for_hit_zone()` thoát sớm thay vì chờ đủ 120ms.
- (Added) Test hit-zone chỉ phát một `TRIGGER_READY`; transport `SENT` không gọi `mark_cast()` hoặc tăng rotation index trước CB3D acknowledgment.
- (Added) Test `combo_start_key` chỉ được gửi một lần mỗi lượt mục tiêu mới, không lặp lại trong vòng rotation của cùng lượt combo đó.

## Session Boundary Gate

**PASSED nếu:**
- Module import bình thường, vượt qua unit test không bị double-press.
- Tọa độ ROI khớp chính xác với thanh Combo Bar ở DPI 100%-150%.
- Không làm nghẽn Main Thread Tkinter.
- `hit_zone_timeout_sec` đọc từ config, khớp giá trị đã chốt ở CB3C (không có giá trị mặc định lệch trong code).
- Cooldown-guard có thể bị ngắt sớm khi target chết, không chặn fast-break tới 120ms.
- Detector không gọi `mark_cast()`; CB3D là nơi commit sau acknowledgment.
- Integration test: Orchestrator gọi `wait_for_hit_zone()` trước mỗi skill cast khi combo mode active.

**REVERTED nếu:**
- Xuất hiện tình trạng spam phím đúp hoặc tràn bộ nhớ GDI.
- `get_latest_frame()` trả về tham chiếu dùng chung gây torn-read.
- Báo cáo kết quả PASSED/REVERTED ở phút thứ 25.

---

## Appendix A: Documentation Reference

### Primary Documents
- **WORKSPACE-REDESIGN-LOGIC-DESIGN.md** — Complete logic specification
  - § 2: Database Schema (skill_presets, preset_skills, user_preset_state tables)
  - § 3.2: AppStateController with combo mode support
  - § 5.6: Hotkey assignment & skill selection workflow
  - § 5.7: Combo mode activation & execution workflow
  - § 11.2: Combo Panel detailed UI specification
  - § 11.5: Three-screen integration & data flow

- **WORKSPACE-REDESIGN-UI-DESIGN.md** — UI layout & design
  - § 2: 4-panel layout architecture
  - § 11: Skill Panel component details
  - § 13: Three-screen architecture reference

### Implementation Sequence (Current Sprint)
```
Session CB6 (THIS)
  └─ Create combo_timing_detector.py module
  └─ Enhance ScreenCapture.get_latest_frame()
  └─ Integrate with HuntOrchestrator
  └─ Add combo config to hunt_config.json
     
Next Sessions (Planned)
  └─ Build Skills Tab (Screen 2) — Tab UI + logic
  └─ CRUD Skill Tab (Screen 3) — Tab UI + logic
  └─ Combo Panel enhancements (Screen 1) — Status, buttons, hotkeys
  └─ Database service layer — SkillPresetService, SkillRepository
  └─ Integration testing & tuning
```

### Project Structure Context
```
lib/
├─ features/
│  ├─ combo/  (CB6 creates this)
│  │  ├─ __init__.py
│  │  └─ combo_timing_detector.py
│  ├─ hunt/
│  │  ├─ hunt_orchestrator.py (CB6 modifies)
│  │  ├─ hunt_runner.py
│  │  └─ ...
│  └─ skills/  (Future: SkillPresetService)
├─ system/
│  └─ screen_capture.py (CB6 modifies)
├─ db/
│  └─ schema.py (Database tables — already documented)
└─ data/
   └─ hunt_config.json (CB6 modifies)

ui/
├─ tabs/
│  ├─ hunt_tab.py (Combo Panel — future enhancement)
│  ├─ build_skills_tab.py (Screen 2 — future)
│  ├─ crud_skill_tab.py (Screen 3 — future)
│  └─ ...
└─ ...

tests/
└─ unit/
   └─ test_combo_timing_detector.py (CB6 creates)
```

### Quick Links to Key Sections
| Topic | Document | Section |
|-------|----------|---------|
| Combo Panel UI | LOGIC-DESIGN | 11.2 |
| Skill Build Tab | LOGIC-DESIGN | 11.3 |
| CRUD Skill Tab | LOGIC-DESIGN | 11.4 |
| Integration | LOGIC-DESIGN | 11.5 |
| Hunt Layout | UI-DESIGN | 2 & 11 |
| Database Schema | LOGIC-DESIGN | 2 |
| AppState Combo | LOGIC-DESIGN | 3.2 |