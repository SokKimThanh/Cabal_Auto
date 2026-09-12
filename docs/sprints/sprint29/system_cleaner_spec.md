# System Cleaner Specification (Hệ thống Dọn Rác)

## 1. Title & Objective
**Tính năng:** Tích hợp hệ thống dọn dẹp các tệp tin "rác" (Junk files) sinh ra trong quá trình sử dụng và phát triển ứng dụng Cabal Auto Hunt.
**Mục tiêu:**
- Cho phép người dùng quét và giải phóng dung lượng ổ cứng an toàn thông qua một giao diện trực quan, tương tự như các ứng dụng tối ưu hóa hệ thống.
- Cung cấp tính phân loại rõ ràng (Logs, Caches, Backups, Temp files) để tránh rủi ro mất dữ liệu quan trọng.
- Đồng nhất với UI Style V2 và kiến trúc Event-Driven của dự án.

## 2. Context & Scope
Trong quá trình vận hành, ứng dụng sinh ra nhiều tệp tin lưu trữ tạm thời như:
- Application logs (`app_output.log`) phát triển theo thời gian.
- Các bản backup tự động cấu hình (`*.bak`, `*_backup.json`).
- Developer caches (ví dụ: `__pycache__`, `.pytest_cache`, `*.pyc`).
- Thư mục chứa file tạm hoặc ảnh debug (`tmp/`, `*.tmp`).

Việc để mặc các tệp này có thể làm phình to dung lượng ổ cứng không cần thiết. Người dùng cần một UI quản lý tích hợp ngay trong app để quét và xoá chúng bằng 1 click.

## 3. UI/UX Requirements
Dựa trên nguyên mẫu (tham chiếu ảnh cung cấp):
- **Vị trí:** Có thể đặt dưới dạng một Tab mới trong **Setup / Settings** hoặc một công cụ ở **Sidebar**.
- **Thành phần chính:**
  - **Header:** Tiêu đề "System Cleaner" và mô tả tính năng.
  - **Category Tree/Checkboxes (Bên trái):** Danh sách các loại rác kèm Checkbox để tick chọn (Logs, Caches, Temp files, Backups). Có thể hiển thị mô tả ngắn gọn bên dưới từng mục.
  - **Storage Info & Progress (Bên phải):**
    - **Dung lượng hiển thị:** Một bộ đếm dung lượng khổng lồ với text màu Cyan `#00E5FF` báo cáo "Total scanned size: XX.X MB".
    - **Hiệu ứng đếm:** Con số dung lượng phải có hiệu ứng tăng dần (count up) sinh động theo thời gian thực trong quá trình quét.
    - **Thanh tiến trình (Progress Bar):** Hiển thị một thanh tiến trình (progress bar) trong quá trình quét để người dùng cảm nhận được tốc độ xử lý mà không làm quá tải giao diện.
    - **Quy đổi đơn vị tự động (Dynamic Unit Conversion):** Dung lượng phải được tự động định dạng và quy đổi sang đơn vị ngắn gọn, dễ đọc nhất (KB, MB, GB...). Ví dụ: tự động chuyển từ 900 MB sang dạng 1.2 GB khi vượt ngưỡng.
    - **Mockup Hiển thị Tiến trình (Progress UI Reference):** Giao diện quét cần mô phỏng cách hiển thị của các phần mềm dọn dẹp hệ thống chuyên nghiệp theo dạng thiết kế sau (cập nhật file hiển thị qua cơ chế throttling để đảm bảo hiệu năng):
      ```
      Đang quét hệ thống...

      [███████████░░░░░░░░] 58%

      Tệp hiện tại:
      C:\Users\Admin\AppData\Local\Temp\abc123.tmp

      Rác đã phát hiện:
      1.4 GB (24,381 tệp)
      ```
  - **Action Bar (Dưới cùng):**
    - `Default`: Chọn các mục an toàn mặc định (VD: Logs, Temp files, System caches) nhưng chừa lại Backups.
    - `Scan`: Bắt đầu quét thư mục. Cập nhật con số hiển thị.
    - `Clean`: Thực hiện xóa. Chỉ Enable khi kết quả Scan > 0 MB. **Yêu cầu dữ liệu:** Tổng dung lượng rác đã dọn dẹp phải bằng chính xác với tổng dung lượng rác đã được phát hiện ở bước Scan trước đó.

- **Translation Keys (i18n):**
  Tất cả text hiển thị cần được tích hợp vào hệ thống i18n của dự án (ví dụ: `system_cleaner_title`, `cleaner_cat_logs`, `btn_scan`, `btn_clean`, `cleaner_success_msg`).

## 4. Architecture & Implementation Guide
Áp dụng mô hình Controller-View-Service hiện tại của dự án.

### 4.1. Core Service (`lib/system/cleanup/cleaner_service.py`)
- Định nghĩa các nhóm rác (`categories`) thông qua từ điển hoặc Enums.
- Sử dụng `pathlib.Path.rglob()` để quét đệ quy các tệp tương ứng.
- **Tính toán & Format:** Tính tổng dung lượng (byte size) và xây dựng một helper function để tự động quy đổi đơn vị (Bytes -> KB -> MB -> GB) để trả về cho View.
- **Thực thi (Clean):** Dùng `path.unlink()` hoặc `shutil.rmtree()` để xoá file/thư mục. Xử lý Exception (`PermissionError`, `FileNotFoundError`) an toàn bằng `try/except`.

### 4.2. UI View (`ui/views/system_cleaner_frame.py`)
- Tái sử dụng `UI.COLORS` và `UI.FONTS` từ `ui.theme.style_v2`.
- **Non-blocking & Animation:** Dùng `threading` để thực hiện quá trình quét. Sử dụng phương thức `.after()` của Tkinter để cập nhật progress bar và tạo hiệu ứng đếm số (count up animation) cho dung lượng mà không làm đứng giao diện.

### 4.3. Controller (`ui/controllers/system_cleaner_controller.py`) (Optional)
- Tuỳ thuộc vào độ phức tạp, có thể đưa logic kết nối View <-> Service ra Controller riêng.
- Phát ra Activity Logs (vd: `[System Cleaner] Freed 15.2 MB`) sau khi người dùng thực hiện lệnh Clean.

## 5. Known Issues, Risks & System Weaknesses
- **Rủi ro xoá nhầm dữ liệu quan trọng (Data Loss Risk):** Nếu các mẫu tìm kiếm (glob patterns) định nghĩa quá rộng (ví dụ: dùng `*.json` thay vì `*_backup.json`), hệ thống có thể vô tình xoá mất các file cấu hình quan trọng của ứng dụng (như `hunt_cfg` hay cơ sở dữ liệu preset). Cần định nghĩa cấu hình quét cực kỳ nghiêm ngặt.
- **Điểm yếu về UI Blocking & Hủy tác vụ (Threading Weakness):** Mặc dù đã có đề xuất dùng `threading` cho quá trình quét, nhưng Tkinter rất dễ bị "đơ" (freeze) nếu việc cập nhật giao diện (update UI) không đồng bộ tốt với background thread. Hơn nữa, hiện tại chưa có cơ chế "Hủy (Cancel)" khi đang quét hoặc xoá nếu quá trình tốn quá nhiều thời gian.
- **Rủi ro về Symlinks (Liên kết mềm) & Cross-Platform:** Nếu hệ thống sử dụng thư mục chứa các symlinks trỏ ra ngoài thư mục gốc của dự án, lệnh xóa đệ quy có thể đi theo symlink và xóa các file ngoài dự kiến của hệ thống. Đồng thời, việc xử lý đường dẫn (paths) cần cẩn thận giữa Windows và các hệ điều hành khác để tránh xoá sai mục tiêu.
- **Trạng thái xoá không hoàn chỉnh (Partial Deletion Risk):** Trong quá trình thực thi lệnh Clean, nếu ứng dụng bị đóng đột ngột hoặc xảy ra lỗi (ngoại lệ không bắt được), một số file đã bị xoá còn một số thì chưa, dẫn đến trạng thái rác không nhất quán nhưng không làm hỏng ứng dụng.
- **Permission Errors:** Ứng dụng có thể đang khoá (lock) file log hiện tại (`app_output.log`). Khi dọn dẹp, cần bỏ qua file đang lock thay vì crash toàn bộ hệ thống.
- **Chỉ xóa những gì đã Scan:** Nút "Clean" chỉ được phép xóa các file đã liệt kê từ lần bấm nút "Scan" gần nhất. Không quét lại ngầm lúc bấm Clean để tránh vô tình xóa mất file user vừa tạo ra.
- **Empty Directories:** Khi xóa tất cả tệp trong một thư mục (VD: `__pycache__`), cân nhắc xoá luôn thư mục gốc đó (nếu nó trở thành empty).

## 6. Acceptance Criteria
- [ ] Giao diện (Mockup) hiện lên đúng vị trí, áp dụng UI Style V2.
- [ ] Có hiển thị thanh tiến trình (Progress bar) trực quan khi đang Scan.
- [ ] Dung lượng tổng cộng có hiệu ứng đếm số tăng dần và tự động quy đổi đơn vị đúng (KB/MB/GB).
- [ ] Tính năng Default chọn đúng các tệp an toàn để xoá.
- [ ] Nút Scan tính chính xác dung lượng của rác trên đĩa và cập nhật Label.
- [ ] Nút Clean xóa vật lý tệp tin; dung lượng hiển thị báo cáo dọn dẹp khớp hoàn toàn với số liệu Scan trước đó.
- [ ] Khi Clean file đang được ứng dụng mở, app không bị crash.
- [ ] Đầy đủ các key đa ngôn ngữ cho Tiếng Anh và Tiếng Việt.
