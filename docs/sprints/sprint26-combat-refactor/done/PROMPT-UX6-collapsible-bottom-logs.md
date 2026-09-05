# Session Prompt UX6: Build Collapsible Bottom Status & Long-Term Activity Log Panel

Timebox: 25–30 minutes.
Priority: High – Provides high-performance, thread-safe, memory-capped logging with responsive auto-collapse.

---

## Objective
Xây dựng container Vùng C2/D ở đáy giao diện (kích thước 1640 x 200 px khi mở) hiển thị luồng nhật ký hoạt động thời gian thực an toàn luồng (thread-safe). Tích hợp cơ chế giới hạn dòng (Circular Buffer 1000 dòng chống tràn RAM ở cả tầng hiển thị lẫn tầng hàng đợi), batch insert tối đa 50 dòng/tick, đồng bộ file log bền vững, tự động thu gọn responsive không xung đột với thao tác thủ công, và hỗ trợ DPI 100% – 200%.

## Target Files
- Modify: `ui/bottom_logs.py` (hoặc frame nhật ký trong `app_gui.py`)
- Modify: `lib/system/hunt_logger.py`
- Modify: `lib/system/i18n.py`
- Reference: `lib/ui_style.py`

---

## Implementation Details

### 1. Bố Cục Container & DPI Scaling Guard (Vùng C2/D)
- Chiều cao container:
  * Khi Mở rộng: `minsize = 160px`, chiều cao chuẩn `200px`.
  * Khi Thu gọn: Cố định `36px` (chỉ hiển thị thanh trạng thái metric và nút toggle).
- Thanh tiêu đề trạng thái (36 px):
  * Cột trái: Nhãn "Nhật Ký Hoạt Động" (i18n).
  * Cột giữa: Badge chỉ số định dạng `⚡ FPS: XX.X | 🎯 Quét: X,XXX | ⏱ Chạy: HH:MM:SS` (Cập nhật 1 lần/giây).
  * Cột phải: Nút Toggle `[▲ Thu Gọn] / [▼ Mở Rộng]` (80 x 28 px) và Nút `[ Xóa Log Màn Hình ]`.

### 2. Batch Insert & Giới Hạn Bộ Nhớ (Circular Buffer — cả tầng Queue lẫn tầng hiển thị)
- Hàng đợi log `queue.Queue(maxsize=5000)` thu nhận sự kiện từ các background worker thread — **có giới hạn kích thước rõ ràng**, không dùng `Queue()` không giới hạn. Nếu tốc độ log đến vượt tốc độ flush tối đa (50 dòng/100ms = 500 dòng/giây, VD: log debug dày đặc từ vòng lặp vision 4ms ở CB6), hàng đợi sẽ đầy trước khi kịp drain — khi đó:
  * Khi `put()` gặp `queue.Full`: bỏ dòng log mới đó (drop-newest, ưu tiên giữ log cũ hơn đã tồn tại trong queue chờ xử lý) và tăng một bộ đếm `dropped_log_count` nội bộ.
  * Định kỳ (VD: mỗi khi flush) nếu `dropped_log_count > 0`, chèn một dòng tổng hợp vào `tk.Text` dạng `[!] Đã bỏ qua N dòng log do quá tải` rồi reset bộ đếm về 0, để người dùng biết có mất log chứ không im lặng.
- Hàm `_flush_log_queue()` chạy định kỳ mỗi 100ms qua `after(100, ...)`:
  * Đọc tối đa **50 dòng / lần** từ hàng đợi để chèn vào `tk.Text`.
  * Tự động cuộn xuống dòng cuối (`text.see(tk.END)`).
  * **Chống rò rỉ RAM dài hạn ở tầng hiển thị:** Đếm tổng số dòng trong `tk.Text`. Nếu vượt quá **1.000 dòng**, xóa ngay các dòng cũ nhất từ đầu:
    ```python
    num_lines = int(self.log_text.index('end-1c').split('.')[0])
    if num_lines > 1000:
        self.log_text.delete("1.0", f"{num_lines - 1000 + 1}.0")
    ```

### 3. Đồng Bộ Log Bền Vững (Log Persistence)
- UI chỉ giữ vai trò hiển thị 1.000 dòng gần nhất (và không nhất thiết hiển thị 100% mọi dòng nếu queue từng bị đầy — xem mục 2).
- Toàn bộ log chi tiết phát sinh từ `HuntLogger` được tự động ghi đồng thời vào file `logs/hunt_<YYYY-MM-DD>.log` (sử dụng `RotatingFileHandler` tối đa 10MB/file, lưu trữ tối đa 5 file backup). File log này ghi trực tiếp từ logger (không đi qua hàng đợi UI), nên **không bị ảnh hưởng** bởi việc drop dòng ở mục 2 — file log đầy đủ vẫn được bảo toàn kể cả khi UI phải bỏ bớt dòng hiển thị do quá tải.

### 4. Tự Động Thu Gọn Responsive & Fallback An Toàn
- Lắng nghe sự kiện co giãn cửa sổ ứng dụng: khi chiều cao cửa sổ giảm xuống dưới **900px** (chỉ kích hoạt tại thời điểm **vượt ngưỡng từ trên xuống**, tức lần đầu tiên đo được `height < 900` sau khi trước đó `height >= 900`), tự động chuyển sang trạng thái thu gọn đúng một lần.
  * **Không lặp lại việc ép thu gọn ở các sự kiện resize tiếp theo** nếu chiều cao vẫn tiếp tục dưới 900px nhưng người dùng đã chủ động mở rộng lại panel thủ công — tôn trọng lựa chọn thủ công cho tới khi chiều cao cửa sổ vượt lại lên trên 900px rồi giảm xuống dưới ngưỡng lần nữa (tức phải "đi lên rồi đi xuống" mới kích hoạt lại auto-collapse), tránh vòng lặp "tự thu gọn → người dùng mở → tự thu gọn lại" mỗi lần có resize event nhỏ.
- Bọc toàn bộ hàm `toggle_logs()` trong `try...except Exception`: nếu gặp lỗi hình học, tự động khôi phục về trạng thái **Mở rộng** (trạng thái mặc định an toàn, dễ debug hơn) và log cảnh báo ra file.

---

## Validation & Testing

### 1. Automated Tests (`tests/unit/test_bottom_logs.py`)
- **Test Circular Buffer & Memory Cap (hiển thị):** Bắn liên tục 5.000 dòng log giả lập vào queue → Chờ flush → Assert số dòng trong widget `tk.Text` không vượt quá 1.000 dòng.
- (Added) **Test Queue Cap & Drop Handling:** Bắn log với tốc độ vượt khả năng flush (VD: 10.000 dòng dồn dập trong thời gian ngắn hơn thời gian cần để drain hết ở tốc độ 500 dòng/giây) → Assert `queue.Queue` không vượt quá `maxsize=5000`, các dòng vượt mức bị drop có kiểm soát (không exception), và một dòng tổng hợp `[!] Đã bỏ qua N dòng...` xuất hiện trong `tk.Text`.
- **Test Batch Insert Rate-Limit:** Đẩy 200 dòng cùng lúc vào queue → Assert lần flush đầu tiên chỉ xử lý tối đa 50 dòng mà không làm treo Main Thread.
- **Test Responsive Auto-Collapse:** Giả lập sự kiện resize cửa sổ với chiều cao 850px → Assert trạng thái container chuyển sang Thu gọn (36px).
- (Added) **Test Auto-Collapse Không Ép Lặp Lại:** Giả lập resize xuống 850px (kích hoạt auto-collapse) → người dùng thủ công mở rộng lại → giả lập thêm một sự kiện resize khác vẫn ở 840px (vẫn dưới ngưỡng) → Assert panel **không** bị tự động thu gọn lại lần thứ hai; sau đó giả lập resize lên trên 900px rồi lại xuống dưới 900px → Assert auto-collapse kích hoạt lại đúng một lần.
- **Test Log File Persistence:** Ghi 10 sự kiện log → Assert file `logs/hunt_*.log` tồn tại và chứa đầy đủ 10 dòng tương ứng (kể cả trong kịch bản queue UI đang bị đầy/drop ở test trên — file log không bị ảnh hưởng).

### 2. Visual & High-DPI Check
- Kiểm tra thanh metric và text log hiển thị sắc nét ở các mức DPI: 100%, 125%, 150%, 175%, 200%.
- Kiểm tra chuyển đổi ngôn ngữ `vi` <-> `en` làm mới text tiêu đề và nút toggle ngay lập tức.

---

## Session Boundary Gate
- **PASSED nếu:**
  * Khung log hoạt động ổn định, tự giới hạn 1.000 dòng ở tầng hiển thị **và** giới hạn kích thước ở tầng hàng đợi, không rò rỉ RAM khi chạy stress test 5.000+ dòng ở cả hai tầng.
  * Chỉ số FPS và Metrics cập nhật mượt mà, ghi file log đầy đủ không phụ thuộc vào việc UI có drop dòng hay không.
  * Nút thu gọn/mở rộng hoạt động an toàn ở mọi mức DPI, và auto-collapse không xung đột/lặp lại vô lý với thao tác thủ công của người dùng.
- **REVERTED nếu:**
  * Gây treo giao diện Main Thread khi ghi log tốc độ cao hoặc phát sinh lỗi `TclError` khi toggle.
  * Hàng đợi nội bộ tăng trưởng không giới hạn dù UI hiển thị đúng 1.000 dòng.
  * Auto-collapse liên tục ép về trạng thái thu gọn dù người dùng đã chủ động mở rộng lại.
  * Báo cáo kết quả PASSED/REVERTED ở phút thứ 25.