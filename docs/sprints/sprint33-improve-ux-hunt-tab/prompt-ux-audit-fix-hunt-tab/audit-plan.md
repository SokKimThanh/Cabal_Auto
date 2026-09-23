# Kế hoạch Audit Cập Nhật - Master Audit Plan

## Phase Mapping
- Batch 1 ↔ Phase 1 (Task 0, 1)
- Batch 2 ↔ Phase 2 (Task 3, 6, 7) (Task 2 đã gộp ở Batch 1)
- Batch 3 ↔ Phase 3 (Task 4, 5)
- Batch 4 ↔ Phase 4 (Task 8, 9, 10) + Tổng hợp (Phần 3 & 4)

## Source Hierarchy (khi mâu thuẫn)
1. Task spec (`0X_task_*.md`) — source of truth
2. Impl plan (`00_implementation_plan.md`) — phase + debt
3. QA checklist (`qa_checklist.md`) — final sweep

## QA Cross-check Rule
Sau khi audit xong task X, mở `qa_checklist.md` phần "Task X", đảm bảo MỌI checkbox đều được đề cập trong báo cáo (không nhất thiết phải PASS, nhưng phải có kết luận PASS/FAIL/N/A).

## Debt Checklist (6 khoản)
- [ ] D1: Tight Coupling UI ↔ Config (grep `hunt_cfg.get` trong `ui/`)
- [ ] D2: Missing Schema Validation (grep `pydantic` trong repo)
- [ ] D3: EventBus Payload Bloat (grep raw frame/numpy trong `publish`)
- [ ] D4: Phân mảnh Tkinter Event Loop (grep `self.after` trong `ui/` ngoại trừ delay 0)
- [x] D5: Bounding Box Scale (verify math trong `VisionSnapshotDebugger`)
- [ ] D6: i18n Hardcode (grep string tiếng Việt cứng trong UI mới)

## Debt Evidence Log
**Batch 1:**
- D1: `ui/panels/monster_target_panel.py:57`, `ui/tabs/hunt_tab.py:70`, ...
- D4: `ui/components/image_library_component.py:150`

**Batch 2:**
- D4: `ui/components/status_badge.py:87-90` (animation loop `_pulse_step` nằm ngoài UIAnimationManager)
- D6: `ui/components/hunt_status_ticker.py:17, 61, 64, 67, 70` (Emoji text hardcode: ℹ️, 🔄, ⚠️, 🔍)
- D6: `ui/components/status_badge.py:16, 22, 28` (Text tiếng Việt hardcode: "Đang chờ", "Sẵn sàng", "Đang săn")

**Batch 3:**
- D6: `ui/panels/target_status_panel.py:26, 29` (Hardcode "📊 Target Status")
- D6: `ui/panels/skill_stats_panel.py:79` (Hardcode "📈 Skill Performance")- skill_panel.py:129 — viết trực tiếp vào app_state.hunt_cfg (bypass Controller) (D1 evidence)
- (verified) — save_hunt_config() KHÔNG được gọi sau khi thay đổi (D1 bug)
- target_status_panel.py — KHÔNG còn self.after cho animation (D4 cải thiện)
