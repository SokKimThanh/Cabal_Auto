# LỘ TRÌNH CABAL AUTO HUNT ASSISTANT (CHUẨN HÓA 26 PHIÊN)

**Kiến trúc:** Four-Zone Command Center & Data-Driven Combat Engine  
**Timebox:** 20-30 phút/session; phút 20/25 validation, phút 25-30 chỉ targeted repair hoặc revert.

## Ghi Chú Bắt Buộc

1. CB4 chạy trước CB2D/UX3A/UX3 để thống nhất schema; không tạo migration song song.
2. DB chỉ cung cấp metadata, không tự nhận diện hình ảnh. CB2D chỉ nhận quái có visual template map DB hợp lệ.
3. UX3A sở hữu DB picker; UX3 quản lý configured list; CB2D tạo detection snapshot; UX3B hiển thị ba mode/hai list và promotion.
4. CB2E chỉ dùng Windows user-mode APIs. Game không nhận background message thì báo `UNSUPPORTED`, không injection/hook/driver và không fallback âm thầm sang global input.
5. CB2C là owner duy nhất của active desired source/pointer và gate cho phép attack.
6. CB3D phân biệt transport `SENT` với game acknowledgment `ACCEPTED`; chỉ accepted mới commit skill cooldown/pointer/stats.
7. `monster_rotation` là persist; detection snapshot và attack queue là transient.
8. CB3 gốc phải được xác nhận hoàn tất trước CB3C.
9. DS1-DS5 là phase visual migration riêng, chỉ chạy sau UX5.2 để không restyle
   widget đang tiếp tục bị tái cấu trúc.
10. `PROMPT-DT-tkinter-adapter.md` là nguồn chuyển đổi bắt buộc; không truyền
   token CSS như `rgba`, gradient, shadow hoặc CSS font string vào Tkinter.
11. Nạp `00-global-rules.md` kèm mỗi session.
12. `PROMPT-R1-core-gate-remediation.md` là recovery gate độc lập: có thể chạy
   ngay, không đổi thứ tự 26 feature session, và phải đóng các blocker đã biết
   trước khi CB1/CB2/CB2B/CB4/CB2D được báo `PASSED`.
13. `PROMPT-R2-project-wide-cleanup.md` là maintenance gate độc lập: có thể
   chạy bất kỳ lúc nào, nhưng chỉ được xóa mục `DELETE_SAFE` sau khi lập
   manifest dry-run; không dùng cleanup để che lỗi hoặc thay đổi logic.

## Ba Chế Độ Săn

| UI | `target_policy` | Nguồn được phép đánh | Identity gate |
| --- | --- | --- | --- |
| Quái đã chọn | `configured_only` | `monster_rotation` | OCR/DB ID phải khớp configured ID |
| Tự nhận diện | `all_resolved` | Runtime candidate đã DB-match | OCR/DB ID phải khớp candidate còn TTL |
| Mọi mục tiêu | `any_target` | Target có Target Bar hợp lệ | CB1 alive gate, không yêu cầu ID |

Unknown vẫn xuất hiện trong danh sách phát hiện nhưng không được promote hoặc đánh trong hai mode kiểm tra danh tính. `any_target` là opt-in và phải cảnh báo rằng danh tính không được kiểm tra.

## Trạng Thái Gửi Và Nhận Skill

```text
READY -> RESERVED -> SENT -> WAITING_ACK
                              |-> ACCEPTED: commit cooldown/pointer/success
                              |-> REJECTED: failure policy
                              |-> UNVERIFIED: không ghi success, quarantine/pause
                              |-> CANCELLED: target chết hoặc Stop
```

Windows API trả thành công chỉ chứng minh `SENT`, không chứng minh game đã cast. Không dùng riêng Target Bar alive, hết cast time hoặc không có exception làm acknowledgment.

## Nguyên Tắc Chung

1. Worker/service không gọi Tkinter trực tiếp; dùng `schedule_ui_task()`/`after()`.
2. Không duy trì hai schema, hai runtime pointer hoặc hai đường ghi config.
3. Runtime detection không tự ghi vào `monster_rotation`.
4. Promote detected -> configured chỉ nhận DB-match, chống trùng và mark unsaved.
5. Mode được snapshot khi Start và không đổi giữa combat.
6. Skill pending không được gửi lặp mỗi worker tick.
7. Không fallback background -> foreground hoặc input API khác nếu người dùng chưa chọn.
8. Hỗ trợ tối thiểu 1366x768 và DPI 100%-200%.
9. Nếu dependency gate fail, báo `BLOCKED`; không mở rộng session để vá dependency.

## Thứ Tự Thực Thi — 38 Sessions (R1-2 + 1-29 ✅ DONE + 30-38 Pending)

**Status**: Sessions 1-29 (all core + enhancement + design phases) đã hoàn tất và lưu trong `done/` folder. Sessions 30-38 (Reference/Advanced docs) chưa làm.

| # | Mã | Tài Liệu | Loại | Kết Quả Chính | Phụ Thuộc |
| :---: | :---: | --- | --- | --- | --- |
| R1 | R1 | `PROMPT-R1-core-gate-remediation.md` | Recovery | Khép blocker CB1/CB2/CB2B/CB4/CB2D đã xác minh. | Chạy ngay |
| R2 | R2 | `PROMPT-R2-project-wide-cleanup.md` | Maintenance | Inventory & cleanup file/thư mục toàn project. | Độc lập |
| 1 | UX1 | `PROMPT-UX1-quick-action-bar.md` | UX | Quick Action Bar & Start/Stop debounce. | Window service |
| 2 | UX2 | `PROMPT-UX2-core-grid-shell.md` | UX | Core shell & view swapping. | UX1 |
| 3 | UX6 | `PROMPT-UX6-collapsible-bottom-logs.md` | UX | Activity logging theo UI hiện hành. | UX2 |
| 4 | CB5 | `PROMPT-CB5-stability-and-scanner-fix.md` | Combat | Window scanner & ScreenCapture buffer. | ScreenCapture |
| 5 | CB1 | `PROMPT-CB1-target-bar-detector.md` | Combat | Target Bar alive/dead & HP%. | CB5 |
| 6 | CB2 | `PROMPT-CB2-fix-hunt-orchestrator-combat-loop.md` | Combat | Hunt loop (không spam target key). | CB1 |
| 7 | CB2B | `PROMPT-CB2B-target-name-ocr-id-mapper.md` | Combat | OCR target name & resolve DB ID/HP. | CB2 |
| 8 | CB4 | `PROMPT-CB4-sync-config-schema.md` | Data | Canonical config & atomic save. | CB2B |
| 9 | CB2D | `PROMPT-CB2D-runtime-scene-monster-detection.md` | Vision | Detection snapshot & attack queue. | CB5, CB2B, CB4 |
| 10 | UX3A | `PROMPT-UX3A-db-monster-picker-dialog.md` | UX | DB Monster Picker dialog. | CB4, CB2B |
| 11 | UX3 | `PROMPT-UX3-dynamic-rotation-queue.md` | UX | Configured rotation & integration. | CB4, UX3A |
| 12 | UX3B | `PROMPT-UX3B-three-mode-detection-workspace.md` | UX | Three-mode UI & detection list. | CB4, UX3A, UX3, CB2D |
| 13 | CB2E | `PROMPT-CB2E-background-window-input.md` | System | Background HWND input. | CB5, CB2 |
| 14 | CB2C | `PROMPT-CB2C-target-rotation-acquisition.md` | Combat | Policy coordination & attack gate. | CB1, CB2, CB2B, CB2D, CB2E, CB4, UX3B |
| 15 | CB3B | `PROMPT-CB3B-Combo Rotation Builder & Hotbar Mapping.md` | UX | Dual-Lane Skill Strip. | UX2, CB4 |
| 16 | UX4.2 | `Prompt-UX4.2 Smart Skill Routing, Key Conflict & JSON Migration.md` | UX | Smart routing & conflict. | CB3B, CB4 |
| 17 | CB6 | `PROMPT-CB6-Implement Cabal Horizontal Combo Bar Timing Detector.md` | Combat | Combo timing trigger. | CB5 |
| 18 | CB3D | `PROMPT-CB3D-skill-command-delivery-verification.md` | Combat | Skill acknowledgment & stats. | CB1, CB2E, CB4, UX4.2, CB6 |
| 19 | CB3C | `PROMPT-CB3C-Harmonize Timing Calculator with Combo Mode & Fast-Break.md` | Combat | Fast-Break & timing. | CB6, CB3D, CB2C |
| 20 | UX5.1 | `Prompt-UX5.1 Active Target Card Shell, Fallback Schema & Image Lifecycle.md` | UX | Active Target Card. | UX2, CB2B |
| 21 | UX5.2 | `Prompt-UX5.2 Dynamic Canvas HP Bar, Throttling & Window Recovery Logic.md` | UX | Dynamic HP Canvas. | UX5.1, CB1 |
| 22 | UX6-WHD | `PROMPT-UX6-window-detection-and-refresh.md` | Enhancement | Window enumeration + scan + screen state. | 1-3 |
| 23 | AH | `PROMPT-UX-auto-hunt-flow.md` | Enhancement | Orchestrator + Start/Stop + session tracking. | 1-21 |
| 24 | DS1 | `PROMPT-DS1-tkinter-safe-tokens.md` | Design | Tkinter-safe tokens & resolvers. | 1-23 ✅ DONE |
| 25 | DS2 | `PROMPT-DS2-ttk-component-primitives.md` | Design | TTK theme & primitives. | DS1 ✅ DONE |
| 26 | DS3 | `PROMPT-DS3-shell-navigation-theme.md` | Design | Shell & navigation theme. | DS1, DS2 ✅ DONE |
| 27 | DS4 | `PROMPT-DS4-hunt-workspace-theme.md` | Design | Hunt workspace theme. | DS3, UX3B, UX4.2, UX5.2 ✅ DONE |
| 28 | DS5 | `PROMPT-DS5-secondary-views-visual-acceptance.md` | Design | Secondary views & acceptance. | DS4 ✅ DONE |
| 29 | DS6 | `PROMPT-DS6-layout-refactor-priority-driven.md` | Design | Layout refactor & priority-driven optimization. | DS5 ✅ DONE |
| 30 | WA | `PROMPT-WA-workspace-architecture.md` | Reference | Workspace architecture alignment. | Độc lập |
| 31 | WL | `PROMPT-WL-workspace-logic-design.md` | Reference | Workspace logic & data flow. | Độc lập |
| 32 | WU | `PROMPT-WU-workspace-ui-design.md` | Reference | Workspace UI design specs. | Độc lập |
| 33 | UM | `PROMPT-UM-ui-master-plan.md` | Reference | UI redesign master plan. | Độc lập |
| 34 | UV | `PROMPT-UV-ui-visual-reference.md` | Reference | Visual reference & component specs. | Độc lập |
| 35 | DT | `PROMPT-DT-tkinter-adapter.md` | Reference | Design tokens (Tkinter adapter). | Độc lập |
| 36 | VISION | `PROMPT-VISION-ENGINE-REFACTOR.md` | Reference | Vision engine refactoring roadmap. | Độc lập |
| 37 | UI-IMP | `PROMPT-UI-IMPROVEMENTS.md` | Reference | UI improvements guide. | Độc lập |
| 38 | UI-REDESIGN-2 | `PROMPT-UI-REDESIGN-PHASE-2.md` | Advanced | UI redesign phase 2 (9 sub-phases). | 1-28 |

**Tài liệu Reference**: Xem bảng execution table rows 30-38 ở trên.

**Annotations**:
- **Sessions 1-29**: ✅ All DONE, files in `done/` folder
- **Sessions 30-38**: ⏳ Pending (Reference & Advanced docs in root folder, not yet executed)

## Luồng Target Và Scene Detection

```text
UX3A DB picker -> UX3 configured monster_rotation
             |
CB2D frame -> visual detection -> DB mapping
             |
             +-> runtime_detection_snapshot -> UX3B detected list
             |                                  +-> promote DB-match
             +-> runtime_attack_queue ----------+
                                                v
CB2B target OCR/DB ID -----------------------> CB2C policy coordinator
                                                |
CB2E targeted input backend <-------------------+
                                                |
                     configured_only: match configured ID
                     all_resolved: match runtime DB candidate
                     any_target: CB1 alive gate, no identity gate
                                                |
                                                v
                                         allow/deny attack
```

## Luồng Gửi Và Xác Minh Skill

```text
CB2C cho phép attack
-> SkillRuntime reserve skill (chưa advance)
-> CB6 chọn hit-zone nếu Combo mode
-> CB2E gửi skill key tới backend
-> TransportStatus SENT/FAILED
-> CB3D quan sát frame hậu kiểm
   -> hotbar cooldown delta hoặc combo progression
   -> ACCEPTED: commit cooldown + pointer + accepted stats
   -> UNVERIFIED: không success, pause/quarantine theo policy
   -> REJECTED: bounded retry/stop theo policy
   -> CANCELLED: target chết/Stop
-> CB3C xử lý timing/fast-break mà không double-advance
```

Không được coi các tín hiệu sau là cast success: `PostMessage=True`, `SendInput` không lỗi, Target Bar còn sống, hết `cast_time`, hoặc HP giảm không gắn được với skill cụ thể.

## Background Input

```text
CB2E SUPPORTED
-> không focus game
-> gửi target/skill key tới selected HWND
-> chuột/bàn phím vật lý vẫn dùng được

CB2E UNVERIFIED/UNSUPPORTED
-> background mode không Start
-> người dùng chủ động chọn foreground mode nếu chấp nhận
-> không fallback âm thầm
```

## Luồng Thay Đổi Giao Diện

```text
21 UX5.2 hoàn tất cấu trúc chức năng
-> 22 DS1 chuyển design tokens sang Tkinter-safe values
-> 23 DS2 cấu hình ttk + button/component semantic roles
-> 24 DS3 áp theme cho shell/sidebar/action bar/footer
-> 25 DS4 áp theme cho Hunt workspace và mọi runtime state
-> 26 DS5 áp secondary views + chạy visual/accessibility gate
```

Design direction:

- dark neutral command-center, không dark-blue một màu;
- green chỉ cho active/hunting/primary, blue cho selected/info, yellow cho ready,
   red cho stop/danger;
- solid colors thay CSS gradient/shadow trên widget native;
- font resolver có fallback, không bắt buộc Rajdhani/Inter phải được cài;
- không đổi business logic, callback, queue hoặc geometry ownership trong session
   style.

## Quy Trình Mỗi Session

1. Nạp `00-global-rules.md` và đúng một prompt theo thứ tự 01-26.
2. Kiểm tra dependency/preflight trước khi sửa.
3. Phút 00-20/25: production code và focused tests.
4. Phút 20/25-30: test, smoke và targeted repair.
5. Chỉ chạy session kế tiếp khi gate đạt.
6. Báo `PASSED`, `BLOCKED`, `UNVERIFIED`, `UNSUPPORTED` hoặc `REVERTED` kèm bằng chứng.

---

## 📊 Trạng Thái Tiến Độ Prompt

| Session | Prompt | Status | File | Ghi Chú |
| :---: | --- | --- | --- | --- |
| UX6 | `PROMPT-UX6` | 🟡 20% UI | `PROMPT-UX6-window-detection-and-refresh.md` | Backend 90% xong; UI wiring incomplete |
| Auto Hunt | `PROMPT-UX-AH` | 🟡 20% Integration | `PROMPT-UX-auto-hunt-flow.md` + `PROMPT-AH-roadmap.md` | Backend 80% xong; HuntOrchestrator integration pending |
| CB3B | `PROMPT-CB3B` | 🟡 ~95% | `PROMPT-CB3B-Combo Rotation Builder & Hotbar Mapping.md` | All 5 phases done; pending test verification + pre-commit |
| UX4.2 | `PROMPT-UX4.2` | 🟡 Ready (after CB3B PASSED) | — | Depends: CB3B Phase 2 (buff_slots) ✅ DONE |
| CB3D | `PROMPT-CB3D` | 🟡 Ready (after UX4.2 PASSED) | — | Depends: UX4.2 (ready after CB3B) |
| CB3C | `PROMPT-CB3C` | 🟡 Ready (after CB3D PASSED) | — | Depends: CB3D |
| DS1-5 | `PROMPT-DS1` thru `DS5` | ⏳ BLOCKED | — | Depends: UX5.2 complete (phút 21) |

### UX6 — Activity Logging

**File**: [PROMPT-UX6.md](PROMPT-UX6.md)  
**Status**: 🟡 Backend 90%, UI 20%  
**Phụ thuộc**: UX2, HuntLogger

**Hoàn Thành**:
- ✅ Backend logging service
- ✅ Session tracking structure
- ✅ Config persistence

**Chưa làm**:
- ❌ UI wiring to HuntTab (Start/Stop events)
- ❌ Log viewing panel integration

### AUTO-HUNT-FLOW — Hunt Loop Orchestration

**File**: [PROMPT-AUTO-HUNT-FLOW.md](PROMPT-AUTO-HUNT-FLOW.md)  
**Status**: 🟡 Backend 80%, Integration 20%  
**Phụ thuộc**: CB1, CB2, CB4, CB2D, HuntOrchestrator

**Hoàn Thành**:
- ✅ AutoHuntOrchestrator class (500+ lines)
- ✅ Hunt state machine
- ✅ Session stats tracking

**Chưa làm**:
- ❌ HuntOrchestrator integration
- ❌ Z-key sending for auto-hunt
- ❌ Screenshot cleanup
- ❌ Session logging

### CB3B — Dual-Lane Skill Strip

**File**: [PROMPT-CB3B.md](PROMPT-CB3B.md)  
**Status**: � ~95% (Ready for PASSED Gate)  
**Phụ thuộc**: UX2 ✅, CB4 ✅  
**Unblocks**: UX4.2, CB3D, CB3C

**Hoàn Thành (95%)**:
- ✅ Dual-Lane Layout (combo + buff lanes)
- ✅ Combo Mode Controls (checkbox + key selector)
- ✅ Skill Card Display (dropdown, stats badges)
- ✅ **Hotkey Conflict Validation** — Implemented in `lib/features/hotkey/hotkey_validator.py`, wired to UI
- ✅ **buff_slots Config Separation** — Migrator + UI + controller refactored, strictly separated
- ✅ **Auto-Refresh Interval (duration_sec)** — Spinbox added to Buff Lane cards, persists to config
- ✅ **Test Suite** — Created `tests/unit/ui/tabs/test_cb3b_validation_suite.py` (hotkey, migration, round-trip, i18n, DPI)
- ✅ i18n + DPI scaling

**Pending PASSED Gate**:
- ⏳ Run full test suite (`pytest tests/unit/ui/tabs/test_cb3b_validation_suite.py`)
- ⏳ Smoke test in-app (hotkey conflict, buff_slots persistence, Auto-Refresh)
- ⏳ Pre-commit checks (tests, linting, no debug prints)

**Immediate Action**: Jules → Run tests & pre-commit → Submit when all PASS

### DS1-DS5 — Design System Phases

**Status**: ⏳ Blocked until UX5.2 complete  
**Timeline**: After session 21 (UX5.2)

| Phase | Prompt | Kết quả chính | Phụ thuộc |
| --- | --- | --- | --- |
| DS1 | `PROMPT-DS1` | Tkinter-safe tokens, font resolver | 01-21 complete |
| DS2 | `PROMPT-DS2` | ttk theme + semantic primitives | DS1 |
| DS3 | `PROMPT-DS3` | Dark shell, sidebar, action bar | DS1, DS2 |
| DS4 | `PROMPT-DS4` | Hunt workspace theme | DS3, UX3B, UX4.2, UX5.2 |
| DS5 | `PROMPT-DS5` | ✅ PASSED | DS4 |

**Design Direction**:
- Dark neutral command-center (no solid dark-blue)
- Green = active/hunting, Blue = selected/info, Yellow = ready, Red = stop/danger
- Solid colors only (no gradients/shadows on native widgets)
- Font fallback required (Rajdhani/Inter optional)

---

## 📂 File Organization & Naming Convention

**Quy tắc thống nhất**: `CATEGORY-NUMBER-CODE-Title.md`

### Categories

| Category | Prefix | Purpose | Example |
|----------|--------|---------|---------|
| **Phase Prompts** | `PHASE-` | Main feature prompts (01-26 + features) | `PHASE-22-DS1-Tkinter-Tokens.md` |
| **Global Rules** | `00-` | Project-wide guidelines | `00-GLOBAL-RULES.md` |
| **Enhancements** | *(code name)* | Optional features (UX6-WHD, AUTO-HUNT) | `UX6-Window-Detection.md` |
| **References** | `REFERENCE-` | Design specs, visual guides, adapter | `REFERENCE-UI-Design-Visual.md` |
| **Summaries** | `INDEX-` | Consolidated tóm tắt across multiple docs | `INDEX-Summary-All-Features.md` |
| **Archive** | `archive/` | Previous versions, deprecated docs | `archive/PROMPT-UX6-old.md` |

### Current File Mapping

**Phase Prompts (Thứ tự 01-26)**:
- `PHASE-01-UX1-Quick-Action-Bar.md`
- `PHASE-02-UX2-Core-Shell.md`
- `PHASE-03-UX6-Activity-Logging.md`
- `PHASE-04-CB5-Window-Scanner.md`
- ... (continues to 26)
- `PHASE-22-DS1-Tkinter-Tokens.md`
- `PHASE-23-DS2-TTK-Primitives.md`
- `PHASE-24-DS3-Shell-Navigation.md`
- `PHASE-25-DS4-Hunt-Workspace.md`
- `PHASE-26-DS5-Secondary-Views.md`

**Enhancements (After Core 26)**:
- `UX6-Window-Detection.md` ← IMPROVED-PROMPT-UX6.md (renamed)
- `AUTO-HUNT-Flow-Integration.md` ← IMPROVED-PROMPT-AUTO-HUNT-FLOW.md (renamed)
- `ROADMAP-Auto-Hunt-UX6.md` ← IMPLEMENTATION-ROADMAP-AUTO-HUNT-UX6.md (renamed)

**Global & References**:
- `00-GLOBAL-RULES.md` ← 00-global-rules.md (no change)
- `REFERENCE-Design-System-Adapter.md` ← DESIGN-SYSTEM-TKINTER-ADAPTER.md (renamed)
- `REFERENCE-UI-Design-Visual.md` ← UI-REDESIGN-VISUAL-REFERENCE.md (renamed)
- `REFERENCE-Workspace-Architecture.md` ← WORKSPACE-REDESIGN-ARCHITECTURE-ALIGNMENT.md (renamed)
- `REFERENCE-Workspace-Logic.md` ← WORKSPACE-REDESIGN-LOGIC-DESIGN.md (renamed)
- `REFERENCE-Master-Plan.md` ← UI-REDESIGN-MASTER-PLAN.md (renamed)

**Consolidated Summary**:
- `INDEX-Summary-All-Features.md` ← Combines: 00-SUMMARY-..., REVIEW-UX6-..., all architecture docs

**Archive** (To be moved to `archive/` folder):
- `PROMPT-UX6-window-detection-and-refresh.md` ← Replaced by `UX6-Window-Detection.md`
- `PROMPT-UX-auto-hunt-flow.md` ← Replaced by `AUTO-HUNT-Flow-Integration.md`
- ~~`00-SUMMARY-FEATURE-REVIEW-AND-IMPROVEMENTS.md`~~ ← Merged into `INDEX-Summary-All-Features.md`
- ~~`REVIEW-UX6-AND-AUTO-HUNT-vs-CURRENT.md`~~ ← Merged into `INDEX-Summary-All-Features.md`

**Design References** (May keep as-is or prefix with REFERENCE-):
- `PROMPT-DS1-tkinter-safe-tokens.md` ← Rename to `PHASE-22-DS1-Tkinter-Tokens.md`
- `PROMPT-DS2-ttk-component-primitives.md` ← Rename to `PHASE-23-DS2-TTK-Primitives.md`
- `PROMPT-DS3-shell-navigation-theme.md` ← Rename to `PHASE-24-DS3-Shell-Navigation.md`
- `PROMPT-DS4-hunt-workspace-theme.md` ← Rename to `PHASE-25-DS4-Hunt-Workspace.md`
- `PROMPT-DS5-secondary-views-visual-acceptance.md` ← Rename to `PHASE-26-DS5-Secondary-Views.md`

**Combat & Feature Prompts** (Will be renamed in future sessions):
- `PROMPT-CB3B-Combo Rotation Builder & Hotbar Mapping.md` ← Rename to `PHASE-15-CB3B-Dual-Lane-Skill-Strip.md`

### How to Find a File

1. **Looking for Phase XX implementation?** → Search `PHASE-XX-`
2. **Looking for feature enhancement?** → Search by code name (UX6, AUTO-HUNT, etc.)
3. **Looking for design system?** → Search `REFERENCE-` or specific phase number
4. **Looking for summary/overview?** → Check `INDEX-Summary-All-Features.md`
5. **Looking for global rules?** → Check `00-GLOBAL-RULES.md`

### Next Actions

- [ ] Rename all files to follow new convention
- [ ] Move old versions to `archive/` folder
- [ ] Update all cross-references in documents
- [ ] Create soft links for backward compatibility (optional)
- [ ] Update this file when new phases are added
