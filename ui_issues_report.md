# Báo cáo Đánh giá Giao diện Người dùng (UI/UX Review)

Dựa trên hình ảnh giao diện được cung cấp, dưới đây là tổng hợp các vấn đề về thiết kế, bố cục, và độ tương phản màu sắc cần được khắc phục để hoàn thiện trải nghiệm người dùng (UX) và tính thẩm mỹ (UI):

## 1. Vấn đề về Độ tương phản & Màu sắc (Contrast & Colors)
* **Khu vực góc trên bên trái ("0 windows"):** Dữ liệu chữ màu đỏ sẫm đặt trên nền xám đen/tối có độ tương phản quá thấp, rất khó đọc. Cần đổi sang màu đỏ sáng hơn (light red/pastel red).
* **Sidebar (Menu trái):** Tab đang được chọn ("Săn") có viền/nền xanh lá nhưng chữ bên trong cũng khá tối, làm giảm khả năng nhận diện.
* **Chữ thông báo trạng thái:** Dòng chữ "Đã lưu tất cả thay đổi" (gần nút Áp dụng) dùng màu xanh lá cây đậm trên nền đen rất khó nhìn. Chữ trạng thái "CHỜ" ở phần Current Target cũng gặp tình trạng tương tự.
* **Lỗi nền trắng phá vỡ Dark Theme:**
  * Dòng hướng dẫn "Nhấp chuột phải để xóa từng quái..." dưới danh sách quái có nền màu trắng tinh.
  * Nhãn "Mục tiêu: Trống" ở góc trên phải có nền trắng.
  -> Hai thành phần này hoàn toàn phá vỡ tổng thể giao diện chế độ tối (dark mode). Cần đổi nền thành màu xám/đen (`BG_SURFACE`) và dùng chữ màu sáng (`TEXT_PRIMARY`).

## 2. Vấn đề về Styling & Widget Mặc định (Unstyled Components)
* **Thanh cuộn (Scrollbar):** Các thanh cuộn ở phần danh sách quái (Current Target) và thống kê kỹ năng (Skill Performance) đang dùng giao diện mặc định của hệ điều hành (màu trắng/xám sáng), cực kỳ lệch tông với giao diện tối của ứng dụng. Cần custom lại scrollbar (màu xám tối).
* **Nút điều khiển danh sách (Listbox controls):** Các nút `+`, `^`, `v`, `x` (màu xanh/đỏ) ở bên phải danh sách quái đang là các nút bấm native chưa được style. Chúng không ăn nhập với thiết kế phẳng của ứng dụng.
* **Thanh điều hướng Tabs (Notebook):** Các tab "Quái đã chọn", "Tự nhận diện", "Mọi mục tiêu" trông giống style mặc định của Windows cũ, thiếu padding, không có đường viền rõ ràng để nhận biết tab nào đang active.
* **Checkbox:** Các checkbox ("Bật Auto Combo", "0 skills valid") đang dùng giao diện mặc định (nền trắng viền nổi), cần được style lại theo giao diện tối.

## 3. Vấn đề về Bố cục & Căn chỉnh (Layout & Alignment)
* **Khung viền (LabelFrame):** Khung "Buff Lane" có đường viền cắt ngang chữ tiêu đề. Đây là style cổ điển của Tkinter, trông không chuyên nghiệp trong thiết kế hiện đại. Nên dùng thẻ tiêu đề độc lập hoặc style viền khác.
* **Khoảng cách (Padding/Margin):**
  * Các nút công cụ nhỏ kế bên chữ "0 windows" nằm khá sát nhau và có vẻ chưa được căn giữa hoàn hảo theo chiều dọc (vertical alignment) so với chữ.
  * Các trường nhập liệu (Dropdown, Entry) trong phần "Combo Chain" hơi chật chội.
* **Dropdown ngôn ngữ ("vi"):** Cấu phần này ở góc trên bên phải khá nhỏ và bị ép sát, gây khó khăn cho việc click.

## 4. Đề xuất tổng thể (Recommendations)
* Rà soát lại tất cả các thành phần `tk.Label`, `tk.Entry` đang bị rò rỉ màu nền hệ thống (system background) và ép chúng sử dụng biến màu của hệ thống thiết kế (ví dụ: `UI.THEME_BG_PANEL` hoặc `UI.BG_SURFACE`).
* Tuân thủ quy tắc độ tương phản: Text hiển thị trên nền tối bắt buộc phải dùng các màu sáng như `TEXT_PRIMARY` (trắng/xám nhạt), thay vì dùng `TEXT_SECONDARY` hoặc các màu sắc độ tối.
