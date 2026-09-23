# Prompt: Verify integrate Task 6

## 📖 Context
Đọc `00_context_audit_summary.md` trước. Task này fix Finding #3.

## 🎯 Scope
- Finding: #3 | Priority: P1 | Estimate: 1h
- Dependency: Task 01, Task 02 đã hoàn tất UI tĩnh
- Dependency Check: `grep -rn "HuntStatusTicker" ui/views/hunt_workspace_frame.py`

## 🔍 Vấn đề cần fix
`HuntStatusTicker` đã được tích hợp vào `HuntWorkspaceFrame`, nhưng do sử dụng `PanedWindow` trong `HuntTab`, có khả năng Ticker đang bị che khuất hoặc không hoạt động chính xác. Cần xác minh quan hệ layout và có thể sửa đổi lại để Ticker luôn hiển thị rõ ràng.

## 📂 Files cần sửa
- `ui/views/hunt_workspace_frame.py` — nơi Ticker được chèn vào, grep: `grep -n "HuntStatusTicker" ui/views/hunt_workspace_frame.py`
- `ui/tabs/hunt_tab.py` — nếu cần phân bổ lại không gian layout.

## 📂 File Ownership
### Primary Owner (toàn quyền)
- `ui/views/hunt_workspace_frame.py`
### Shared File (chỉ sửa subsection)
- `ui/tabs/hunt_tab.py` (chỉ giới hạn trong việc cấu hình `pack` hoặc `grid` của Ticker).
- `ui/components/hunt_status_ticker.py` (chỉ sửa bug logic update đè message nếu có).

## ✅ Requirements
1. `HuntStatusTicker` phải được render và hiển thị rõ ràng ở cuối workspace, không bị PanedWindow che lấp.
   **Trace:** Source: Finding #3
2. Fix bug logic: `_update_state_ui` không được phép ghi đè thông báo mà `_update_status_ui` vừa set ngay lập tức. Cần quản lý priority cho các event này.
   **Trace:** Source: Finding #3

## 🚫 Out of scope
- Sửa đổi nội dung event từ EventBus.

## 🧪 Acceptance Criteria
- [ ] AC1: Ticker hiển thị rõ ràng trong quá trình chạy, ngay cả khi thay đổi kích thước các khung chứa qua sash.
- [ ] AC2: Thông báo trạng thái không bị giật hoặc đè liên tục khi nhận hai event cùng lúc.
- [ ] AC3: Giao diện PanedWindow của HuntTab không bị vỡ.
- [ ] AC4: Tuân thủ quy chuẩn D4.

## 🧪 Verification
**Grep:** `grep -n "pack.*side=" ui/views/hunt_workspace_frame.py` → Expected: Kiểm tra vị trí pack phù hợp (thường là BOTTOM).
**Test:** `pytest -v tests/ui/` → Expected: X/Y passed (Nếu có test liên quan).
**Manual:** Kéo thanh chia (sash) của HuntTab về nhỏ nhất, kiểm tra `HuntStatusTicker` vẫn hiển thị ở cuối không bị che mất. Gửi liên tiếp hai tín hiệu trạng thái và kiểm tra UI.

## 📤 Output format
1. Files đã sửa.
2. Diff tóm tắt thay đổi layout.
3. Kết quả Manual test screenshot/video (nếu được yêu cầu).
4. Blocker nếu có.

## 🛑 Stop Conditions
DỪNG và báo user nếu:
- Cách pack hiện tại đã đúng nhưng lỗi nằm ở container cha (root window).
- Phải refactor lại toàn bộ `HuntTab` để chứa Ticker.

## 🔗 Reference
- Context: `00_context_audit_summary.md`
- Audit: `audit-batch-2.md`
- Spec gốc: `06_task_status_ticker.md`