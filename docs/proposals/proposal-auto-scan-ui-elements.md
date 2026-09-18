# Proposal: Tự động Quét và Đăng ký UI Element ID (Auto-Scan UI Elements)

## Bối cảnh và Vấn đề
Hiện tại, trong Icon Manager, phần "Quản lý Nơi Dùng (Usages)" yêu cầu người dùng phải gõ tên (ID) của element (như button, label) để map một Icon vào element đó.
Để giải quyết tạm thời UX, chúng ta đã dùng `Combobox` hiển thị các ID *đã từng được map* trong database. Tuy nhiên, nếu một button mới được code vào UI, người dùng vẫn phải xem code để nhớ chính xác ID, gõ tay vào lần đầu, tiềm ẩn rủi ro sai chính tả.
Vì vậy, cần có một hệ thống tự động quét (scan) tất cả các UI Element có khả năng gắn Icon, đăng ký chúng vào một "Registry", và đổ ra Combobox ngay cả khi chúng chưa từng được gán Icon bao giờ.

## Mục tiêu
- Tạo một bộ nhớ đệm (Registry) lưu trữ danh sách toàn bộ ID của các widget có hỗ trợ Icon (VD: các button, label) trên toàn bộ ứng dụng.
- Icon Manager có thể đọc Registry này để đưa ra danh sách gợi ý chính xác và đầy đủ 100% trong chức năng Gắn (Map) Usages.

## Giải pháp Đề xuất

### Giai đoạn 1: Chuẩn hóa tham số `id`
1. Sửa đổi định nghĩa của các hàm UI Helpers: `create_icon_button`, `create_icon_label` (nằm rải rác ở `ui/components/icon_button.py` hoặc các file liên quan).
2. Thêm tham số `element_id: str = None` (hoặc `widget_id`) vào các hàm này.
3. Khi lập trình viên gọi `create_icon_button(..., element_id="btn_settings")`, hàm này sẽ lưu trữ ID đó vào widget: `button._element_id = element_id`.

### Giai đoạn 2: Tự động đăng ký (Runtime Registry)
1. Tạo một Singleton tên là `UIElementRegistry` (có thể nằm ở `lib/events/ui_registry.py`).
2. Registry này chứa tập hợp `set` các ID.
3. Khi `create_icon_button` được gọi ở runtime, nếu có `element_id`, nó sẽ gọi `UIElementRegistry.register(element_id)`.
4. Hạn chế: Cách này chỉ quét được các ID của những màn hình *đã được khởi tạo* (rendered). Một số tab bị ẩn có thể không quét được nếu chưa mở.

### Giai đoạn 3: Quét tĩnh qua AST (Tùy chọn nâng cao)
- Viết một script nhỏ `scripts/scan_ui_elements.py` sử dụng thư viện `ast` (Abstract Syntax Tree) của Python.
- Script sẽ duyệt qua toàn bộ thư mục `ui/`, tìm các lệnh gọi `create_icon_button` hoặc `create_button`, trích xuất giá trị truyền vào tham số `element_id` và xuất ra một file JSON tĩnh: `config/ui_elements.json`.
- Icon Manager sẽ đọc file JSON này thay vì đợi Runtime. Cách này đảm bảo có đủ 100% ID trước cả khi chạy ứng dụng.

## Kế hoạch Thực thi (Sprint Tiếp Theo)
1. Review tất cả các lời gọi hàm tạo nút (`create_icon_button`, `create_button`) và bổ sung định danh `element_id`.
2. Quyết định chọn **Giai đoạn 2** (Dễ làm, Runtime) hoặc **Giai đoạn 3** (Triệt để, Tĩnh). Đề xuất ưu tiên Giai đoạn 3.
3. Tích hợp danh sách ID thu được (từ Registry hoặc JSON) vào `self._available_usage_ids` của form "Usages" trong `IconManagerFrame`.

## Lợi ích
- Đảm bảo tính toàn vẹn dữ liệu: Không bao giờ gõ sai ID.
- Lập trình viên không cần nhảy qua lại giữa code và UI để tra cứu tên biến.
- Tự động hóa hoàn toàn quy trình liên kết Icon-UI.