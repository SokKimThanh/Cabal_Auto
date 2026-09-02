# Session 12 - Chuyển Nhật Ký Thành Trang Sidebar Riêng

## Thông tin session

- **Người xử lý:** Jules
- **Timebox:** 25-30 phút
- **Ưu tiên:** P1
- **Phụ thuộc:** Session 07 đã merge; tương thích với Session 10
- **Thay thế:** Cơ chế Bottom Logs thu/mở trong màn hình Hunt

## Mục tiêu duy nhất

Xóa panel Logs thu/mở khỏi màn hình Hunt và hiển thị cùng dữ liệu log trong một
view riêng có mục điều hướng ở sidebar. Hunt phải nhận lại toàn bộ chiều cao từng
dành cho Logs.

Session này chỉ di chuyển viewer hiện có. Không thêm hệ thống logging mới, không
tạo queue consumer thứ hai và chưa triển khai bộ lọc/tìm kiếm nâng cao.

## Hành vi mục tiêu

Sidebar có mục mới:

```text
Săn
Nhật ký hoạt động
```

Khi chọn `Nhật ký hoạt động`:

- `switch_view("logs")` hiển thị trang log trong `shell_zone_b`;
- trang dùng toàn bộ vùng workspace, không phải panel nổi hoặc card lồng nhau;
- log mới vẫn được nhận khi người dùng đang ở view khác;
- mở trang Logs không làm thay đổi trạng thái Hunt;
- ứng dụng không tự chuyển sang Logs khi có warning/error.

Màn hình Hunt không còn header `Nhật ký`, nút Thu/Mở rộng hoặc Text log ở đáy.

## Code hiện tại đã xác nhận

- Bottom Logs nằm tại `main_shell` row 2 qua `shell_zone_c2`.
- `logs_text_widget` hiện được tạo trực tiếp trong `App._build_ui()`.
- `App._poll_log_queue()` là consumer duy nhất của `HuntLogger.ui_queue`, chạy
  bằng `after(100, ...)` trên Tk main thread.
- Các trang được đăng ký trong `self._views` và chuyển bằng `switch_view()`.
- Sidebar dùng tuple `(translation_key, command, font, view_target)` để quản lý
  selected state.

## File trong phạm vi

- `app_gui.py`
- thêm `ui/views/activity_logs_frame.py`
- `lib/i18n/translations.py`
- `tests/unit/test_bottom_logs.py` hoặc test UI Logs mới
- test sidebar/navigation liên quan

Không sửa logger producer, HuntRunner, HuntOrchestrator, Scan hoặc Apply All.

## Thiết kế view tối thiểu

`ActivityLogsFrame` cần có:

- tiêu đề `Nhật ký hoạt động` / `Activity Logs`;
- một `tk.Text` read-only, wrap word, scrollbar dọc;
- nút icon Xóa phần hiển thị, dùng translation `logs_clear` hiện có;
- auto-scroll khi đang ở cuối;
- giới hạn 1.000 dòng như hành vi hiện tại.

Không thêm bộ lọc level, tìm kiếm, badge hoặc mở thư mục log trong session này.
Các tính năng đó là follow-up riêng.

## Ownership và luồng dữ liệu

Chỉ tồn tại một consumer của `HuntLogger.ui_queue`.

Phương án yêu cầu:

1. `ActivityLogsFrame` sở hữu Text widget và cung cấp các method nhỏ như
   `append_message(text)`, `clear()` và `trim_to_limit(limit)`.
2. `App._poll_log_queue()` tiếp tục chạy trên main thread và gọi API của logs
   view, kể cả khi view đang hidden.
3. Không cập nhật Tkinter từ background thread.
4. Không tạo `after()` polling thứ hai trong logs view.
5. Có thể giữ alias `self.logs_text_widget = logs_view.text_widget` tạm thời nếu
   cần tương thích test/call site, nhưng không được tạo Text widget thứ hai.

## Các bước thực hiện

1. Viết test cho navigation `logs` và một queue consumer duy nhất.
2. Tạo `ActivityLogsFrame` theo pattern của `HuntWorkspaceFrame`/
   `StatsContentFrame`.
3. Đăng ký `self._views["logs"]` và thêm sidebar item với
   `view_target="logs"` ngay sau `Săn`.
4. Chuyển Text widget cùng thao tác append/clear/trim sang logs view.
5. Cập nhật `_poll_log_queue()` để ghi qua API view mà không thay đổi batching
   50 record, queue cap 5.000 hoặc buffer cap 1.000 dòng.
6. Xóa khỏi `App._build_ui()`:
   - `shell_zone_c2`;
   - `logs_header_frame`, `logs_toggle_btn`, `logs_content_frame`;
   - trạng thái `logs_expanded` và lịch `after` kiểm tra collapse.
7. Xóa logic `_toggle_bottom_logs()`, `_check_initial_logs_state()` và phần
   auto-collapse Logs trong `_on_window_configure()` nếu không còn call site.
8. Cấu hình lại `main_shell`: workspace row 1 nhận toàn bộ chiều cao nội dung;
   không giữ row 2/minsize dành riêng cho Logs; sidebar không cần rowspan qua row
   Logs đã xóa.
9. Cập nhật test Bottom Logs cũ: xóa test thu/mở không còn ý nghĩa, thay bằng test
   view navigation, append, clear, cap và queue formatting.
10. Cập nhật selected state/i18n cho mục sidebar mới ở cả `vi` và `en`.

## I18n bắt buộc

Thêm key sidebar rõ nghĩa:

- `sidebar_activity_logs`: `Nhật ký hoạt động`
- `sidebar_activity_logs`: `Activity Logs`

Tái sử dụng `logs_title` và `logs_clear` nếu phù hợp. Không hard-code text song
ngữ trong widget.

## Kiểm thử bắt buộc

```powershell
py -m pytest tests/unit/test_bottom_logs.py -q
py -m pytest tests -m ui -k "logs or navigation or hunt" -q
```

Tìm call site cũ trước khi hoàn tất:

```powershell
rg "shell_zone_c2|logs_expanded|logs_toggle_btn|_toggle_bottom_logs|_check_initial_logs_state" .
```

Kết quả `rg` chỉ được còn trong tài liệu lịch sử hoặc test đã được chủ động đánh
dấu legacy; không được còn call site runtime.

## Kiểm tra thủ công

1. Chạy `py .\app_gui.py` ở 1366x768.
2. Xác nhận Hunt sử dụng toàn bộ chiều cao và không còn Bottom Logs.
3. Chọn `Nhật ký hoạt động`; xác nhận trang Logs chiếm toàn workspace.
4. Chuyển sang Hunt, phát sinh log, quay lại Logs và xác nhận log vẫn được thêm.
5. Xóa phần hiển thị và xác nhận file log không bị xóa.
6. Chuyển `vi`/`en`, xác nhận label sidebar và tiêu đề đúng.
7. Xác nhận Start/Stop Hunt không tự chuyển view.

## Tiêu chí nghiệm thu

- Chỉ có một Text widget hiển thị activity log và một queue consumer.
- Mục sidebar Logs có selected state đúng qua `switch_view("logs")`.
- Hunt không còn row/panel/header/toggle Logs ở đáy.
- Hunt nhận lại chiều cao cũ của row Logs; Skill và Stats không bị panel log che.
- Log vẫn cập nhật khi logs view hidden.
- Batching 50, queue cap 5.000 và buffer cap 1.000 tiếp tục hoạt động.
- Xóa UI log không xóa file log.
- Không có cập nhật Tkinter từ background thread.
- Footer Global Apply và DB Status không bị di chuyển vào logs view.
- Test bắt buộc pass.

## Điểm dừng bắt buộc

Không thêm filter/search/badge, không tự mở trang Logs khi lỗi và không thay đổi
format record. Nếu việc loại bỏ auto-collapse làm test cũ fail, cập nhật test theo
hành vi mới thay vì giữ code collapse chết để làm test pass.

## Báo cáo Jules cần để lại

- Cây widget Logs trước/sau.
- File production và test đã thay đổi.
- Xác nhận số queue consumer và Text widget.
- Kết quả `rg` call site legacy.
- Lệnh test cùng kết quả.
- Ảnh Hunt và trang Nhật ký ở 1366x768.
