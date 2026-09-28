# Prompt 08 — Feature: hiển thị thông tin window đang quét

## Mục tiêu
User thấy ngay: tên window, handle, tọa độ, trạng thái kết nối, preview.

## Phạm vi
- SỬA: `ui/tabs/hunt_tab.py`, `ui/components/window_info_panel.py` (mới nếu cần).
- Depends: prompt-06.

## Công việc
1. Tạo/thêm panel "Window Source" hiển thị:
   - Tên cửa sổ (title).
   - Handle / PID.
   - Tọa độ (x, y, w, h).
   - Trạng thái: `CONNECTED` / `LOST` / `NOT_SELECTED`.
   - Thumbnail preview (cập nhật mỗi ~1s, không spam main thread).
2. Nút "Chọn lại cửa sổ" (chỉ enable khi không scan).
3. i18n cho mọi label.

## Kiểm thử
- [ ] Chọn window → info hiển thị đúng.
- [ ] Đóng game → trạng thái chuyển `LOST`.
- [ ] Preview cập nhật, không giật UI.
- [ ] i18n: VI + EN.

## Commit
```
feat(ui): display active window source info in hunt tab
```
