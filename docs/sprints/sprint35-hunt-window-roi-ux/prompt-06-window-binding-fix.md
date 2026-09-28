# Prompt 06 — Fix: Lock selected game window cho mọi Scan

## Mục tiêu
Đảm bảo mọi thao tác Scan trong Hunt tab đều dùng `selected_window`, không phụ thuộc `active_window`.

## Root Cause
(theo kết quả prompt-01) Window context không được lock, rơi về active window.

## Phạm vi
- CHỈ SỬA 1-2 file: `lib/system/window_manager.py`, `ui/tabs/hunt_tab.py`.
- KHÔNG chạm ROI Scanner (sẽ làm ở prompt-07).

## Công việc
1. Trong `WindowManager`, thêm/làm rõ:
   ```python
   def get_selected_window(self) -> WindowInfo | None: ...
   def lock_selection(self) -> None: ...
   def unlock_selection(self) -> None: ...
   ```
2. Trong Hunt tab, khi user chọn game window:
   - Gọi `lock_selection()`.
   - Disable nút "đổi window" khi đang scan.
3. Khi scan: LUÔN dùng `get_selected_window()`, KHÔNG fallback `active_window`.
4. Nếu `selected_window is None` → raise/return lỗi rõ ràng, KHÔNG tự chọn active.

## Kiểm thử bắt buộc
- [ ] Game foreground → scan đúng.
- [ ] Game background → scan đúng (không lấy cửa sổ khác).
- [ ] Nhiều cửa sổ CABAL → dùng đúng cửa sổ đã chọn.
- [ ] Không có game → báo lỗi rõ ràng, không crash.

## Tiêu chí hoàn thành
- `grep -rn "active_window" lib/features/hunt/scanner.py` → không còn dùng cho scan.
- Test mới: `tests/vision/test_window_manager_lock.py` pass.

## Commit
```
fix(vision): lock selected game window for all hunt scans
```
