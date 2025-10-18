# Hướng Dẫn: Advanced Window Settings (Cài Đặt Nâng Cao Cửa Sổ)

**Date:** October 18, 2025
**Target Users:** Advanced users
**Location:** Setup Tab → Advanced Window Settings (chỉ hiện khi mode = Advanced)

---

## Tổng Quan

**Advanced Window Settings** là phần cài đặt dành cho người dùng nâng cao, giúp **tối ưu hiệu suất** và **tùy chỉnh vùng tìm kiếm** khi hunt.

---

## Khi Nào Cần Dùng?

### ✅ Nên Dùng Khi:
1. **Game chạy chậm hoặc giật lag** → Giới hạn vùng tìm kiếm để tăng FPS
2. **Monster xuất hiện ở vị trí cố định** → Chỉ tìm kiếm trong khu vực nhỏ
3. **Nhiều object giống nhau trên màn hình** → Tránh nhầm lẫn bằng cách thu hẹp vùng
4. **Muốn tối ưu hiệu suất CPU** → Region nhỏ = ít pixel cần xử lý

### ❌ KHÔNG Cần Dùng Khi:
1. **Bạn là người mới** → Dùng mode Beginner/Intermediate là đủ
2. **Game chạy mượt** → Không cần tối ưu thêm
3. **Monster di chuyển khắp màn hình** → Region cố định sẽ miss target

---

## Các Thiết Lập Trong Section

### 1️⃣ Template Path (Đường dẫn template)

**Chức năng:** Chỉ định file ảnh template để OpenCV nhận diện monster.

**Cách dùng:**
```
Template: assets/images/monsters/coc_go__capture_1760736387994.png
[Browse]
```

**Giải thích:**
- Template là ảnh **chụp từ màn hình game** (monster frame, HP bar, icon...)
- OpenCV sẽ **so khớp template** với màn hình để tìm monster
- Click **Browse** để chọn ảnh khác (PNG, JPG)

**Lưu ý:**
- ⚠️ Template phải **rõ nét**, không bị mờ
- ⚠️ Kích thước **không quá nhỏ** (< 20x20 pixel) hoặc **quá lớn** (> 500x500)
- ✅ Best practice: Chụp ảnh monster frame khoảng 100x100 → 200x200 pixel

---

### 2️⃣ Region (Vùng tìm kiếm)

**Chức năng:** Giới hạn vùng tìm kiếm monster trên màn hình.

**Cấu trúc:**
```
Region:  [L] 1074   T: [456]   W: [204]   H: [217]
         ^^^         ^^^        ^^^        ^^^
         Left        Top        Width      Height
```

**Giải thích:**
- **L (Left)**: Tọa độ X bên trái vùng tìm kiếm (pixel từ mép trái màn hình)
- **T (Top)**: Tọa độ Y phía trên vùng tìm kiếm (pixel từ mép trên màn hình)
- **W (Width)**: Chiều rộng vùng tìm kiếm
- **H (Height)**: Chiều cao vùng tìm kiếm

**Ví dụ thực tế:**

#### Scenario 1: Monster ở góc phải dưới màn hình
```
Màn hình 1920x1080
Monster thường xuất hiện ở góc phải dưới (x: 1500-1800, y: 800-1000)

Thiết lập:
L: 1500
T: 800
W: 300  (1500 + 300 = 1800)
H: 200  (800 + 200 = 1000)
```

**Lợi ích:**
- Không tìm kiếm toàn bộ màn hình 1920x1080 (2,073,600 pixels)
- Chỉ tìm trong vùng 300x200 (60,000 pixels) → **Nhanh hơn 34 lần!**

#### Scenario 2: Monster ở giữa màn hình
```
Màn hình 1920x1080
Monster ở trung tâm (x: 800-1120, y: 400-680)

Thiết lập:
L: 800
T: 400
W: 320
H: 280
```

**Khi nào để trống (empty)?**
- Region = [empty] → Tìm kiếm **toàn bộ màn hình**
- Dùng khi: Monster di chuyển không theo pattern cố định

---

### 3️⃣ Window Bounds (Giới hạn cửa sổ)

**Chức năng:** Lưu vị trí và kích thước cửa sổ game để tối ưu bring-to-front.

**Hiển thị:**
```
Window Bounds: (100, 50) 1920x1080  [Clear Bounds]
               ^^^^^^^^^ ^^^^^^^^^^
               Vị trí    Kích thước
               (x, y)    (width x height)
```

**Cách hoạt động:**

1. **Lần đầu chọn window** (trong Hunt tab topbar):
   - App tự động lưu vị trí và kích thước cửa sổ game
   - Ví dụ: Cửa sổ game ở tọa độ (100, 50), size 1920x1080

2. **Khi click "Bring Window to Front"**:
   - Thay vì tìm kiếm window mỗi lần (chậm)
   - App dùng cached bounds để **đưa window lên ngay lập tức** (nhanh)

3. **Click "Clear Bounds"**:
   - Xóa cached bounds
   - Lần bring-to-front tiếp theo sẽ tìm lại window và cache mới

**Khi nào cần Clear Bounds?**
- ✅ Khi bạn **di chuyển cửa sổ game** sang vị trí khác
- ✅ Khi bạn **resize cửa sổ game**
- ✅ Khi bring-to-front **không hoạt động đúng**

---

## So Sánh: Có Region vs Không có Region

### Tình Huống: Tìm monster trên màn hình 1920x1080

| Cấu hình | Pixels cần xử lý | Tốc độ (ước tính) | CPU Usage |
|----------|------------------|-------------------|-----------|
| **Full screen** (no region) | 2,073,600 | ~30 FPS | Cao |
| **Region 500x500** | 250,000 | ~120 FPS | Trung bình |
| **Region 200x200** | 40,000 | ~200+ FPS | Thấp |

**Kết luận:**
- Region nhỏ hơn = Nhanh hơn + Ít CPU hơn
- Nhưng: Region quá nhỏ = Dễ miss monster nếu nó di chuyển ra ngoài

---

## Workflow Cài Đặt Region (Hướng Dẫn Chi Tiết)

### Bước 1: Xác định vùng monster xuất hiện

1. **Chạy game và đứng ở hunting spot**
2. **Quan sát vị trí monster xuất hiện**:
   - Monster luôn spawn ở góc nào?
   - Di chuyển trong khu vực nào?
   - Có pattern cố định không?

### Bước 2: Chụp screenshot để đo pixel

**Cách 1: Dùng Paint/Photoshop**
```
1. Chụp screenshot màn hình game (PrtScn)
2. Mở Paint, paste screenshot
3. Dùng Select tool, chọn vùng monster thường xuất hiện
4. Nhìn vào status bar Paint → Xem tọa độ & size
   Ví dụ: "1074, 456 - 1278, 673" → L=1074, T=456, W=204, H=217
```

**Cách 2: Dùng Windows Snipping Tool**
```
1. Win + Shift + S
2. Chọn vùng monster
3. Nhìn vào dimensions hiển thị
```

**Cách 3: Dùng code Python (cho dev)**
```python
import pyautogui
# Di chuột đến góc trái trên vùng monster, xem tọa độ
print(pyautogui.position())  # Ví dụ: (1074, 456)

# Di chuột đến góc phải dưới vùng monster
print(pyautogui.position())  # Ví dụ: (1278, 673)

# Tính toán:
# L = 1074
# T = 456
# W = 1278 - 1074 = 204
# H = 673 - 456 = 217
```

### Bước 3: Nhập vào Setup tab

```
Setup tab → Advanced Window Settings (chỉ hiện ở mode Advanced)

Region:
L: 1074
T: 456
W: 204
H: 217

[Apply Settings]
```

### Bước 4: Test và điều chỉnh

1. **Bắt đầu hunt** → Xem bot có tìm thấy monster không
2. **Nếu miss monster**:
   - Tăng W và H (mở rộng vùng)
   - Hoặc xóa region (để trống) để tìm toàn màn hình
3. **Nếu chậm/lag**:
   - Giảm W và H (thu hẹp vùng)

---

## Best Practices (Thực Hành Tốt Nhất)

### ✅ Nên Làm

1. **Bắt đầu với full screen (no region)**:
   ```
   L: [empty]
   T: [empty]
   W: [empty]
   H: [empty]
   ```
   → Chạy vài phút để xác nhận bot hoạt động

2. **Sau đó thu hẹp dần**:
   - Quan sát vùng monster xuất hiện
   - Đặt region rộng hơn 20-30% so với vùng thực tế
   - Ví dụ: Monster trong 200x200 → Đặt region 260x260

3. **Kiểm tra định kỳ**:
   - Khi game update map/monster
   - Khi đổi hunting spot
   - Khi thấy bot miss monster

### ❌ Tránh Làm

1. **Đừng đặt region quá chặt**:
   ```
   ❌ Monster 200x200, đặt region 200x200
   ✅ Monster 200x200, đặt region 260x260 (buffer 30%)
   ```

2. **Đừng dùng region khi monster di chuyển random**:
   - Một số game monster spawn random khắp màn hình
   - Dùng region = Miss nhiều target

3. **Đừng quên Clear Bounds khi di chuyển cửa sổ game**:
   - Bounds cũ → Bring-to-front sai vị trí
   - Click "Clear Bounds" để reset

---

## Troubleshooting (Xử Lý Sự Cố)

### ❓ Bot không tìm thấy monster

**Nguyên nhân:**
- Region quá nhỏ, monster ở ngoài vùng
- Template không khớp (monster đổi skin/animation)

**Giải pháp:**
```
1. Xóa region (để trống L, T, W, H) → Test lại
2. Nếu vẫn không tìm thấy → Vấn đề ở template, không phải region
3. Chụp template mới từ game (Browse → chọn ảnh mới)
```

### ❓ Game chạy chậm/lag khi bot hoạt động

**Nguyên nhân:**
- Region quá lớn hoặc không có region (tìm full screen)
- CPU phải xử lý quá nhiều pixels

**Giải pháp:**
```
1. Đặt region nhỏ hơn:
   - Full HD 1920x1080 → Giảm xuống 500x500
   - 500x500 → Giảm xuống 300x300
   
2. Kiểm tra Confidence (trong Advanced Settings):
   - Confidence càng thấp → Càng nhiều false positive → Chậm
   - Tăng Confidence lên 0.85 - 0.90
```

### ❓ Bring-to-front không đúng vị trí

**Nguyên nhân:**
- Window Bounds lưu vị trí cũ
- Bạn đã di chuyển cửa sổ game sau khi chọn window

**Giải pháp:**
```
1. Click "Clear Bounds"
2. Chọn lại window game trong Hunt tab topbar
3. Thử bring-to-front lại
```

---

## Tóm Tắt

| Thiết lập | Mục đích | Khi nào dùng |
|-----------|----------|--------------|
| **Template Path** | Ảnh để nhận diện monster | Khi thay đổi target monster |
| **Region (L,T,W,H)** | Giới hạn vùng tìm kiếm | Tối ưu tốc độ, monster ở vị trí cố định |
| **Window Bounds** | Cache vị trí cửa sổ game | Tự động, không cần chỉnh tay |

**Khuyến nghị:**
- 🔰 **Beginner**: Không cần đụng Advanced Window Settings
- 📊 **Intermediate**: Có thể thử region nếu game chạy chậm
- ⚙️ **Advanced**: Tối ưu region và template để đạt hiệu suất cao nhất

---

**Lưu ý cuối cùng:**
- Advanced Window Settings chỉ hiện khi bạn chọn **Mode: Advanced** trong Setup tab
- Nếu không thấy section này → Chuyển mode lên Advanced
- Mọi thay đổi cần click **"Apply Settings"** để lưu vào hunt_config.json

---

**Liên quan:**
- Hunt Tab: Basic controls (window selection, skills, buttons)
- Setup Tab → Advanced Settings: Confidence, grayscale, search/attack intervals
- Help Tab: Troubleshooting guide
