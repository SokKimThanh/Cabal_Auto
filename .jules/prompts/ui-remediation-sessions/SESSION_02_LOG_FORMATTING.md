# Session 02 - Loại Bỏ Log Bị Format Lặp

## Thông tin session

- **Người xử lý:** Jules
- **Timebox:** 15-20 phút
- **Ưu tiên:** P0
- **Phụ thuộc:** Không
- **Tham chiếu tài liệu gốc:** Đề Xuất Khắc Phục Giao Diện Hunt Hiện Tại (v2), mục 5.3 và mục 6 (bước 2)
- **AC liên quan:** AC-10, AC-12, AC-16

## Mục tiêu duy nhất

Bảo đảm mỗi record hiển thị trên Bottom Logs chỉ có một timestamp và một log level mà không thay đổi định dạng file log hoặc console.

## File trong phạm vi

- `app_gui.py`
- `lib/system/hunt_logger.py` chỉ khi test chứng minh cần thay đổi phía producer
- `tests/unit/test_bottom_logs.py`

## Nguyên nhân đã xác nhận

Theo mục 4.5 của tài liệu gốc: `QueueHandler.prepare()` đã chuẩn bị message có formatter; `_poll_log_queue()` gọi formatter thêm lần nữa nên timestamp và level bị lặp. Session này viết test để tái hiện lỗi trước khi sửa, không phải để kiểm chứng lại xem nguyên nhân có đúng hay không.

## Các bước thực hiện

1. Thêm test đẩy một record qua queue và đếm số lần xuất hiện timestamp/level trong Text widget; xác nhận test này fail trên code hiện tại (tái hiện lỗi) trước khi sửa.
2. Sửa `_poll_log_queue()` để chỉ một tầng chịu trách nhiệm format.
3. Giữ nguyên batching 50 record, queue tối đa 5.000 record và buffer UI 1.000 dòng.
4. Không thay đổi nội dung message nghiệp vụ.

## Kiểm thử bắt buộc

```powershell
py -m pytest tests/unit/test_bottom_logs.py -k "format or queue or buffer" -q
```

Nếu test mới ở bước 1 không có tên khớp `format`, `queue` hoặc `buffer`, cập nhật lại pattern `-k` cho khớp (hoặc chạy toàn bộ file test) trước khi báo cáo kết quả.

## Điều kiện hoàn tất

- Một record tạo đúng một timestamp và một level trên UI.
- Test queue cap và buffer cap vẫn pass.
- File `logs/hunt.log` và console vẫn có định dạng hiện tại.

## Điểm dừng bắt buộc

Không sửa auto-collapse, layout hoặc style trong session này.

## Báo cáo Jules cần để lại

- Nơi cuối cùng chịu trách nhiệm format record.
- Diff hoặc commit liên quan (nếu có).
- Lệnh test cùng kết quả.
- Trạng thái AC-10, AC-12 và AC-16. 