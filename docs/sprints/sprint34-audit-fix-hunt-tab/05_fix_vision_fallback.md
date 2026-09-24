# Prompt: Fix vision fallback

## 📖 Context
Đọc `00_context_audit_summary.md` trước. Task này fix Finding #6.


## 🔄 Trạng thái hiện tại
- 🟢 **Đã hoàn thành**: Luồng xử lý timeout trong `VisionSnapshotDebugger` đã loại bỏ lệnh `self.canvas.delete("all")`. Khi frame mới được tạo, ảnh cũ được xóa bằng tag `delete("image")` thay vì xóa toàn bộ canvas.
- **Hành động**: Đã thay thế `delete("all")` bằng `delete("image")` và `delete("timeout_text")`.

## 🎯 Scope
- Finding: #6 | Priority: P2 | Estimate: 0.5h
- Dependency: Independent
- Dependency Check: `grep -rn "self.canvas.delete" ui/components/vision_snapshot_debugger.py`

## 🔍 Vấn đề cần fix
Trong `VisionSnapshotDebugger`, đoạn code hiện tại thực hiện `self.canvas.delete("all")` khi gặp timeout (`frame is None`), điều này vi phạm yêu cầu gốc: "Nếu Timeout, UI phải dùng lại ảnh Snapshot cũ". Cần sửa để giữ nguyên ảnh trên canvas và có thể chỉ hiển thị cảnh báo timeout mà không xóa ảnh.

## 📂 Files cần sửa
- `ui/components/vision_snapshot_debugger.py` — grep: `grep -n "frame is None" ui/components/vision_snapshot_debugger.py`

## 📂 File Ownership
### Primary Owner (toàn quyền)
- `ui/components/vision_snapshot_debugger.py`
### Shared File (chỉ sửa subsection)
- KHÔNG CÓ

## ✅ Requirements
1. Khi phương thức lấy snapshot gặp timeout (nhận về `None`), giao diện phải duy trì hình ảnh quét cuối cùng trên canvas.
   **Trace:** Source: Finding #6 / Spec violation
2. Hiển thị thông báo (ví dụ overlay text "Timeout/No Frame") nhưng không xóa ảnh.
   **Trace:** Source: Finding #6

## 🚫 Out of scope
- Thay đổi logic timeout của `VisionEngine` backend.

## 🧪 Acceptance Criteria
- [x] AC1: Lệnh `self.canvas.delete("all")` không được thực thi trong nhánh `frame is None`.
- [x] AC2: Hình ảnh cũ được giữ lại và không gây crash hay rò rỉ bộ nhớ.
- [x] AC3: Pass unit test `test_vision_snapshot_debugger.py`.
- [x] AC4: Tuân thủ quy định i18n cho text "Timeout".

## 🧪 Verification
**Grep:** `grep -A 5 -n "frame is None" ui/components/vision_snapshot_debugger.py` → Expected: Không chứa lệnh `delete("all")`.
**Test:** `pytest tests/ui/components/test_vision_snapshot_debugger.py -v` → Expected: Toàn bộ pass.
**Manual:** Mở debugger, cố ý trigger timeout từ Vision Engine và xác nhận canvas vẫn giữ nguyên ảnh.

## 📤 Output format
1. File sửa duy nhất.
2. Diff logic (10 dòng).
3. Kết quả test.
4. Blocker nếu có.

## 🛑 Stop Conditions
DỪNG và báo user nếu:
- Timeout xảy ra liên tục khiến app bị treo.
- Cần thay đổi kiến trúc của Toplevel.

## 🔗 Reference
- Context: `00_context_audit_summary.md`
- Audit: `audit-batch-2.md`
- Spec gốc: `07_task_vision_debugger.md`