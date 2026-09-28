# Prompt 11 — Feature: preview kết quả Scan (input → processed → output)

## Mục tiêu
Sau khi scan, user thấy: ảnh ROI, ảnh tiền xử lý, kết quả OCR/Vision, Pass/Fail.

## Phạm vi
- SỬA: `ui/components/vision_snapshot_debugger.py`, `ui/tabs/hunt_tab.py`.
- Depends: prompt-03.

## Công việc
1. Sau mỗi scan, panel Debug hiển thị 4 tab nhỏ:
   - Tab 1: Ảnh ROI gốc.
   - Tab 2: Ảnh đã tiền xử lý (grayscale/threshold).
   - Tab 3: Kết quả OCR/Vision (text + box).
   - Tab 4: Trạng thái Pass/Fail + lý do fail (nếu có).
2. Cho phép user mở rộng ảnh để đối chiếu.
3. Không lưu ảnh vĩnh viễn (tránh rò rỉ bộ nhớ).

## Kiểm thử
- [ ] Scan thành công → cả 4 tab có dữ liệu.
- [ ] Scan fail → tab 4 hiển thị lý do.
- [ ] Không rò rỉ bộ nhớ sau 100 lần scan.

## Commit
```
feat(ui): show scan result preview pipeline input-processed-output
```
