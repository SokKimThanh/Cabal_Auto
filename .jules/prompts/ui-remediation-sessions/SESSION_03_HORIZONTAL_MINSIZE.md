# Session 03 - Gỡ Xung Đột Chiều Ngang Hunt

## Thông tin session

- **Người xử lý:** Jules
- **Timebox:** 20-25 phút
- **Ưu tiên:** P0
- **Phụ thuộc:** Không chặn về mặt file (khác file với Session 01). Khuyến nghị chạy sau khi Session 01 hoàn tất, vì Logs tự thu giúp quan sát chiều ngang dễ hơn khi kiểm tra thủ công.
- **Tham chiếu tài liệu gốc:** Đề Xuất Khắc Phục Giao Diện Hunt Hiện Tại (v2), mục 5.2 (chỉ phần ràng buộc chiều ngang hai cột `minsize=776`) và mục 6 (một phần của bước 3)
- **AC liên quan:** AC-3, AC-5

## Mục tiêu duy nhất

Loại bỏ yêu cầu hai cột Hunt cùng có `minsize=776` để workspace vừa chiều ngang của cửa sổ 1366x768.

## Ngoài phạm vi

Các ràng buộc chiều cao khác trong mục 5.2 của tài liệu gốc (`minsize=552` của hàng chính Hunt, chiều cao tối thiểu hàng skill 120px, chiều cao tối thiểu Treeview) **không** thuộc session này và sẽ xử lý ở session riêng.

## File trong phạm vi

- `ui/tabs/hunt_tab.py`
- test UI hẹp hiện có hoặc một test mới cạnh nhóm test Hunt

Không thay đổi thứ tự widget hoặc chuyển sang layout dọc trong session này.

## Các bước thực hiện

1. Thêm kiểm tra geometry để chứng minh tổng chiều rộng yêu cầu không vượt workspace.
2. Gỡ hoặc giảm `minsize` tuyệt đối của hai cột chính.
3. Giữ tỷ lệ hai panel cân bằng bằng `weight`, `uniform` hoặc cơ chế grid hiện có.
4. Kiểm tra nhãn tiếng Anh và tiếng Việt không đẩy control khỏi panel.

## Kiểm thử bắt buộc

```powershell
py -m pytest tests -m ui -k "hunt and layout" -q
```

Nếu chưa có test phù hợp, chạy file test mới được tạo thay cho biểu thức trên.

## Kiểm tra thủ công nhanh

1. Mở ứng dụng ở 1366x768.
2. Xác nhận Monster Rotation và Active Target & Status không tràn ngang.
3. Chuyển ngôn ngữ `en` và `vi`.

## Điều kiện hoàn tất

- Không có cột con yêu cầu chiều rộng lớn hơn workspace.
- Monster Rotation, status và Start/Stop không bị cắt ngang.
- Không phát sinh thanh cuộn ngang giả hoặc widget chồng nhau.

## Điểm dừng bắt buộc

Không triển khai breakpoint xếp dọc; nội dung đó thuộc Session 07 (mục 5.5 trong tài liệu gốc).
Không sửa ràng buộc chiều cao (`minsize=552`, hàng skill, Treeview); nội dung đó thuộc session riêng cho phần còn lại của mục 5.2.

## Báo cáo Jules cần để lại

- Giá trị/ràng buộc chiều ngang trước và sau thay đổi.
- Diff hoặc commit liên quan (nếu có).
- Kết quả test và kiểm tra hai ngôn ngữ.
- Trạng thái AC-3 và AC-5.
