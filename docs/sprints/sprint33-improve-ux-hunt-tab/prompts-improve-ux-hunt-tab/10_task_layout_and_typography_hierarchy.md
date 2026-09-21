# Task 10: Tái cấu trúc Layout và Phân cấp Typography (HuntTab)

## Bối cảnh (Context)
Tab Hunt đang được chia thành 2 cột với tỷ lệ cứng `58/42` sử dụng `ResponsiveGridBase` bằng cách chia lưới 12 cột (cột trái chiếm 7, phải chiếm 5). Việc này tuy đảm bảo tính responsive nhưng lại thiếu tính tùy biến không gian (người dùng không thể thu nhỏ phần bên trái để soi chi tiết thanh máu bên phải). Đồng thời, các tiêu đề Panel (Header) không có phân cấp font (Typography hierarchy) khiến giao diện thiếu chiều sâu.

## Yêu cầu (Requirements)
1. Trong file `ui/tabs/hunt_tab.py`:
   - Thay thế việc phân chia `12-column grid` của `ResponsiveGridBase` bằng một component `ttk.PanedWindow(orient=tk.HORIZONTAL)`. LƯU Ý: Chỉ thay thế component này ở trong file `HuntTab`, KHÔNG xóa class `ResponsiveGridBase` đi vì nó có thể đang được các tab khác dùng.
   - Đưa `left_col_frame` và `right_col_frame` vào làm 2 khung (pane) của `PanedWindow` này.
   - Thiết lập tỷ lệ (weight) khởi tạo sao cho 2 cột cân bằng theo tỷ lệ cũ nhưng cho phép người dùng kéo thanh chia (Sash).
2. Chuẩn hóa Phân cấp Typography:
   - Các tiêu đề lớn của Panel (như "Target Setup", "Active Skills", "Target Status") phải sử dụng `UIStyleV2.get_font("title", weight="bold")`.
   - Các tiêu đề phụ (Section) dùng `UIStyleV2.get_font("header", weight="bold")`.
   - Các Text mô tả dùng `UIStyleV2.get_font("body")`.

## Rủi ro (Risks & Pitfalls)
- **Sash Dragging (Lỗi kéo thả):** Trong Tkinter, nếu các component bên trong (ví dụ Treeview) không có tham số `min_width` hoặc dùng `pack/grid` không cẩn thận, khi kéo PanedWindow quá nhỏ sẽ gây vỡ layout (đẩy component tràn ra ngoài). Cần đảm bảo các cột có `minsize`.
- Chú ý hàm get_font của UIStyleV2 đang trả về Tuple, hãy set nó vào thuộc tính `font=` của Label.

## Unit Tests Cần Thêm (Unit Tests to Add)
- Kiểm tra thủ công: Mở Tab Hunt, dùng chuột kéo thanh chia (sash) ở giữa qua lại. Đảm bảo 2 cột tự động thay đổi kích thước mượt mà không văng lỗi hay biến dạng text.
## Hướng dẫn trả Nợ Kỹ Thuật (Technical Debt Paydown)
- **Phá vỡ Grid Cố Định:** Hãy xóa toàn bộ các dòng lệnh code tính toán vòng lặp chia 12 cột (Bootstrap-style `columnconfigure(i, weight=1)`) tĩnh ở Tab Hunt cũ. Khoản nợ thiết kế không linh hoạt này phải được thay thế hoàn toàn bằng `ttk.PanedWindow` để trả lại khả năng tùy biến màn hình (resizable) cho user.
