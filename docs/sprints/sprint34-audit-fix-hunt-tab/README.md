# Sprint 34: Audit Fix Hunt Tab

## 🎯 Mục đích và Cách dùng
Thư mục này chứa 8 task prompt được sinh ra từ báo cáo kiểm toán Sprint 33 (`docs/sprints/sprint33-improve-ux-hunt-tab/prompt-ux-audit-fix-hunt-tab/audit-ux-hunt-tab.md`).
Mục tiêu là giải quyết 6 "Findings" nghiêm trọng, xử lý các lỗi cascade, bug gây crash (TclError), dọn dẹp tech debt (D1, D4, D6), và xóa bỏ code smell (MagicMock trên production).

Các prompt được thiết kế theo nguyên tắc Self-Contained, không cần đọc chéo file khác, với đầy đủ các Scope, Requirements định lượng, Acceptance Criteria, File Ownership và Stop Conditions rõ ràng.

## 📊 Bảng 8 Task

| Task ID | Tên Task | Phân loại | Ước lượng | Prioriy |
|---------|----------|-----------|-----------|---------|
| 01 | Fix cascade Task 1 ↔ 4 | Bug Tích Hợp | 2h | P0 |
| 02 | Fix TclError fallback | Crash Risk | 1h | P0 |
| 03 | Sweep emoji standardize icon | Tech Debt | 1h | P1 |
| 04 | Verify integrate Task 6 | Integration | 1h | P1 |
| 05 | Fix vision fallback | Spec Bug | 0.5h | P2 |
| 06 | Decouple D1 config | Tech Debt | 2h | P1 |
| 07 | Cleanup D4 D6 | Tech Debt | 2h | P1 |
| 08 | Fix MagicMock & backend i18n | Code Hygiene | 2h | P2 |

## 🔗 Dependency Rules & Thứ tự thực thi (5 Ngày)

Để tránh conflict và blocking chéo, tiến độ code chia theo 5 ngày dựa trên sự phụ thuộc:

- **Ngày 1 - Critical Fixes (Độc lập):**
  - `01_fix_cascade_task1_4.md` (Xử lý bug cascade làm rỗng UI).
  - `02_fix_tclerror_fallback.md` (Ngừa TclError crash app trên production).
- **Ngày 2 - Integration & Fallback:**
  - `04_verify_integrate_task6.md` (Cần UI ổn định ở Ngày 1 để test tích hợp).
  - `05_fix_vision_fallback.md` (Độc lập).
- **Ngày 3 - Heavy Sweep (Cần trọn 1 ngày):**
  - `03_sweep_emoji_standardize_icon.md` (Sửa diện rộng 20+ chỗ trên UI và backend).
- **Ngày 4 - Deep Refactor:**
  - `06_decouple_d1_config.md` (Refactor luồng config, làm sau khi UI đã fix ổn định).
  - `07_cleanup_d4_d6.md` (Phụ thuộc vào kiến trúc đã được làm sạch phần icon).
- **Ngày 5 - Code Hygiene & Testing:**
  - `08_fix_magicmock_backend_i18n.md`
  - Chạy Regression Test tổng thể cho tất cả các tab.

## 📂 File Ownership Matrix

| File (Ví dụ tiêu biểu) | Primary Owner (Toàn quyền) | Shared Access (Chỉ sửa phần thuộc task) |
|-----------------------|----------------------------|-----------------------------------------|
| `ui/panels/skill_panel.py` | Task 01, Task 06 | Task 03 |
| `ui/components/skill_timeline_strip.py` | Task 02 | Task 01, Task 03 |
| `ui/components/hunt_status_ticker.py` | Task 04 | Task 03 |
| `ui/components/vision_snapshot_debugger.py` | Task 05 | Task 03 |
| `lib/features/hunt/hunt_config.py` | Task 06 | - |
| `ui/components/status_badge.py` | Task 07 | Task 03 |
| `lib/features/hunt/monster_manager_win.py` | Task 08 | Task 03 |
| `lib/features/hunt/hunt_orchestrator.py` | Task 08 | Task 03 |

> **Lưu ý:** Việc áp dụng File Ownership giúp kiểm soát rủi ro merge conflict. Khi đụng đến một "Shared Access" file, kĩ sư phải tuân thủ nghiêm Stop Condition nếu buộc phải sửa ngoài phạm vi quy định.

## 🔗 Link Audit Gốc
- Nguồn tham chiếu: `docs/sprints/sprint33-improve-ux-hunt-tab/prompt-ux-audit-fix-hunt-tab/audit-ux-hunt-tab.md`
