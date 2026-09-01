# Session 05 - Bật Resize Cửa Sổ An Toàn

## Thông tin session

- **Người xử lý:** Jules
- **Timebox:** 20-25 phút
- **Ưu tiên:** P1
- **Phụ thuộc:** Session 01 (trùng file `app_gui.py`), Session 04 (cần giá trị minsize theo chiều dọc đã xác định)
- **Tham chiếu tài liệu gốc:** Đề Xuất Khắc Phục Giao Diện Hunt Hiện Tại (v2), mục 5.4 (không bao gồm phần lưu/khôi phục geometry) và mục 6 (bước 4)
- **AC liên quan:** AC-6

## Mục tiêu duy nhất

Cho phép người dùng resize cửa sổ và đặt kích thước khởi tạo/tối thiểu không vượt vùng làm việc khả dụng.

## File trong phạm vi

- `app_gui.py`
- test khởi tạo cửa sổ liên quan

## Các bước thực hiện

1. Thêm test cho trạng thái resizable và kích thước tối thiểu.
2. Thay `resizable(False, False)` bằng cấu hình cho phép resize.
3. Đặt `minsize()` theo kích thước nhỏ nhất đã được các Session 03-04 hỗ trợ.
4. Giới hạn geometry khởi tạo để không che title bar/taskbar trên Windows.
5. Xác nhận callback `<Configure>` không tạo vòng lặp resize.

## Kiểm thử bắt buộc

```powershell
py -m pytest tests/unit/test_bottom_logs.py -k responsive -q
```

Chạy thêm test cửa sổ mới được tạo ở bước 1 (nếu nằm ở file khác, chạy trực tiếp file đó thay vì chỉ dựa vào lệnh trên).

## Điều kiện hoàn tất

- Cửa sổ resize được theo cả hai chiều.
- Không thể co nhỏ dưới mức làm mất control chính.
- Geometry khởi tạo nằm trong vùng màn hình khả dụng.
- Auto-collapse Logs vẫn hoạt động.

## Điểm dừng bắt buộc

Không triển khai lưu/khôi phục geometry trong session này, kể cả khi dự án đã có cơ chế lưu cấu hình sẵn có — việc này thuộc một task riêng. Không triển khai breakpoint layout hẹp.

## Báo cáo Jules cần để lại

- Kích thước khởi tạo và tối thiểu đã chọn.
- Diff hoặc commit liên quan (nếu có).
- Kết quả test.
- Trạng thái AC-6.
