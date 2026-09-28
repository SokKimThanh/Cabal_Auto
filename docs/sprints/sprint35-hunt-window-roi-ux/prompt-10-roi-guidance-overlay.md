# Prompt 10 — Feature: overlay hướng dẫn khi chọn ROI

## Mục tiêu
Khi user bấm Scan, overlay hiển thị tiêu đề + hướng dẫn + ví dụ vùng đúng/sai.

## Phạm vi
- SỬA: `ui/windows/overlay_window.py` (hoặc `ui/controllers/overlay_controller.py`), i18n files.
- Depends: prompt-05.

## Công việc
1. Trên overlay, thêm:
   - Header: "Đang thiết lập: {tên nghiệp vụ}".
   - Body: mô tả "Khoanh vùng X trên cửa sổ game. Vùng cần chứa Y."
   - Side preview: ảnh mẫu đúng + ảnh mẫu sai (nếu có asset).
   - Nút "Hủy" + "Xác nhận".
2. Text i18n cho mọi ngôn ngữ hỗ trợ.
3. Không block main thread; overlay phải có nút Esc để thoát.

## Kiểm thử
- [ ] Mở overlay cho từng loại ROI → hiển thị đúng.
- [ ] Esc đóng được.
- [ ] i18n đầy đủ.

## Commit
```
feat(ui): add contextual guidance overlay for roi selection
```
