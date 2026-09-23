# Prompt: Cleanup D4 D6

## 📖 Context
Đọc `00_context_audit_summary.md` trước. Task này fix Tech Debt D4 và D6.


## 🔄 Trạng thái hiện tại
- 🟡 **Hoàn thành 1 phần**: Không còn tìm thấy `_pulse_step` gây phân mảnh event loop trong `status_badge.py` (D4 đã ổn). Tuy nhiên, các chuỗi text hardcode (D6) vẫn chưa được wrap bằng hàm đa ngôn ngữ `_t()`.
- **Hành động**: Tiếp tục quét các file UI để thay thế hardcode string sang i18n key.

## 🎯 Scope
- Finding: D4, D6 | Priority: P1 | Estimate: 4h
- Dependency: Task 03 hoàn thiện (Đã xử lý emoji cứng)
- Dependency Check: `grep -rn "_pulse_step" ui/components/status_badge.py`

## 🔍 Vấn đề cần fix
Hệ thống UI đang bị phân mảnh vòng lặp Tkinter (D4) do gọi độc lập các hàm `.after()` như `_pulse_step` trong `status_badge.py` thay vì dùng `UIAnimationManager`. Đồng thời, vẫn còn nhiều hardcode tiếng Anh/Việt (D6) không được wrap bằng `_t()`. Cần chuẩn hóa toàn bộ vào trung tâm.

## 📂 Files cần sửa
- `ui/components/status_badge.py` — grep: `grep -n "_pulse_step" ui/components/status_badge.py`
- Các file có timer `.after` không đăng ký qua AnimationManager.
- Các file UI có hardcode string tĩnh chưa được thay thế ở Task 03.

## 📂 File Ownership
### Primary Owner (toàn quyền)
- `ui/components/status_badge.py`
### Shared File (chỉ sửa subsection)
- Các file UI bị vướng hardcode text.

## ✅ Requirements
1. Animation hoặc logic pulse (ví dụ đổi màu chớp tắt) phải thông qua `UIAnimationManager` hoặc `HuntStatusTicker` thay vì tự tạo `.after()` vòng lặp.
   **Trace:** Source: Debt D4
2. Áp dụng chuẩn `_t("...")` cho 100% text hiển thị. Không sử dụng hardcode string như "Đang chờ", "Sẵn sàng".
   **Trace:** Source: Debt D6

## 🚫 Out of scope
- Cập nhật backend (Task 08 sẽ lo).
- Viết thêm hiệu ứng mới cho AnimationManager.

## 🧪 Acceptance Criteria
- [ ] AC1: `grep -rn "def _pulse_step" ui/` → Trả về rỗng.
- [ ] AC2: `grep -rn "Đang chờ" ui/` → Trả về rỗng.
- [ ] AC3: Behavior của Status Badge (nhấp nháy) vẫn hoạt động tương đương.
- [ ] AC4: Không phá vỡ Unit test hiện có của `UIAnimationManager`.

## 🧪 Verification
**Grep:** `grep -rn "\.after(" ui/components/status_badge.py` → Expected: Rỗng (hoặc chỉ dùng để gọi init, không lặp).
**Test:** `pytest tests/ui/ -v` → Expected: All pass.
**Manual:** Kiểm tra tab Hunt, xem phần trạng thái nhấp nháy có hoạt động đúng và sử dụng i18n hay không.

## 📤 Output format
1. Danh sách các file.
2. Diff logic Animation.
3. Kết quả test `UIAnimationManager`.
4. Blocker.

## 🛑 Stop Conditions
DỪNG và báo user nếu:
- `UIAnimationManager` không hỗ trợ pulse loop logic, cần update thư viện lõi.
- `_t()` thiếu dictionary ngôn ngữ hiện tại gây lỗi dịch thuật hiển thị rỗng.

## 🔗 Reference
- Context: `00_context_audit_summary.md`
- Audit: `audit-batch-4.md`