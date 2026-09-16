# Sprint 31: Context Menu cho Tính năng Thay đổi Icon Nhanh

## Mục tiêu
Thiết kế tính năng cho phép người dùng thay đổi icon của một component cụ thể trực tiếp trên giao diện bằng cách sử dụng Context Menu (click chuột phải), thay vì phải quét toàn bộ UI Tree để tạo danh sách quản lý tập trung.

## Ngữ cảnh
Hiện tại kiến trúc của dự án áp dụng Composite Pattern và Event-Driven Architecture (SRP được tuân thủ nghiêm ngặt). Việc tạo một "Trung tâm đăng ký vị trí" quét qua toàn bộ UI Tree để thay đổi icon là không khả thi và sẽ phá vỡ tính decoupling.
Mọi UI Component hiện tại chỉ giao tiếp với nhau và với dữ liệu thông qua `icon_key`. Để hỗ trợ người dùng dễ dàng đổi icon cho một nút cụ thể, chúng ta cần một giải pháp dựa trên sự kiện (Event-Driven).

## Yêu cầu (Acceptance Criteria)
1. Thêm một tính năng Context Menu (menu chuột phải) vào các thành phần giao diện (UI Components) hỗ trợ icon (ví dụ: các nút bấm có icon_key).
2. Khi người dùng click chuột phải vào component đó, hiển thị tùy chọn: "Thay đổi Icon".
3. Khi click vào "Thay đổi Icon", hệ thống phát ra một sự kiện (ví dụ: `OpenIconManagerEvent(icon_key="start_btn")`).
4. Icon Manager sẽ lắng nghe sự kiện này, tự động mở lên, focus vào đúng dòng có `icon_key` tương ứng và đặt ở chế độ Edit.
5. Cập nhật cơ sở dữ liệu `icons` để sử dụng các cột `category` và `description` hiệu quả hơn (Data-Driven), giúp người dùng dễ nhận biết vị trí của icon (ví dụ: Category="Menu Chính", Description="Nút Bắt đầu").

## Risks and Things to Avoid
- Tránh việc truyền cứng reference của Icon Manager vào các UI Components (giữ nguyên quy tắc EventBus).
- Cẩn thận với các widget không được hỗ trợ bind sự kiện chuột phải trên các hệ điều hành khác nhau (đặc biệt giữa Windows và macOS `<Button-2>` vs `<Button-3>`).
- Không tạo một registry quản lý biến toàn cục mới cho các vị trí UI.
