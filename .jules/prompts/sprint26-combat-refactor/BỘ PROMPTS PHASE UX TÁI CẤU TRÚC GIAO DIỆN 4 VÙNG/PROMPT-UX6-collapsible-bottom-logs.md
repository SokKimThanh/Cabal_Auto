# Session Prompt UX6: Build Collapsible Bottom Status & Long-Term Activity Log Panel

Timebox: 25–30 minutes.  
Priority: High – Provides high-performance, thread-safe, memory-capped logging with responsive auto-collapse.

---

## Objective
Xây dựng container Vùng C2/D ở đáy giao diện (kích thước 1640 x 200 px khi mở) hiển thị luồng nhật ký hoạt động thời gian thực an toàn luồng (thread-safe). Tích hợp cơ chế giới hạn dòng (Circular Buffer 1000 dòng chống tràn RAM), batch insert tối đa 50 dòng/tick, đồng bộ file log bền vững, tự động thu gọn responsive và hỗ trợ DPI 100% – 200%.

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

### 2. Batch Insert & Giới Hạn Bộ Nhớ (Circular Text Buffer)
- Hàng đợi log `queue.Queue` thu nhận sự kiện từ các background worker thread.
- Hàm `_flush_log_queue()` chạy định kỳ mỗi $100\text{ms}$ qua `after(100, ...)`:
  * Đọc tối đa **50 dòng / lần** từ hàng đợi để chèn vào `tk.Text`.
  * Tự động cuộn xuống dòng cuối (`text.see(tk.END)`).
  * **Chống rò rỉ RAM dài hạn:** Đếm tổng số dòng trong `tk.Text`. Nếu vượt quá **1.000 dòng**, xóa ngay các dòng cũ nhất từ đầu:
    ```python
    num_lines = int(self.log_text.index('end-1c').split('.')[0])
    if num_lines > 1000:
        self.log_text.delete("1.0", f"{num_lines - 1000 + 1}.0")
    ```

### 3. Đồng Bộ Log Bền Vững (Log Persistence)
- UI chỉ giữ vai trò hiển thị $1.000$ dòng gần nhất.
- Toàn bộ log chi tiết phát sinh từ `HuntLogger` được tự động ghi đồng thời vào file `logs/hunt_<YYYY-MM-DD>.log` (sử dụng `RotatingFileHandler` tối đa 10MB/file, lưu trữ tối đa 5 file backup).

### 4. Tự Động Thu Gọn Responsive & Fallback An Toàn
- Lắng nghe sự kiện co giãn cửa sổ ứng dụng: Khi chiều cao cửa sổ $< 900\text{px}$, tự động chuyển sang trạng thái thu gọn.
- Bọc toàn bộ hàm `toggle_logs()` trong `try...except Exception`: Nếu gặp lỗi hình học, tự động khôi phục về trạng thái hiển thị mặc định và log cảnh báo ra file.

---

## Validation & Testing

### 1. Automated Tests (`tests/unit/test_bottom_logs.py`)
- **Test Circular Buffer & Memory Cap:**
  * Bắn liên tục $5.000$ dòng log giả lập vào queue -> Chờ flush -> Assert số dòng trong widget `tk.Text` không vượt quá $1.000$ dòng.
- **Test Batch Insert Rate-Limit:**
  * Đẩy 200 dòng cùng lúc vào queue -> Assert lần flush đầu tiên chỉ xử lý tối đa 50 dòng mà không làm treo Main Thread.
- **Test Responsive Auto-Collapse:**
  * Giả lập sự kiện resize cửa sổ với chiều cao $850\text{px}$ -> Assert trạng thái container chuyển sang Thu gọn ($36\text{px}$).
- **Test Log File Persistence:**
  * Ghi 10 sự kiện log -> Assert file `logs/hunt_*.log` tồn tại và chứa đầy đủ 10 dòng tương ứng.

### 2. Visual & High-DPI Check
- Kiểm tra thanh metric và text log hiển thị sắc nét ở các mức DPI: 100%, 125%, 150%, 175%, 200%.
- Kiểm tra chuyển đổi ngôn ngữ `vi` <-> `en` làm mới text tiêu đề và nút toggle ngay lập tức.

---

## Session Boundary Gate
- **PASSED nếu:**
  * Khung log hoạt động ổn định, tự giới hạn 1.000 dòng, không rò rỉ RAM khi chạy stress test $5.000+$ dòng.
  * Chỉ số FPS và Metrics cập nhật mượt mà, ghi file log đầy đủ.
  * Nút thu gọn/mở rộng hoạt động an toàn ở mọi mức DPI.
- **REVERTED nếu:**
  * Gây treo giao diện Main Thread khi ghi log tốc độ cao hoặc phát sinh lỗi `TclError` khi toggle.
  * Báo cáo kết quả PASSED/REVERTED ở phút thứ 25.