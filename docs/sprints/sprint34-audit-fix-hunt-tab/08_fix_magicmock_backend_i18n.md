# Prompt: Fix MagicMock & backend i18n

## 📖 Context
Đọc `00_context_audit_summary.md` trước. Task này fix Finding #5 và phần backend của D6.

## 🎯 Scope
- Finding: #5, D6 | Priority: P2 | Estimate: 2h
- Dependency: Independent (Code backend)
- Dependency Check: `grep -rn "MagicMock" lib/features/hunt/`

## 🔍 Vấn đề cần fix
Trong `monster_manager_win.py`, production code sử dụng `isinstance(..., MagicMock)` để phát hiện framework test, là một "code smell" nghiêm trọng. Cần thiết kế mock đúng trong file test thay vì code chính. Ngoài ra, backend như `hunt_orchestrator.py` đang gửi thông báo qua EventBus bằng hardcode tiếng Anh/tiếng Việt thay vì dùng key i18n.

## 📂 Files cần sửa
- `lib/features/hunt/monster_manager_win.py` — grep: `grep -n "MagicMock" lib/features/hunt/monster_manager_win.py`
- `lib/features/hunt/hunt_orchestrator.py` — grep text tĩnh.

## 📂 File Ownership
### Primary Owner (toàn quyền)
- `lib/features/hunt/monster_manager_win.py`
- `lib/features/hunt/hunt_orchestrator.py`
### Shared File (chỉ sửa subsection)
- KHÔNG CÓ

## ✅ Requirements
1. Loại bỏ toàn bộ từ khóa `MagicMock` trong thư mục `lib/` (không tính `tests/`). Production code không được biết mình đang chạy trong test.
   **Trace:** Source: Finding #5
2. Trong test, sử dụng mocker patch đúng chuẩn để giả lập messagebox mà không cần modify source code.
   **Trace:** Source: Finding #5
3. `hunt_orchestrator.py` gửi Event qua EventBus với i18n key (`_t`) hoặc gửi tín hiệu trạng thái thuần túy để UI tự translate.
   **Trace:** Source: Debt D6

## 🚫 Out of scope
- Thiết kế lại `hunt_orchestrator` loop core.

## 🧪 Acceptance Criteria
- [ ] AC1: `grep -rn "MagicMock" lib/` → Trả về 0 kết quả.
- [ ] AC2: `monster_manager_win.py` không crash và test liên quan trong `tests/` pass 100%.
- [ ] AC3: EventBus payloads sạch text tiếng Anh cứng.

## 🧪 Verification
**Grep:** `grep -rn "MagicMock" lib/` → Expected: Rỗng.
**Test:** `pytest tests/lib/features/hunt/ -v` → Expected: All pass.
**Manual:** Bật hunt_orchestrator và xác minh console/log xuất dữ liệu đã được map chuẩn i18n hoặc signal.

## 📤 Output format
1. File đã sửa.
2. Diff logic mock removal.
3. Test pass evidence.
4. Blocker.

## 🛑 Stop Conditions
DỪNG và báo user nếu:
- Cách viết test hiện tại bị phá vỡ và không thể patch bằng pytest-mock bình thường.
- Gửi signal thuần túy phá vỡ UI client đang lắng nghe string cũ.

## 🔗 Reference
- Context: `00_context_audit_summary.md`
- Audit: `audit-batch-4.md`