# Audit UI Guidance & Phản hồi thao tác Scan

## 1. Phản hồi UI hiện tại khi user bấm Scan
Khi người dùng bấm vào các nút Scan/Vẽ lại (như `setup_roi.combo_bar`, `setup_roi.self_stats`, `setup_roi.minimap` hoặc `hunt_area.set`), hệ thống gọi `CaptureHelper.start_region_selection()`.
Phản hồi giao diện hiện tại như sau:
- **Text**: Không có bất kỳ dòng chữ hướng dẫn nào hiển thị.
- **Overlay**: Chỉ có một lớp phủ toàn màn hình màu đen mờ (alpha = 0.2) với con trỏ chuột hình chữ thập (`crosshair`). Khi người dùng kéo chuột, một khung hình chữ nhật viền màu `#00E5FF` xuất hiện. Không dùng các tính năng nâng cao trong `overlay_window.py` / `overlay_controller.py` để hỗ trợ hướng dẫn.
- **Tooltip**: Không có.
- **Status bar**: Không có phản hồi hay cập nhật trạng thái nào cho người dùng.

## 2. Kiểm tra các thành phần Guidance
Kết quả đánh giá Instruction Layer:

- [ ] Tiêu đề mục đích ("Đang thiết lập: Minimap ROI")
- [ ] Mô tả nghiệp vụ
- [ ] Hướng dẫn "khoanh vùng X trên game"
- [ ] Ví dụ vùng đúng
- [ ] Ví dụ vùng sai
- [ ] Preview kết quả kỳ vọng
- [ ] Thông báo Pass/Fail sau scan
- [ ] Lý do từ chối dữ liệu

Tất cả 8 hạng mục trên đều đang bị **thiếu**.

## 3. Kết luận
- **Technical Debt UX**: Thiếu toàn bộ các yếu tố hướng dẫn, giải thích và phản hồi (Guidance & Feedback) trong quy trình thiết lập vùng quét (ROI). Người dùng khi bấm Scan sẽ bị đưa vào một màn hình tối mờ mà không biết phải làm gì tiếp theo, phải chọn vùng như thế nào, làm sao để xác nhận kết quả là đúng hay sai.
- Cần xây dựng một hệ thống UI Overlay hoặc hộp thoại hướng dẫn (sử dụng hoặc mở rộng từ hệ thống overlay hiện có như `ui/windows/overlay_window.py`) để cung cấp bối cảnh, ví dụ minh họa và phản hồi kết quả sau khi chọn vùng.
