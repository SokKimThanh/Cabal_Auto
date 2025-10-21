# Hướng Dẫn Nhanh - Tính Năng User Level trong Setup Wizard

## Dành Cho Người Mới 🌱

### Bước 1: Chọn "Người mới"
Khi bắt đầu Setup Wizard, bạn sẽ thấy hai lựa chọn:
- ✅ **Chọn: 🌱 Người mới**
- ❌ Không chọn: ⚙️ Người có kinh nghiệm

### Bước 2-3: Chọn Window và Monster
Làm bình thường như hướng dẫn wizard.

### Bước 4: Thiết Lập Kỹ Năng
Ở bước này, bạn sẽ thấy:
1. **9 ô skill** để chọn kỹ năng
2. Nút "Xóa tất cả ô"
3. **NÚT MỚI: "🎯 Mở công cụ thiết lập kỹ năng"** ← Màu xanh, bấm được!

#### Cách Dùng Nút Rotation Builder:

**A. Nếu bạn biết skill rotation:**
- Chọn skills vào 9 ô như bình thường
- Bỏ qua nút rotation builder
- Sang bước 5

**B. Nếu bạn chưa biết setup rotation:**
1. **Bấm nút "🎯 Mở công cụ thiết lập kỹ năng"**
2. Cửa sổ Library Manager sẽ mở ra
3. Trong Library Manager:
   - Tab "Monsters": Quản lý quái
   - Tab "Skills": Quản lý kỹ năng
   - **Tab "Rotation"**: Thiết lập thứ tự skill tự động
4. Trong tab Rotation:
   - Chọn monster muốn săn
   - Chọn skills để dùng
   - Hệ thống tính toán thời gian tối ưu
   - Bấm "Apply" để áp dụng
5. Đóng Library Manager
6. Quay lại wizard, skills đã được cập nhật
7. Sang bước 5

### Bước 5: Hoàn Tất
Xem lại cấu hình và bấm "Finish"!

---

## Dành Cho Người Có Kinh Nghiệm ⚙️

### Bước 1: Chọn "Người có kinh nghiệm"
- ❌ Không chọn: 🌱 Người mới
- ✅ **Chọn: ⚙️ Người có kinh nghiệm**

### Bước 2-4: Setup Nhanh
Làm như bình thường. Ở bước 4, bạn sẽ thấy:
- 9 ô skill (bình thường)
- Nút "Xóa tất cả ô" (bình thường)
- Nút rotation builder **BỊ KHÓA** (màu xám)
  - Lý do: Bạn đã chọn "Người có kinh nghiệm"
  - Hint: "Tính năng này chỉ dành cho người mới..."

### Bước 5: Hoàn Tất
Xem lại và finish!

---

## So Sánh Feature

| Tính Năng | Người Mới 🌱 | Người Kinh Nghiệm ⚙️ |
|-----------|--------------|---------------------|
| Chọn skills thủ công | ✅ Có | ✅ Có |
| Nút Rotation Builder | ✅ **ENABLED** | ❌ **DISABLED** |
| Mở Library Manager | ✅ Có thể | ❌ Không thể (từ wizard) |
| Hint text | "Bấm để mở..." | "Chỉ dành cho người mới..." |
| Workflow | Có hỗ trợ | Nhanh, đơn giản |

---

## Câu Hỏi Thường Gặp (FAQ)

### Q1: Tôi chọn sai user level, làm sao đổi?
**A:** Quay lại Step 1 (bấm nút "Back"), chọn lại user level mong muốn.

### Q2: Nút rotation builder bị xám, sao bấm không được?
**A:** Bạn đã chọn "Người có kinh nghiệm" ở Step 1. Muốn dùng nút này:
1. Quay lại Step 1
2. Chọn "🌱 Người mới"
3. Quay lại Step 4 → Nút sẽ màu xanh

### Q3: Library Manager là gì?
**A:** Công cụ quản lý toàn bộ monsters, skills, và tính toán timing tối ưu. Có 3 tabs:
- **Monsters:** Quản lý quái
- **Skills:** Quản lý kỹ năng
- **Rotation:** Thiết lập rotation tự động

### Q4: Tôi nên chọn user level nào?
**A:** 
- Chọn **"Người mới"** nếu:
  - Lần đầu dùng bot
  - Chưa biết cách setup skill rotation
  - Muốn có hướng dẫn chi tiết
  - Muốn dùng công cụ tự động

- Chọn **"Người có kinh nghiệm"** nếu:
  - Đã biết cách dùng bot
  - Tự setup được rotation
  - Muốn workflow nhanh
  - Không cần hỗ trợ thêm

### Q5: Có thể mở Library Manager sau khi hoàn tất wizard không?
**A:** Có! Trong main app:
1. Vào tab "Setup"
2. Trong phần "Libraries"
3. Bấm nút "Open Library Manager"

### Q6: Thay đổi trong Library Manager có được lưu không?
**A:** Có! Mọi thay đổi:
- Tự động lưu vào `data/monsters.json`
- Tự động lưu vào `data/skills.json`
- Wizard tự động refresh khi bạn đóng Library Manager

---

## Tips & Tricks

### 💡 Tip 1: Test Setup Trước
Sau khi hoàn tất wizard, test lại config:
1. Bấm "Test Recognition" để test nhận quái
2. Bấm "Start Hunt" (thử 10-20s)
3. Bấm "Stop Hunt"
4. Xem log để kiểm tra

### 💡 Tip 2: Dùng Template Multiple
Một monster có thể có nhiều templates (hình ảnh khác nhau):
- Template 1: Monster đứng yên
- Template 2: Monster đang đánh
- Template 3: Monster bị hit (màu đỏ)

Càng nhiều templates → Nhận diện càng chính xác!

### 💡 Tip 3: Timing Là Quan Trọng
Trong Rotation tab, hệ thống tự tính:
- **Lost Timeout:** Thời gian giữ đánh sau khi mất visual
- **Attack Duration:** Thời gian đánh tối thiểu

→ Không cần phải đoán giá trị nữa!

### 💡 Tip 4: Backup Config
Trước khi thử nghiệm, backup files:
- `data/hunt_config.json`
- `data/monsters.json`
- `data/skills.json`

---

## Liên Hệ / Support

Nếu gặp vấn đề:
1. Đọc lại hướng dẫn này
2. Xem file `docs/HUONG_DAN_NGUOI_MOI.md`
3. Kiểm tra console log
4. Report lỗi với screenshot

---

**Cập nhật:** October 21, 2025  
**Version:** Sprint 20 - User Level Feature  
**Trạng thái:** ✅ Hoàn thành và sẵn sàng sử dụng
