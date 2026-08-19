# Database Module Documentation

Module Python `database.py` quản lý CSDL SQLite cho ứng dụng Auto Bot.

## Cấu trúc Database

### Bảng: `dungeons`
- `dungeonId` (TEXT PRIMARY KEY): ID dungeon
- `name` (TEXT): Tên dungeon

### Bảng: `monsters` (30 columns)
**Core Fields:**
- `id` (TEXT PRIMARY KEY): ID quái vật
- `name` (TEXT): Tên quái vật
- `dungeonId` (TEXT FK): Foreign Key liên kết `dungeons(dungeonId)`

**Stats Fields:**
- `level`, `exp`, `hp`, `defense`
- `attackRate`, `defenseRate`, `hpRecharge`, `accuracy`
- `penetration`, `damageReduction`, `evasion`, `resistCritRate`

**Attack Fields:**
- `primaryAttackMin`, `primaryAttackMax`
- `secondaryAttackMin`, `secondaryAttackMax`

**Resistance Fields:**
- `ignoreAccuracy`, `ignoreDamageReduction`, `ignorePenetration`
- `absoluteDamage`, `resistSkillAmp`, `resistCritDamage`
- `resistSuppress`, `resistSilence`, `resistDiffDamage`
- `hpProportionDamage`, `serverBossType`

## Sử dụng

### 1. Khởi tạo Database khi ứng dụng start

```python
from database import init_database

# Gọi hàm này khi app khởi động
# Nó sẽ:
# - Tạo schema nếu chưa tồn tại
# - Import dữ liệu từ file monster-db-cabal.txt (nếu chưa có)
# - Kích hoạt PRAGMA foreign_keys = ON
init_database()
```

### 2. Lấy danh sách quái vật

```python
from database import get_all_monsters

# Lấy 100 quái vật đầu tiên (mặc định)
monsters = get_all_monsters()

# Lấy 5 quái vật đầu tiên
monsters = get_all_monsters(limit=5)

# Mỗi object có: id, name, level, hp
for m in monsters:
    print(f"{m['id']}: {m['name']} Lv.{m['level']} HP:{m['hp']}")
```

### 3. Lấy thông tin chi tiết quái vật

```python
from database import get_monster_by_id

# Lấy tất cả 30 chỉ số của quái vật
monster = get_monster_by_id('1')  # Nipperlug

if monster:
    print(f"Name: {monster['name']}")
    print(f"Level: {monster['level']}")
    print(f"HP: {monster['hp']}")
    print(f"Attack Min: {monster['primaryAttackMin']}")
    print(f"Attack Max: {monster['primaryAttackMax']}")
    print(f"Dungeon ID: {monster['dungeonId']}")
```

### 4. Tìm kiếm quái theo tên

```python
from database import search_monsters

# Tìm quái có tên chứa "Lug"
results = search_monsters('Lug', limit=10)

for m in results:
    print(f"{m['id']}: {m['name']} Lv.{m['level']}")
```

### 5. Sử dụng Direct Class (Advanced)

```python
from database import MonsterDatabase

# Tạo instance trực tiếp
db = MonsterDatabase()
db.setup_schema()
db.init_database_data()

# Các phương thức sẵn có
all_monsters = db.get_all_monsters(limit=50)
monster = db.get_monster_by_id('1')
search_results = db.search_monsters('Queen', limit=20)

db.close()  # Đóng kết nối
```

## Thông tin Import Dữ liệu

**Nguồn dữ liệu:** `lib/data/monster-db-cabal.txt`
- Định dạng: JSON array được wrap trong webpack format
- Tự động parse và extract JSON từ webpack bundle
- Import flow:
  1. Quét tất cả `dungeonId` duy nhất từ monsters
  2. Insert vào bảng `dungeons` trước
  3. Insert tất cả monsters vào bảng `monsters` (dùng `executemany()`)
  4. Nếu monsters thiếu field nào, dùng giá trị mặc định (0 hoặc "")

**Điều kiện chạy import:**
- Chỉ chạy nếu bảng `monsters` còn trống
- Nếu đã có dữ liệu, bỏ qua import

**Thống kê hiện tại:**
- Total monsters: 3948
- Total dungeons: 70

## Database Location

Database file lưu tại: `monsters.db` (cùng thư mục với `database.py`)

## Error Handling

Tất cả các hàm đã có error handling:
- `get_monster_by_id()` trả về `None` nếu không tìm thấy
- `search_monsters()` trả về empty list nếu không có kết quả
- Import process có try-catch và in log thích hợp

## Performance Notes

- Database dùng `sqlite3.Row` factory để truy cập column theo tên
- `executemany()` được dùng để import bulk data trong 1 transaction
- Foreign keys được kích hoạt: `PRAGMA foreign_keys = ON;`
- Tất cả queries được optimize để lấy chỉ columns cần thiết
