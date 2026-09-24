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

## 4. Kết Luận & Đề Xuất (Next Steps)

Hệ thống Quét (Scan) và Vision cơ bản **đã hoàn thành khung sườn (skeleton)** và hoạt động tốt đối với tính năng Auto Detect Template và phát hiện Quái vật (Monster Detection). Tuy nhiên, để hoàn thiện toàn bộ và đáp ứng kỳ vọng liên kết hiển thị kết quả trên màn hình:

1. **Về Quái Vật:** Đã liên kết ổn. Cần đảm bảo UI nhận được danh sách ưu tiên từ `RuntimeMonsterQueue` (thông qua `get_attack_queue`) và render nó mượt mà (có thể dùng Treeview theo quy tắc chống lag UI).
2. **Về Skill & Cooldown:** Cần bổ sung pipeline nhận diện icon skill và trạng thái cooldown vào quá trình `run_scan()`.
3. **Về Combo:** Cần tách một luồng (thread) xử lý Vision độc lập với tần số cao hơn (khoảng 30-60 FPS) chỉ dành riêng cho việc crop và đọc màu của thanh Combo Bar. Luồng này nên bắn Event trực tiếp thay vì xếp hàng đợi như quái vật.

*Báo cáo được tạo bởi Jules trong Sprint 24.*