# Hướng Dẫn: Hệ Thống Nhận Diện (Vision) và Quét Tự Động (Auto Scanner)

Tài liệu này giải thích cách hoạt động của hệ thống nhận diện hình ảnh và quét tự động trong phần mềm bằng những thuật ngữ đơn giản, giúp bạn dễ dàng hiểu và cài đặt.

---

## 1. Tổng Quan
Hệ thống **Vision (Nhận diện hình ảnh)** đóng vai trò như "đôi mắt" của phần mềm. Nó giúp phần mềm nhìn thấy và hiểu được những gì đang diễn ra trên màn hình game.
Hệ thống **Auto Scanner (Quét tự động)** là quá trình phần mềm sử dụng "đôi mắt" đó để chủ động tìm kiếm các thông tin cần thiết (như quái vật, kỹ năng, thanh máu) và báo cáo lại kết quả cho bạn.

---

## 2. Cách Hệ Thống Nhận Diện (Vision) Hoạt Động
Cách thức phần mềm nhận ra các đối tượng trên màn hình rất đơn giản:
1. **Chụp ảnh:** Phần mềm chụp lại hình ảnh cửa sổ game đang chạy.
2. **So sánh:** Nó đem bức ảnh vừa chụp so sánh với các hình mẫu đã được lưu từ trước (ví dụ: hình dáng của một con quái vật, biểu tượng của một kỹ năng).
3. **Phát hiện:** Nếu tìm thấy phần nào trên màn hình giống với hình mẫu, phần mềm sẽ xác định vị trí của nó (đánh dấu bằng một khung hình chữ nhật).

---

## 3. Thiết Lập Vùng Quét (ROI - Region of Interest)
Thay vì bắt phần mềm phải tìm kiếm trên toàn bộ màn hình rộng lớn (điều này vừa chậm vừa dễ sai sót), chúng ta có thể chỉ định cho nó những **Vùng Quét (ROI)** cụ thể. Bạn khoanh vùng ở đâu, phần mềm chỉ tập trung nhìn vào đó.

Hệ thống quản lý ROI được chia làm 2 phần để dễ sử dụng:

*   **Vùng săn quái (Hunt Area):**
    *   **Nơi cấu hình:** Tab **Hunt**.
    *   **Cách hoạt động:** Khi bạn bấm chọn "Set Hunt Area", màn hình sẽ mờ đi để bạn bôi đen khu vực quái vật thường xuất hiện. Phần mềm sẽ chỉ tìm quái trong ô vuông bạn vừa vẽ.
*   **Vùng hệ thống (System ROI):**
    *   **Nơi cấu hình:** Tab **Setup**.
    *   **Cách hoạt động:** Dùng để cấu hình các khu vực cố định trên giao diện game như: Thanh Combo, Thanh Máu (HP) của bản thân, hoặc Bản đồ nhỏ (Minimap). Bên cạnh mỗi mục sẽ có nút "Vẽ lại" để bạn khoanh vùng tương tự như trên.

---

## 4. Quy Trình Quét Tự Động (Auto Scanner)
Khi bạn nhấn nút quét trên giao diện, phần mềm sẽ thực hiện quy trình ngầm sau:
1. **Kết nối:** Tìm đúng cửa sổ game đang mở.
2. **Thu thập:** Chụp lại hình ảnh màn hình hiện tại.
3. **Phân tích:** Gửi bức ảnh cho hệ thống Vision để tìm kiếm. Lúc này, phần mềm sẽ kết hợp với các **Vùng Quét (ROI)** bạn đã cài đặt để quá trình tìm kiếm nhanh và chính xác hơn.
4. **Lưu trữ:** Tổng hợp các mục tiêu tìm thấy (quái vật, kỹ năng) và lưu kết quả vào cơ sở dữ liệu.

---

## 5. Kết Quả Trả Về Trên Giao Diện (UI)
Sau khi quá trình phân tích hoàn tất, phần mềm sẽ thông báo kết quả cho bạn thông qua 3 cách chính trên giao diện:

### A. Thông Báo Trạng Thái
Ngay lập tức, bạn sẽ thấy trạng thái hiển thị như "Đang quét...", "✅ Quét hoàn tất" hoặc "❌ Lỗi khi quét" kèm theo các biểu tượng trực quan để biết tiến trình đã xong chưa.

### B. Lịch Sử Quét (Scan History)
Mọi kết quả quét thành công sẽ được ghi lại trong bảng Lịch Sử Quét. Tại đây, bạn có thể xem lại thời gian, loại quái vật và các kỹ năng mà phần mềm đã phát hiện được trong những lần quét trước.

### C. Công cụ "Debug Vision" (Xem trực tiếp những gì phần mềm thấy)
Trong quá trình sử dụng, đôi khi phần mềm nhận diện không chuẩn. Tính năng **Debug Vision (Chụp ảnh tức thời)** sinh ra để giúp bạn kiểm tra điều này:
*   Bạn có thể bấm nút **Debug Vision** ở góc giao diện.
*   Một cửa sổ nhỏ sẽ hiện ra, chụp lại hình ảnh game ngay tại thời điểm đó.
*   Trên hình ảnh sẽ có các **khung hình chữ nhật màu xanh** bao quanh những vật thể mà phần mềm nhận ra, kèm theo một **con số độ tin cậy** (ví dụ: Mục tiêu [0.85] nghĩa là phần mềm chắc chắn 85% đây là mục tiêu).
*   Nếu phần mềm khoanh sai hoặc không khoanh gì cả, bạn sẽ biết ngay là mình cần cài đặt lại Vùng Quét (ROI) hoặc cập nhật lại hình mẫu. Nút "Refresh Snapshot" giúp bạn chụp lại một bức ảnh mới ngay tức thì để kiểm tra lại.
