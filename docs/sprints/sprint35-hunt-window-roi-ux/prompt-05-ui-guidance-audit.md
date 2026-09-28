# Prompt 05 — Audit UI guidance & phản hồi thao tác Scan

## Mục tiêu
Đánh giá Instruction Layer của màn hình Scan/ROI.

## Root Cause
Khi bấm nút Scan, UI chỉ hiện khung chọn vùng trống, không có hướng dẫn.

## Phạm vi
- CHỈ ĐỌC.
- Đọc: `ui/tabs/hunt_tab.py`, `ui/windows/overlay_window.py`, `ui/controllers/overlay_controller.py`, i18n files. (Sử dụng module overlay thay vì `ui/components/roi_selection_overlay.py` dựa trên thực tế codebase).

## Công việc
1. Liệt kê TẤT CẢ phản hồi UI khi user bấm Scan:
   - Text?
   - Overlay?
   - Tooltip?
   - Status bar?
2. Kiểm tra có các thành phần sau không:
   - [ ] Tiêu đề mục đích ("Đang thiết lập: Minimap ROI")
   - [ ] Mô tả nghiệp vụ
   - [ ] Hướng dẫn "khoanh vùng X trên game"
   - [ ] Ví dụ vùng đúng
   - [ ] Ví dụ vùng sai
   - [ ] Preview kết quả kỳ vọng
   - [ ] Thông báo Pass/Fail sau scan
   - [ ] Lý do từ chối dữ liệu
3. Mỗi mục thiếu → đánh dấu là technical debt UX.

## Output
- Checklist đầy đủ.
- Danh sách gap.
- Lưu tại: `docs/sprints/sprint35-hunt-window-roi-ux/audit-05-ui-guidance.md`

## Commit
```
docs(sprint35): audit ui guidance layer for roi scan workflow
```
