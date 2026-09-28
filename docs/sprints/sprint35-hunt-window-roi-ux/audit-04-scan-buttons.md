# Audit 04: Đặc tả hành vi 4 nút Scan (ROI)

## Tổng quan
Tài liệu này xác định mục đích, đầu vào, đầu ra và cơ chế validation của 4 nút Scan ROI hiện có trong ứng dụng: `setup_roi.combo_bar`, `setup_roi.self_stats`, `setup_roi.minimap`, và `hunt_area.set`.

## Đặc tả từng nút

### 1. `setup_roi.combo_bar`
- **Quét cái gì?** Thanh kỹ năng (combo bar / quick slot) của nhân vật.
- **Dữ liệu đọc là gì?** Các template icon của skill.
- **ROI yêu cầu chứa thành phần UI nào của game?** Khung chứa các kỹ năng đang dùng để bắt cooldown / availability.
- **Đầu ra là gì?** Tọa độ mảng 4 số `[x, y, w, h]` lưu vào `hunt_config["rois"]["combo_bar"]`.
- **Đi đến panel nào?** System ROI Manager trong Setup Tab (`setup_tab.py`).
- **Có validation không?** Không có validation tại thời điểm vẽ (chỉ kiểm tra `if region`). Khi gọi sử dụng (`scanner.py`), chỉ kiểm tra độ dài mảng `len == 4`.
- **Có chặn dữ liệu bất thường không?** Không chặn người dùng vẽ sai vùng hoặc vùng rỗng (width/height = 0).

### 2. `setup_roi.self_stats`
- **Quét cái gì?** Chỉ số sinh tồn của nhân vật (HP/MP).
- **Dữ liệu đọc là gì?** **UNKNOWN** (Không tìm thấy implement logic xử lý `self_stats` trong codebase. Technical debt).
- **ROI yêu cầu chứa thành phần UI nào của game?** Thanh máu (HP) và năng lượng (MP/SP) của người chơi.
- **Đầu ra là gì?** Tọa độ `[x, y, w, h]` lưu vào `hunt_config["rois"]["self_stats"]`.
- **Đi đến panel nào?** System ROI Manager trong Setup Tab.
- **Có validation không?** Không.
- **Có chặn dữ liệu bất thường không?** Không.

### 3. `setup_roi.minimap`
- **Quét cái gì?** Bản đồ nhỏ.
- **Dữ liệu đọc là gì?** **UNKNOWN** (Chưa có tính năng đọc hay sử dụng `minimap` trong codebase. Technical debt).
- **ROI yêu cầu chứa thành phần UI nào của game?** Minimap ở góc màn hình.
- **Đầu ra là gì?** Tọa độ `[x, y, w, h]` lưu vào `hunt_config["rois"]["minimap"]`.
- **Đi đến panel nào?** System ROI Manager trong Setup Tab.
- **Có validation không?** Không.
- **Có chặn dữ liệu bất thường không?** Không.

### 4. `hunt_area.set`
- **Quét cái gì?** Vùng xuất hiện của quái vật.
- **Dữ liệu đọc là gì?** Monster templates, Monster HP bars.
- **ROI yêu cầu chứa thành phần UI nào của game?** Khu vực chiến đấu 3D (loại trừ các thành phần UI xung quanh để tối ưu tốc độ match template).
- **Đầu ra là gì?** Tọa độ `[x, y, w, h]` lưu vào `hunt_config["rois"]["hunt_area"]`.
- **Đi đến panel nào?** Monster Target Panel trong Hunt Tab (`hunt_tab.py`). Nút chỉ lưu dữ liệu chứ không hiển thị tọa độ cụ thể trên panel này.
- **Có validation không?** Ở UI vẽ chỉ kiểm tra `if region`. Khi đọc config ở `scanner.py` có kiểm tra `len(rois["hunt_area"]) == 4`.
- **Có chặn dữ liệu bất thường không?** Không có cơ chế chặn user vẽ vùng sai/nhỏ/lớn bất thường ở cấp độ UI.

---

## Bảng tổng hợp

| Nút | Mục đích | Dữ liệu đọc | ROI yêu cầu | Đầu ra | Panel nhận | Validation |
|---|---|---|---|---|---|---|
| **combo_bar** | Quét thanh kỹ năng | Skill icons | Thanh kỹ năng | `[x, y, w, h]` | Setup Tab | Không (chỉ lúc dùng) |
| **self_stats** | Quét HP/MP người chơi | UNKNOWN | Thanh máu nhân vật | `[x, y, w, h]` | Setup Tab | Không |
| **minimap** | Quét bản đồ | UNKNOWN | Minimap góc màn hình | `[x, y, w, h]` | Setup Tab | Không |
| **hunt_area** | Quét quái vật | Monster templates | Vùng chiến đấu 3D | `[x, y, w, h]` | Hunt Tab | Không (chỉ lúc dùng) |

---

## Technical Debt (Danh sách ô "UNKNOWN")
- Dữ liệu đọc cho `self_stats`: Nút được khai báo trên UI nhưng hoàn toàn thiếu implementation (luồng đọc giá trị máu/mana).
- Dữ liệu đọc cho `minimap`: Chưa có implementation cho vision engine quét `minimap`.
- Cả 4 nút đều thiếu validation tại thời điểm thiết lập tọa độ ở cấp độ UI.
