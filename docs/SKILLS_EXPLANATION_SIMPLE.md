# 📚 GIẢI THÍCH: KỸ NĂNG TRONG AUTO CABAL

## 🎯 Câu Hỏi: "Cài đặt kỹ năng chính nghĩa là gì? Còn những kỹ năng khác thì sao?"

---

## 📋 1. CÓ 2 LOẠI KỸ NĂNG

Trong file `hunt_config.json`, mỗi kỹ năng có trường `"type"`:

### ⚔️ Loại 1: Kỹ Năng TẤN CÔNG (`"type": "attack"`)
```json
{
  "name": "Dark Explosion",
  "key": "1",
  "type": "attack",          ← ĐÂY LÀ KỸ NĂNG CHÍNH!
  "cooldown": 1.9,
  "cast_time": 1.7
}
```

**Ý nghĩa**:
- ✅ **Kỹ năng CHÍNH** = Kỹ năng **TẤN CÔNG** (`type: "attack"`)
- 🎯 Auto sẽ dùng để **đánh quái**
- 🔄 Auto sẽ **luân phiên bấm** các kỹ năng này
- ⏱️ Timing Calculator **CHỈ TÍNH DỰA TRÊN** các skill này

### 🛡️ Loại 2: Kỹ Năng PHỤ TRỢ (`"type": "buff"`)
```json
{
  "name": "Regeneration",
  "key": "4",
  "type": "buff",           ← Kỹ năng phụ (hồi máu, tăng sức mạnh...)
  "cooldown": 2.2,
  "cast_time": 1.0
}
```

**Ý nghĩa**:
- 🛡️ Kỹ năng **PHỤ TRỢ** (hồi máu, tăng phòng thủ, tăng tốc độ...)
- ⏰ Auto sẽ bấm **định kỳ** (theo cooldown)
- ❌ **KHÔNG DÙNG** để tính timing đánh quái
- ✅ Chạy **SONG SONG** với kỹ năng tấn công

---

## 🔄 2. AUTO SẼ SỬ DỤNG NHƯ THẾ NÀO?

### 📖 Ví Dụ Cụ Thể:

```json
"skill_slots": [
  {
    "name": "Dark Explosion",
    "key": "1",
    "type": "attack",        ← Kỹ năng tấn công #1
    "cooldown": 1.9,
    "cast_time": 1.7
  },
  {
    "name": "Bone Javelin",
    "key": "2",
    "type": "attack",        ← Kỹ năng tấn công #2
    "cooldown": 2.4,
    "cast_time": 1.5
  },
  {
    "name": "Skull Shooter",
    "key": "3",
    "type": "attack",        ← Kỹ năng tấn công #3
    "cooldown": 2.2,
    "cast_time": 1.5
  },
  {
    "name": "Regeneration",
    "key": "4",
    "type": "buff",          ← Kỹ năng phụ trợ (hồi máu)
    "cooldown": 2.2,
    "cast_time": 1.0
  }
]
```

---

### ⚔️ CÁCH AUTO ĐÁNH QUÁI (Kỹ Năng Tấn Công):

**Bước 1**: Auto lọc ra các kỹ năng `type: "attack"`:
```python
attack_skills = [
  "Dark Explosion" (phím 1),
  "Bone Javelin" (phím 2),
  "Skull Shooter" (phím 3)
]
```

**Bước 2**: Auto tính toán chu kỳ luân phiên:
```
Rotation Cycle = 1.7s + 1.5s + 1.5s = 4.7 giây
Attack Speed = 3 skills / 4.7s = 0.64 đòn/giây
```

**Bước 3**: Auto bấm lần lượt:
```
Giây 0.0: Bấm phím 1 (Dark Explosion) - giữ 1.7 giây
Giây 1.9: Bấm phím 2 (Bone Javelin) - giữ 1.5 giây
Giây 4.3: Bấm phím 3 (Skull Shooter) - giữ 1.5 giây
Giây 6.5: Quay lại phím 1 (Dark Explosion)...
→ Cứ thế lặp đi lặp lại mãi mãi!
```

**⏱️ Quan trọng**: 
- Auto **ĐỢI COOLDOWN** trước khi bấm lại skill cũ
- Nếu skill 1 cooldown = 1.9s, auto sẽ đợi 1.9s trước khi bấm lại
- **KHÔNG BẤM LIÊN TỤC 1 PHÍM!**

---

### 🛡️ CÁCH AUTO DÙNG KỸ NĂNG PHỤ TRỢ (Buff):

**Song song với việc đánh quái**:
```
Giây 0.0: Bấm phím 4 (Regeneration) - hồi máu
Giây 2.2: Cooldown hết, bấm lại phím 4
Giây 4.4: Cooldown hết, bấm lại phím 4
→ Cứ mỗi 2.2 giây bấm 1 lần!

ĐỒNG THỜI:
Giây 0.0: Bấm phím 1 (Dark Explosion) - đánh quái
Giây 1.9: Bấm phím 2 (Bone Javelin) - đánh quái
Giây 4.3: Bấm phím 3 (Skull Shooter) - đánh quái
```

**Kết quả**:
- ⚔️ Nhân vật vừa **ĐÁNH QUÁI** (skill 1, 2, 3)
- 🛡️ Vừa **HỒI MÁU** (skill 4) tự động
- 🤖 Máy tính điều khiển 2 việc cùng lúc!

---

## 🧮 3. TIMING CALCULATOR CHỈ TÍNH KỸ NĂNG TẤN CÔNG

### ✅ Tại Sao?

```python
# Code trong calculator.py
attack_skills = [s for s in skill_rotation if s.get('type') == 'attack']
                                                    ↑
                                CHỈ LẤY SKILL CÓ type='attack'!
```

**Lý do**:
1. ⚔️ **Kỹ năng tấn công** quyết định **TỐC ĐỘ HẠ QUÁI**
2. 🛡️ **Kỹ năng buff** KHÔNG gây sát thương → không cần tính
3. 🧮 Timing Calculator cần biết:
   - Bao lâu đánh 1 đòn? → Từ cast_time của attack skills
   - Bao nhiêu đòn để giết quái? → Từ damage của attack skills
   - Bao lâu để giết 1 con? → Từ rotation_cycle_time

---

## 📊 4. SO SÁNH 2 LOẠI KỸ NĂNG

| Tiêu Chí | Kỹ Năng Tấn Công (`attack`) | Kỹ Năng Phụ Trợ (`buff`) |
|----------|------------------------------|---------------------------|
| **Mục đích** | Đánh quái, gây sát thương | Hồi máu, tăng sức mạnh |
| **Dùng khi nào** | Khi thấy quái | Định kỳ (theo cooldown) |
| **Luân phiên** | Có (1→2→3→1→2→3...) | Không (chỉ bấm phím 4) |
| **Timing Calculator** | ✅ CÓ TÍNH | ❌ KHÔNG TÍNH |
| **attack_interval** | Dựa vào cooldown/cast_time | Không ảnh hưởng |
| **attack_press_ms** | Dựa vào avg cast_time | Không ảnh hưởng |
| **Quan trọng** | ⭐⭐⭐⭐⭐ (Quyết định tốc độ farm) | ⭐⭐⭐ (Tăng sinh tồn) |

---

## 🎮 5. VÍ DỤ THỰC TẾ TRONG GAME

### Tình Huống 1: Warrior (Chiến Binh)
```json
"skill_slots": [
  {"name": "Chém Mạnh", "key": "1", "type": "attack"},      ← Đánh quái
  {"name": "Đâm Xuyên", "key": "2", "type": "attack"},      ← Đánh quái
  {"name": "Hồi Máu", "key": "3", "type": "buff"}           ← Hồi máu
]
```
**Auto sẽ**:
- Luân phiên chém (1) và đâm (2) để đánh quái
- Định kỳ hồi máu (3) khi cooldown hết
- Timing Calculator chỉ tính skill 1 và 2

### Tình Huống 2: Wizard (Phù Thủy)
```json
"skill_slots": [
  {"name": "Cầu Lửa", "key": "1", "type": "attack"},        ← Đánh quái
  {"name": "Sấm Sét", "key": "2", "type": "attack"},        ← Đánh quái
  {"name": "Băng Giá", "key": "3", "type": "attack"},       ← Đánh quái
  {"name": "Tăng Mana", "key": "4", "type": "buff"}         ← Hồi mana
]
```
**Auto sẽ**:
- Luân phiên 3 spell tấn công (1→2→3→1...)
- Định kỳ hồi mana (4)
- Timing Calculator tính cả 3 spell tấn công

---

## ❓ 6. CÂU HỎI THƯỜNG GẶP

### Q1: Tôi có 5 kỹ năng tấn công, auto có bấm hết không?
**A**: ✅ CÓ! Auto sẽ luân phiên bấm TẤT CẢ kỹ năng có `type: "attack"`.

### Q2: Tôi muốn chỉ dùng 2 kỹ năng tấn công thôi, làm sao?
**A**: Có 2 cách:
1. Xóa các skill không dùng khỏi `skill_slots`
2. Hoặc đổi `type` thành `"buff"` (nhưng sẽ bấm định kỳ)
3. **TỐT NHẤT**: Chỉ để 2 skill có `type: "attack"`

### Q3: Tôi có thể có nhiều buff không?
**A**: ✅ CÓ! Ví dụ:
```json
{"name": "Hồi Máu", "key": "4", "type": "buff"},
{"name": "Tăng Phòng Thủ", "key": "5", "type": "buff"},
{"name": "Tăng Tốc Độ", "key": "6", "type": "buff"}
```
Auto sẽ bấm cả 3 buff định kỳ, không ảnh hưởng timing tấn công.

### Q4: Buff có tính vào attack_interval không?
**A**: ❌ KHÔNG! Buff chạy riêng, không ảnh hưởng đến chu kỳ đánh quái.

### Q5: Nếu tôi không có buff thì sao?
**A**: ✅ OK! Auto vẫn chạy bình thường với chỉ attack skills.

---

## 🎯 7. TÓM TẮT CHO HỌC SINH LỚP 5

### 📌 Kỹ Năng CHÍNH (Attack):
- **Là gì**: Chiêu đánh quái
- **Auto làm gì**: Bấm lần lượt 1→2→3→1→2→3...
- **Timing Calculator**: CÓ TÍNH
- **Ví dụ**: Chém, đâm, phóng cầu lửa

### 📌 Kỹ Năng PHỤ (Buff):
- **Là gì**: Chiêu giúp nhân vật (hồi máu, tăng sức mạnh)
- **Auto làm gì**: Bấm định kỳ (cứ mỗi vài giây bấm 1 lần)
- **Timing Calculator**: KHÔNG TÍNH
- **Ví dụ**: Hồi máu, hồi mana, tăng phòng thủ

### 🎮 Khi Chạy Auto:
```
Nhân vật sẽ:
  ⚔️ Tay phải: Đánh quái (skill 1, 2, 3 luân phiên)
  🛡️ Tay trái: Tự hồi máu (skill 4 định kỳ)
  
→ Giống như bạn điều khiển 2 tay cùng lúc,
  nhưng máy tính làm giúp!
```

---

## 🔧 8. HƯỚNG DẪN SETUP

### Bước 1: Xác Định Kỹ Năng Của Bạn
```
Kỹ năng ĐÁNH QUÁI:
  ☐ Skill 1: ___________ (phím ___)
  ☐ Skill 2: ___________ (phím ___)
  ☐ Skill 3: ___________ (phím ___)

Kỹ năng PHỤ TRỢ:
  ☐ Skill 4: ___________ (phím ___)
  ☐ Skill 5: ___________ (phím ___)
```

### Bước 2: Sửa hunt_config.json
```json
"skill_slots": [
  {
    "name": "TÊN_KỸ_NĂNG_1",
    "key": "PHÍM",
    "type": "attack",          ← Nếu là skill đánh quái
    "cooldown": X.X,           ← Thời gian hồi chiêu
    "cast_time": X.X           ← Thời gian ra chiêu
  }
]
```

### Bước 3: Test
1. Chạy auto
2. Quan sát xem nhân vật có:
   - Luân phiên các skill tấn công? ✅
   - Tự hồi máu định kỳ? ✅
3. Nếu OK → Hoàn thành! 🎉

---

## ✅ KẾT LUẬN

**Kỹ năng CHÍNH** = Kỹ năng **TẤN CÔNG** (`type: "attack"`)
- Dùng để đánh quái
- Auto luân phiên bấm
- Timing Calculator dựa vào đây tính toán

**Kỹ năng KHÁC** = Kỹ năng **PHỤ TRỢ** (`type: "buff"`)
- Dùng để hỗ trợ nhân vật (hồi máu, tăng buff)
- Auto bấm định kỳ
- KHÔNG ảnh hưởng timing tấn công

**Cả 2 loại chạy SONG SONG** → Nhân vật vừa đánh quái vừa tự buff! 🚀
