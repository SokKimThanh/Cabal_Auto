# Session 10 - Cải Tiến Action Bar Và Di Chuyển Nút Scan

> **Lưu ý phạm vi:** Session này KHÔNG nằm trong tài liệu "Đề Xuất Khắc Phục Giao Diện Hunt Hiện Tại (v2)" và không map vào AC-1 đến AC-17. Đây là yêu cầu bổ sung mới (action bar / nút Scan), cần được thêm vào README như một hạng mục riêng (xem gợi ý cập nhật README bên dưới) trước khi giao cho Jules, để không bị lẫn với chuỗi khắc phục gốc.

## Thông tin session

- **Người xử lý:** Jules
- **Timebox:** 25-30 phút
- **Ưu tiên:** P1
- **Phụ thuộc:** Session 09 (Gate) đã đạt — đảm bảo toàn bộ Session 01, 04, 05, 06, 08 (đều sửa `app_gui.py`) đã ổn định và được nghiệm thu trước khi thay đổi thêm vùng action bar/footer, tránh xung đột merge.
- **File chính:** `app_gui.py`

## Mục tiêu duy nhất

Gom các thao tác chuẩn bị và điều khiển Hunt vào một hàng trên cùng, đồng thời di chuyển **nút Scan thủ công hiện có** khỏi footer lên action bar theo đúng thứ tự thao tác.

Session này chỉ thay đổi vị trí và bố cục control. Không thay đổi nghiệp vụ scan, không tự động lưu cài đặt và không gộp callback Scan vào Start/Stop.

## Bố cục bắt buộc

Thứ tự từ trái sang phải:

```text
[Cửa sổ game                         ▼] [Refresh] [Scan] [Trạng thái readiness] [Start/Stop] [Ngôn ngữ]
```

Quy tắc vị trí:

1. Combobox chọn cửa sổ ở cột 0, nhận toàn bộ chiều rộng dư (`weight=1`).
2. Refresh ở cột 1, là icon button kích thước cố định.
3. Scan ở cột 2, ngay sau Refresh vì cả hai là thao tác chuẩn bị cửa sổ.
4. Readiness ở cột 3, hiển thị trạng thái chọn cửa sổ/scan.
5. Start/Stop ở cột 4, luôn ở bên phải readiness và không đổi vị trí khi đổi trạng thái.
6. Ngôn ngữ ở cột 5, ngoài cùng bên phải.

Không đặt Scan sau Start/Stop, trong footer, hoặc cạnh nút Apply All Settings.

## Widget và callback phải tái sử dụng

Nút cần di chuyển là `self.btn_manual_scan` hiện được tạo trong `apply_frame`.

Giữ nguyên:

- thuộc tính `self.btn_manual_scan`
- icon `Icons.SCAN_SCREEN`
- callback `self.scan_controller.run_scan(manual=True)`
- khả năng `_update_scan_status_icon()` cập nhật icon của cùng widget

Không tạo nút Scan thứ hai. Sau thay đổi, toàn bộ code tạo và layout `btn_manual_scan` trong footer phải được xóa khỏi vị trí cũ.

## File trong phạm vi

- `app_gui.py`
- `lib/i18n/translations.py` nếu cần bổ sung tooltip Scan
- test action bar, ưu tiên `tests/unit/test_action_bar.py` hoặc test UI mới cạnh file này

Không sửa `ui/tabs/hunt_tab.py`, Bottom Logs, layout Skill hoặc hành vi `on_global_apply` trong session này.

## Các bước thực hiện

1. Viết test thất bại trước khi sửa, xác nhận thứ tự grid column của các widget action bar.
2. Chuyển phần tạo `btn_manual_scan` lên ngay sau phần tạo `refresh_btn`.
3. Parent của Scan phải là `self.action_bar_frame`, không phải `apply_frame`.
4. Cập nhật cấu hình sáu cột theo thứ tự bắt buộc; bỏ cột Stop riêng đang không được sử dụng.
5. Giữ Start/Stop là một widget thống nhất và đặt ở cột 4.
6. Xóa việc tạo/pack Scan ở footer. Footer chỉ giữ trạng thái lưu và Apply All Settings theo hành vi hiện tại.
7. Thêm tooltip i18n cho Scan, ví dụ `Quét/kiểm tra cửa sổ đã chọn`; không dùng text dài trực tiếp trên nút icon.
8. Cập nhật compact mode nếu cần để readiness rút gọn trước; không được ẩn Scan hoặc Start/Stop.

## Trạng thái control

- Chưa chọn cửa sổ: Scan disabled nếu ScanController không tự chặn trạng thái này; Start vẫn theo state controller hiện có.
- Đã chọn cửa sổ: Scan enabled.
- Đang scan: icon có thể được `_update_scan_status_icon()` cập nhật như hiện tại.
- Đang Hunt: Start đổi thành Stop tại cùng vị trí; không làm các control khác dịch chuyển.

Không tự động gọi Scan khi nhấn Start trong session này. Nếu muốn thêm preflight Scan cho Start, tạo session nghiệp vụ riêng sau khi toolbar ổn định.

## Kiểm thử bắt buộc

```powershell
py -m pytest tests/unit/test_action_bar.py -q
py -m pytest tests -m ui -k "action_bar or scan" -q
```

Nếu test mới không khớp biểu thức `-k`, chạy trực tiếp file test mới trước khi báo cáo.

## Kiểm tra thủ công

1. Chạy `py .\app_gui.py` ở 1366x768.
2. Xác nhận thứ tự: Window, Refresh, Scan, Readiness, Start/Stop, Language.
3. Xác nhận footer không còn nút kính lúp.
4. Nhấn Scan và xác nhận vẫn chạy đúng callback/manual scan.
5. Chuyển `vi`/`en`, kiểm tra readiness không đè Start/Stop.
6. Thu/mở Logs và chuyển view, action bar không đổi vị trí hoặc bị tạo lại.

## Tiêu chí nghiệm thu

Các tiêu chí dưới đây là riêng cho session này, không thuộc AC-1..AC-17 của tài liệu gốc:

- Chỉ tồn tại một `btn_manual_scan` trong toàn bộ root UI.
- `btn_manual_scan.master is self.action_bar_frame`.
- Grid columns lần lượt là: combobox `0`, Refresh `1`, Scan `2`, readiness `3`, Start/Stop `4`, language `5`.
- Scan nằm sát Refresh, trước readiness và Start/Stop.
- Footer chỉ còn trạng thái lưu và nút Apply All Settings.
- Callback Scan và cập nhật icon vẫn hoạt động.
- Ở 1366x768 không control nào chồng, cắt hoặc làm Start/Stop dịch chuyển.
- Test bắt buộc pass.
- Regression: các AC-1, AC-3, AC-5, AC-6 của tài liệu gốc (không cắt/chồng control chính, resize vẫn an toàn) vẫn đạt sau khi thay đổi action bar, vì đây cũng là widget nằm trong `main_shell`.

## Điểm dừng bắt buộc

Không triển khai auto-save, không gộp Scan vào Start và không thiết kế lại footer trong session này. Nếu action bar không đủ chiều rộng, rút gọn readiness/spacing trước; không chuyển control xuống hàng thứ hai.

## Báo cáo Jules cần để lại

- Diff production code và test.
- Sơ đồ cột trước/sau.
- Xác nhận không còn Scan trong footer và không có widget trùng.
- Lệnh test cùng kết quả.
- Ảnh action bar ở 1366x768 cho cả `vi` và `en` nếu môi trường cho phép.