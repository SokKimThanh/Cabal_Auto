# Prompt 09: Xử lý các Edge Cases & Known Issues

## Mục tiêu
Khắc phục các rủi ro hệ thống đã được liệt kê trong phần "8. Các Vấn Đề Còn Tồn Đọng & Rủi Ro Hệ Thống", đảm bảo hệ thống vận hành an toàn, không sinh rác dữ liệu, không văng lỗi ngoài ý muốn.

## Ngữ cảnh & Yêu cầu từ Đặc tả
Cần xử lý 5 vấn đề:
1.  **Orphaned Files (Rác dữ liệu):** Dọn file khi xóa.
2.  **File Name Collision (Trùng tên):** Sửa tên file tự động khi chép.
3.  **Image Dimensions (Kích thước lớn):** Resize ảnh.
4.  **Referential Integrity (Toàn vẹn xóa):** Chặn xóa nếu còn usage.
5.  **i18n Validation:** Kiểm tra Tooltip Key có hợp lệ.

## Các bước triển khai chi tiết dành cho Người/AI

### Bước 1: Xử lý Orphaned Files (Rác Dữ Liệu)
- **Vị trí:** `IconService.delete_icon()` (hoặc `upsert_icon` khi đổi ảnh).
- **Hành động:**
  - Trước khi xóa 1 icon, lấy `filepath` của nó. Truy vấn DB xem có `icon` nào khác đang dùng chung tên file này không.
  - Nếu số đếm = 1 (tức là chỉ mình nó xài), thì gọi `IconFileManager.delete_icon_file(filepath)` để xóa file vật lý.
  - (Tương tự khi Edit đổi sang ảnh khác, cần kiểm tra và xóa file cũ nếu không ai dùng).

### Bước 2: Xử lý File Name Collision (Xung đột Tên)
- **Vị trí:** `IconFileManager.import_icon_file()`.
- **Hành động:**
  - Trước khi copy, kiểm tra xem `target_filename` đã tồn tại chưa (`os.path.exists`).
  - Nếu có, viết vòng lặp thêm hậu tố số (VD: `file_1.png`, `file_2.png`) cho đến khi tìm được tên chưa tồn tại.
  - Copy với tên mới và trả về tên mới đó.

### Bước 3: Xử lý Image Dimensions (Resize)
- **Vị trí:** `IconFileManager.import_icon_file()`.
- **Hành động:**
  - Dùng thư viện PIL (Pillow): `from PIL import Image`.
  - Mở file bằng PIL, kiểm tra `.size`.
  - Nếu max(width, height) > 128 (hoặc thông số cấu hình), dùng `img.thumbnail((128, 128), Image.Resampling.LANCZOS)`.
  - Lưu lại đè lên file vừa copy. Tránh làm sập bộ nhớ.

### Bước 4: Xử lý Referential Integrity (Toàn vẹn Dữ liệu)
- **Vị trí:** UI - Hàm `self._on_delete()` hoặc `IconService.delete_icon()`.
- **Hành động:**
  - Khi xóa, đếm số lượng record trong `icon_usages` cho `icon_key` đó.
  - Nếu > 0, văng lỗi `ValueError("Cannot delete icon in use")` (ở tầng Service).
  - Tầng UI bắt lỗi này, hiển thị cảnh báo: "Icon đang được sử dụng ở X nơi. Vui lòng gỡ bỏ trước khi xóa."

### Bước 5: Xử lý i18n Translation Validation
- **Vị trí:** UI - Hàm Load Icon Detail hoặc Validate.
- **Hành động:**
  - Trong logic hàm `self._render_preview()` hoặc một hàm kiểm tra, lấy giá trị của `tooltip_translation_key`.
  - Gọi service đa ngôn ngữ hiện tại (VD: `TranslationService.get(key)`). Nếu trả về đúng chuỗi gốc (hoặc lỗi), hiển thị một icon ⚠️ (Warning) nhỏ bên cạnh ô nhập liệu để báo "Key chưa được khai báo trong từ điển i18n".

### Bước 6: Viết Unit Test cho Edge Cases
- **Vị trí:** Bổ sung vào các file test tương ứng.
- **Hành động:**
  - Test xóa icon -> file vật lý bị xóa (Orphaned).
  - Test chép 2 file cùng tên -> hệ thống sinh hậu tố.
  - Test xóa icon đang bị ràng buộc -> Văng exception.

## Tiêu chí hoàn thành (Definition of Done)
- [ ] Xóa/đổi ảnh không để lại file rác trong `assets/images/icon/`.
- [ ] Chép trùng tên không bị ghi đè.
- [ ] Ảnh bự (>128px) tự động bị thu nhỏ khi Import.
- [ ] Không thể xóa icon đang dùng trên giao diện.
- [ ] Có cảnh báo nếu điền sai mã đa ngôn ngữ.

## Thời gian dự kiến: ~40 phút
