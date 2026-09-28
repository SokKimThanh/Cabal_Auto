# Prompt 09 — Feature: nhãn mô tả nghiệp vụ cho 4 nút Scan

## Mục tiêu
Mỗi nút Scan có: tên nghiệp vụ, mô tả mục đích, tooltip hướng dẫn.

## Phạm vi
- SỬA: `ui/tabs/hunt_tab.py`, i18n files.
- Depends: prompt-04.

## Công việc
1. Với MỖI nút (`combo_bar`, `self_stats`, `minimap`, `hunt_area.set`):
   - Đổi label UI sang tên nghiệp vụ:
     - `combo_bar` → "Thiết lập thanh Combo"
     - `self_stats` → "Thiết lập chỉ số nhân vật"
     - `minimap` → "Thiết lập Minimap"
     - `hunt_area.set` → "Thiết lập vùng săn"
   - Thêm tooltip mô tả: mục đích + dữ liệu đọc + kết quả kỳ vọng.
2. Nếu prompt-04 đánh dấu ô UNKNOWN → hiển thị "Chưa có đặc tả" (TODO).

## Kiểm thử
- [ ] Hover mỗi nút → tooltip hiển thị đúng.
- [ ] i18n VI + EN.
- [ ] Không phá layout hiện tại.

## Commit
```
feat(ui): add business labels and tooltips for hunt scan buttons
```
