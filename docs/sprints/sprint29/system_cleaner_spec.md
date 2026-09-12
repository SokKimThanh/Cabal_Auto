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
  - **Storage Info (Bên phải):** Một bộ đếm dung lượng khổng lồ với text màu Cyan `#00E5FF` báo cáo "Total scanned size: XX.X MB".
  - **Action Bar (Dưới cùng):**
    - `Default`: Chọn các mục an toàn mặc định (VD: Logs, Temp files, System caches) nhưng chừa lại Backups.
    - `Scan`: Bắt đầu quét thư mục. Cập nhật con số hiển thị.
    - `Clean`: Thực hiện xóa. Chỉ Enable khi kết quả Scan > 0 MB.

- **Translation Keys (i18n):**
  Tất cả text hiển thị cần được tích hợp vào hệ thống i18n của dự án (ví dụ: `system_cleaner_title`, `cleaner_cat_logs`, `btn_scan`, `btn_clean`, `cleaner_success_msg`).

## 4. Architecture & Implementation Guide
Áp dụng mô hình Controller-View-Service hiện tại của dự án.

### 4.1. Core Service (`lib/system/cleanup/cleaner_service.py`)
- Định nghĩa các nhóm rác (`categories`) thông qua từ điển hoặc Enums.
- Sử dụng `pathlib.Path.rglob()` để quét đệ quy các tệp tương ứng.
- **Tính toán:** Phải cộng dồn byte size và trả về cho View (đổi ra MB/GB).
- **Thực thi (Clean):** Dùng `path.unlink()` hoặc `shutil.rmtree()` để xoá file/thư mục. Xử lý Exception (`PermissionError`, `FileNotFoundError`) an toàn bằng `try/except`.

### 4.2. UI View (`ui/views/system_cleaner_frame.py`)
- Tái sử dụng `UI.COLORS` và `UI.FONTS` từ `ui.theme.style_v2`.
- Không khóa giao diện (Non-blocking): Nếu số lượng file rác cực lớn, hàm `Scan` nên được gọi bằng `threading` kết hợp với `.after()` của Tkinter, hoặc hiển thị text `Scanning...` trước khi gọi hàm xử lý đồng bộ.

### 4.3. Controller (`ui/controllers/system_cleaner_controller.py`) (Optional)
- Tuỳ thuộc vào độ phức tạp, có thể đưa logic kết nối View <-> Service ra Controller riêng.
- Phát ra Activity Logs (vd: `[System Cleaner] Freed 15.2 MB`) sau khi người dùng thực hiện lệnh Clean.

## 5. Pitfalls & Notes
- **Permission Errors:** Ứng dụng có thể đang khoá (lock) file log hiện tại (`app_output.log`). Khi dọn dẹp, cần bỏ qua file đang lock thay vì crash toàn bộ hệ thống.
- **Chỉ xóa những gì đã Scan:** Nút "Clean" chỉ được phép xóa các file đã liệt kê từ lần bấm nút "Scan" gần nhất. Không quét lại ngầm lúc bấm Clean để tránh vô tình xóa mất file user vừa tạo ra.
- **Empty Directories:** Khi xóa tất cả tệp trong một thư mục (VD: `__pycache__`), cân nhắc xoá luôn thư mục gốc đó (nếu nó trở thành empty).

## 6. Acceptance Criteria
- [ ] Giao diện (Mockup) hiện lên đúng vị trí, áp dụng UI Style V2.
- [ ] Tính năng Default chọn đúng các tệp an toàn để xoá.
- [ ] Nút Scan tính chính xác số MB của rác trên đĩa và cập nhật Label.
- [ ] Nút Clean xóa vật lý tệp tin và thông báo MessageBox thành công.
- [ ] Khi Clean file đang được ứng dụng mở, app không bị crash.
- [ ] Đầy đủ các key đa ngôn ngữ cho Tiếng Anh và Tiếng Việt.
