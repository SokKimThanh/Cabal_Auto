# Prompt 2: Cập nhật UI Helpers với `element_id`

**Mục tiêu:**
Sửa đổi các hàm tạo UI component để chấp nhận tham số `element_id` và tự động đăng ký vào Registry. Task này mất khoảng 20-30 phút.

**Các bước thực hiện:**
1. Mở file `ui/components/icon_button.py` (và các file helpers tương tự nếu có).
2. Tìm hàm `create_icon_button` và các hàm wrapper (`create_add_button`, `create_save_button`, `create_delete_button`, `create_refresh_button`...).
3. Cập nhật signature: Thêm tham số `element_id: Optional[str] = None` vào tất cả các hàm này.
4. Xử lý logic:
   - Nếu `element_id` có giá trị, gán giá trị đó vào widget (VD: `btn._element_id = element_id`).
   - Gọi `UIElementRegistry.register(element_id)` (import từ class đã tạo ở Prompt 1) để đăng ký ID vào bộ nhớ đệm.
5. Chạy unit tests liên quan đến UI Helpers (VD: `pytest tests/ -k "test_icon_button"`) để đảm bảo không phá hỏng các tham số cũ.

**Ràng buộc (Memory):**
- Đảm bảo tham số mới không phá vỡ (break) backward compatibility với các code cũ đang gọi `create_icon_button` (phải để default là `None`).
- Tkinter UI components must strictly adhere to UI-only concerns. Việc gán thuộc tính ẩn (`_element_id`) là phù hợp để quản lý metadata.

**Các rủi ro cần tránh (Risk Mitigation):**
- **ID Collision:** Thêm comment/docstring vào tham số `element_id` khuyến nghị lập trình viên nên sử dụng namespace/prefix (VD: `module_name_btn_id`) thay vì đặt tên chung chung như `btn_save`.
