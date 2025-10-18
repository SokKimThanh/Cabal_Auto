# 🎮 Hướng Dẫn Sử Dụng Cho Người Mới

## 🚀 Bắt Đầu Nhanh (5 Phút)

### **Bước 1: Chạy Chương Trình**

```powershell
# Mở PowerShell tại thư mục dự án
cd E:\Cabal_Auto

# Chạy ứng dụng
.\venv\Scripts\python.exe app_gui.py
```

### **Bước 2: Trả Lời Câu Hỏi Chào Mừng**

Lần đầu chạy, bạn sẽ thấy hộp thoại:

```
┌──────────────────────────────────────────────┐
│  Chào mừng đến Cabal Auto Hunt!              │
│                                              │
│  Có vẻ đây là lần đầu bạn sử dụng Cabal     │
│  Auto Hunt.                                  │
│                                              │
│  Bạn có muốn chạy Trợ lý thiết lập để cấu   │
│  hình không?                                 │
│                                              │
│  Trợ lý sẽ hướng dẫn bạn:                   │
│    • Chọn cửa sổ game                       │
│    • Chọn quái để săn                       │
│    • Cấu hình kỹ năng tấn công              │
│                                              │
│  Bạn luôn có thể chạy trợ lý sau bằng nút   │
│  '🧙 Trợ lý thiết lập'.                      │
│                                              │
│          [  Có  ]        [  Không  ]        │
└──────────────────────────────────────────────┘
```

**👉 Nhấn "Có"** để bắt đầu thiết lập!

### **Bước 3: Hoàn Thành 5 Bước Trợ Lý**

#### **📍 Bước 1/5: Chào Mừng**

<img src="wizard_step1.png" alt="Bước 1" width="600"/>

- Chọn ngôn ngữ: **Tiếng Việt** hoặc **English**
- Đọc thông tin về những gì trợ lý sẽ làm
- Nhấn **"Next →"**

---

#### **🪟 Bước 2/5: Chọn Cửa Sổ Game**

<img src="wizard_step2.png" alt="Bước 2" width="600"/>

**Cách làm:**
1. Mở game Cabal trước khi chọn
2. Trợ lý tự động tìm cửa sổ có chữ "Cabal"
3. Chọn cửa sổ game trong danh sách (có PID và HWND)
4. Nhấn **"Next →"**

**💡 Mẹo:** 
- Nếu không thấy game, gõ tên khác vào ô "Filter" và nhấn "Search"
- Chọn đúng PID để không nhầm cửa sổ khác

---

#### **👾 Bước 3/5: Chọn Quái Để Săn**

<img src="wizard_step3.png" alt="Bước 3" width="600"/>

**Cách làm:**
1. Xem danh sách quái có sẵn
2. Chọn 1 quái (ví dụ: "Cọc gỗ" cho người mới)
3. Xem thông tin: HP, Damage, số lượng ảnh mẫu
4. Nhấn **"Next →"**

**ℹ️ Thông tin hiển thị:**
- **HP:** Máu của quái
- **Damage:** Sát thương trung bình
- **Templates:** Số ảnh mẫu để nhận diện (nhiều = chính xác hơn)

---

#### **⚔️ Bước 4/5: Cấu Hình Kỹ Năng**

<img src="wizard_step4.png" alt="Bước 4" width="600"/>

**Cách làm:**
1. Có 9 ô kỹ năng (từ slot 1 đến slot 9)
2. Chọn kỹ năng cho từng ô (hoặc để "(Empty)")
3. Thứ tự kỹ năng = thứ tự tấn công trong game
4. Nhấn **"Clear All"** nếu muốn xóa hết
5. Nhấn **"Next →"**

**💡 Mẹo:**
- Slot 1-3: Kỹ năng sát thương cao
- Slot 4-6: Kỹ năng buff/hỗ trợ
- Slot 7-9: Kỹ năng cooldown dài
- Có thể để trống nếu không dùng đủ 9 kỹ năng

---

#### **✅ Bước 5/5: Xem Lại và Lưu**

<img src="wizard_step5.png" alt="Bước 5" width="600"/>

**Tóm tắt cấu hình:**

```
🪟 Cửa Sổ Game:
   • Title: Cabal Online
   • PID: 12345
   • HWND: 0x001A0B2C

👾 Quái:
   • Tên: Cọc gỗ
   • HP: 10,000
   • Damage: 500
   • Templates: 2 ảnh mẫu

⚔️ Kỹ Năng:
   • Slot 1: Dark Explosion
   • Slot 2: Fire Ball
   • Slot 3: Ice Blade
   • (Slots 4-9 trống)

⏱️ Thời Gian:
   • Lost Timeout: 0.5s
   • Attack Duration: 5.0s
```

**Nhấn "✓ Finish"** để lưu cấu hình!

---

### **Bước 4: Bắt Đầu Săn**

Sau khi hoàn thành trợ lý:

1. Tab **Hunt** sẽ hiển thị cấu hình đã lưu
2. Mở game Cabal, đứng gần quái
3. Nhấn nút **"Start Hunt"**
4. Nhấn **F9** để dừng bất cứ lúc nào

**✨ Hoàn Tất!** Bot sẽ tự động:
- Tìm quái (nhấn TAB)
- Đánh quái (dùng kỹ năng đã chọn)
- Lặp lại cho đến khi bạn dừng

---

## ❓ Câu Hỏi Thường Gặp

### **1. Tôi nhấn "Không" ở màn hình chào mừng, giờ muốn chạy lại trợ lý?**

**Trả lời:**
- Vào tab **Hunt**
- Nhấn nút **"🧙 Trợ lý thiết lập"**
- Trợ lý sẽ mở lại

---

### **2. Lần sau chạy app có bị hỏi lại không?**

**Trả lời:**
- **KHÔNG** - Nếu bạn đã hoàn thành trợ lý
- App sẽ tự động nhận biết bạn đã cấu hình rồi
- Chỉ người mới chưa có `window_title`, `monster_selected_name`, `skill_slots` mới bị hỏi

---

### **3. Muốn đổi quái/kỹ năng khác thì làm sao?**

**Trả lời:**

**Cách 1: Chạy lại trợ lý**
- Nhấn nút **"🧙 Trợ lý thiết lập"**
- Chọn lại quái và kỹ năng
- Nhấn Finish → ghi đè cấu hình cũ

**Cách 2: Sửa thủ công (Advanced mode)**
- Chọn **Mode: 🔧 Nâng cao**
- Sửa trực tiếp trong tab Hunt
- Nhấn **"Save hunt config"**

---

### **4. Trợ lý báo "No windows matched" - không tìm thấy game?**

**Nguyên nhân:**
- Game chưa mở
- Tên game không chứa "Cabal"

**Giải pháp:**
1. Mở game trước
2. Gõ tên khác trong ô "Filter" (ví dụ: "CABAL", "VTC")
3. Nhấn "Search"
4. Chọn cửa sổ có PID đúng

---

### **5. Sau khi Finish, bot không chạy?**

**Kiểm tra:**
- ✅ Đã nhấn "Start Hunt" chưa?
- ✅ Game đã focus chưa? (click vào game window)
- ✅ Đứng gần quái chưa? (phải trong tầm nhìn)
- ✅ Có ảnh mẫu quái trong `assets/images/monsters/` chưa?

---

### **6. Muốn xóa config và chạy lại từ đầu?**

**Cách làm:**
```powershell
# Xóa file config
Remove-Item hunt_config.json

# Chạy lại app
.\venv\Scripts\python.exe app_gui.py

# Trợ lý sẽ hiện lại vì phát hiện bạn là người mới
```

---

## 🎯 Chế Độ Giao Diện (3 Cấp Độ)

### **🌱 Người Mới (Beginner)**

**Ai nên dùng:** Người mới, chỉ cần basic

**Hiển thị:**
- Chọn cửa sổ game
- Chọn quái
- Chọn kỹ năng
- Start/Stop hunt

**Tổng cộng:** 4 trường duy nhất!

---

### **⚙️ Trung Cấp (Intermediate)**

**Ai nên dùng:** Đã quen, muốn tinh chỉnh timing

**Hiển thị:** 
- Tất cả ở chế độ Beginner
- **+ Lost Timeout** (thời gian mất dấu quái)
- **+ Attack Duration** (thời gian tấn công tối thiểu)

**Tổng cộng:** 6 trường

---

### **🔧 Nâng Cao (Advanced)**

**Ai nên dùng:** Pro, muốn full control

**Hiển thị:**
- Tất cả ở chế độ Intermediate
- **+ Target Key** (phím chuyển mục tiêu)
- **+ Attack Keys** (danh sách phím tấn công thủ công)
- **+ Search/Attack Intervals** (tần suất quét/đánh)
- **+ Template/Region** (đường dẫn ảnh, vùng tìm kiếm)
- **+ PID/HWND** (Process ID, Window Handle)

**Tổng cộng:** 35+ trường!

---

## 📊 Quy Trình Hoàn Chỉnh

```
┌─────────────────────────────────────────────┐
│  1. Chạy app_gui.py                         │
└──────────────┬──────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────┐
│  2. Thấy hộp thoại "Chào mừng"              │
│     → Nhấn "Có"                             │
└──────────────┬──────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────┐
│  3. Trợ Lý 5 Bước:                          │
│     Step 1: Chọn ngôn ngữ                   │
│     Step 2: Chọn cửa sổ game                │
│     Step 3: Chọn quái                       │
│     Step 4: Chọn kỹ năng (9 slots)          │
│     Step 5: Xem lại → Finish                │
└──────────────┬──────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────┐
│  4. Config lưu vào hunt_config.json         │
│     → Tab Hunt load cấu hình                │
└──────────────┬──────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────┐
│  5. Mở game, đứng gần quái                  │
└──────────────┬──────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────┐
│  6. Nhấn "Start Hunt"                       │
│     → Bot bắt đầu tìm và đánh quái          │
└──────────────┬──────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────┐
│  7. Nhấn F9 hoặc "Stop Hunt" để dừng        │
└─────────────────────────────────────────────┘
```

---

## 🛠️ Khắc Phục Sự Cố

### **Vấn đề: Trợ lý không mở**

**Nguyên nhân:** Lỗi code hoặc thiếu module

**Giải pháp:**
```powershell
# Kiểm tra log
Get-Content hunt.log -Tail 20

# Cài đủ dependencies
.\venv\Scripts\pip.exe install -r requirements.txt
```

---

### **Vấn đề: Không nhìn thấy nút Next**

**Nguyên nhân:** Cửa sổ quá nhỏ, nút bị che

**Giải pháp:**
- Kéo to cửa sổ trợ lý (resize)
- Scroll xuống dưới (dùng chuột cuộn)
- Nút Next luôn ở dưới cùng màn hình

---

### **Vấn đề: Chọn quái nhưng không có ảnh mẫu**

**Nguyên nhân:** Quái chưa được chụp ảnh template

**Giải pháp:**
1. Vào **Monster Manager** (tab Hunt)
2. Chọn quái
3. Nhấn **"Capture screenshot"** để chụp ảnh quái
4. Kéo chọn vùng quái trên màn hình
5. Lưu → Chạy lại trợ lý

---

## 🎓 Học Thêm

- **Tài liệu đầy đủ:** [README.md](../README.md)
- **Cấu hình nâng cao:** [hunt_config.json](../hunt_config.json)
- **Quản lý quái:** [Monster Manager Guide](MONSTER_MANAGER.md)
- **Quản lý kỹ năng:** [Skills Manager Guide](SKILLS_MANAGER.md)

---

**Chúc bạn săn quái vui vẻ! 🎮🔥**

*Cập nhật lần cuối: 2025-01-18 (Sprint 16 Phase 2)*
