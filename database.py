# -*- coding: utf-8 -*-
"""
Module quản lý CSDL SQLite cho ứng dụng Auto Bot.
Xử lý schema setup, data import, và các query hỗ trợ UI.
"""

import sqlite3
import json
import re
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional

# Set encoding for console output
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


class MonsterDatabase:
    """Quản lý kết nối và thao tác với database monsters.db"""
    
    DB_PATH = Path(__file__).parent / "monsters.db"
    DATA_FILE = Path(__file__).parent / "lib" / "data" / "monster-db-cabal.txt"
    
    # 30 cột chính xác cho bảng monsters
    MONSTER_COLUMNS = [
        'id', 'name', 'level', 'exp', 'hp', 'defense', 'attackRate', 
        'defenseRate', 'hpRecharge', 'accuracy', 'penetration', 
        'damageReduction', 'evasion', 'resistCritRate', 'primaryAttackMin', 
        'primaryAttackMax', 'secondaryAttackMin', 'secondaryAttackMax', 
        'ignoreAccuracy', 'ignoreDamageReduction', 'ignorePenetration', 
        'absoluteDamage', 'resistSkillAmp', 'resistCritDamage', 
        'resistSuppress', 'resistSilence', 'resistDiffDamage', 
        'hpProportionDamage', 'serverBossType', 'dungeonId'
    ]
    
    def __init__(self):
        """Khởi tạo database connection"""
        self.conn = None
        self._connect()
    
    def _connect(self) -> None:
        """Kết nối tới SQLite database"""
        self.conn = sqlite3.connect(str(self.DB_PATH))
        self.conn.row_factory = sqlite3.Row  # Cho phép truy cập column theo tên
        cursor = self.conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON;")
        self.conn.commit()
    
    def setup_schema(self) -> None:
        """Tạo schema bảng nếu chưa tồn tại"""
        cursor = self.conn.cursor()
        
        # Bảng dungeons
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS dungeons (
                dungeonId TEXT PRIMARY KEY,
                name TEXT
            )
        """)
        
        # Bảng monsters với 30 cột chính xác
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS monsters (
                id TEXT PRIMARY KEY,
                name TEXT,
                level INTEGER,
                exp INTEGER,
                hp INTEGER,
                defense INTEGER,
                attackRate INTEGER,
                defenseRate INTEGER,
                hpRecharge INTEGER,
                accuracy INTEGER,
                penetration INTEGER,
                damageReduction INTEGER,
                evasion INTEGER,
                resistCritRate INTEGER,
                primaryAttackMin INTEGER,
                primaryAttackMax INTEGER,
                secondaryAttackMin INTEGER,
                secondaryAttackMax INTEGER,
                ignoreAccuracy INTEGER,
                ignoreDamageReduction INTEGER,
                ignorePenetration INTEGER,
                absoluteDamage INTEGER,
                resistSkillAmp INTEGER,
                resistCritDamage INTEGER,
                resistSuppress INTEGER,
                resistSilence INTEGER,
                resistDiffDamage INTEGER,
                hpProportionDamage INTEGER,
                serverBossType INTEGER,
                dungeonId TEXT,
                FOREIGN KEY (dungeonId) REFERENCES dungeons(dungeonId) ON DELETE SET NULL
            )
        """)
        
        self.conn.commit()
    
    def _extract_json_from_webpack(self, content: str) -> str:
        """
        Trích xuất JSON từ webpack bundle format.
        Tìm pattern: JSON.parse('[...]')
        """
        match = re.search(r"JSON\.parse\('(.+?)'\)", content)
        if match:
            json_str = match.group(1)
            # Unescape escaped quotes nếu có
            json_str = json_str.replace("\\'", "'")
            return json_str
        return ""
    
    def _load_monsters_data(self) -> List[Dict[str, Any]]:
        """
        Load dữ liệu quái vật từ file JSON.
        Parse webpack format và trả về list of dicts.
        """
        if not self.DATA_FILE.exists():
            raise FileNotFoundError(f"File dữ liệu không tồn tại: {self.DATA_FILE}")
        
        with open(self.DATA_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Trích xuất JSON từ webpack bundle
        json_str = self._extract_json_from_webpack(content)
        
        if not json_str:
            raise ValueError("Không thể trích xuất JSON từ file dữ liệu")
        
        # Parse JSON
        monsters = json.loads(json_str)
        
        if not isinstance(monsters, list):
            raise ValueError("Dữ liệu JSON phải là list/array")
        
        return monsters
    
    def _import_dungeons(self, monsters_data: List[Dict[str, Any]]) -> None:
        """
        Import danh sách dungeons duy nhất từ monsters data.
        Quét tất cả monsters, lấy unique dungeonId, insert vào bảng dungeons.
        """
        cursor = self.conn.cursor()
        
        # Lấy tất cả unique dungeonId (không lấy None/null/empty string)
        dungeon_ids = set()
        for monster in monsters_data:
            dungeon_id = monster.get('dungeonId')
            if dungeon_id and dungeon_id.strip():  # Chỉ lấy giá trị không None/null/empty
                dungeon_ids.add(dungeon_id.strip())
        
        # Insert vào bảng dungeons
        for dungeon_id in dungeon_ids:
            cursor.execute("""
                INSERT OR IGNORE INTO dungeons (dungeonId, name)
                VALUES (?, ?)
            """, (dungeon_id, dungeon_id))  # Dùng dungeonId làm name mặc định
        
        self.conn.commit()
    
    def _import_monsters(self, monsters_data: List[Dict[str, Any]]) -> None:
        """
        Import danh sách quái vật vào bảng monsters.
        Dùng executemany() để tăng tốc độ nạp dữ liệu trong 1 transaction.
        """
        cursor = self.conn.cursor()
        
        # Chuẩn bị dữ liệu cho insert
        insert_data = []
        for monster in monsters_data:
            row_data = {}
            for col in self.MONSTER_COLUMNS:
                val = monster.get(col)
                # Xử lý dungeonId: nếu empty string hoặc None, set thành None
                if col == 'dungeonId':
                    if val and isinstance(val, str) and val.strip():
                        row_data[col] = val.strip()
                    else:
                        row_data[col] = None
                else:
                    # Các cột khác: sử dụng giá trị mặc định
                    if col in ('name', 'id') and not val:
                        row_data[col] = ''
                    else:
                        row_data[col] = val if val is not None else 0
            
            row = tuple(row_data.get(col) for col in self.MONSTER_COLUMNS)
            insert_data.append(row)
        
        # Tạo placeholders cho INSERT
        placeholders = ','.join(['?'] * len(self.MONSTER_COLUMNS))
        columns_str = ','.join(self.MONSTER_COLUMNS)
        
        query = f"INSERT OR REPLACE INTO monsters ({columns_str}) VALUES ({placeholders})"
        
        # Insert tất cả trong 1 transaction
        cursor.executemany(query, insert_data)
        self.conn.commit()
        
        print(f"[SUCCESS] Da import thanh cong {len(insert_data)} quai vat vao CSDL.")
    
    def init_database_data(self) -> None:
        """
        Tự động khởi tạo schema và import dữ liệu nếu chưa có.
        Gọi hàm này khi ứng dụng khởi động.
        """
        # Setup schema nếu chưa tồn tại
        self.setup_schema()
        
        cursor = self.conn.cursor()
        
        # Kiểm tra nếu bảng monsters đã có dữ liệu
        cursor.execute("SELECT COUNT(*) as count FROM monsters")
        count = cursor.fetchone()['count']
        
        if count > 0:
            print("[INFO] Database da co du lieu, bo qua import.")
            return
        
        # Load dữ liệu từ file
        try:
            monsters_data = self._load_monsters_data()
            print(f"[INFO] Loaded {len(monsters_data)} quai vat tu file du lieu.")
        except Exception as e:
            print(f"[ERROR] Loi khi load du lieu: {e}")
            return
        
        # Bước A: Import Dungeons trước
        try:
            self._import_dungeons(monsters_data)
            print("[SUCCESS] Da import dungeons thanh cong.")
        except Exception as e:
            print(f"[ERROR] Loi khi import dungeons: {e}")
        
        # Bước B: Import Monsters
        try:
            self._import_monsters(monsters_data)
        except Exception as e:
            print(f"[ERROR] Loi khi import monsters: {e}")
    
    def get_all_monsters(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Lấy danh sách toàn bộ quái vật (id, name, level, hp).
        Dùng để load lên UI.
        
        Args:
            limit: Giới hạn số lượng bản ghi (default 100)
            
        Returns:
            List of dicts chứa: id, name, level, hp
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, name, level, hp FROM monsters
            LIMIT ?
        """, (limit,))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_monster_by_id(self, monster_id: str) -> Optional[Dict[str, Any]]:
        """
        Lấy đầy đủ thông tin quái vật theo ID.
        Trả về Dict chứa tất cả 30 chỉ số để Bot xử lý đánh tự động.
        
        Args:
            monster_id: ID của quái vật
            
        Returns:
            Dict chứa toàn bộ 30 columns, hoặc None nếu không tìm thấy
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM monsters WHERE id = ?
        """, (monster_id,))
        
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def search_monsters(self, keyword: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Tìm kiếm quái vật theo tên (LIKE search).
        
        Args:
            keyword: Từ khóa tìm kiếm
            limit: Giới hạn số lượng kết quả
            
        Returns:
            List of dicts chứa: id, name, level, hp
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, name, level, hp FROM monsters
            WHERE name LIKE ?
            LIMIT ?
        """, (f"%{keyword}%", limit))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def close(self) -> None:
        """Đóng kết nối database"""
        if self.conn:
            self.conn.close()


# Global instance
_db_instance: Optional[MonsterDatabase] = None


def get_db() -> MonsterDatabase:
    """
    Lấy singleton instance của MonsterDatabase.
    Khởi tạo lần đầu tiên nếu chưa tồn tại.
    """
    global _db_instance
    if _db_instance is None:
        _db_instance = MonsterDatabase()
        _db_instance.init_database_data()
    return _db_instance


def close_db() -> None:
    """Đóng database connection"""
    global _db_instance
    if _db_instance:
        _db_instance.close()
        _db_instance = None


# ============================================================================
# Convenience Functions (API đơn giản để sử dụng trong app)
# ============================================================================

def init_database() -> None:
    """Khởi tạo database khi ứng dụng start"""
    get_db()


def get_all_monsters(limit: int = 100) -> List[Dict[str, Any]]:
    """Lấy danh sách quái vật"""
    return get_db().get_all_monsters(limit)


def get_monster_by_id(monster_id: str) -> Optional[Dict[str, Any]]:
    """Lấy thông tin chi tiết quái vật theo ID"""
    return get_db().get_monster_by_id(monster_id)


def search_monsters(keyword: str, limit: int = 50) -> List[Dict[str, Any]]:
    """Tìm kiếm quái vật theo tên"""
    return get_db().search_monsters(keyword, limit)
