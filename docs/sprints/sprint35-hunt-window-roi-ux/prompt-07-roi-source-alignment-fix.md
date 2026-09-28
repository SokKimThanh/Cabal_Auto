# Prompt 07 — Fix: ROI Scanner dùng đúng selected window

## Mục tiêu
ROI capture lấy ảnh từ `selected_window`, tọa độ tính theo origin của cửa sổ đó.

## Phạm vi
- SỬA: `lib/features/hunt/scanner.py`, `lib/system/screen_capture.py`.
- Depends: prompt-02, prompt-06.

## Công việc
1. Thay mọi screenshot full-screen / active-window bằng capture từ `selected_window`.
2. Chuẩn hóa origin tọa độ:
   - Nếu ROI lưu theo absolute screen coords → convert sang client coords của window.
   - Hoặc ngược lại, thống nhất 1 hệ.
3. Không thay đổi signature public (tránh break UI).
4. Log window source mỗi lần capture (DEBUG level).

## Kiểm thử
- [ ] ROI crop từ đúng window dù window ở background.
- [ ] Di chuyển window → ROI vẫn đúng.
- [ ] Resize window → ROI vẫn đúng (nếu hỗ trợ).
- [ ] Test `tests/vision/test_roi_scanner_source.py` pass.

## Commit
```
fix(vision): roi scanner captures from selected window with consistent coords
```
