# Prompt 03 — Audit Debug Vision display

## Mục tiêu
Xác định Debug Vision có hiển thị đúng ảnh đang được quét hay không.

## Root Cause
Người dùng không thể đối chiếu ảnh Debug với ROI đã chọn.

## Phạm vi
- CHỈ ĐỌC.
- Đọc: `ui/components/vision_snapshot_debugger.py`, `lib/vision/vision_engine.py`.

## Công việc
1. Xác định Debug Vision đang show loại ảnh nào:
   - Full frame?
   - ROI crop?
   - Ảnh đã tiền xử lý (grayscale/threshold)?
   - Kết quả sau OCR/detect?
2. Kiểm tra có overlay ROI box không.
3. Kiểm tra có hiển thị window source không.
4. Kiểm tra có so sánh được input vs output không.

## Output
- Bảng: `Loại ảnh | Có hiển thị? | Widget | Nguồn dữ liệu`
- Danh sách gap so với kỳ vọng user.
- Lưu tại: `docs/sprints/sprint35-hunt-window-roi-ux/audit-03-debug-vision.md`

## Commit
```
docs(sprint35): audit debug vision image source and overlays
```
