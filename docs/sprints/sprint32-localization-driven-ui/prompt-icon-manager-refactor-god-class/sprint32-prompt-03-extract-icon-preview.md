# Prompt 03: Tách IconPreviewComponent

**Thời gian dự kiến:** 15-20 phút

## Mục tiêu
Tách rời khu vực "Preview Zone" (Hiển thị ảnh thu nhỏ của Icon, Empty State) thành component độc lập.

## Yêu cầu thực hiện
1. **Tạo file mới:** Tạo file `ui/components/icon_preview_component.py`.
2. **Khai báo Class:** Tạo class `IconPreviewComponent(tk.Frame)`.
3. **Di chuyển giao diện (View):** Chuyển nội dung hàm `_build_preview_zone` vào class mới.
4. **Di chuyển Logic:** Chuyển hàm `_render_preview(icon_data)` vào component này (có thể đổi tên thành `render(icon_data)`).
5. **Độc lập dữ liệu:** `IconPreviewComponent` cần nhận đầy đủ thông tin (filepath, fallback_emoji, tooltip_key, icon_key) qua tham số truyền vào hàm `render()`. Nó không được trực tiếp đọc `self.var_...` của form mẹ.
6. **Cập nhật IconManagerFrame:** Thay thế code render preview cũ bằng việc gọi `self.preview_component.render(icon_data)`.

## Điều kiện hoàn thành (DoD)
- Khi chọn Icon trên danh sách, hình ảnh hoặc emoji fallback hiển thị chính xác trong khung preview.
- Tooltip của ảnh (nếu có cấu hình) hiển thị đúng ưu tiên.
- Khung preview hiển thị Empty State nếu không có icon nào được chọn.
