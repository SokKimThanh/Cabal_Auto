# Prompt 02: Tách ImageLibraryComponent từ IconManagerFrame

**Thời gian dự kiến:** < 30 phút

## Mục tiêu
Tách rời phần khung "Thư viện Ảnh" (Image Library) bao gồm danh sách ảnh, thanh tìm kiếm và nút import ra khỏi `IconManagerFrame`.

## Yêu cầu thực hiện
1. **Tạo file mới:** Tạo file `ui/components/image_library_component.py`.
2. **Khai báo Class:** Tạo class `ImageLibraryComponent(tk.Frame)`.
3. **Di chuyển giao diện (View):** Chuyển nội dung hàm `_build_image_library_panel` từ `icon_manager_frame.py` sang class mới.
4. **Di chuyển Logic:** Di chuyển các hàm:
   - `_on_img_search_change`
   - `_perform_img_search`
   - `_on_image_library_scanned`
   - `_update_image_listbox`
   - `_highlight_image_in_list`
   - `_on_import_image_clicked` (Một phần logic UI. Lưu ý: File dialog có thể giữ ở đây nhưng luồng lưu/cảnh báo nên tương tác qua Model).
5. **Thiết lập Callback:** Khi người dùng chọn một ảnh (`_on_image_selected`), component này không được phép trực tiếp sửa đổi các biến `var_filepath` của form chính. Thay vào đó, nó phải phát ra một sự kiện (hoặc gọi callback `on_image_selected(filepath)`). Form chính sẽ nhận filepath này và tự cập nhật biến.
6. **Cập nhật IconManagerFrame:** Thay thế code cũ bằng việc nhúng `ImageLibraryComponent` và nối callback xử lý tương ứng.

## Điều kiện hoàn thành (DoD)
- Giao diện thư viện ảnh hiển thị danh sách file đúng đắn.
- Chức năng tìm kiếm và highlight file ảnh khi chọn Icon vẫn hoạt động mượt mà.
- File gốc `icon_manager_frame.py` được tinh gọn đáng kể.
