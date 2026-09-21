# Task 8: Tích hợp `Hunt Area Manager` và Cấu trúc lại HUD System Rois

## Bối cảnh (Context)
Hệ thống Hunt không chỉ nhận diện quái vật, mà còn phải đọc thanh máu bản thân, soi thanh combo, xem bản đồ (minimap). Do đó cấu hình vùng quét cần chuyển sang dictionary (`rois`). Tuy nhiên, theo nguyên tắc Separation of Concerns, "Hunt Tab" chỉ nên dùng để cài đặt mục tiêu đi săn, trong khi "HUD" (Combo, HP của mình, Minimap) thuộc về cấu trúc hệ thống (Setup).

## Yêu cầu (Requirements)
1. **Tại Hunt Tab (`MonsterTargetPanel`):** Chỉ thêm nút "Set Hunt Area" (Chọn vùng bãi quái). Nút này mở `RegionSelector` và lưu tọa độ vào `hunt_cfg["rois"]["hunt_area"]`.
2. **Tại Setup/Vision Tab:** Thiết kế bảng `Multi-ROI Manager` cho các System ROIs (`combo_bar`, `self_stats`, `minimap`).
3. Cập nhật hệ thống Backend (HuntOrchestrator) để lấy ROI theo kiến trúc Dict mới.
4. Xây dựng **Validation Layer / Schema** (Kiểm tra Key hợp lệ) ngay khi hàm load config chạy. Nếu gặp file cũ (mảng `region`), tự động viết hàm Migration chuyển sang Dict an toàn, fallback về rỗng nếu lỗi để chống crash (KeyError).

## Rủi ro (Risks & Pitfalls)
- **Data Migration Crash:** Đọc nhầm dữ liệu kiểu mảng bằng Key Dict gây sập ứng dụng. Hàm load_config phải bắt buộc chạy qua validation middleware.

## Unit Tests Cần Thêm (Unit Tests to Add)
- Khởi tạo Validation Layer bằng một file config cũ (`{"region": [0,0,10,10]}`). Đảm bảo Parser xuất ra đúng kiểu dict và không throw error.