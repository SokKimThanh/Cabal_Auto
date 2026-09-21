# Task 8: Tích hợp `Multi-ROI Manager` (Trình quản lý Đa vùng quét)

## Bối cảnh (Context)
Hệ thống Hunt không chỉ nhận diện quái vật, mà còn phải đọc thanh máu bản thân, soi thanh combo, xem bản đồ (minimap). Do đó, cấu hình vùng quét (`region`) không thể chỉ là 1 biến duy nhất, mà phải là một danh sách hoặc thư viện các vùng khác nhau. Cần cung cấp giao diện để người dùng định nghĩa, phân loại và vẽ lại các vùng ROI này (cũng là nền tảng để Bot học và lưu lại vào DB sau này).

## Yêu cầu (Requirements)
1. Thêm một Panel mới hoặc một Nút mở Popup mang tên "Quản lý Vùng Quét (ROI Manager)" trên giao diện cấu hình Hunt.
2. Giao diện này bao gồm một danh sách (List/Treeview) hiển thị các loại ROI cần thiết. Tối thiểu gồm:
   - `hunt_area` (Vùng quét quái)
   - `combo_bar` (Vùng thanh Combo)
   - `self_stats` (Vùng máu/mana của nhân vật)
   - `minimap` (Vùng bản đồ nhỏ)
3. Cạnh mỗi mục trong danh sách, có một nút **[✏️ Vẽ lại]**.
4. Khi bấm "Vẽ lại":
   - Sử dụng class `RegionSelector` (từ `ui/helpers/capture_helper.py`) để làm mờ màn hình và cho phép kéo thả chuột bôi đen khu vực.
   - Khi kéo xong, lưu tọa độ `[left, top, width, height]` tương ứng vào cấu hình `hunt_cfg["rois"]["tên_vùng"]` thay vì ghi đè lên 1 biến chung.
5. Cập nhật `hunt_config.json` để hỗ trợ format JSON mới (dạng Dictionary chứa nhiều ROIs).

## Rủi ro (Risks & Pitfalls)
- **Migration Data:** Vì file `hunt_config.json` cũ có thể đang lưu `region` dưới dạng mảng 1 chiều, khi đọc cấu hình lên, cần viết một đoạn code Migration để tự động chuyển `region` cũ thành `rois.hunt_area` để không làm hỏng file của người dùng cũ.
- **Tương tác Backend:** Phải cập nhật lại các Scanner phía Backend (`HuntOrchestrator`, `CabalComboDetector`) để chúng lấy đúng tọa độ ROI theo Key (VD: lấy ROI `combo_bar` thay vì dùng tọa độ cứng). Tạm thời ở Task này chỉ làm phần UI, Backend sẽ ráp vào sau, nhưng dữ liệu phải được lưu chuẩn chỉ.

## Unit Tests Cần Thêm (Unit Tests to Add)
- Khởi tạo `MultiRoiManager`, giả lập ghi tọa độ cho 2 vùng `hunt_area` và `minimap`. Kiểm tra xem file config xuất ra có chứa node dictionary `"rois"` với 2 keys tương ứng không.