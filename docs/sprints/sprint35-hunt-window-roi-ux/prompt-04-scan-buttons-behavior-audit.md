# Prompt 04 — Audit đặc tả hành vi 4 nút Scan

## Mục tiêu
Xác định mục đích, input, output, validation của từng nút Scan trong Hunt tab.

## Root Cause
4 nút (`setup_roi.combo_bar`, `setup_roi.self_stats`, `setup_roi.minimap`, `hunt_area.set`) bấm lên chỉ hiện khung trống, không có mô tả nghiệp vụ.

## Phạm vi
- CHỈ ĐỌC.
- Đọc: `ui/tabs/hunt_tab.py`, `lib/features/hunt/*`, i18n files.

## Công việc
1. Với MỖI nút, trả lời:
   - Quét cái gì?
   - Dữ liệu đọc là gì?
   - ROI yêu cầu chứa thành phần UI nào của game?
   - Đầu ra là gì?
   - Đi đến panel nào?
   - Có validation không?
   - Có chặn dữ liệu bất thường không?
2. Tạo bảng:

| Nút | Mục đích | Dữ liệu đọc | ROI yêu cầu | Đầu ra | Panel nhận | Validation |
|---|---|---|---|---|---|---|
| combo_bar | ? | ? | ? | ? | ? | ? |
| self_stats | ? | ? | ? | ? | ? | ? |
| minimap | ? | ? | ? | ? | ? | ? |
| hunt_area | ? | ? | ? | ? | ? | ? |

3. Đánh dấu ô nào KHÔNG xác định được từ code → ghi nhận là "thiếu đặc tả hệ thống".

## Output
- Bảng hoàn chỉnh.
- Danh sách ô "UNKNOWN" = technical debt.
- Lưu tại: `docs/sprints/sprint35-hunt-window-roi-ux/audit-04-scan-buttons.md`

## Commit
```
docs(sprint35): audit behavior spec for 4 hunt scan buttons
```
