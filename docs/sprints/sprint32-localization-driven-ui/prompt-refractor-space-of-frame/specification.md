# Đặc tả Kỹ thuật: Khắc phục lỗi hiển thị "Khoảng đen thừa" trên các Màn hình Quản lý

## 1. Bối cảnh & Vấn đề (Context & Problem)
Khi xem ứng dụng trên màn hình lớn hoặc thay đổi kích thước cửa sổ, các màn hình quản lý (ví dụ: `MonsterManagerFrame`) xuất hiện khoảng không gian thừa (khoảng đen) rất lớn ở phía dưới.
Danh sách dữ liệu chính (Treeview) không tự động mở rộng (expand) để chiếm hết không gian khả dụng, mặc dù đã được thiết lập `expand=True` và `fill="both"` trong layout.

## 2. Nguyên nhân Cốt lõi (Root Cause)
Vấn đề bắt nguồn từ hai yếu tố chính:
1. **Hạn chế của `ResponsiveGridBase`**: Lớp cơ sở `ResponsiveGridBase` sử dụng `Canvas` để hỗ trợ cuộn dọc. Khi cửa sổ thay đổi kích thước (`<Configure>`), nó chỉ đồng bộ chiều rộng (`width`) của `content_frame` bên trong với `Canvas`, nhưng **bỏ qua chiều cao (`height`)**. Do đó, `content_frame` chỉ giữ chiều cao vừa đủ cho các thành phần bên trong (dựa trên cấu hình tối thiểu), chặn sự kiện `expand` lan truyền xuống danh sách Treeview.
2. **Thứ tự đóng gói (`pack`) trong UI Frames**: Tại các màn hình (như `MonsterManagerFrame`), các thành phần thường được `pack` từ trên xuống dưới theo thứ tự xuất hiện trong code. Khi khung Treeview (chiếm diện tích lớn nhất) được `pack` trước thanh công cụ (Action Bar) hoặc các Panel phụ ở dưới, `tkinter` không thể phân bổ không gian còn lại một cách tối ưu, dẫn đến cấu trúc UI bị nén lên trên.

## 3. Hướng dẫn Khắc phục & Tiêu chuẩn Thiết kế (Fix & Guidelines)

Để xử lý dứt điểm vấn đề này cho màn hình hiện tại và các màn hình khác trong tương lai, cần tuân thủ các bước sau:

### 3.1. Cập nhật lớp `ResponsiveGridBase`
Cần điều chỉnh hàm `_on_canvas_configure` trong `ui/components/base/responsive_grid_base.py` để đồng bộ cả chiều cao (height) nếu Canvas lớn hơn chiều cao nội dung yêu cầu (reqheight).

**Mã giả (Pseudo-code) / Hướng thay đổi:**
```python
def _on_canvas_configure(self, event):
    if self.canvas.winfo_width() > 0:
        # Ép chiều rộng nội dung bằng với Canvas
        self.canvas.itemconfig(self.content_window, width=event.width)

        # [MỚI] Ép chiều cao tối thiểu để content_frame giãn ra hết Canvas
        # Nếu màn hình to hơn nội dung, content_frame sẽ lấp đầy.
        # Nếu màn hình nhỏ hơn nội dung, cuộn dọc vẫn hoạt động bình thường.
        req_height = self.content_frame.winfo_reqheight()
        if event.height > req_height:
            self.canvas.itemconfig(self.content_window, height=event.height)
        else:
            self.canvas.itemconfig(self.content_window, height='') # Xóa ép chiều cao để cuộn

        if self._resize_timer:
            self.after_cancel(self._resize_timer)
        self._resize_timer = self.after(100, lambda: self._on_resize(event.width, event.height))
```

### 3.2. Chuẩn hóa Layout (`pack`) trong UI Frames (ví dụ: `MonsterManagerFrame`)
Khi xây dựng một màn hình có danh sách mở rộng (Treeview), bắt buộc áp dụng nguyên tắc đóng gói: **Ghim đỉnh, Ghim đáy, Lấp đầy ở giữa (Top -> Bottom -> Fill Middle)**.

1. **Top Bars (Header, Search Bar):**
   ```python
   header_frame.pack(side="top", fill="x", pady=...)
   search_frame.pack(side="top", fill="x", pady=...)
   ```
2. **Bottom Bars (Action Bar, Stats, Pagination):**
   ```python
   # Thanh công cụ dưới cùng LUÔN được pack trước khối nội dung chính nhưng gắn side="bottom"
   bottom_bar.pack(side="bottom", fill="x", pady=...)
   ```
3. **Expandable Panels (ví dụ: Quản lý Loại Quái vật):**
   ```python
   # Panel này nằm sát trên thanh bottom_bar
   type_panel_container.pack(side="bottom", fill="x", pady=...)
   ```
4. **Main Content (Treeview):**
   ```python
   # Pack khối giữa sau cùng để nó tự động chiếm toàn bộ không gian còn lại ở giữa Top và Bottom
   table_frame.pack(side="top", fill="both", expand=True, padx=..., pady=...)
   ```

### 3.3. Áp dụng cho các màn hình khác
Tất cả các màn hình kế thừa từ `ResponsiveGridBase` và có chứa bảng biểu/danh sách (Treeview) hoặc nội dung động cần được refactor lại theo chuẩn **3.2** nói trên.
* Chuyển các khối Bottom (`bottom_bar`) lên cấu trúc code sớm hơn phần bảng và set `side="bottom"`.
* Đảm bảo khung bao ngoài bảng (`table_frame`) có `expand=True, fill="both"` và được cấu hình row/column `weight=1`.

## 4. Mục tiêu đạt được (Acceptance Criteria)
* Khi phóng to màn hình, bảng danh sách tự động kéo giãn xuống, lấy hết khoảng không gian thừa.
* Các thanh công cụ như Thêm/Sửa/Xóa luôn nằm cố định ở sát mép dưới màn hình.
* Khi thêm mới dữ liệu làm nội dung dài ra và nhỏ hơn cửa sổ màn hình, thanh cuộn của `ResponsiveGridBase` hoạt động ổn định và bình thường, không che khuất dữ liệu dưới cùng.