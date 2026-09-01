# Session 08 - Chuẩn Hóa Khả Năng Đọc Và Điều Hướng

## Thông tin session

- **Người xử lý:** Jules
- **Timebox:** 20-25 phút
- **Ưu tiên:** P2
- **Phụ thuộc:** Session 07 — trùng file `ui/tabs/hunt_tab.py` và `app_gui.py`; cần layout đã ổn định (breakpoint) trước khi chuẩn hóa font/spacing để tránh phải sửa lại token do layout còn thay đổi.
- **Tham chiếu tài liệu gốc:** Đề Xuất Khắc Phục Giao Diện Hunt Hiện Tại (v2), mục 5.7, mục 5.8 và mục 6 (bước "chuẩn hóa font, spacing và selected state")
- **AC liên quan:** hỗ trợ AC-3, AC-9 (session này không thay thế việc kiểm tra DPI đầy đủ — xem phần "Còn lại sau session này" bên dưới)

## Mục tiêu duy nhất

Chuẩn hóa font/spacing trong Hunt và làm rõ selected state của sidebar mà không thay đổi cấu trúc layout.

## File trong phạm vi

- `app_gui.py`
- `ui/tabs/hunt_tab.py`
- `lib/ui_style.py` chỉ khi cần dùng hoặc bổ sung token chung

## Các bước thực hiện

1. Thay font `Arial` 8px/9px rải rác bằng token gần nhất trong `UIStyle`.
2. Giữ kích thước chữ đủ đọc nhưng không làm vỡ layout đã nghiệm thu.
3. Áp dụng selected state rõ ràng cho view sidebar đang mở.
4. Cập nhật selected state khi `switch_view()` chạy.
5. Kiểm tra độ tương phản của Hunt status và Start/Stop bằng token hiện có.

## Kiểm thử bắt buộc

```powershell
py -m pytest tests -m ui -k "hunt or view" -q
```

Nếu test mới không có tên khớp `hunt` hoặc `view`, cập nhật lại pattern `-k` cho khớp (hoặc chạy toàn bộ file test liên quan) trước khi báo cáo kết quả.

## Kiểm tra thủ công nhanh

- Chuyển qua Hunt, Setup và Help; chỉ view hiện tại có selected state.
- Kiểm tra nhãn ở `en` và `vi`.
- Xác nhận không có chữ bị cắt ở 1366x768.

## Điều kiện hoàn tất

- Không còn font 8px cho thông tin Hunt cần đọc thường xuyên.
- Sidebar thể hiện đúng view hiện tại.
- Style dùng token chung, không thêm bảng màu cục bộ mới.

## Điểm dừng bắt buộc

Không thiết kế lại sidebar, icon system hoặc palette toàn ứng dụng.

## Còn lại sau session này

Bước 8 trong bảng triển khai của tài liệu gốc — "Bổ sung kiểm thử GUI và kiểm tra thủ công trên nhiều DPI" (mục 4.6, mục 7 toàn bộ) — chưa có session riêng. Cần một Session 09 để:

- Chạy kiểm tra chuyển đổi 100%, 125%, 150% DPI (AC-9) trên thực tế, không chỉ dựa vào việc dùng token nhất quán.
- Rà soát lại toàn bộ AC-1 đến AC-17 một lượt cuối sau khi tất cả các session P0-P2 đã hoàn tất, để bắt các lỗi hồi quy xuất hiện giữa các session.
- Xác nhận `xvfb-run -a pytest <test_paths>` hoặc mock Tkinter tương đương chạy được trên môi trường headless nếu dự án có CI Linux.

## Báo cáo Jules cần để lại

- Token style đã dùng hoặc bổ sung.
- Diff hoặc commit liên quan (nếu có).
- Kết quả test và kiểm tra hai ngôn ngữ.
- Ảnh trước/sau nếu có thể.