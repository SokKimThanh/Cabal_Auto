# Prompt 04: File Management & Logic Fallback cho Icon

## Mục tiêu
Xây dựng module quản lý tập tin (sao chép, di chuyển, xóa) ảnh và viết logic kiểm tra cấp độ ưu tiên (Fallback Priority) để quyết định hiển thị `.png`, `.ico` hay `emoji` như mô tả trong phần 3 và 7 của Đặc tả.

## Ngữ cảnh & Yêu cầu từ Đặc tả
- **Quản lý file:** Khi người dùng chọn file ảnh từ máy, tự động copy vào thư mục `assets/images/icon/`.
- **Cơ chế Fallback:** `png` -> `ico` -> `fallback_emoji`.
- **Đánh giá trạng thái:** Phải cung cấp hàm kiểm tra và trả về mã màu (Xanh, Vàng, Đỏ) dựa trên sự tồn tại của file và khai báo DB.

## Các bước triển khai chi tiết dành cho Người/AI

### Bước 1: Viết module IconFileManager (Sao chép / Xóa file)
- **Vị trí:** Tạo file `lib/managers/icon_file_manager.py` (hoặc đặt trong helper).
- **Hành động:**
  - Viết hàm `import_icon_file(source_path: str, target_filename: str = None) -> str`:
    - Nhận vào đường dẫn file gốc.
    - Nếu không cấp `target_filename`, lấy tên file từ `source_path`.
    - Sử dụng `shutil.copy2` để copy file vào thư mục `assets/images/icon/`.
    - Trả về tên file mới được lưu.
  - Viết hàm `delete_icon_file(filename: str) -> bool`:
    - Kiểm tra `os.path.exists`. Nếu có, dùng `os.remove` để xóa file để tránh rác hệ thống (xử lý Orphaned Files ở mức cơ bản). Trả về True/False.

### Bước 2: Viết logic Fallback Priority (Render)
- **Vị trí:** Tích hợp vào `IconHelper` hiện tại (VD: `ui/helpers/icon_helper.py`) hoặc tạo service mới `IconRenderer`.
- **Hành động:**
  - Sửa hoặc thêm hàm `resolve_icon_display(icon_data: Dict) -> Tuple[str, str, bool]`:
    - (Đầu ra VD: Tuple gồm `(đường_dẫn_thực_tế, loại_resource, thành_công)`)
    - **Ưu tiên 1:** Lấy `icon_data['filepath']`, đổi đuôi thành `.png`, kiểm tra tồn tại. Nếu có -> Trả về path `.png`.
    - **Ưu tiên 2:** Đổi đuôi thành `.ico`, kiểm tra tồn tại. Nếu có -> Trả về path `.ico`.
    - **Ưu tiên 3:** Trả về `icon_data['fallback_emoji']` và cờ báo hiệu đây là text, không phải image path.

### Bước 3: Viết logic tính toán Trạng Thái (Status)
- **Hành động:** Viết hàm `evaluate_icon_status(icon_data: Dict) -> str`:
  - Trả về `"GREEN"` nếu: Có `filepath` VÀ file vật lý thực sự tồn tại (dùng logic ở Bước 2 để check).
  - Trả về `"YELLOW"` nếu: `filepath` rỗng/null, nhưng có `fallback_emoji`. (Chủ ý dùng Fallback).
  - Trả về `"RED"` nếu: Có `filepath` NHƯNG file không tồn tại, phải ép dùng Emoji.

### Bước 4: Viết Unit Test cho File Manager & Fallback
- **Vị trí:** Tạo file `tests/unit/test_icon_file_manager.py`.
- **Hành động:**
  - Dùng `tmp_path` (nếu dùng Pytest) hoặc module `tempfile` để tạo các file giả (.png, .ico).
  - Test `import_icon_file` xem file có được copy thành công vào thư mục đích không.
  - Test `resolve_icon_display` theo đúng thứ tự 3 cấp độ (có png -> ưu tiên png; xóa png -> rớt xuống ico; xóa cả 2 -> rớt xuống emoji).
  - Test `evaluate_icon_status` trả về đúng GREEN/YELLOW/RED với các bộ dữ liệu khác nhau.

## Tiêu chí hoàn thành (Definition of Done)
- [ ] Hàm copy file hoạt động ổn định, bắt lỗi an toàn (VD: thư mục đích không tồn tại).
- [ ] Logic Fallback tuân thủ tuyệt đối quy tắc `.png` > `.ico` > `emoji`.
- [ ] Bộ tính toán trạng thái (Status) hoạt động chính xác.
- [ ] Chạy Unit Test Pass.

## Thời gian dự kiến: ~25-30 phút
