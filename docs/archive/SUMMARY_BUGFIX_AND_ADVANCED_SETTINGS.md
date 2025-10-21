# Tóm Tắt: Bug Fix + Giải Thích Advanced Window Settings

**Date:** October 18, 2025 (Late Evening)
**Session:** Sprint 18 Phase 4 Bug Fixes

---

## ✅ Bug Fix Hoàn Thành

### Vấn đề: Timing Recommendation Unhashable Dict Error

**Lỗi gặp phải:**
```
Error: cannot use 'dict' as a dict key (unhashable type: 'dict')
```

**Nguyên nhân:**
- Code giả định `skill_slots` là array of STRING: `["Dark Explosion", "Bone Javelin"]`
- Thực tế trong hunt_config.json lưu array of DICT (full skill objects):
  ```json
  "skill_slots": [
    {
      "name": "Dark Explosion",
      "key": "1",
      "type": "attack",
      "cooldown": 1.9
    }
  ]
  ```

**Giải pháp:**
- Thay đổi code để extract skill name từ dict objects
- Thêm type checking: `isinstance(skill_slot, dict)`
- Hỗ trợ cả 2 format (dict và string) để tương thích ngược

**Kết quả:**
- ✅ Timing recommendation hoạt động bình thường
- ✅ Hiển thị chính xác "3 kỹ năng TẤN CÔNG + 1 kỹ năng BUFF (không tính)"
- ✅ Tính toán đúng từ attack skills, loại trừ buff skills

---

## 📖 Giải Thích: Advanced Window Settings

### Advanced Window Settings Là Gì?

**Định nghĩa:** 
Phần cài đặt nâng cao trong Setup tab (chỉ hiện khi Mode = Advanced) giúp **tối ưu hiệu suất** và **tùy chỉnh vùng tìm kiếm monster**.

**Vị trí:** 
Setup Tab → Mode: Advanced → Section 4: Window Settings (ở cuối cùng)

---

### Khi Nào Cần Dùng?

#### ✅ Nên Dùng Khi:

1. **Game chạy chậm/lag khi bot hoạt động**
   - Nguyên nhân: OpenCV phải xử lý toàn bộ màn hình (hàng triệu pixels)
   - Giải pháp: Giới hạn Region chỉ tìm trong khu vực nhỏ

2. **Monster xuất hiện ở vị trí cố định**
   - Ví dụ: Map hunting có spawn point cố định ở góc phải dưới
   - Lợi ích: Tìm nhanh hơn, chính xác hơn

3. **Nhiều object giống nhau trên màn hình**
   - Ví dụ: Có NPC, player khác giống monster
   - Giải pháp: Thu hẹp Region để tránh nhầm lẫn

#### ❌ KHÔNG Cần Dùng Khi:

1. **Bạn là người mới** → Dùng Mode Beginner/Intermediate
2. **Game chạy mượt** → Không cần tối ưu
3. **Monster di chuyển random** → Region cố định sẽ miss target

---

### Các Thiết Lập Chi Tiết

#### 1️⃣ Template Path (Đường dẫn ảnh template)

**Chức năng:** 
File ảnh để OpenCV nhận diện monster (monster frame, HP bar, icon...)

**Ví dụ:**
```
Template: assets/images/monsters/coc_go__capture_1760736387994.png
[Browse]
```

**Lưu ý:**
- ⚠️ Ảnh phải rõ nét, không mờ
- ⚠️ Kích thước tốt nhất: 100x100 → 200x200 pixel
- ✅ Chụp từ màn hình game thật (không edit, không resize)

---

#### 2️⃣ Region (Vùng tìm kiếm) - QUAN TRỌNG NHẤT

**Chức năng:** 
Giới hạn vùng tìm kiếm monster trên màn hình để tăng tốc độ.

**Cấu trúc:**
```
Region:  L: [1074]   T: [456]   W: [204]   H: [217]
         ^^^         ^^^        ^^^        ^^^
         Left        Top        Width      Height
         (X bên     (Y phía    (Chiều     (Chiều
          trái)      trên)      rộng)      cao)
```

**Giải thích bằng hình ảnh:**

```
┌─────────────────────────────────────┐
│ Màn hình game 1920x1080             │
│                                     │
│                                     │
│              ┌──────────┐           │ 
│              │ Region   │ ← Vùng tìm monster
│              │ W x H    │   (nhỏ hơn màn hình)
│              └──────────┘           │
│              ↑                      │
│              L, T (tọa độ góc trái trên)
│                                     │
└─────────────────────────────────────┘
```

**Ví dụ thực tế:**

**Case 1: Monster ở góc phải dưới**
```
Màn hình: 1920x1080
Monster thường ở: x=1500-1800, y=800-1000

Thiết lập:
L: 1500  (khoảng cách từ mép trái màn hình)
T: 800   (khoảng cách từ mép trên màn hình)
W: 300   (chiều rộng vùng: 1500 + 300 = 1800)
H: 200   (chiều cao vùng: 800 + 200 = 1000)

Lợi ích:
- Full screen: 2,073,600 pixels
- Region này: 60,000 pixels
- Nhanh hơn: 34 LẦN! 🚀
```

**Case 2: Để trống (tìm toàn màn hình)**
```
L: [empty]
T: [empty]
W: [empty]
H: [empty]

Khi nào dùng:
- Monster di chuyển khắp màn hình
- Chưa biết pattern spawn
- Đang test ban đầu
```

**Cách tìm tọa độ Region:**

**Phương pháp 1: Dùng Paint (dễ nhất)**
```
1. Chụp screenshot game (PrtScn)
2. Mở Paint, paste (Ctrl+V)
3. Dùng Select tool (khung chữ nhật), chọn vùng monster
4. Nhìn status bar Paint → Hiển thị tọa độ
   Ví dụ: "1074, 456 - 1278, 673"
   
   L = 1074 (số đầu)
   T = 456  (số thứ 2)
   W = 1278 - 1074 = 204
   H = 673 - 456 = 217
```

**Phương pháp 2: Dùng Windows Snipping Tool**
```
1. Win + Shift + S
2. Chọn vùng monster
3. Xem dimensions hiển thị
```

---

#### 3️⃣ Window Bounds (Giới hạn cửa sổ)

**Chức năng:** 
Lưu vị trí và kích thước cửa sổ game để tối ưu "Bring to Front".

**Hiển thị:**
```
Window Bounds: (100, 50) 1920x1080  [Clear Bounds]
               ^^^^^^^^^  ^^^^^^^^^^
               Vị trí     Kích thước
               X, Y       Width x Height
```

**Cách hoạt động:**

1. **Lần đầu chọn window** (Hunt tab topbar):
   - App tự động lưu vị trí cửa sổ game
   - Ví dụ: Game ở tọa độ (100, 50), size 1920x1080

2. **Khi click "Bring to Front"**:
   - Dùng cached bounds → Đưa window lên ngay (nhanh)
   - Thay vì tìm window mỗi lần (chậm)

3. **Click "Clear Bounds"**:
   - Xóa cache
   - Lần bring-to-front tiếp theo sẽ tìm lại window

**Khi nào cần Clear Bounds?**
- ✅ Di chuyển cửa sổ game sang vị trí khác
- ✅ Resize cửa sổ game
- ✅ Bring-to-front không hoạt động đúng

---

### So Sánh Hiệu Suất

| Cấu hình | Pixels xử lý | FPS (ước tính) | CPU Usage | Khi nào dùng |
|----------|--------------|----------------|-----------|--------------|
| **Full screen** (no region) | 2,073,600 | ~30 FPS | Cao ⚠️ | Monster di chuyển random |
| **Region 500x500** | 250,000 | ~120 FPS | Trung bình | Monster trong khu vực lớn |
| **Region 200x200** | 40,000 | ~200+ FPS | Thấp ✅ | Monster vị trí cố định |

**Kết luận:**
- Region càng nhỏ → Càng nhanh, ít CPU
- Nhưng: Quá nhỏ → Dễ miss monster nếu nó di chuyển

---

### Workflow Thiết Lập (Từng Bước)

#### Bước 1: Chuyển sang Mode Advanced
```
Setup Tab → Mode Selection → Chọn "Advanced"
```

#### Bước 2: Xác định vùng monster
```
1. Chạy game, đứng ở hunting spot
2. Quan sát: Monster spawn ở đâu? Di chuyển trong khu vực nào?
3. Chụp screenshot
```

#### Bước 3: Đo pixel bằng Paint
```
1. Paste screenshot vào Paint
2. Dùng Select tool, khoanh vùng monster
3. Đọc tọa độ từ status bar
```

#### Bước 4: Nhập vào Setup tab
```
Setup Tab → Advanced Window Settings

Region:
L: 1074
T: 456
W: 204
H: 217

[Apply Settings]
```

#### Bước 5: Test và điều chỉnh
```
1. Bắt đầu hunt → Xem có tìm thấy monster không
2. Nếu miss → Tăng W, H (mở rộng vùng)
3. Nếu chậm → Giảm W, H (thu hẹp vùng)
```

---

### Best Practices (Thực Hành Tốt)

#### ✅ Nên Làm

1. **Bắt đầu với full screen**
   - Để trống L, T, W, H
   - Chạy vài phút xác nhận bot hoạt động

2. **Thu hẹp dần dần**
   - Đặt region rộng hơn 20-30% so với vùng thực tế
   - Ví dụ: Monster 200x200 → Region 260x260

3. **Kiểm tra định kỳ**
   - Khi game update
   - Khi đổi hunting spot

#### ❌ Tránh Làm

1. **Đừng đặt region quá chặt**
   ```
   ❌ Monster 200x200, region 200x200 → Dễ miss
   ✅ Monster 200x200, region 260x260 → Buffer 30%
   ```

2. **Đừng dùng region khi monster random**
   - Monster spawn khắp nơi = Dùng full screen

3. **Đừng quên Clear Bounds khi di chuyển window**

---

### Troubleshooting (Xử Lý Lỗi)

#### ❓ Bot không tìm thấy monster

**Giải pháp:**
```
1. Xóa region (để trống L, T, W, H)
2. Test lại → Nếu vẫn không tìm thấy = lỗi ở template
3. Chụp template mới
```

#### ❓ Game chạy chậm/lag

**Giải pháp:**
```
1. Thu hẹp region:
   - Full HD → 500x500
   - 500x500 → 300x300
   
2. Tăng Confidence (Setup → Advanced Settings):
   - 0.75 → 0.85 (giảm false positive)
```

#### ❓ Bring-to-front sai vị trí

**Giải pháp:**
```
1. Click "Clear Bounds"
2. Chọn lại window ở Hunt tab
3. Test lại
```

---

## 📁 Tài Liệu Liên Quan

### Bug Fix Documentation
- **[BUGFIX_TIMING_UNHASHABLE_DICT.md](bugfixes/BUGFIX_TIMING_UNHASHABLE_DICT.md)** - Chi tiết kỹ thuật bug fix
- **[BUGFIX_TIMING_RECOMMENDATION_UX.md](bugfixes/BUGFIX_TIMING_RECOMMENDATION_UX.md)** - UX improvements timing recommendation

### User Guides
- **[ADVANCED_WINDOW_SETTINGS_GUIDE.md](ADVANCED_WINDOW_SETTINGS_GUIDE.md)** - Hướng dẫn chi tiết Advanced Window Settings
- **[HUONG_DAN_NGUOI_MOI.md](HUONG_DAN_NGUOI_MOI.md)** - Hướng dẫn người mới
- **[INDEX.md](INDEX.md)** - Index tất cả tài liệu

---

## 📊 Tóm Tắt Thay Đổi

### Files Modified
- `app_gui.py`: ~40 lines (timing recommendation skill extraction)
- `docs/bugfixes/BUGFIX_TIMING_UNHASHABLE_DICT.md`: ~350 lines (new)
- `docs/ADVANCED_WINDOW_SETTINGS_GUIDE.md`: ~600 lines (new)
- `docs/INDEX.md`: Updated với 2 files mới
- `docs/context/CONTEXT_MAIN.txt`: Updated bug count (5 bugs)

### Bug Fixes Count (Sprint 18 Phase 4)
1. ✅ Setup apply settings error
2. ✅ OpenCV missing
3. ✅ Logger parameter error
4. ✅ Timing recommendation UX
5. ✅ Timing unhashable dict ⭐ **Latest**

### Documentation Count
- Total: ~42 files (+2 new)
- Lines added: ~950 lines
- New guides: 2 (bug fix + advanced settings)

---

## 🎯 Kết Luận

### Bug Fix
- ✅ Lỗi timing recommendation đã được sửa hoàn toàn
- ✅ Feature hoạt động bình thường với skill_slots format mới
- ✅ Không có breaking changes

### Advanced Window Settings
- 📖 Đã có hướng dẫn chi tiết, dễ hiểu
- 🎯 Người dùng hiểu khi nào cần dùng, khi nào không cần
- 🛠️ Workflow rõ ràng từng bước (Paint → Region → Test)

### Next Steps
- Continue Sprint 18 Phase 4: Task #4 (Stats Tab)
- Integration & Testing
- Release Sprint 18 Phase 4 (target: 100% completion)

---

**Updated:** October 18, 2025 (Late Evening)  
**Status:** ✅ All issues resolved, documentation complete  
**Sprint Progress:** 75% (6/8 tasks done)
