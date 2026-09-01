# Session 07 - Breakpoint Bố Cục Hunt Hẹp

## Thông tin session

- **Người xử lý:** Jules
- **Timebox:** 25-30 phút
- **Ưu tiên:** P1
- **Phụ thuộc:** Session 03 đến Session 06 — breakpoint cần layout nền tảng (chiều ngang, chiều dọc, resize, giảm vùng trống) đã ổn định từ các session trước để không phá lại kết quả đã đạt; trùng file `ui/tabs/hunt_tab.py` với Session 03, 04, 06.
- **Tham chiếu tài liệu gốc:** Đề Xuất Khắc Phục Giao Diện Hunt Hiện Tại (v2), mục 5.5 và mục 6 (bước "thêm breakpoint bố cục hẹp cho Hunt workspace")
- **AC liên quan:** AC-1, AC-2, AC-3, AC-5, AC-6 (phần lớn là kiểm tra hồi quy — các AC này đã đạt ở session trước, session này xác nhận vẫn đúng sau khi thêm breakpoint)

## Mục tiêu duy nhất

Thêm một breakpoint hẹp để các panel Hunt đổi cách xếp mà không bị tràn hoặc mất control.

## Phạm vi tối thiểu

- `ui/tabs/hunt_tab.py`
- test layout responsive Hunt

Chỉ dùng widget hiện có; không tạo phiên bản widget thứ hai.

## Thiết kế mục tiêu

Ở chiều rộng hẹp:

- status trở thành hàng gọn ở đầu workspace
- Monster Rotation nằm dưới status
- Skill slots và thống kê xếp dọc, hoặc nằm trong control chuyển view hiện có
- không widget nào có `minsize` lớn hơn workspace

## Các bước thực hiện

1. Viết test cho hai phía của một breakpoint duy nhất.
2. Tạo hàm áp dụng layout rộng/hẹp có thể gọi lặp mà không lỗi.
3. Bind resize ở đúng owner của Hunt tab và debounce nếu cần.
4. Dùng `grid_configure()`/`grid_remove()` hoặc cơ chế layout hiện có; không dùng `place()`.
5. Xác nhận widget không bị tạo lại và callback vẫn giữ nguyên.

## Kiểm thử bắt buộc

```powershell
py -m pytest tests -m ui -k "hunt and responsive" -q
```

Nếu test mới ở bước 1 không có tên khớp `hunt` hoặc `responsive`, cập nhật lại pattern `-k` cho khớp (hoặc chạy toàn bộ file test layout Hunt) trước khi báo cáo kết quả.

## Kiểm tra thủ công nhanh

- Kéo qua lại breakpoint ít nhất năm lần.
- Thử cả `en` và `vi`.
- Xác nhận combobox, nút monster và skill vẫn thao tác được.

## Điều kiện hoàn tất

- Layout chuyển đổi ổn định ở cả hai phía breakpoint.
- Không widget trùng, mất callback hoặc chồng nhau.
- Toàn bộ control Hunt chính vẫn truy cập được.

## Điểm dừng bắt buộc

Nếu việc chuyển layout đòi hỏi tái tạo widget hoặc refactor lớn hơn một class, dừng session và ghi blocker; không mở rộng phạm vi quá 30 phút.

## Báo cáo Jules cần để lại

- Breakpoint đã chọn và lý do.
- Cơ chế chuyển layout.
- Diff hoặc commit liên quan (nếu có).
- Kết quả test cùng trạng thái các AC liên quan.
