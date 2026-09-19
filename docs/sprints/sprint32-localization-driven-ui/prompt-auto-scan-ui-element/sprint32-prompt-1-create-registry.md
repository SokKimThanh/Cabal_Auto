# Prompt 1: Tạo UI Element Registry

**Mục tiêu:**
Tạo một Singleton Registry in-memory để quản lý các Element ID (chủ yếu là cho các nút hoặc UI widget có hỗ trợ Icon). Task này mất khoảng 15-20 phút.

**Các bước thực hiện:**
1. Tạo file mới: `lib/events/ui_element_registry.py` (hoặc đặt ở `ui/helpers/` nếu thấy phù hợp hơn với kiến trúc frontend).
2. Định nghĩa class `UIElementRegistry`.
3. Biến nó thành Singleton Pattern (chú ý đến việc không dùng biến toàn cục bừa bãi, nếu có bootstrapper/DI thì tốt, nhưng theo memory context thì có thể tiêm qua App bootstrapper hoặc dùng dạng đơn giản để các helper có thể call trực tiếp). Do tính chất đơn giản, ta có thể tạo `_instance`.
4. Cung cấp các method:
   - `register(element_id: str)`: Lưu id vào một Set in-memory để loại bỏ trùng lặp.
   - `get_all() -> list[str]`: Trả về danh sách các id đã được sort.
   - `clear()`: (Dùng cho unit test).
5. Viết một file unit test ngắn: `tests/ui/test_ui_element_registry.py` để verify registry này hoạt động bình thường.

**Ràng buộc (Memory):**
- Tránh tạo các Global Singletons mới nếu có thể dùng bootstrapper, NHƯNG đối với UI Helper (static function), việc pass DI rất khó. Cân nhắc kỹ việc tạo instance. Tham khảo cách `IconHelper` đang dùng bộ nhớ đệm nội bộ (class attributes). Bạn có thể implement nó dưới dạng Class Methods trên `UIElementRegistry` (như một static class) thay vì Singleton instance.
