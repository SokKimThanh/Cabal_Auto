# Session 04 - Sửa Phân Bổ Chiều Cao Hunt

## Thông tin session

- **Người xử lý:** Jules
- **Timebox:** 25-30 phút
- **Ưu tiên:** P0
- **Phụ thuộc:** Session 01 (trùng file `app_gui.py`), Session 03 (trùng file `ui/tabs/hunt_tab.py`) — cần hoàn tất trước để tránh xung đột khi sửa cùng file.
- **Tham chiếu tài liệu gốc:** Đề Xuất Khắc Phục Giao Diện Hunt Hiện Tại (v2), mục 5.2 (phần chiều cao còn lại sau Session 03: `minsize=552`, hàng skill 120px, Treeview) và mục 5.6 (chỉ phần giảm không gian trống của Active Target & Status), mục 6 bước 3 (phần còn lại)
- **AC liên quan:** AC-1, AC-2, AC-4, AC-18, AC-19

## Mục tiêu duy nhất

Điều chỉnh các `minsize` và `weight` theo chiều dọc để ba hàng Skill slots và ít nhất hai dòng thống kê hiển thị ở 1366x768 khi Logs đã thu.

Lỗi chặn cần sửa trong session này: khi Logs đã thu, chỉ nội dung Text log biến mất; Hunt workspace vẫn giữ requested height lớn hơn row được cấp. Biên Logs vì vậy cắt ngang Hunt, toàn bộ hàng Skill nằm ngoài vùng nhìn thấy, và child widget bị clip/overflow ngoài chiều cao form. Không được xử lý bằng cách chỉ đưa Logs lên trên hoặc ẩn thêm widget.

## Ngoài phạm vi

Phần còn lại của mục 5.6 trong tài liệu gốc — giới hạn chiều cao Logs khi mở và cho phép người dùng thay đổi tỷ lệ — **không** thuộc session này. Việc bật resize cửa sổ (mục 5.4) và breakpoint bố cục hẹp (mục 5.5) cũng không thuộc session này.

## File trong phạm vi

- `app_gui.py`
- `ui/tabs/hunt_tab.py`
- test layout Hunt liên quan

Không bật resize cửa sổ và không xây breakpoint mới trong session này.

## Các bước thực hiện

1. Đo chiều cao khả dụng sau action bar và Logs header trong test hoặc runtime. Ghi nhận cả requested height và allocated height của `shell_zone_b`, Hunt tab và `skill_strip_frame`.
2. Gỡ xung đột giữa `main_shell` row tối thiểu, Hunt row `552px` và skill row `120px`.
3. Dành chiều cao tối thiểu thực tế cho ba hàng skill.
4. Bảo đảm Treeview thống kê hiển thị tiêu đề và ít nhất hai dòng.
5. Giảm không gian trống của Active Target & Status bằng phân bổ grid, không dùng `place()`.
6. Thêm test biên hình học sau `update_idletasks()` ở 1366x768 khi Logs thu:
   - đáy `skill_strip_frame` không vượt đáy Hunt tab;
   - đáy Hunt content không vượt đỉnh `logs_header_frame`;
   - đỉnh và đáy Logs nằm trong vùng client của root;
   - không dùng riêng `winfo_ismapped()` làm bằng chứng vì widget vẫn có thể mapped nhưng bị clip.

## Kiểm thử bắt buộc

```powershell
py -m pytest tests -m ui -k "hunt or bottom_logs" -q
```

Nếu có test mới được thêm ở bước 1 mà tên không khớp `hunt` hoặc `bottom_logs`, cập nhật lại pattern `-k` cho khớp (hoặc chạy toàn bộ file test liên quan) trước khi báo cáo kết quả.

## Kiểm tra thủ công nhanh

- Chạy ở 1366x768 với Logs thu gọn.
- Xác nhận ba hàng skill thao tác được.
- Mở rồi thu Logs và xác nhận widget không chồng nhau.

## Điều kiện hoàn tất

- Skill slots hiển thị đủ ba hàng.
- Treeview có tiêu đề và ít nhất hai dòng khả dụng.
- Không widget nào bị Logs che hoặc chồng lên Logs.
- Hunt workspace không có requested height ép child vượt khỏi row được cấp.
- Đáy Skill/Hunt nhỏ hơn hoặc bằng đỉnh Logs khi quy đổi về cùng hệ tọa độ root.
- Không còn vùng nội dung bị mất chỉ vì nằm ngoài chiều cao form.

## Điểm dừng bắt buộc

Không thay đổi font, sidebar hoặc cơ chế resize cửa sổ.

## Báo cáo Jules cần để lại

- Phân bổ row trước và sau thay đổi.
- Diff hoặc commit liên quan (nếu có).
- Ảnh hoặc số đo widget ở 1366x768 nếu có thể.
- Số đo `winfo_reqheight()`, `winfo_height()` và các tọa độ biên trước/sau.
- Kết quả test và trạng thái AC-1, AC-2, AC-4, AC-18, AC-19.
