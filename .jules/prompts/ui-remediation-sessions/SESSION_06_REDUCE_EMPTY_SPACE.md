# Session 06 - Giảm Vùng Trống Và Giới Hạn Logs

> **CẦN XÁC NHẬN TRƯỚC KHI CHẠY:** Session 03 ghi rằng breakpoint xếp dọc thuộc "Session 06", nhưng tài liệu này (Session 06) lại là về giảm vùng trống & giới hạn Logs (mục 5.6), không phải breakpoint (mục 5.5). Cần xác nhận số thứ tự đúng — nếu breakpoint chưa có tài liệu riêng, có thể tài liệu này nên đổi thành Session 07 và breakpoint giữ số 06 theo đúng thứ tự bước 5/bước 6 trong mục 6 của tài liệu gốc.

## Thông tin session

- **Người xử lý:** Jules
- **Timebox:** 20-25 phút
- **Ưu tiên:** P1
- **Phụ thuộc:** Session 04 (trùng file, đã bắt đầu giảm không gian trống Active Target & Status ở bước 5 — session này tinh chỉnh tiếp, không làm lại từ đầu), Session 05 (trùng file `app_gui.py`)
- **Tham chiếu tài liệu gốc:** Đề Xuất Khắc Phục Giao Diện Hunt Hiện Tại (v2), mục 5.6 và mục 6 (bước "giảm diện tích trống / giới hạn chiều cao Logs khi mở")
- **AC liên quan:** AC-2, AC-4 (kiểm tra hồi quy sau khi thay đổi thêm không gian, đã đạt lần đầu ở Session 04), AC-11

## Mục tiêu duy nhất

Giảm không gian trống của Active Target & Status và giới hạn chiều cao Logs khi mở để nội dung Hunt giữ quyền ưu tiên.

## File trong phạm vi

- `app_gui.py`
- `ui/tabs/hunt_tab.py`
- test layout/Bottom Logs liên quan

## Các bước thực hiện

1. Ghi nhận chiều cao status panel và Logs mở trước thay đổi.
2. Cho status panel cao theo nội dung khi chưa có preview hoặc chi tiết target (tinh chỉnh tiếp phần grid đã đổi ở Session 04, không quay lại dùng `place()`).
3. Đặt chiều cao mở hợp lý cho Logs; không để Logs lấy hết phần chiều cao tăng thêm.
4. Giữ nội dung log khi thu/mở và không tạo lại Text widget.
5. Thêm kiểm tra không có `TclError` khi toggle nhanh.

## Kiểm thử bắt buộc

```powershell
py -m pytest tests/unit/test_bottom_logs.py -q
```

## Điều kiện hoàn tất

- Status rỗng không còn chiếm phần lớn workspace.
- Logs mở có giới hạn hợp lý và không che Skill slots.
- Thu/mở Logs không mất nội dung hoặc phát sinh lỗi.
- AC-2 và AC-4 vẫn đạt sau khi thay đổi thêm không gian (không bị hồi quy so với Session 04).

## Điểm dừng bắt buộc

Không thay đổi cách xếp cột ở breakpoint hẹp và không sửa style.

## Báo cáo Jules cần để lại

- Số đo chiều cao trước/sau.
- Diff hoặc commit liên quan (nếu có).
- Kết quả test.
- Trạng thái AC-2, AC-4 và AC-11.