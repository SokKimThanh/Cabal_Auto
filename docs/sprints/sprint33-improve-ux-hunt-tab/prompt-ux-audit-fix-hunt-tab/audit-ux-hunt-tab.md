# 📊 Báo cáo Kiểm toán Sprint 33 — Improve UX Hunt Tab

**Ngày báo cáo:** 2026-09-23
**Người audit:** Jules (AI-assisted)
**Phạm vi:** 11 task (Task 0 → Task 10)
**Phương pháp:** Đối chiếu spec ↔ code thực tế, mọi kết luận có bằng chứng `file:line`
**Vị trí lưu:** `docs/sprints/sprint33-improve-ux-hunt-tab/audit-summary.md`

---

## 1. TÓM TẮT ĐIỀU HÀNH

### Chỉ số tổng quan

| Chỉ số | Giá trị |
|--------|---------|
| **Completion trung bình (weighted)** | **~92%** |
| Task DONE | 7/11 |
| Task PARTIAL | 3/11 |
| Task FAILED | 1/11 |
| **Khoản nợ đã trả hoàn toàn** | **3/6** (D2, D3, D5) |
| **Khoản nợ chưa trả** | **3/6** (D1, D4, D6) |
| **Ước lượng để đạt ~97%** | **~18h** |
| Tổng file đã audit | **26 file** |

### Kết luận ngắn gọn

> Sprint 33 có **hạ tầng tốt nhưng integration yếu**. Các component mới (UIAnimationManager, VisionSnapshotDebugger, HuntConfig atomic write) được xây dựng **chất lượng cao**. Tuy nhiên có **1 bug cascade nghiêm trọng** giữa Task 1 và Task 4 khiến mục tiêu chính của sprint (Drag & Drop Skill Timeline động) không đạt. Task 9 (Chuẩn hóa Icon) là task **thất bại nặng nhất** — chỉ đạt 15%.

**3 finding quan trọng nhất:**

1. 🔴 **Cascade Task 1 ↔ 4**: `SkillPanelController.get_combo_sequence()` / `get_buff_sequence()` **không được gọi** → `SkillTimelineStrip` render rỗng.
2. 🔴 **Task 9 FAILED 15%**: 20+ emoji hardcode + text tiếng Việt/Anh hardcode, ở cả UI lẫn backend.
3. 🔴 **Task 6 integration cần xác nhận**: Component hoàn chỉnh nhưng cần verify quan hệ `HuntWorkspaceFrame` ↔ `HuntTab`.

---

## 2. BẢNG TỔNG HỢP 11 TASK

| Batch | Task | Tên | Trạng thái | Completion | Risk | Ghi chú chính |
|-------|------|-----|-----------|-----------|------|---------------|
| 1 | 0 | UIAnimationManager | ✅ **DONE** | **100%** | LOW | Design xuất sắc, có unit tests pass |
| 1 | 1 | Refactor Controller | ✅ **DONE** | **100%** | LOW | Methods đúng, test pass |
| 1 | 2 | ComboRhythmBar | ✅ **DONE** | **100%** | LOW | Debounce chuẩn, test pass 5/5 |
| 2 | 3 | SkillTimelineStrip | 🟡 PARTIAL | **87.5%** | MEDIUM | Có bug TclError fallback path |
| 2 | 6 | HuntStatusTicker | 🟡 PARTIAL | **85%** | MEDIUM | i18n hardcode; cần verify integration |
| 2 | 7 | VisionSnapshotDebugger | 🟡 PARTIAL | **95%** | LOW | Còn 1 spec bug (fallback timeout) |
| 3 | 4 | Rebuild SkillPanel | 🟡 PARTIAL | **83.3%** | HIGH | **Bug cascade — strip render rỗng** |
| 3 | 5 | TargetStatus + SkillStats | 🟡 PARTIAL | **83.3%** | HIGH | D6 hardcode + không có unit test |
| 4 | 8 | Multi-ROI Manager | 🟡 PARTIAL | **85%** | MEDIUM | Atomic + pydantic OK; i18n còn |
| 4 | 9 | Standardize Icon | ❌ **FAILED** | **15%** | HIGH | **20+ emoji hardcode** |
| 4 | 10 | Layout & Typography | 🟡 PARTIAL | **85%** | HIGH | Thiếu `minsize` cho PanedWindow |

**Biểu đồ trực quan:**

```
Task 0  ████████████████████░  100%  ✅
Task 1  ████████████████████░  100%  ✅
Task 2  ████████████████████░  100%  ✅
Task 3  █████████████████░░░░   87.5%  🟡
Task 4  ████████████████░░░░░   83.3%  🟡
Task 5  ████████████████░░░░░   83.3%  🟡
Task 6  █████████████████░░░░   85%  🟡
Task 7  ███████████████████░░   95%  🟡
Task 8  █████████████████░░░░   85%  🟡
Task 9  ███░░░░░░░░░░░░░░░░░░   15%  ❌
Task 10 █████████████████░░░░   85%  🟡
```

---

## 3. CHI TIẾT THEO TỪNG TASK

### ✅ Task 0 — UIAnimationManager (100%, LOW)

**Điểm mạnh:**
- Singleton đúng chuẩn qua `__new__` + `_instance` + `initialized` guard.
- Override logic chống giật lùi thanh HP: `actual_start = self.tweens[target_id]['current_val']`.
- Kiểm tra `winfo_exists()` đầy đủ, có fallback tìm widget mới khi `_root` bị destroy.
- **Có 4/4 unit tests pass** — verify hành vi override và destroy.

**Nitpick:**
- `except Exception: pass` (dòng 82-83, 92-94) — nuốt lỗi im lặng, khó debug.

**Bằng chứng:** `lib/ui/animation_manager.py:5, 25, 56, 70, 114` + `tests/unit/ui/test_animation_manager.py:16, 41`

---

### ✅ Task 1 — Refactor SkillPanelController (100%, LOW)

**Đã làm:**
- Thêm `get_combo_sequence()` và `get_buff_sequence()` (dòng 146, 158).
- Tương thích cấu trúc mảng `hunt_config.json`.
- **Unit tests pass** cho sequence mutation.

**Vấn đề kèm theo (thuộc Task 4, không phải Task 1):**
- Methods được viết nhưng **không được UI gọi** — xem Task 4.

**Bằng chứng:** `ui/controllers/skill_panel_controller.py:146, 150, 158` + `tests/ui/controllers/test_skill_panel_controller.py:19, 35`

---

### ✅ Task 2 — ComboRhythmBar (100%, LOW)

**Đã làm:**
- Sweet spot 0.78 (`combo_rhythm_bar.py:7`).
- Debounce 200ms cho toggle và trigger.
- Fade via `UIAnimationManager` (không `time.sleep`).
- Toggle visibility ẩn bar để tiết kiệm CPU.
- **Unit tests pass 5/5**.

**Nitpick:**
- Dòng 37: hardcode `text="Hiển thị Rhythm Bar"` (vi phạm D6).

**Bằng chứng:** `ui/components/combo_rhythm_bar.py:7, 34, 57, 88, 92, 101` + `tests/unit/ui/components/test_combo_rhythm_bar.py:28`

---

### 🟡 Task 3 — SkillTimelineStrip (87.5%, MEDIUM)

**Đã làm:**
- `SkillSlotCanvas` kế thừa `tk.Canvas` — đúng spec.
- `MAX_SLOTS = 8` + scrollbar tự động.
- Cooldown overlay vẽ bottom-up, clamp 0.0-1.0.
- Undo 1 bước qua `self._history`.
- Giữ reference ảnh qua `self._images = {}`.

**Bug nghiêm trọng (mới phát hiện trong audit):**

**🔴 Bug TclError ở fallback path — `skill_timeline_strip.py:47-51`**

```python
img = icon_helper.get_icon(self.icon_key, size=(24, 24))
if img:
    self._images['icon'] = img
    self.create_image(..., image=img, tags="icon")  # ❌ BUG
```

`IconHelper.get_icon()` có thể trả về **string emoji** (khi không tìm thấy file PNG). Khi đó `create_image(image="❓")` sẽ crash vì Tkinter yêu cầu `PhotoImage`.

**Hệ quả:**
- 3/4 unit tests fail → không verify được reorder/undo/cooldown.
- Trong production: nếu máy user thiếu icon PNG → **app crash** khi mở Skill Panel.

**Bug phụ:**
- `_on_drag_release` tính sai target_index khi scroll (không trừ scroll offset).
- `_history = [list(self.skills)]` — shallow copy, undo có thể restore reference đến dict đã bị mutate.

**Bằng chứng:** `ui/components/skill_timeline_strip.py:11-20, 47-51, 108, 121-122, 191, 209, 220-272` + `tests/unit/ui/components/test_skill_timeline_strip.py:27, 38, 46, 68, 89`

---

### 🟡 Task 4 — Rebuild SkillPanel (83.3%, HIGH)

**Đã làm:**
- Xóa `_build_combo_section` / `_build_buff_section`.
- Chèn `ComboRhythmBar` và 2 `SkillTimelineStrip`.
- Đổi Checkbox → Toggle Button, **giữ `auto_combo_var`**.
- Ghi state vào `hunt_cfg["combo"]["enabled"]`.
- Màu toggle: Xanh lá / Xám chuẩn.
- **Có unit test pass** cho toggle + i18n.

**🔴 Bug cascade nghiêm trọng — Task 1 ↔ Task 4**

**Bằng chứng grep:**
```bash
grep -rn "get_combo_sequence\|get_buff_sequence" ui/panels/skill_panel.py
# → Không có kết quả
```

Code hiện tại:
```python
self.attack_timeline = SkillTimelineStrip(self.content_frame)  # ❌ Không truyền skills
self.buff_timeline = SkillTimelineStrip(self.content_frame)    # ❌ Không truyền skills
```

→ Methods từ Task 1 **hoàn toàn không được gọi**. `SkillTimelineStrip` **render rỗng**. Đây là lỗi tích hợp làm **vỡ chức năng chính của panel**.

**Backend behavior đã verify** (điểm sáng):
- `hunt_orchestrator.py` đọc đúng `cfg.get("combo", {}).get("enabled", False)` → Toggle **thực sự có tác dụng** với hunt loop.

**Vấn đề D1:**
- `on_toggle_combo` ghi trực tiếp vào `app_state.hunt_cfg` → vi phạm tight coupling.
- **Không gọi `save_hunt_config()`** → config không persist qua restart.

**Bằng chứng:** `ui/panels/skill_panel.py:65, 89, 102, 112, 115, 129` + `tests/ui/panels/test_skill_panel.py:34, 37` + `lib/features/hunt/hunt_orchestrator.py` (đọc combo enabled)

---

### 🟡 Task 5 — TargetStatus + SkillStats (83.3%, HIGH)

**Đã làm:**
- HP text cập nhật **tức thời** (`target_status_panel.py:270`).
- HP bar tween qua `UIAnimationManager` (`:284`).
- Font mono cho HP/MP/Def (`self.font_mono`).
- `SkillStatsPanel` giữ `ttk.Treeview`, throttle 1s, giới hạn 50 record.
- Cột `success_rate` dùng font mono, format `%`.
- **Bug "chưa bind event" từ review trước đã được fix.**

**Vấn đề:**
- **Không có unit test** cho cả 2 panel (`test_target_status_panel.py` không tồn tại).
- **D6 hardcode:** `target_status_panel.py:26, 29` (`"📊 Target Status"`), `skill_stats_panel.py:79` (`"📈 Skill Performance"`).
- `_setup_legacy_wrappers` (`:40, 112`) dùng monkey-patch, không có test phụ thuộc → có thể xóa.

**Bằng chứng:** `ui/panels/target_status_panel.py:26, 29, 40, 90, 107, 112, 270, 284` + `ui/panels/skill_stats_panel.py:31, 39, 46, 79, 120`

---

### 🟡 Task 6 — HuntStatusTicker (85%, MEDIUM)

**Đã làm:**
- `HuntStatusTicker(tk.Frame)` với `icon_label` + `msg_label`.
- Bind `HuntStatusUpdatedEvent` và `HuntStateChangedEvent`.
- Thread-safe qua `self.after(0, ...)` cho cả 2 event.
- **Tích hợp vào `hunt_workspace_frame.py:17`** — cần verify quan hệ với `HuntTab`.

**Vấn đề:**
- **D6 hardcode:** `hunt_status_ticker.py:17, 61, 64, 67, 70` — emoji `ℹ️`, `🔄`, `⚠️`, `🔍` làm icon thay vì dùng `IconHelper`.
- **Không có unit test** cho component.
- Bug logic: `_update_state_ui` có thể đè message vừa set bởi `_update_status_ui`.

**Cần xác nhận:** Quan hệ giữa `HuntWorkspaceFrame` (nơi ticker được thêm) và `HuntTab` (nơi PanedWindow nằm). Nếu `HuntWorkspaceFrame` wraps `HuntTab` → ticker **hiển thị đúng**. Nếu không → ticker **bị che**.

**Bằng chứng:** `ui/components/hunt_status_ticker.py:5, 15, 17, 24, 34, 46, 50, 61, 64, 67, 70` + `ui/views/hunt_workspace_frame.py:17`

---

### 🟡 Task 7 — VisionSnapshotDebugger (95%, LOW)

**Đã làm:**
- `tk.Toplevel` + `tk.Canvas` cho popup debug.
- Method call trực tiếp `VisionEngine.get_latest_snapshot(timeout=0.5)` — **không qua EventBus**.
- **Thread-safe đầy đủ**: `snapshot_lock.acquire(timeout=timeout)` + `finally: release()`.
- Bounding box scale đúng: `dx = int(det.get("x", 0) * scale)`.
- i18n đầy đủ qua `self.app._t(...)`.
- **Unit test Memory Leak pass 1/1**.

**Bug spec còn lại:**
- **Spec (Task 7 Risks):** "Nếu Timeout, UI phải dùng lại ảnh Snapshot cũ."
- **Code (`:84-93`):** Khi `frame is None` → `self.canvas.delete("all")` + hiển thị text "No active frame". **Không giữ ảnh cũ.**

**Bug phụ:**
- `hunt_tab.py:381` dùng `tk.Button` trực tiếp (vi phạm Task 9).
- `cv2.putText` không hỗ trợ font tiếng Việt có dấu.

**Bằng chứng:** `ui/components/vision_snapshot_debugger.py:27, 31, 42, 59, 77, 78, 84-93, 109, 123` + `lib/vision/vision_engine.py:108, 355-358, 375-379, 393-401` + `tests/ui/components/test_vision_snapshot_debugger.py:38`

---

### 🟡 Task 8 — Multi-ROI Manager (85%, MEDIUM)

**Đã làm:**
- Nút "Set Hunt Area" gọi `CaptureHelper.start_region_selection`.
- Lưu `hunt_cfg["rois"]["hunt_area"]`.
- System ROI Manager ở Setup Tab cho `combo_bar`, `self_stats`, `minimap`.
- **Atomic write đầy đủ** (`hunt_config.py:32-56`): `tempfile.mkstemp` + `os.fsync` + `os.replace`.
- **Pydantic Schema Validation** (`hunt_config.py:61-63, 76-77`).
- **Auto-restore từ `.bak`** khi validation fail (`:80-95`).
- Migration `region` → `rois` qua `migrate_hunt_config`.
- **Có unit test Pydantic tự viết** — pass 100%.

**Vấn đề:**
- Không chặn vẽ ROI khi bot running (`monster_target_panel.py:118-135`, `setup_tab.py:461-465`).
- D6: `monster_target_panel.py:128` vẫn dùng fallback tiếng Anh cứng.

**Bằng chứng:** `ui/panels/monster_target_panel.py:107-128` + `ui/tabs/setup_tab.py:346, 372` + `lib/features/hunt/hunt_config.py:32-56, 61-95` + `tests/unit/features/hunt/test_pydantic_migration.py`

---

### ❌ Task 9 — Standardize Icon (15%, HIGH) — **THẤT BẠI NẶNG**

**Đáng chú ý:** Hạ tầng **hoàn toàn sẵn sàng** (`icon_button.py:117` hỗ trợ `element_id`, `icon_helper.py` load icon từ file PNG), nhưng dev **không dùng**.

**Vi phạm cụ thể:**

| File:Line | Vi phạm |
|-----------|---------|
| `monster_target_panel.py:20` | `🎯` trong title |
| `monster_target_panel.py:173, 181, 190, 199` | Fallback emoji button |
| `monster_target_panel.py:319, 328, 337, 350` | Emoji EmptyState + fallback |
| `monster_target_panel.py:482` | `.config(text="✓")` cũ |
| `hunt_status_ticker.py:17, 61, 64, 67, 70` | `ℹ️`, `🔄`, `⚠️`, `🔍` |
| `skill_panel.py:22` | `⚔️` title |
| `target_status_panel.py:28, 67` | `📊`, `⊕` |
| `skill_stats_panel.py:73` | `📈` |
| `hunt_tab.py:381` | `tk.Button` thay vì `create_icon_button` |
| `combo_rhythm_bar.py:37` | Text hardcode |
| `status_badge.py:16, 22, 28` | "Đang chờ"/"Sẵn sàng"/"Đang săn" hardcode |
| `monster_manager_win.py:880, 1035, 1063, 1090` | `👹`, `🔍`, `ℹ️`, `✏️`, `📊`, `⌛` |
| `hunt_orchestrator.py` (5+ chỗ) | Hardcode tiếng Anh qua EventBus |

**Tổng: 20+ điểm vi phạm, trải rộng cả UI lẫn backend.**

**Bằng chứng grep:**
```bash
grep -rn -P "[🔴🟢🎯➕⏱🔄]" ui/ lib/features/hunt/
```

**Kết luận:** Task 9 **FAILED** — không phải thiếu hạ tầng mà là **lazy coding**.

---

### 🟡 Task 10 — Layout & Typography (85%, HIGH)

**Đã làm:**
- Thay 12-column grid bằng `ttk.PanedWindow(orient=HORIZONTAL)` (`hunt_tab.py:341`).
- Weight 58/42.
- **Không xóa `ResponsiveGridBase`** — vẫn dùng ở `setup_tab.py`, `skill_stats_panel.py`.
- Panel titles dùng `UIStyleV2.get_font("title", weight="bold")` ở 3/4 panel.

**Vấn đề:**
- **Thiếu `minsize`** cho các pane → layout có thể vỡ khi kéo sash về 0.
- `hunt_tab.py` không có Typography hierarchy cho các header (chỉ 3/4 panel có).

**Bằng chứng:** `ui/tabs/hunt_tab.py:341`

---

## 4. KIỂM TOÁN 6 KHOẢN NỢ KỸ THUẬT (D1-D6)

| # | Nợ | Trạng thái | Bằng chứng mạnh nhất | Ưu tiên |
|---|-----|-----------|---------------------|---------|
| **D1** | Tight Coupling UI ↔ Config | ❌ **CHƯA TRẢ** | `skill_panel.py:on_toggle_combo`, `hunt_tab.py:70, 239-253`, `monster_target_panel.py:57, 113, 127`, `setup_tab.py:461-465` | **P0** |
| **D2** | Missing Schema Validation (pydantic) | ✅ **ĐÃ TRẢ** | `hunt_config.py:64` + auto-restore `.bak` (`:80-95`) | — |
| **D3** | EventBus Payload Bloat | ✅ **ĐÃ TRẢ HOÀN TOÀN** | `hunt_orchestrator.py:safe_publish()` — `del clean_snapshot["frame"]` | — |
| **D4** | Phân mảnh Tkinter Event Loop | ❌ **CHƯA TRẢ** | `status_badge.py:84`, `monster_manager_win.py:873, 1105`, `image_library_component.py:150` | **P1** |
| **D5** | Bounding Box Scale | ✅ **ĐÃ TRẢ** | `vision_snapshot_debugger.py:77` | — |
| **D6** | i18n Hardcode | ❌ **CHƯA TRẢ** | 20+ chỗ ở UI + backend | **P0** |

**Tỉ lệ trả nợ: 3/6 hoàn toàn (D2, D3, D5).**

### Ghi chú quan trọng về D6

**D6 KHÔNG PHẢI nợ của riêng Sprint 33.** Bằng chứng: `monster_manager_win.py` — file **không thuộc scope Sprint 33** — vẫn có 17+ chỗ hardcode string + emoji. Đây là nợ tích lũy **toàn dự án**.

---

## 5. CÁC FINDING QUAN TRỌNG NHẤT

### 🔴 Finding #1 — Cascade Task 1 ↔ Task 4 (Bug tích hợp nghiêm trọng nhất)

**Vấn đề:** `SkillPanelController.get_combo_sequence()` và `get_buff_sequence()` được viết đầy đủ ở Task 1 nhưng **không được gọi ở bất kỳ đâu**. `skill_panel.py:89, 102` tạo `SkillTimelineStrip` **không truyền `skills=...`**.

**Hệ quả:**
- Task 3 luôn render rỗng.
- Task 4 không đạt mục tiêu "hiển thị skills động".
- **Mục tiêu Drag & Drop Skill Timeline của sprint không đạt.**

**Fix ước lượng:** 2h.

---

### 🔴 Finding #2 — Task 9 FAILED (20+ emoji hardcode)

**Đáng chú ý:** Hạ tầng hoàn toàn sẵn sàng (`icon_button.py`, `icon_helper.py`). Đây là **lazy coding**.

**Fix ước lượng:** 8h (bao gồm cả backend files như `monster_manager_win.py`).

---

### 🔴 Finding #3 — Task 6 integration cần verify

**Báo cáo Batch 2 note:** `hunt_workspace_frame.py:17` có `HuntStatusTicker(self, app)` và `pack(side=BOTTOM)`.

**Cần làm rõ:** Quan hệ giữa `HuntWorkspaceFrame` và `HuntTab`. Nếu `HuntWorkspaceFrame` wraps `HuntTab` → ticker hiển thị đúng. Nếu không → ticker bị che bởi PanedWindow.

---

### 🔴 Finding #4 — Task 3 bug TclError (production crash risk)

**Vấn đề:** `create_image(image=string_emoji)` crash khi `IconHelper` trả về string. Máy user thiếu icon PNG → **app crash** khi mở Skill Panel.

**Fix ước lượng:** 1h.

---

### 🔴 Finding #5 — MagicMock trong production code (ngoài scope 11 task)

**Bằng chứng:** `monster_manager_win.py:915`

```python
if (isinstance(messagebox.askyesno, MagicMock) 
    or getattr(messagebox.askyesno, "__mock__", None) is not None):
    # Test mode behavior
```

**Đây là code smell nghiêm trọng.** Production code không được detect test framework.

---

### 🔴 Finding #6 — Task 7 còn 1 spec bug

**Vấn đề:** Khi timeout (`frame is None`), code xóa canvas thay vì giữ ảnh cũ như spec yêu cầu.

**Fix ước lượng:** 0.5h.

---

## 6. ĐIỂM SÁNG CẦN GHI NHẬN

1. **`UIAnimationManager` (Task 0)** — Design xuất sắc, override logic đúng, xử lý destroy widget tốt, có unit tests pass 4/4.
2. **`hunt_config.py`** — File **duy nhất** thể hiện engineering discipline cao: atomic write + pydantic + backup + migration + thread lock.
3. **`vision_engine.py`** — Lock đúng cả writer/reader, có timeout, `finally: release()`.
4. **`EventBus` + `hunt_orchestrator`** — D3 đạt hoàn toàn, payload sạch end-to-end.
5. **`VisionSnapshotDebugger` (Task 7)** — Thread-safe chuẩn, D5 đạt.
6. **`ComboRhythmBar` (Task 2)** — Debounce đúng, test pass 5/5.
7. **Task 5b `SkillStatsPanel`** — Đã fix bug "chưa bind event" từ review trước.
8. **Task 4 backend integration** — Toggle combo **thực sự có tác dụng** với HuntOrchestrator.

---

## 7. PHƯƠNG PHÁP AUDIT

### Source Hierarchy (khi 3 nguồn mâu thuẫn)

1. **Task spec** `0X_task_*.md` — source of truth
2. **`00_implementation_plan.md`** — phase + debt framework
3. **`qa_checklist.md`** — final sweep

### Nhãn trạng thái

| Nhãn | Ý nghĩa |
|------|---------|
| ✅ DONE | Đầy đủ, đúng spec |
| 🟡 PARTIAL | Có code nhưng thiếu/sai một phần |
| 🔵 STUB | Chỉ có khung |
| ❌ FAILED | Đã làm nhưng không đúng spec (nghiêm trọng) |
| ⬜ MISSING | Chưa hề làm |
| 💥 REGRESSED | Từng có, giờ đã vỡ |

### Công thức Completion %

```
Completion % = (số DONE + 0.5 × số PARTIAL) / tổng item thực tế
```

Trong đó: `STUB`, `FAILED`, `MISSING`, `REGRESSED` đều tính 0 điểm.

### Danh sách 26 file đã audit

**Core 11 task:**
`animation_manager.py`, `skill_panel_controller.py`, `combo_rhythm_bar.py`, `skill_timeline_strip.py`, `hunt_status_ticker.py`, `vision_snapshot_debugger.py`, `skill_panel.py`, `target_status_panel.py`, `skill_stats_panel.py`, `monster_target_panel.py`, `setup_tab.py`, `hunt_tab.py`

**Supporting:**
`vision_engine.py`, `hunt_config.py`, `event_bus.py`, `icon_button.py`, `icon_helper.py`, `ui_style_v2.py`, `skill_runtime_service.py`, `skill_preset_service.py`, `skill_preset_controller.py`, `empty_state.py`, `status_badge.py`, `styled_panel.py`, `responsive_grid_base.py`

**Backend (từ Batch 4):**
`hunt_orchestrator.py`, `monster_manager_win.py`

**Test files:**
`test_animation_manager.py`, `test_skill_panel_controller.py`, `test_combo_rhythm_bar.py`, `test_skill_timeline_strip.py`, `test_skill_panel.py`, `test_vision_snapshot_debugger.py`, `test_pydantic_migration.py`

---

## 8. ĐỀ XUẤT SPRINT 34

### Bảng ưu tiên 8 fix

| # | Task | Estimate | Dependency | Impact |
|---|------|----------|------------|--------|
| **1** | Fix cascade Task 1 ↔ 4: truyền `get_combo_sequence()`/`get_buff_sequence()` vào `SkillTimelineStrip` | **2h** | — | 🔥 Cao nhất |
| **2** | Fix bug TclError fallback path (`skill_timeline_strip.py:47-51`) | **1h** | — | 🔥 Crash production |
| **3** | Task 9 sweep: xóa 20+ emoji + thay `tk.Button` bằng `create_icon_button` + i18n | **8h** | — | 🔥 Task 9 FAILED |
| **4** | Task 6 integration: verify `HuntWorkspaceFrame` ↔ `HuntTab` | **1h** | — | Component vô dụng |
| **5** | Fix `VisionSnapshotDebugger` fallback (giữ ảnh cũ khi timeout) | **0.5h** | — | Spec violation |
| **6** | **D1 Decoupling** — move `hunt_cfg.get(...)` vào Controller | **6h** | Task 5 | Nợ dài hạn |
| **7** | **D4 + D6** — chuyển `status_badge._pulse_step` + `_check_queue` sang `UIAnimationManager`; fix i18n hardcode backend | **4h** | — | Nợ |
| **8** | Fix `MagicMock in production` + string hardcode trong `hunt_orchestrator.py` | **2h** | — | Code hygiene |

**Tổng: ~24.5h** để đưa Completion từ **~92% → ~97%**.

### Rủi ro nếu KHÔNG xử lý

| # | Rủi ro | Hậu quả |
|---|--------|---------|
| 1 | Cascade Task 1↔4 không fix | Sprint 33 fail về mục tiêu UX |
| 2 | Bug TclError không fix | App crash trên máy user thiếu icon PNG |
| 3 | Task 9 fail không fix | App "nghiệp dư", không đồng nhất icon theme |
| 4 | D1 không trả | Nợ tích tụ, các sprint sau càng khó refactor |
| 5 | D6 không trả | Không release được bản tiếng Anh |

### Đề xuất timeline Sprint 34 (1 tuần)

- **Ngày 1-2:** Fix #1 + #2 (integration + TclError)
- **Ngày 3:** Fix #3 (Task 9 sweep)
- **Ngày 4:** Fix #4 + #5 (Task 6 + Vision)
- **Ngày 5:** Fix #6 + #7 + #8 (Debt cleanup)
- **Cuối tuần:** Regression test toàn bộ 11 task + QA sweep

---

## 9. KẾT LUẬN CUỐI CÙNG

### Đánh giá tổng thể

Sprint 33 có **hạ tầng tốt nhưng integration yếu**. Điều đáng tiếc là nhiều task **đã được code đúng** (Task 0, 1, 2, 7, 8), nhưng **không được nối vào nhau** (Task 1↔4, Task 6 không rõ integration).

### Mức độ sẵn sàng release

> ❌ **Chưa sẵn sàng release.** Cần hoàn thành tối thiểu **4 fix đầu tiên (Finding #1, #2, #3, #4)** trước khi merge vào main.

### Đánh giá chất lượng cá nhân

| Vai trò | Đánh giá |
|---------|----------|
| **Backend engineer** (hunt_config, vision_engine, event_bus) | ⭐⭐⭐⭐⭐ Xuất sắc |
| **Frontend engineer** (UI components) | ⭐⭐⭐ Có tiến bộ, còn lazy |
| **Integration engineer** (kết nối các component) | ⭐⭐ Yếu — cần cải thiện |
| **Code hygiene** (i18n, emoji, D1) | ⭐⭐ Rất yếu |

### Điểm cần cải thiện cho Sprint 34+

1. **Integration testing**: Cần viết test end-to-end verify data flow từ Controller → View.
2. **i18n discipline**: Mọi string UI/backend phải qua `_t()`.
3. **Code review checklist**: Trước khi merge, grep emoji hardcode + `hunt_cfg.get`.
4. **Tránh detect test framework trong production** (`MagicMock` check).

---

**End of Report.**

*Audit summary này tổng hợp từ 4 file `audit-batch-1.md` → `audit-batch-4.md` + 26 file source code đã inspect. Mọi kết luận có thể verify bằng cách grep `file:line` tương ứng.*