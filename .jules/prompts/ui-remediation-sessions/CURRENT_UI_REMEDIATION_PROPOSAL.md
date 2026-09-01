# Đề Xuất Khắc Phục Giao Diện Hunt Hiện Tại (v2)

> **Vai trò tài liệu:** Đây là tài liệu nguồn tổng hợp, không phải một session triển khai.
> Công việc đã được chia thành các session dưới 30 phút tại
> [Bộ session khắc phục giao diện Hunt](ui-remediation-sessions/README.md).
> Mỗi lần chỉ giao cho Jules một tài liệu session con.

## Mục lục

1. Mục tiêu
2. Phạm vi
3. Hiện trạng quan sát được
4. Nguyên nhân đã xác nhận
5. Đề xuất khắc phục (P0 / P1 / P2)
6. Thứ tự triển khai đề xuất
7. Tiêu chí nghiệm thu
8. Rủi ro và nguyên tắc thực hiện
9. Kết quả mong đợi

## 1. Mục tiêu

Tài liệu này tập hợp các vấn đề quan sát được trên giao diện Hunt tại độ phân giải 1366x768, đối chiếu với code hiện tại, và đề xuất lộ trình khắc phục có thể kiểm thử.

Mục tiêu ưu tiên:

1. Bảo đảm các thao tác Hunt chính luôn hiển thị và có thể sử dụng.
2. Không để Logs hoặc panel phụ che, đẩy, hay cắt nội dung nghiệp vụ.
3. Hỗ trợ cửa sổ nhỏ và DPI scaling mà không phụ thuộc vào kích thước pixel cố định.
4. Sửa hiển thị log bị lặp thông tin.
5. Bổ sung kiểm thử giao diện theo đúng luồng sự kiện Tkinter thực tế.

## 2. Phạm vi

Phạm vi trực tiếp gồm:

- cửa sổ chính và cơ chế resize
- bố cục `main_shell`
- Hunt workspace
- Monster Rotation
- Active Target & Status
- Skill slots
- Skill Performance Statistics
- Bottom Logs
- kiểm thử responsive liên quan

Tài liệu không đề xuất thay đổi nghiệp vụ hunt, vision engine, database, hay cấu hình skill.

## 3. Hiện trạng quan sát được

Trên cửa sổ 1366x768:

- Skill slots và Skill Performance Statistics bị cắt ngay dưới tiêu đề.
- Logs đang mở chiếm phần lớn nửa dưới cửa sổ dù chỉ có vài dòng nội dung.
- Active Target & Status có một vùng trống rất lớn.
- Các thành phần điều khiển và chữ bị ép nhỏ.
- Timestamp và log level bị lặp trên mỗi dòng log.
- Người dùng không thể kéo giãn cửa sổ để tự khắc phục bố cục.

Đây là lỗi bố cục và responsive, không chỉ là vấn đề thẩm mỹ.

## 4. Nguyên nhân đã xác nhận

### 4.1 Auto-collapse của Logs không được kích hoạt bởi GUI

`App._on_window_configure()` có logic thu Logs khi chiều cao dưới 900px, nhưng hàm này chưa được bind vào sự kiện `<Configure>`. `App._check_initial_logs_state()` hiện cũng không thực hiện kiểm tra nào.

Hệ quả: `logs_expanded` khởi tạo bằng `True` và có thể giữ nguyên trạng thái mở trên màn hình thấp.

### 4.2 Các ràng buộc minsize mâu thuẫn với viewport

Bố cục hiện tại đặt nhiều kích thước tối thiểu tuyệt đối:

- action bar: 80px
- main workspace: 540px
- hai cột Hunt: mỗi cột 776px
- hàng chính Hunt: 552px
- hàng skill: 120px
- Logs khi mở: khoảng 200px

Tổng kích thước yêu cầu lớn hơn vùng client trên màn hình 1366x768. Tkinter buộc phải ép hoặc cắt widget, dẫn đến hàng skill không còn diện tích hiển thị.

### 4.3 Cửa sổ bị khóa kích thước

Cửa sổ dùng `resizable(False, False)` và đặt geometry gần bằng kích thước màn hình. Cách này không tính đầy đủ phần title bar, taskbar và DPI, đồng thời không cho người dùng điều chỉnh khi nội dung vượt khung.

### 4.4 Phân bổ không gian chưa đúng mức độ ưu tiên

Active Target & Status đang nằm trong panel lớn có `weight=1`, dù nội dung chính chỉ là một status bar. Trong khi đó Skill slots và Skill Performance Statistics bị đặt trong hàng có chiều cao tối thiểu chỉ 120px.

Logs là thông tin hỗ trợ nhưng đang có khả năng chiếm nhiều không gian hơn các điều khiển nghiệp vụ.

### 4.5 Log bị format hai lần

`QueueHandler` đã gán formatter cho record. Khi đọc queue, UI lại tìm `QueueHandler` và gọi `handler.format(record)` lần nữa. Do `QueueHandler.prepare()` đã chuyển message thành chuỗi được format, lần format sau chèn thêm timestamp và level lần thứ hai.

### 4.6 Kiểm thử tạo cảm giác an toàn sai

Test responsive hiện gọi trực tiếp `_on_window_configure()` thay vì phát sinh sự kiện `<Configure>`. Vì vậy test vẫn pass dù ứng dụng không bind callback này trong luồng GUI thật.

## 5. Đề xuất khắc phục

### P0 - Khôi phục khả năng sử dụng

#### 5.1 Kết nối và khởi tạo auto-collapse

- Bind `<Configure>` của cửa sổ chính vào `_on_window_configure()`.
- Gọi một lần kiểm tra sau `update_idletasks()` hoặc bằng `after_idle()` khi UI đã có kích thước thực.
- Chỉ tự động thu Logs khi người dùng chưa chủ động mở lại trong cùng một khoảng kích thước; nếu người dùng đã chủ động mở, resize nhỏ trong cùng khoảng không được tự động đóng lại (xem tiêu chí 7.2).
- Khi thiếu chiều cao, ưu tiên thu Logs trước khi co nhỏ hàng Skill.

#### 5.2 Loại bỏ xung đột kích thước tối thiểu

- Giảm hoặc bỏ `minsize=552` của hàng chính Hunt.
- Không đặt hai cột Hunt cùng có `minsize=776`.
- Cho phép cột và hàng co lại theo nội dung tối thiểu thực tế.
- Đặt chiều cao hợp lý cho Skill slots để tất cả ba hàng skill luôn hiển thị.
- Để Treeview thống kê có chiều cao tối thiểu từ hai đến ba dòng.

#### 5.3 Sửa log bị lặp

- Chọn một nơi duy nhất chịu trách nhiệm format log.
- Phương án đề xuất: queue truyền `LogRecord`, UI dùng chuỗi đã được `QueueHandler` chuẩn bị mà không format lại.
- Bảo đảm file log và console vẫn giữ định dạng hiện tại.

### P1 - Làm bố cục responsive

#### 5.4 Cho phép resize an toàn

- Bật resize cho cửa sổ chính.
- Đặt `minsize()` theo kích thước nhỏ nhất đã kiểm thử thay vì khóa geometry.
- Giới hạn geometry khởi tạo theo vùng làm việc khả dụng, không dùng toàn bộ screen height một cách tuyệt đối.
- Lưu và khôi phục geometry nếu cấu hình hiện tại có vị trí phù hợp.

#### 5.5 Tái phân bổ Hunt workspace

Bố cục rộng:

- hàng trên: Monster Rotation và Active Target & Status
- hàng dưới: Skill slots và Skill Performance Statistics
- Logs mặc định thu gọn nếu chiều cao không đủ

Bố cục hẹp:

- Active Target & Status chuyển thành thanh ngang gọn ở đầu workspace
- Monster Rotation nằm bên dưới status
- Skill slots và thống kê xếp dọc hoặc chuyển qua tab/segmented view
- không cho phép thành phần nào có chiều rộng tối thiểu lớn hơn viewport

#### 5.6 Giảm diện tích trống

- Status panel chỉ cao theo nội dung khi không có chi tiết target.
- Vùng trống bổ sung chỉ được mở rộng khi có preview, thông tin target, hoặc dữ liệu runtime cần hiển thị.
- Logs khi mở nên có chiều cao giới hạn và cho phép người dùng thay đổi tỷ lệ nếu cần.

### P2 - Hoàn thiện trải nghiệm và khả năng bảo trì

#### 5.7 Tăng khả năng đọc

- Không dùng font 8px cho thông tin cần đọc thường xuyên.
- Dùng font và spacing từ `UIStyle` thay cho các giá trị `Arial` rải rác.
- Bảo đảm trạng thái, target hiện tại và nút Start/Stop có độ tương phản rõ ràng.

#### 5.8 Làm rõ điều hướng hiện tại

- Sidebar cần có selected state khác biệt cho view đang mở.
- Không dùng cùng một nền nhạt cho section label, navigation item và selected item.
- Hunt phải được nhận biết là màn hình hiện tại ngay khi mở ứng dụng.

## 6. Thứ tự triển khai đề xuất

| # | Bước | Ưu tiên | Mục liên quan |
| --- | --- | --- | --- |
| 1 | Sửa binding `<Configure>` và khởi tạo trạng thái Logs | P0 | 5.1 |
| 2 | Sửa log bị format lặp | P0 | 5.3 |
| 3 | Điều chỉnh các `minsize` để nội dung hiển thị đủ ở 1366x768 | P0 | 5.2 |
| 4 | Bật resize và xác định kích thước tối thiểu của cửa sổ | P1 | 5.4 |
| 5 | Thêm breakpoint bố cục hẹp cho Hunt workspace | P1 | 5.5 |
| 6 | Giảm diện tích trống / giới hạn chiều cao Logs khi mở | P1 | 5.6 |
| 7 | Chuẩn hóa font, spacing và selected state | P2 | 5.7, 5.8 |
| 8 | Bổ sung kiểm thử GUI và kiểm tra thủ công trên nhiều DPI | P0-P2 | 4.6, mục 7 |

Mỗi bước cần được kiểm thử độc lập; không nên đổi toàn bộ bố cục trong một thay đổi lớn.

## 7. Tiêu chí nghiệm thu

### 7.1 Hiển thị

- AC-1: Ở 1366x768, cả ba hàng Skill slots đều hiển thị và thao tác được.
- AC-2: Tiêu đề và ít nhất hai dòng của Skill Performance Statistics hiển thị đầy đủ.
- AC-3: Monster Rotation, Hunt status và Start/Stop không bị cắt.
- AC-4: Không có widget chồng lên Logs hoặc bị Logs che.
- AC-5: Không có thành phần yêu cầu chiều rộng lớn hơn vùng workspace.

### 7.2 Responsive

- AC-6: Resize cửa sổ không làm mất control chính.
- AC-7: Khi chiều cao không đủ, Logs tự thu gọn đúng một lần.
- AC-8: Sau khi người dùng chủ động mở Logs, sự kiện resize nhỏ trong cùng khoảng không lập tức đóng lại.
- AC-9: Chuyển qua lại giữa 100%, 125% và 150% DPI không gây cắt chữ hoặc mất widget.

### 7.3 Logs

- AC-10: Mỗi dòng chỉ có một timestamp và một log level.
- AC-11: Thu/mở Logs không mất nội dung và không phát sinh `TclError`.
- AC-12: Giới hạn buffer 1.000 dòng và queue 5.000 record tiếp tục hoạt động.

### 7.4 Kiểm thử

- AC-13: Test phát sinh `<Configure>` thật và xác nhận callback đã được gọi.
- AC-14: Test geometry 1366x768 xác nhận các widget chính có `winfo_ismapped()` và kích thước lớn hơn 0.
- AC-15: Test trạng thái Logs ở cả dưới và trên ngưỡng responsive.
- AC-16: Test một record qua queue chỉ tạo một timestamp trên Text widget.
- AC-17: Chạy test UI bằng `xvfb-run -a pytest <test_paths>` trên Linux headless hoặc dùng mock Tkinter phù hợp.

## 8. Rủi ro và nguyên tắc thực hiện

- Không thay đổi callback nghiệp vụ hunt trong quá trình sắp xếp giao diện.
- Không cập nhật Tkinter widget từ background thread; mọi cập nhật phải được schedule về main thread.
- Không dùng `place()` để che lỗi grid/pack vì sẽ tạo lỗi mới khi resize.
- Không thêm một bộ layout song song rồi bỏ qua code cũ; phần bố cục được thay thế phải được xóa rõ ràng sau khi kiểm thử thành công.
- Kiểm tra cả ngôn ngữ Anh và Việt vì độ dài nhãn khác nhau.

## 9. Kết quả mong đợi

Sau khi hoàn thành P0 và P1, giao diện Hunt phải sử dụng được trên màn hình laptop 1366x768, không cần người dùng tự sửa DPI hay ẩn taskbar. Các điều khiển Hunt chính luôn được ưu tiên, Logs trở lại đúng vai trò thông tin hỗ trợ, và bố cục có nền tảng để mở rộng mà không tiếp tục dựa vào kích thước pixel cố định.
