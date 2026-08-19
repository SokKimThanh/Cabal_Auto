-- Bật tính năng kiểm tra khóa ngoại (Foreign Key) trong SQLite
PRAGMA foreign_keys = ON;

-- Xóa các bảng cũ nếu chúng đã tồn tại (Lưu ý: Xóa bảng con trước, bảng cha sau)
DROP TABLE IF EXISTS monsters;
DROP TABLE IF EXISTS dungeons;
DROP TABLE IF EXISTS monster_type;

-- 1. Bảng lưu trữ hầm ngục/khu vực (Dungeons) - Đồng bộ với database.py
CREATE TABLE dungeons (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL
);

-- 2. Bảng phân loại quái vật (Monster Type)
CREATE TABLE monster_type (
    value TEXT PRIMARY KEY,
    label TEXT NOT NULL
);

-- 3. Bảng lưu trữ thông tin chi tiết của quái vật (Monsters) sử dụng dungeonId
CREATE TABLE monsters (
    id TEXT PRIMARY KEY,
    name TEXT,
    level INTEGER DEFAULT 0,
    exp INTEGER DEFAULT 0,
    hp INTEGER DEFAULT 0,
    defense INTEGER DEFAULT 0,
    attackRate INTEGER DEFAULT 0,
    defenseRate INTEGER DEFAULT 0,
    hpRecharge INTEGER DEFAULT 0,
    accuracy INTEGER DEFAULT 0,
    penetration INTEGER DEFAULT 0,
    damageReduction INTEGER DEFAULT 0,
    evasion INTEGER DEFAULT 0,
    resistCritRate INTEGER DEFAULT 0,
    primaryAttackMin INTEGER DEFAULT 0,
    primaryAttackMax INTEGER DEFAULT 0,
    secondaryAttackMin INTEGER DEFAULT 0,
    secondaryAttackMax INTEGER DEFAULT 0,
    ignoreAccuracy INTEGER DEFAULT 0,
    ignoreDamageReduction INTEGER DEFAULT 0,
    ignorePenetration INTEGER DEFAULT 0,
    absoluteDamage INTEGER DEFAULT 0,
    resistSkillAmp INTEGER DEFAULT 0,
    resistCritDamage INTEGER DEFAULT 0,
    resistSuppress INTEGER DEFAULT 0,
    resistSilence INTEGER DEFAULT 0,
    resistDiffDamage INTEGER DEFAULT 0,
    hpProportionDamage INTEGER DEFAULT 0,
    
    -- Cột liên kết (Foreign Keys)
    serverBossType TEXT,
    dungeonId TEXT,
    
    -- Định nghĩa ràng buộc khóa ngoại tới bảng dungeons và monster_type
    FOREIGN KEY (dungeonId) REFERENCES dungeons(id) ON DELETE SET NULL,
    FOREIGN KEY (serverBossType) REFERENCES monster_type(value) ON DELETE SET NULL
);

-- 4. Tạo Index (Chỉ mục) để tăng tốc độ tìm kiếm và JOIN
CREATE INDEX IF NOT EXISTS idx_monsters_dungeonId ON monsters(dungeonId);
CREATE INDEX IF NOT EXISTS idx_monsters_serverBossType ON monsters(serverBossType);