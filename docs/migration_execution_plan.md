# Tài Liệu Thực Thi: Di Dời Sang Hệ Thống Grid Cải Tiến (Migration Execution Plan)

**Mục Tiêu:**
Hướng dẫn chi tiết từng bước thực thi (step-by-step) quá trình chuyển đổi (migration) toàn bộ giao diện sang hệ thống Grid mới (`ResponsiveGridBase`), đảm bảo tính nhất quán (UIStyleV2), tính đáp ứng (zero-occlusion), và giảm thiểu rủi ro phá vỡ tính năng hiện hành.

Tài liệu này đóng vai trò là "Blueprint" dành cho Software Engineer khi bắt đầu code.

---

## Giai Đoạn 1: Xây Dựng Nền Tảng (Base Implementation)

*Mục tiêu:* Thiết lập các class gốc và công cụ cơ bản. Chưa tác động đến các luồng UI hiện tại.

### Bước 1: Khởi tạo Component `ResponsiveGridBase`
1. **Tạo file mới:** `ui/components/base/responsive_grid_base.py`. (Cần tạo thêm thư mục `base/` nếu chưa có).
2. **Kế thừa và Kiến trúc:**
   - Class `ResponsiveGridBase` kế thừa từ `ttk.Frame` (hoặc `tk.Frame`).
   - Khởi tạo một `tk.Canvas` làm nền và một `tk.Frame` (nội dung chính) bên trong Canvas (sử dụng `canvas.create_window`).
   - Thêm một `ttk.Scrollbar` (orient='vertical') và liên kết (link) nó với Canvas (`yscrollcommand` và `yview`).
3. **Responsive Resizing:**
   - Bind event `<Configure>` của Canvas để tự động điều chỉnh `width` của Frame nội dung cho bằng với `width` của Canvas.
   - Bind event `<Configure>` của Frame nội dung để cập nhật lại vùng cuộn của Canvas: `canvas.configure(scrollregion=canvas.bbox("all"))`.
4. **Tương thích ngược (Backward Compatibility):**
   - Đảm bảo constructor nhận tham số `parent` và truyền xuống `super().__init__(parent, **kwargs)` như một `tk.Frame` bình thường.
   - Thêm method `get_content_frame(self)` để trả về Frame con bên trong (nơi chứa nội dung thực sự). Các Panel kế thừa sẽ add widget vào frame này thay vì add thẳng vào `self`.

### Bước 2: Tích hợp Cross-Platform Scrolling
*(ĐÂY LÀ ĐIỂM YẾU CHÍNH CẦN TRÁNH - Cực kỳ dễ gây crash TclError hoặc xung đột)*
- Trong `ResponsiveGridBase`, thực hiện binding cuộn chuột:
  - **Windows:** Bind `<MouseWheel>`. Hàm xử lý cần dùng `event.delta`.
  - **Linux:** Bind `<Button-4>` (cuộn lên) và `<Button-5>` (cuộn xuống).
  - **Mac:** Tương tự Windows nhưng xử lý delta khác.
- **Biện pháp phòng ngừa (Gotcha):**
  - Tránh dùng `bind_all` bừa bãi. Chỉ bind khi trỏ chuột vào vùng Canvas (`<Enter>`) và unbind khi ra khỏi vùng (`<Leave>`) để tránh scrollbar của base class xung đột với scrollbar của listbox con bên trong.
  - Phải bọc hàm scroll trong `try...except Exception:` để chặn lỗi `_tkinter.TclError` nếu widget bị destroy trước khi event kịp xử lý.

### Bước 3: Tích hợp Logging Sinh Mệnh (Lifecycle)
- Import thư viện `logging` tiêu chuẩn.
- Thêm log mức độ `DEBUG` trong constructor (`_on_mount`), trong hàm resize (`_on_resize`).

---

## Giai Đoạn 2: Thử Nghiệm và Áp Dụng Từng Phần (Pilot Migration)

*Mục tiêu:* Áp dụng class base vào một Panel nhỏ lẻ, ít quan trọng để kiểm tra tính ổn định.

### Bước 1: Pilot trên `SkillStatsPanel`
1. Sửa file `ui/panels/skill_stats_panel.py`.
2. Đổi kế thừa của class từ `ttk.Frame`/`tk.Frame` sang `ResponsiveGridBase`.
3. Thay thế các lệnh `tk.Label(self, ...)` thành `tk.Label(self.get_content_frame(), ...)`.
4. **Kiểm tra Token `UIStyleV2`:** Đảm bảo toàn bộ màu sắc, padding (`padx`, `pady`) đang sử dụng các hằng số đúng như `UI.SPACE_MD`, `UI.SPACE_LG` chứ không dùng số cứng.
5. Chạy ứng dụng, mở tab Hunt, ép nhỏ kích thước cửa sổ để xem thanh cuộn dọc (scroll) của `SkillStatsPanel` có hoạt động đúng không.

### Bước 2: Pilot trên Sidebar (Vùng C1)
1. Trong file `app_gui.py`, sửa `self.shell_zone_c1` từ một `tk.Frame` tĩnh thành một instance của `ResponsiveGridBase`.
2. Truyền các nút menu điều hướng (Navigation buttons) vào trong `content_frame` của sidebar.
3. Chạy ứng dụng và thay đổi chiều cao cửa sổ xuống mức siêu nhỏ (ví dụ 400px). Đảm bảo sidebar xuất hiện thanh cuộn và vẫn có thể bấm vào được tab "Help" (nằm ở cuối).

---

## Giai Đoạn 3: Triển Khai Toàn Diện và Loại Bỏ Điểm Nghẽn (Full Rollout)

*Mục tiêu:* Triển khai sang các khu vực quan trọng (Workspace) và loại bỏ các layout che lấp cứng ngắc.

### Bước 1: Thay thế hệ thống của Tab Hunt (`HuntTab`)
1. Hiện tại, `HuntTab` (trong `ui/tabs/hunt_tab.py`) đang dùng `ttk.PanedWindow` chia màn hình làm 4 mảng 2x2.
2. Xóa bỏ `ttk.PanedWindow` (vì chúng ép nén diện tích).
3. Đổi layout cha của `HuntTab` thành một luồng (flow) xếp từ trên xuống dưới hoặc lưới (grid) sử dụng `ResponsiveGridBase`.
   - Các component nặng như `MonsterTargetPanel` hay `SkillPanel` nay sẽ xếp chồng lên nhau (stack).
   - Nếu màn hình đủ lớn, chúng sẽ hiện hết. Nếu màn hình hẹp, thanh cuộn tổng của màn hình (hoặc thanh cuộn nội tại của từng Component) sẽ kích hoạt, đảm bảo "Zero-occlusion" (không che mất data).

### Bước 2: Thiết lập Ngưỡng Ưu Tiên Hiển Thị (Stacking Priority)
*(ĐÂY LÀ ĐIỂM YẾU VỀ UX CẦN TRÁNH)*
- Khi cuộn, những dữ liệu sinh tử của HuntTab (như Thanh HP của quái, Kỹ năng đang cast) tuyệt đối không được trôi đi mất.
- **Giải pháp:** Tách `MonsterTargetPanel` (chứa HP quái) khỏi `ResponsiveGridBase` chung. Đóng ghim (pin) nó ở trên cùng (sử dụng `pack(side='top')` với parent frame tĩnh), và chỉ áp dụng `ResponsiveGridBase` cho các panel nằm bên dưới nó.

---

## Giai Đoạn 4: Kiểm Soát Chất Lượng (QA & Metrics)

*Mục tiêu:* Đảm bảo không phá vỡ UI/UX hiện có và đáp ứng tiêu chí tài liệu.

### Bước 1: Chạy kiểm thử hồi quy (Regression Test)
- Chạy `python3 run_tests.py` sau khi viết xong code. Đảm bảo logic import hoặc mock tests không bị gãy (đặc biệt lưu ý các test về UI như `test_mock_guideline.py`).

### Bước 2: Kiểm thử Hộp Đen (Blackbox Visual Testing)
- **Zero-Occlusion Verify:** Mở app, thu hẹp ứng dụng về kích thước nhỏ nhất cho phép `800x600`. Kiểm tra thủ công:
  - Có thanh scrollbar không?
  - Dữ liệu bị đẩy xuống dưới hay bị đè (overlap)? (Yêu cầu phải bị đẩy xuống dưới).
- Khởi chạy một "Hunt" giả lập, quan sát xem việc liên tục update UI thông qua `after` có làm thanh cuộn nhảy giật cục loạn xạ không. Nếu có, cần chặn event cập nhật resize trừ khi thực sự cần thiết.

---

## TỔNG HỢP CÁC ĐIỂM YẾU CẦN TRÁNH (GOTCHAS & PITFALLS)

1. **Xung đột Scrollbar (Ghost Scrollbars):**
   - **Vấn đề:** Frame con đã thay đổi kích thước nhưng `canvas.bbox("all")` chưa kịp update, khiến scrollbar hiển thị sai tỷ lệ.
   - **Xử lý:** Gọi cập nhật `bbox("all")` một cách trì hoãn (debounce) thông qua `self.after(50, ...)` thay vì cập nhật ngay lập tức trong event `<Configure>`.

2. **Dính Lỗi `TclError` ở Background Threads:**
   - **Vấn đề:** Các panel nhận dữ liệu từ luồng nền (như `ScreenStateAnalyzer`). Việc thay đổi UI kích hoạt event resize, gọi thẳng vào Tkinter loop và bị crash.
   - **Xử lý:** Luôn sử dụng `app.after(0, update_ui_method)` cho mọi thay đổi giao diện bắt nguồn từ thread bên ngoài.

3. **Sai lệch Font chữ và Màu Sắc:**
   - **Vấn đề:** Dev dùng hardcode color `#FFFFFF` hoặc size `12` thay vì dùng chuẩn hệ thống.
   - **Xử lý:** Tuyệt đối dùng `UIStyleV2.TEXT_PRIMARY`, `UIStyleV2.FONT_BODY`. Đặc biệt với font, hãy dùng class method `UIStyleV2.get_font('body')` để đảm bảo cơ chế fallback tự động hoạt động nếu OS bị thiếu font.

4. **Kế thừa hỏng (Constructor Signature Mismatch):**
   - **Vấn đề:** Các panel cũ khi khởi tạo thường truyền một mớ kwargs riêng. Nếu `ResponsiveGridBase` chỉ nhận `*args`, nó sẽ lỗi.
   - **Xử lý:** Constructor của Base Class phải luôn thiết kế rộng mở: `def __init__(self, parent, *args, **kwargs)`. Lọc ra các kwargs hợp lệ cho `ttk.Frame` trước khi gọi `super().__init__`.
