# Session 3: Xây dựng UI Combobox Chọn Class trên SkillPanel

## 1. Tiêu đề & Mục tiêu
- **Tiêu đề:** Tích hợp UI Combobox chọn Class vào giao diện.
- **Mục tiêu:** Hiển thị dropdown cho người dùng chọn class chủ động, liên kết với AppState, và đảm bảo làm mới giao diện không bị giật lag (Flickering). Task này cần hoàn thành dưới 30 phút.

## 2. Ngữ cảnh (Context)
Dựa theo tài liệu đặc tả:
> Giao diện: Thêm `ttk.Combobox` trên thanh tiêu đề của `SkillPanel` với nhãn "Class:".
> Sự kiện onChange: Gọi `app_state.set_current_class(new_id)`, dọn dẹp kỹ năng "mồ côi".
> Rủi ro (Pitfalls): Xử lý kỹ năng "mồ côi" (làm sạch lane) và Trải nghiệm giật nháy (UI Flickering - chỉ xóa và cập nhật `values` của Combobox, không destroy/tạo lại widget).

## 3. Các file cần thay đổi
1. `ui/panels/skill_panel.py`

## 4. Hướng dẫn thực hiện chi tiết

### 4.1. Khởi tạo Widget trên UI
- Trong hàm `_build()` hoặc hàm khởi tạo top-bar của `SkillPanel`.
- Tạo một `Frame` nhỏ chứa `Label` (dùng `t("lbl_class_select")`) và một `ttk.Combobox`.
- Giao diện sử dụng `UIStyleV2` thay vì style cứng (nếu dự án áp dụng).

### 4.2. Nạp dữ liệu vào Combobox
- Gọi `ClassService.get_all_classes()` (đã làm ở Session 1).
- Format dữ liệu thành danh sách string: `"{id} - {name}"`.
- Đưa vào thuộc tính `values` của Combobox.
- Đặt giá trị mặc định dựa trên `self.app_state.root._current_class_id`.

### 4.3. Xử lý Sự kiện OnChange
- Bind sự kiện `<<ComboboxSelected>>` cho combobox.
- Trong hàm callback `_on_class_selected(event)`:
  - Lấy chuỗi được chọn, parse ra `class_id` bằng lệnh `split(" - ")[0]`.
  - Gọi `success = self.app_state.set_current_class(class_id)`.
  - Nếu `success == False` (người dùng huỷ vì unsaved changes): Set lại combobox về giá trị cũ (cần lưu giá trị trước đó vào một biến nội bộ).
  - Nếu `success == True`:
    - Gọi hàm dọn dẹp các kỹ năng đang gắn trên các slots (lanes) nếu chúng không thuộc class mới.
    - Gọi logic cập nhật lại tập data của các dropdown skill nhỏ bên dưới. **QUAN TRỌNG:** Chỉ ghi đè thuộc tính `.configure(values=...)`, KHÔNG destroy và vẽ lại toàn bộ các panel con để tránh UI flickering.

## 5. Tiêu chí Hoàn thành (Acceptance Criteria / Verification)
1. Giao diện SkillPanel hiển thị đúng combobox trên đầu.
2. Thả xuống thấy danh sách class (ví dụ: `1 - Blader`, `2 - Wizard`).
3. Chọn class mới, các ô kỹ năng tự động load đúng danh sách skill của class đó mà màn hình không bị nhấp nháy mạnh.
4. Nếu từ chối đổi (tại dialog unsaved), giá trị của combobox trả về như cũ.
