# Báo Cáo Đánh Giá: Mức Độ Hoàn Thiện và Liên Kết Của Hệ Thống Quét (Scan) và Thị Giác (Vision)

## 1. Tổng Quan
Báo cáo này đánh giá mức độ hoàn thiện của hệ thống Vision và Scan trong Cabal Auto, đặc biệt tập trung vào khả năng nhận diện, phân tích và luân chuyển dữ liệu liên quan đến **Quái vật (Monsters)**, **Kỹ năng (Skills)**, và **Chuỗi Combo (Combo Trips)** khi trả về kết quả hiển thị trên màn hình.

## 2. Hệ Thống Vision và Quét (Scan)
Hệ thống hiện tại sử dụng `VisionEngine` kết hợp với `AutoScanner` và `ScanController` để phân tích khung hình (frame) nhận được từ màn hình game.

### **2.1. Ưu điểm hiện tại:**
- **Capture tự động (Auto Capture):** Đã sửa lỗi phím tắt `Ctrl+Shift+T` chụp nhầm giao diện Bot. `WindowManager` giờ đây xác định chính xác cửa sổ game đang active để kích hoạt `VisionAddTemplateEvent`.
- **Trích xuất dữ liệu mượt mà:** `ScanController` hiện tại xử lý đa luồng (threading) tốt, tự động trích xuất các template kích thước 100x100 xung quanh trung tâm màn hình, và tự động thu nhỏ lại (thumbnail) một cách hiệu quả để giảm tải hiển thị lên UI.

### **2.2. Điểm cần cải thiện:**
- Hiện tại, `ScanController` mới chỉ tập trung trích xuất *template patches* (lưu mẫu hình ảnh tự động) từ `frame` để chuyển cho `TemplateStorageManager`. Nó chưa kết nối trực tiếp với kết quả trả về của hệ thống **Skills** hay **Combo** lên UI thông qua `ScanController.run_scan()`.

---

## 3. Đánh Giá Mức Độ Liên Kết Các Hệ Thống

### **3.1. Hệ thống Quái Vật (Monsters)**
**Mức độ hoàn thiện: Tốt (70%)**
- **Liên kết Vision & Monster DB:** File `scene_monster_detector.py` thể hiện rõ sự gắn kết. Nó dùng `VisionEngine.detect_monster_pipeline` để đối chiếu template. Khi tìm thấy, nó truy xuất cơ sở dữ liệu (`get_monster_by_id_api`) thông qua bộ nhớ đệm (cache) để lấy thông tin chi tiết.
- **Quản lý Hàng Đợi (RuntimeMonsterQueue):** Hệ thống có cơ chế hàng đợi rất mạnh (`runtime_monster_queue.py`). Nó tính toán IOU (Intersection over Union) và khoảng cách vị trí để chống trùng lặp nhận diện (deduplication), đồng thời sắp xếp ưu tiên theo độ chính xác (confidence).
- **Điểm yếu:** Sự kiện trả về (publish callback) từ `RuntimeMonsterQueue` lên UI cần phải đảm bảo không đẩy trực tiếp object nặng. Hiện tại, nó chỉ trả về snapshot định kỳ.

### **3.2. Hệ thống Kỹ Năng (Skills)**
**Mức độ hoàn thiện: Trung bình (40%)**
- **Phân tích:** Các hàm phát hiện skill và trạng thái hồi chiêu (cooldown) chưa được tích hợp chặt chẽ vào vòng lặp của `scene_monster_detector.py` hoặc `scan_controller.py`.
- **Thiếu sót:** `VisionEngine` có thể đã có hàm nhận diện thanh HP/MP hoặc Cooldown, nhưng kết quả này chưa được gộp chung vào payload của kết quả Scan (`results["skills"]`) để hiển thị ở `show_results`.

### **3.3. Hệ thống Chuỗi Combo (Combo Trips)**
**Mức độ hoàn thiện: Yếu (20%)**
- **Phân tích:** Chuỗi combo đòi hỏi việc nhận diện thanh bar combo cực kỳ nhanh và chính xác. Hàng đợi quái vật (Monster Queue) tối đa cập nhật 5 FPS (0.2s/lần), điều này là tốt đối với quái vật nhưng **quá chậm** để nhận diện timing của thanh Combo.
- **Thiếu sót:** Chưa thấy luồng dữ liệu (Data Pipeline) nào trích xuất trực tiếp thông tin thanh Combo (combo gauge timing) để gửi qua `EventBus` hoặc `ScanController`.

---

## 4. Kết Luận & Đề Xuất Khắc Phục Chi Tiết (Remediation Plan)

Hệ thống Quét (Scan) và Vision cơ bản **đã hoàn thành khung sườn (skeleton)** và hoạt động tốt đối với tính năng Auto Detect Template và phát hiện Quái vật (Monster Detection). Tuy nhiên, để hoàn thiện toàn bộ và đáp ứng kỳ vọng liên kết hiển thị kết quả trên màn hình, dưới đây là mô tả khắc phục chi tiết cho từng phần:

### 4.1. Khắc Phục Liên Kết Hệ Thống Quái Vật (Monster)
- **Vấn đề:** Dữ liệu quái vật đã được đưa vào `RuntimeMonsterQueue` nhưng cần được hiển thị mượt mà trên giao diện (UI) mà không gây tắc nghẽn main thread của Tkinter.
- **Giải pháp:**
  1. Thay vì sử dụng vòng lặp `while` hoặc `time.sleep` trên UI, tạo một phương thức `update_monster_list()` trong file controller của UI.
  2. Sử dụng `EventBus` để lắng nghe sự kiện `MonsterQueueSnapshotEvent`. Tuy nhiên, chỉ truyền các ID và tọa độ cơ bản.
  3. Trên UI (Tkinter), sử dụng `ttk.Treeview` để render danh sách quái vật. Chỉ gọi lệnh `item(..., values=...)` để cập nhật các cột (Tên, Máu, Khoảng cách) thay vì xóa và tạo lại toàn bộ row để tránh giật lag (flicker).

### 4.2. Khắc Phục Hệ Thống Kỹ Năng (Skills & Cooldown)
- **Vấn đề:** Kết quả quét (scan) chưa bao gồm dữ liệu skill và cooldown để trả về `ScanController`.
- **Giải pháp:**
  1. Trong `VisionEngine`, tạo thêm phương thức `detect_skills_pipeline(frame)`. Phương thức này sẽ cắt nhỏ (crop) các vùng tĩnh (ROI - Region of Interest) đã được cấu hình sẵn cho thanh kỹ năng ở dưới đáy màn hình.
  2. Sử dụng OpenCV (`cv2.matchTemplate` hoặc dò tìm màu xám `grayscale`) để nhận diện trạng thái hồi chiêu (skill đang sáng hay đang bị mờ/đen).
  3. Trong `ScanController.run_scan()`, gọi `detect_skills_pipeline(frame)` ngay sau khi quét quái vật, và gộp kết quả vào biến `results` (ví dụ: `results['skills_ready'] = [1, 2, 4]`).
  4. Trả kết quả này về UI thông qua hàm `show_results(results)` để UI có thể sáng/tối các nút kỹ năng tương ứng.

### 4.3. Khắc Phục Hệ Thống Chuỗi Combo (Combo Trips)
- **Vấn đề:** Tần số quét 5 FPS của `RuntimeMonsterQueue` quá chậm để bắt đúng nhịp (timing) của thanh Combo (thường yêu cầu độ trễ dưới 50ms).
- **Giải pháp:**
  1. **Tách Luồng Độc Lập:** Tạo một Worker Thread riêng biệt có tên `ComboVisionThread`. Luồng này không chạy chung với luồng tìm quái vật.
  2. **Crop Cực Nhỏ:** `ComboVisionThread` chỉ yêu cầu hệ thống chụp (capture) một vùng ảnh cực kỳ nhỏ (ví dụ 200x20 pixels) ngay tại vị trí thanh Combo. Kích thước ảnh nhỏ giúp đẩy tốc độ xử lý lên 60 FPS mà không ngốn CPU.
  3. **Nhận Diện Pixel/Màu Sắc:** Thay vì dùng Template Matching nặng nề, chỉ cần dò tìm một dải màu (Ví dụ: màu vàng sáng/đỏ rực) chạy ngang qua thanh Combo. Khi dải màu chạm đến tọa độ điểm "Perfect" hoặc "Excellent", lập tức kích hoạt sự kiện.
  4. **Bắn Sự Kiện Khẩn Cấp:** Sử dụng `EventBus.trigger(ComboTimingEvent(status="PERFECT"))`. Hệ thống điều khiển bàn phím (Keyboard/Mouse Controller) sẽ lắng nghe event này và lập tức gửi phím nhấn skill tiếp theo mà không cần thông qua UI.

*Báo cáo được cập nhật bởi Jules trong Sprint 24.*