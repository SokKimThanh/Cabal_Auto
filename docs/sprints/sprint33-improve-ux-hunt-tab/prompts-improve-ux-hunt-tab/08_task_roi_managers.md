# Task 8: Tích hợp `Hunt Area Manager` và Cấu trúc lại HUD System Rois

## Bối cảnh (Context)
Hệ thống Hunt không chỉ nhận diện quái vật, mà còn phải đọc thanh máu bản thân, soi thanh combo, xem bản đồ (minimap). Do đó cấu hình vùng quét cần chuyển sang dictionary (`rois`). Tuy nhiên, theo nguyên tắc Separation of Concerns, "Hunt Tab" chỉ nên dùng để cài đặt mục tiêu đi săn, trong khi "HUD" (Combo, HP của mình, Minimap) thuộc về cấu trúc hệ thống (Setup).

## Yêu cầu (Requirements)

### Task 8a: Hunt Area Manager (Chỉ thực hiện ở Hunt Tab)
1. **Tại `ui/panels/monster_target_panel.py`**: Thêm nút "Set Hunt Area" (Chọn vùng bãi quái). Nút này mở `RegionSelector` (từ `ui/helpers/capture_helper.py`) để làm mờ màn hình và bôi đen khu vực.
2. Lưu tọa độ `[left, top, width, height]` thu được vào cấu hình `hunt_cfg["rois"]["hunt_area"]`.
3. Ghi đè file bằng Atomic Write (xem Phụ lục).

### Task 8b: System ROI Manager (Chỉ thực hiện ở Setup Tab)
1. **Tại `ui/tabs/setup_tab.py`**: Thiết lập một bảng hoặc một danh sách cấu hình có tên `System ROI Manager`.
2. Danh sách này bao gồm cấu hình cho các hệ thống: `combo_bar`, `self_stats`, `minimap`.
3. Có một nút "Vẽ lại" bên cạnh mỗi hệ thống để gọi `RegionSelector`.
4. Lưu tọa độ vào các key tương ứng trong `hunt_cfg["rois"]`.

## Rủi ro (Risks & Pitfalls)
- **Data Migration Crash:** Đọc nhầm dữ liệu kiểu mảng bằng Key Dict gây sập ứng dụng. Hàm load_config phải bắt buộc chạy qua validation middleware.

## Unit Tests Cần Thêm (Unit Tests to Add)
- Khởi tạo Validation Layer bằng một file config cũ (`{"region": [0,0,10,10]}`). Đảm bảo Parser xuất ra đúng kiểu dict và không throw error.

## Hướng dẫn trả Nợ Kỹ Thuật (Technical Debt Paydown)
- **Bảo hiểm Dữ liệu (Schema Validation):** File `hunt_config.json` phải được validate bằng thư viện `pydantic`. Nếu migration lỗi, BẮT BUỘC phải viết mã khôi phục tự động (Auto-restore) file `.bak` về lại file gốc!
- **Lỗi 0 byte JSON (Atomic Write):** Khi lưu tọa độ vùng vẽ mới vào `hunt_config.json`, tuyệt đối không ghi đè trực tiếp. Bạn phải ghi ra file `hunt_config.tmp`, sau đó dùng `os.replace` để đổi tên nhằm tránh lỗi rỗng file khi luồng ngầm đang đọc đồng thời (Race condition file I/O).
- **i18n Hardcode:** Các Text "Quản lý Vùng Quét", "Vẽ lại", "Set Hunt Area" phải được khai báo key đa ngôn ngữ, không dùng chữ tiếng Việt cứng trong code.
