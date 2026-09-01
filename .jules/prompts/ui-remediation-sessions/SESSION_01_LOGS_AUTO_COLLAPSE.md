# Session 01 - Kích Hoạt Auto-collapse Cho Logs

## Thông tin session

- **Người xử lý:** Jules
- **Timebox:** 20-25 phút
- **Ưu tiên:** P0
- **Phụ thuộc:** Không
- **Tham chiếu tài liệu gốc:** Đề Xuất Khắc Phục Giao Diện Hunt Hiện Tại (v2), mục 5.1 và mục 6 (bước 1)
- **AC liên quan:** AC-7, AC-8, AC-13, AC-15

## Mục tiêu duy nhất

Kết nối logic `_on_window_configure()` với sự kiện Tkinter thật và bảo đảm Logs tự thu đúng một lần khi cửa sổ không đủ chiều cao.

## File trong phạm vi

- `app_gui.py`
- `tests/unit/test_bottom_logs.py`

Không chỉnh sửa bố cục Hunt hoặc kích thước `minsize` trong session này.

## Hiện trạng cần xác nhận

- `_on_window_configure()` đã có logic ngưỡng 900px.
- Hàm chưa được bind vào `<Configure>`.
- `_check_initial_logs_state()` đang để trống, chưa gọi logic kiểm tra chiều cao ban đầu.
- Test hiện gọi callback trực tiếp, chưa kiểm chứng binding GUI.

## Các bước thực hiện

1. Viết hoặc sửa test để phát sinh `<Configure>` trên cửa sổ và xác nhận callback có hiệu lực.
2. Bind sự kiện cấu hình của cửa sổ chính vào `_on_window_configure()` đúng một lần.
3. Cài logic vào `_check_initial_logs_state()` để hàm này gọi kiểm tra chiều cao ngay khi khởi động, dùng `update_idletasks()` hoặc `after_idle()` (chọn phương án nào cho geometry ổn định trước khi kiểm tra là được).
4. Giữ hành vi hiện tại: sau khi người dùng chủ động mở Logs trong cùng khoảng chiều cao thấp, resize tiếp không được tự đóng ngay.
5. Không cập nhật widget từ background thread.

## Kiểm thử bắt buộc

```powershell
py -m pytest tests/unit/test_bottom_logs.py -k "responsive or rapid_expand" -q
```

Nếu test mới ở bước 1 không có tên khớp `responsive` hoặc `rapid_expand`, cập nhật lại pattern `-k` cho khớp (hoặc chạy toàn bộ file test) trước khi báo cáo kết quả.

Kiểm tra thủ công nhanh:

1. Chạy `py .\app_gui.py` ở màn hình 1366x768.
2. Xác nhận Logs tự thu và hàng Skill có thêm không gian.
3. Mở Logs thủ công, thay đổi nhẹ kích thước cửa sổ và xác nhận Logs không đóng lại ngay.

## Điều kiện hoàn tất

- `<Configure>` thực sự kích hoạt logic responsive.
- `_check_initial_logs_state()` thực hiện kiểm tra chiều cao ngay khi khởi động, không còn để trống.
- Auto-collapse chỉ xảy ra một lần khi đi từ vùng cao sang vùng thấp.
- Các test mục tiêu pass, kể cả test mới viết ở bước 1.
- Không thay đổi hành vi nút thu/mở Logs thủ công.

## Điểm dừng bắt buộc

Kết thúc session sau khi binding và test tương ứng pass. Không tiếp tục sửa `minsize`, geometry, log formatter hoặc style trong cùng session.

## Báo cáo Jules cần để lại

- File và hàm đã sửa.
- Diff hoặc commit liên quan (nếu có).
- Lệnh test cùng kết quả.
- Xác nhận AC-7, AC-8, AC-13 và AC-15 đạt hay chưa.
- Rủi ro hoặc hành vi chưa kiểm chứng thủ công.