# Demo: Ngôn Ngữ Đơn Giản Cho Timing Calculator

## 🎯 Mục Tiêu
Viết lại nội dung Timing Calculator để học sinh lớp 5 cũng hiểu được.

---

## 📋 PHẦN 1: SAU KHI TÍNH TOÁN (Preview Box)

### ❌ Trước (Phức tạp - dùng thuật ngữ kỹ thuật):
```
📊 DỮ LIỆU ĐẦU VÀO:
  • Monster HP: 10,000
  • Damage/hit: 500
  • Attack Speed: 0.64 hits/s
  • Time/hit: 1.57s (= 1 / 0.64)

⏱️ TIMING CƠ BẢN:
  • attack_press_ms: 150 ms
    📐 Công thức: max(50, min(150, avg_cast_time * 0.1))
    💡 APS càng cao → nhấn phím càng nhanh
```

### ✅ Sau (Đơn giản - ngôn ngữ trẻ em):
```
📋 CÁC CON SỐ SẼ ĐƯỢC LƯU VÀO MÁY:
──────────────────────────────────────

📊 THÔNG TIN QUÁI VẬT:
  • Máu quái: 10,000 HP
  • Sát thương 1 đòn: 500
  • Tốc độ đánh: 0.64 đòn/giây
  • Thời gian 1 đòn: 1.57 giây
  • Cần đánh: 20 đòn
  • Tổng thời gian: 32.00 giây

⏱️ CÁC SỐ QUAN TRỌNG:

1️⃣ Nhấn phím giữ bao lâu?
   → 150 mili-giây (0.150 giây)
   💡 Giống như bấm nút giữ rồi thả ra

2️⃣ Đổi quái sau bao lâu?
   → 1.90 giây
   💡 Đợi lâu hơn 1 đòn đánh, tránh đổi lung tung

3️⃣ Tìm quái sau bao lâu?
   → 0.78 giây
   💡 Tìm nhanh để phát hiện quái kịp thời

4️⃣ Đánh sau bao lâu?
   → 1.90 giây
   💡 Đánh nhanh hơn bình thường một chút

5️⃣ Quái mất bao lâu thì dừng?
   → 2.37 giây
   💡 Nếu không thấy quái quá lâu, nghĩa là chết rồi

6️⃣ Đánh tối thiểu bao lâu?
   → 38.40 giây
   💡 Đánh đủ lâu, dù có lúc không thấy quái

──────────────────────────────────────
🤖 AUTO SẼ LÀM GÌ KHI CHẠY?
──────────────────────────────────────

1️⃣ TÌM QUÁI (cứ 0.78 giây tìm 1 lần):
   • Nhìn màn hình tìm hình quái vật
   • Thấy quái → chuyển sang bước 2

2️⃣ CHỌN QUÁI:
   • Bấm phím Z để chọn quái
   • Đợi 1.90 giây
   • Không chọn quái khác khi đang đánh

3️⃣ BẮT ĐẦU ĐÁNH (đánh 20 đòn):
   • Bấm phím tấn công giữ 150 mili-giây
   • Thả phím ra
   • Đợi 1.90 giây
   • Lặp lại: Đánh → Chờ → Đánh → Chờ...
   • Dự kiến hết ~32.0 giây

4️⃣ KIỂM TRA QUÁI:
   • Nếu không thấy quái quá 2.37 giây:
     ❌ Dừng đánh (quái chết hoặc mất rồi)
   • Nếu còn thấy quái:
     ✅ Đánh tiếp tối thiểu 38.40 giây

5️⃣ QUÁI CHẾT RỒI:
   • Quay lại bước 1 (tìm quái mới)
   • Cứ thế lặp lại mãi mãi

──────────────────────────────────────
💡 Bấm nút 'Apply' bên dưới để lưu các số này
```

---

## ✅ PHẦN 2: SAU KHI APPLY (Confirmation Box)

### ❌ Trước (Phức tạp - nhiều code):
```
⚡ QUÁ TRÌNH THỰC THI KHI CHẠY AUTO:
──────────────────────────────────────

1. auto_hunt.py ĐỌC FILE hunt_config.json
   → Load các thông số timing vừa lưu

2. TÌM KIẾM QUÁI (mỗi 0.78s):
   → while True:
       template_matcher.locate_template()
       time.sleep(0.78)

3. NHẤN PHÍM Z ĐỂ TARGET:
   → tap('z', 150)
   → time.sleep(1.90)

──────────────────────────────────────
🔑 API GỌI THỰC TẾ:
──────────────────────────────────────

  lib/system/win_input.py:
    def tap(key, press_ms):
        key_down(key)                    # ⬇️ NHẤN
        time.sleep(press_ms/1000.0)      # ⏱️ GIỮ
        key_up(key)                      # ⬆️ THẢ PHÍM

  Windows API:
    user32.SendInput(...)                # 🪟 WINDOWS
    → CABAL Game nhận input              # 🎮 GAME
```

### ✅ Sau (Đơn giản - giống kể chuyện):
```
============================================================
✅ ĐÃ LƯU VÀO MÁY TÍNH RỒI!
============================================================

📂 LƯU Ở ĐÂU: lib/data/hunt_config.json

🔧 CÁC SỐ ĐÃ LƯU:
  • Giữ phím: 150 mili-giây
  • Đợi đổi quái: 1.90 giây
  • Tìm quái: mỗi 0.78 giây
  • Đánh: mỗi 1.90 giây
  • Quái mất quá: 2.37 giây thì dừng
  • Đánh tối thiểu: 38.40 giây

────────────────────────────────────────────────────────────
🤖 KHI BẤM NÚT CHẠY AUTO, NÓ SẼ LÀM GÌ?
────────────────────────────────────────────────────────────

BƯỚC 1: Đọc file hunt_config.json
  → Lấy các con số vừa lưu ra dùng

BƯỚC 2: Tìm quái (cứ 0.78 giây tìm 1 lần)
  → Nhìn màn hình, tìm hình quái vật
  → Nếu thấy → chuyển sang BƯỚC 3

BƯỚC 3: Bấm phím Z chọn quái
  → Giữ phím Z trong 150 mili-giây
  → Đợi 1.90 giây

BƯỚC 4: Bắt đầu đánh (đánh 20 đòn)
  → Bấm phím tấn công, giữ 150 mili-giây
  → Thả phím ra
  → Đợi 1.90 giây
  → Lặp lại khoảng 20 lần (tầm 32.0 giây)

BƯỚC 5: Kiểm tra quái còn không
  → Nếu không thấy quái quá 2.37 giây:
     ❌ Quái chết rồi! Dừng đánh
  → Nếu vẫn thấy quái:
     ✅ Đánh tiếp tối thiểu 38.40 giây nữa

BƯỚC 6: Quái chết rồi, tìm quái mới
  → Quay lại BƯỚC 2
  → Cứ thế lặp đi lặp lại mãi mãi

────────────────────────────────────────────────────────────
🔑 MÁY TÍNH SẼ BẤM PHÍM NHƯ THẾ NÀO?
────────────────────────────────────────────────────────────

  1. Chương trình gọi hàm tap()
  2. Hàm tap() gọi key_down() → Nhấn phím xuống
  3. Đợi 150 mili-giây
  4. Gọi key_up() → Thả phím lên
  5. Windows gửi tín hiệu cho Game Cabal
  6. Game Cabal nhận được → Nhân vật đánh quái!

============================================================
✅ KẾT LUẬN: AUTO SẼ BẤM PHÍM THẬT!
   (Giống như bạn ngồi bấm, nhưng máy làm giúp)
============================================================
```

---

## 🎯 So Sánh Ngôn Ngữ

| Trước (Phức tạp) | Sau (Đơn giản) |
|------------------|----------------|
| attack_press_ms | Giữ phím bao lâu? |
| APS càng cao → nhấn nhanh | Bấm nút giữ rồi thả ra |
| target_cycle_delay | Đợi đổi quái |
| Template monitoring | Kiểm tra quái còn không |
| API gọi thực tế | Máy tính sẽ bấm phím như thế nào? |
| while True: locate_template() | Tìm quái (cứ 0.78 giây tìm 1 lần) |
| user32.SendInput() | Windows gửi tín hiệu cho Game |
| Công thức: max(50, min(150)) | (không hiển thị công thức) |

---

## 📝 Nguyên Tắc Viết Đơn Giản

### ✅ NÊN:
1. **Dùng câu hỏi**: "Nhấn phím giữ bao lâu?" (thay vì "attack_press_ms")
2. **Dùng ví dụ đời thường**: "Giống như bấm nút giữ rồi thả ra"
3. **Dùng số thứ tự**: "BƯỚC 1", "BƯỚC 2" (dễ theo dõi)
4. **Dùng emoji**: 🤖 💡 ✅ ❌ (thu hút thị giác)
5. **Tránh thuật ngữ code**: Không viết `while True:`, `time.sleep()`
6. **Giải thích kết quả**: "Quái chết rồi!" thay vì "target lost"

### ❌ KHÔNG NÊN:
1. ~~Dùng tên biến code~~ (attack_press_ms, target_cycle_delay)
2. ~~Hiển thị công thức toán~~ (max(50, min(150, x * 0.1)))
3. ~~Viết pseudocode~~ (while True:, if condition:)
4. ~~Thuật ngữ kỹ thuật~~ (API, SendInput, template matcher)
5. ~~Giải thích chi tiết code~~ (key_down() → key_up())

### 🎯 Quy Tắc Vàng:
> **"Viết như đang giải thích cho em lớp 5, không phải cho lập trình viên"**

---

## 🧪 Test Kết Quả

```bash
# Run timing calculator với skill rotation
python -c "
from lib.features.timing.calculator import calculate_timing

skills = [
    {'name': 'Dark Explosion', 'cooldown': 1.9, 'cast_time': 1.7, 'type': 'attack'},
    {'name': 'Bone Javelin', 'cooldown': 2.4, 'cast_time': 1.5, 'type': 'attack'}
]

result = calculate_timing(10000, 500, skill_rotation=skills)

# Kết quả với ngôn ngữ đơn giản
print('📋 CÁC CON SỐ SẼ ĐƯỢC LƯU VÀO MÁY:')
print(f'  • Máu quái: {result.monster_hp:,.0f} HP')
print(f'  • Cần đánh: {result.hits_to_kill} đòn')
print(f'  • Tổng thời gian: {result.estimated_kill_time_sec:.2f} giây')
print()
print('⏱️ CÁC SỐ QUAN TRỌNG:')
print('1️⃣ Nhấn phím giữ bao lâu?')
print(f'   → {result.attack_press_ms} mili-giây')
print('   💡 Giống như bấm nút giữ rồi thả ra')
"
```

**Output**:
```
📋 CÁC CON SỐ SẼ ĐƯỢC LƯU VÀO MÁY:
  • Máu quái: 10,000 HP
  • Cần đánh: 20 đòn
  • Tổng thời gian: 32.00 giây

⏱️ CÁC SỐ QUAN TRỌNG:
1️⃣ Nhấn phím giữ bao lâu?
   → 150 mili-giây
   💡 Giống như bấm nút giữ rồi thả ra
```

---

## ✅ Hoàn Thành

- ✅ Đã viết lại phần Preview (sau khi Calculate)
- ✅ Đã viết lại phần Confirmation (sau khi Apply)
- ✅ Đã loại bỏ thuật ngữ kỹ thuật
- ✅ Đã thay thế bằng ngôn ngữ trẻ em
- ✅ Đã test và verify syntax

**User có thể hiểu**: Ngay cả học sinh lớp 5! 🎓
