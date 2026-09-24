# Hướng Dẫn: Hệ Thống Nhận Diện (Vision) và Quét Tự Động (Auto Scanner)

Tài liệu này giải thích cách hoạt động của hệ thống nhận diện hình ảnh và quét tự động trong phần mềm bằng những thuật ngữ đơn giản, giúp bạn dễ dàng hiểu và cài đặt.

---

## 1. Tổng Quan
Hệ thống **Vision (Nhận diện hình ảnh)** đóng vai trò như "đôi mắt" của phần mềm. Nó giúp phần mềm nhìn thấy và hiểu được những gì đang diễn ra trên màn hình game.
Hệ thống **Auto Scanner (Quét tự động)** là quá trình phần mềm sử dụng "đôi mắt" đó để chủ động tìm kiếm các thông tin cần thiết (như quái vật, kỹ năng, thanh máu) và báo cáo lại kết quả cho bạn.

---

## 2. Cách Hệ Thống Nhận Diện (Vision) Hoạt Động

**Lưu ý về Thư Viện Hình Mẫu (Templates / Monster Editor)**
Để phần mềm biết cần phải tìm cái gì, bạn cần cung cấp cho nó các "bức ảnh gốc".
*   Nếu bạn muốn săn một con quái vật tên "Goblin", bạn dùng tính năng **Monster Manager (Quản lý quái)** để chụp và lưu lại hình dáng của con quái vật đó vào thư viện.
*   Trong quá trình chạy, phần mềm sẽ liên tục lấy bức ảnh "Goblin" trong thư viện ra và dò tìm trên màn hình. Nếu thấy khớp, nó sẽ nhận ra: *"À, đây chính là mục tiêu!"*

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

**Lưu ý quan trọng về Tác dụng của việc khoanh vùng:**
Nhiều người lầm tưởng việc khoanh vùng nhỏ lại sẽ giúp phần mềm "nhìn" quái vật rõ hơn, nhưng thực tế không phải vậy. Việc khoanh vùng mang lại 2 lợi ích chính:
*   **Tránh nhận diện nhầm (Giảm nhiễu):** Giúp phần mềm không bị nhầm lẫn với các biểu tượng, khung chat hay kỹ năng có màu sắc/hình dáng giống với quái vật ở các khu vực khác trên màn hình.
*   **Tăng tốc độ xử lý:** Tìm kiếm trong một ô nhỏ chắc chắn sẽ nhanh hơn rất nhiều so với việc quét toàn bộ màn hình.
*   Tuy nhiên, **khoanh vùng KHÔNG làm tăng độ chính xác (độ giống nhau) của thuật toán**. Để phần mềm nhận diện đúng quái vật, điều quan trọng nhất là bạn phải chụp **hình mẫu (template) trong thư viện** thật rõ nét và chuẩn xác.

**Làm thế nào để có ROI Tự Động?**
Ngoài việc vẽ tay thủ công, phần mềm có khả năng tự động thiết lập một số vùng quét thông qua **Auto Scanner**:
*   Khi bạn chạy tính năng Quét toàn màn hình, phần mềm sẽ dùng bộ nhận diện để quét qua toàn bộ cửa sổ game một lần.
*   Nếu nó nhận diện được các đặc điểm cố định (như hình dáng thanh máu chung của quái vật, hình dạng ô kỹ năng), nó sẽ ghi nhận lại tọa độ [X, Y, Rộng, Cao] của những vị trí đó.
*   Từ dữ liệu này, phần mềm có thể gợi ý hoặc tự động điền các Vùng Quét (ROI) vào cấu hình mà không cần bạn phải tự tay khoanh vùng.

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
