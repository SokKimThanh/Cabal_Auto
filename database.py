# -*- coding: utf-8 -*-
"""
Module quản lý CSDL SQLite cho ứng dụng Auto Bot.
Xử lý schema setup, data import, và các query hỗ trợ UI.
"""

import sqlite3
import json
import math
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
    LOCATION_FILE = Path(__file__).parent / "lib" / "data" / "location-db-cabal.txt"
    MONSTER_TYPE_FILE = Path(__file__).parent / "lib" / "data" / "type-monster-db-cabal.txt"
    
    # Bảng bắt buộc phải tồn tại trong CSDL
    REQUIRED_TABLES = ['monsters', 'dungeons', 'location', 'monster_type']
    
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

        # Bảng location: lưu danh sách các vị trí/khu vực trong game
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS location (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL
            )
        """)

        # Bảng monster_type: lưu các loại quái vật
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS monster_type (
                value TEXT PRIMARY KEY,
                label TEXT NOT NULL
            )
        """)
        
        self.conn.commit()

    def _seed_location(self) -> None:
        """Đọc file location-db-cabal.txt và chèn dữ liệu vào bảng location (nếu chưa có)."""
        if not self.LOCATION_FILE.exists():
            print(f"[DB] Bỏ qua seed location: không tìm thấy {self.LOCATION_FILE}")
            return

        with open(self.LOCATION_FILE, 'r', encoding='utf-8') as f:
            content = f.read()

        # Parse các cặp id: "name" từ webpack bundle format
        entries = re.findall(r'(\d+):\s*"([^"]+)"', content)
        if not entries:
            print("[DB] Không tìm thấy dữ liệu location trong file.")
            return

        with sqlite3.connect(str(self.DB_PATH)) as conn:
            cursor = conn.cursor()
            cursor.executemany(
                "INSERT OR IGNORE INTO location (id, name) VALUES (?, ?)",
                [(int(loc_id), name) for loc_id, name in entries]
            )
            conn.commit()
        print(f"[DB] Seed location: đã xử lý {len(entries)} bản ghi.")

    def _seed_monster_type(self) -> None:
        """Đọc file type-monster-db-cabal.txt và chèn dữ liệu vào bảng monster_type (nếu chưa có)."""
        if not self.MONSTER_TYPE_FILE.exists():
            print(f"[DB] Bỏ qua seed monster_type: không tìm thấy {self.MONSTER_TYPE_FILE}")
            return

        with open(self.MONSTER_TYPE_FILE, 'r', encoding='utf-8') as f:
            content = f.read()

        # Parse các cặp value/label từ format: {value: "X", label: "Y"}
        entries = re.findall(r'value:\s*"([^"]+)"[^}]*label:\s*"([^"]+)"', content)
        if not entries:
            print("[DB] Không tìm thấy dữ liệu monster_type trong file.")
            return

        # Bỏ qua entry "all" vì không phải type cụ thể
        filtered = [(v, label) for v, label in entries if v != 'all']

        with sqlite3.connect(str(self.DB_PATH)) as conn:
            cursor = conn.cursor()
            cursor.executemany(
                "INSERT OR IGNORE INTO monster_type (value, label) VALUES (?, ?)",
                filtered
            )
            conn.commit()
        print(f"[DB] Seed monster_type: đã xử lý {len(filtered)} bản ghi.")

    def seed_reference_data(self) -> None:
        """Seed dữ liệu tham chiếu cho location và monster_type nếu bảng còn trống."""
        cursor = self.conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM location")
        if cursor.fetchone()[0] == 0:
            self._seed_location()

        cursor.execute("SELECT COUNT(*) FROM monster_type")
        if cursor.fetchone()[0] == 0:
            self._seed_monster_type()

    def init_db(self) -> None:
        """Khởi tạo database schema và seed dữ liệu tham chiếu."""
        self.setup_schema()
        self.seed_reference_data()
    
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
        Tự động khởi tạo schema.
        Gọi hàm này khi ứng dụng khởi động.
        """
        self.init_db()
    
    def get_monster_types(self) -> List[Any]:
        """Lấy danh sách các serverBossType distinct dùng cho filter Monster Type."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT DISTINCT serverBossType
            FROM monsters
            WHERE serverBossType IS NOT NULL AND serverBossType != ''
            ORDER BY serverBossType
        """)
        return [row[0] for row in cursor.fetchall()]

    def get_locations(self) -> List[Any]:
        """Lấy danh sách location/dungeonId từ bảng dungeons."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT DISTINCT dungeonId
            FROM dungeons
            WHERE dungeonId IS NOT NULL AND dungeonId != ''
            ORDER BY dungeonId
        """)
        return [row[0] for row in cursor.fetchall()]

    def get_filtered_monsters(
        self,
        keyword: str = '',
        monster_type: Optional[str] = None,
        location: Optional[str] = None,
        page: int = 1,
        page_size: int = 25,
        sort_column: str = 'name',
        sort_order: str = 'ASC',
    ) -> Dict[str, Any]:
        """Lấy danh sách quái vật theo filter, toàn bộ dữ liệu đã được sanitize và phân trang."""
        safe_page = max(1, int(page or 1))
        safe_page_size = max(1, int(page_size or 25))
        allowed_columns = {
            'name', 'level', 'hp', 'defense', 'defenseRate',
            'ignorePenetration', 'resistCritRate', 'resistSkillAmp', 'resistCritDamage'
        }
        safe_sort_column = sort_column if sort_column in allowed_columns else 'name'
        safe_sort_order = str(sort_order or 'ASC').upper()
        if safe_sort_order not in {'ASC', 'DESC'}:
            safe_sort_order = 'ASC'

        filters: List[str] = []
        params: List[Any] = []

        if keyword and str(keyword).strip():
            filters.append('name LIKE ?')
            params.append(f"%{str(keyword).strip()}%")

        if monster_type and str(monster_type).strip() not in ('All Monsters', 'All', ''):
            filters.append('serverBossType = ?')
            params.append(str(monster_type).strip())

        if location and str(location).strip() not in ('All Locations', 'All', ''):
            filters.append('dungeonId = ?')
            params.append(str(location).strip())

        where_clause = (f" WHERE {' AND '.join(filters)}" if filters else '')

        count_query = f"SELECT COUNT(*) AS total FROM monsters{where_clause}"
        cursor = self.conn.cursor()
        cursor.execute(count_query, params)
        total_records = int(cursor.fetchone()['total'] or 0)
        total_pages = max(1, math.ceil(total_records / safe_page_size)) if total_records else 1

        offset = (safe_page - 1) * safe_page_size
        sql = (
            f"SELECT * FROM monsters{where_clause} "
            f"ORDER BY {safe_sort_column} {safe_sort_order} "
            f"LIMIT ? OFFSET ?"
        )
        cursor.execute(sql, params + [safe_page_size, offset])
        items = [dict(row) for row in cursor.fetchall()]

        return {
            'items': items,
            'total_records': total_records,
            'total_pages': total_pages,
        }

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
        _db_instance.init_db()
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


def get_monster_types() -> List[Any]:
    """Lấy danh sách type toàn bộ quái vật."""
    return get_db().get_monster_types()


def get_locations() -> List[Any]:
    """Lấy danh sách location/dungeonId."""
    return get_db().get_locations()


def get_filtered_monsters(
    keyword: str = '',
    monster_type: Optional[str] = None,
    location: Optional[str] = None,
    page: int = 1,
    page_size: int = 25,
    sort_column: str = 'name',
    sort_order: str = 'ASC',
) -> Dict[str, Any]:
    """Lấy danh sách quái vật theo filter, phân trang và sắp xếp an toàn."""
    return get_db().get_filtered_monsters(
        keyword=keyword,
        monster_type=monster_type,
        location=location,
        page=page,
        page_size=page_size,
        sort_column=sort_column,
        sort_order=sort_order,
    )


def check_db_health() -> Dict[str, Any]:
        """
        Kiểm tra tình trạng hoàn chỉnh của CSDL monsters.db.

        Returns:
            dict với các keys:
                - ok (bool): True nếu CSDL đầy đủ
                - missing_tables (list): danh sách bảng bị thiếu
                - counts (dict): số bản ghi của từng bảng (chỉ khi ok=True)
                - error (str | None): mô tả lỗi nếu có
        """
        db_path = MonsterDatabase.DB_PATH
        required = MonsterDatabase.REQUIRED_TABLES

        if not db_path.exists():
            return {
                'ok': False,
                'missing_tables': required,
                'counts': {},
                'error': f"Không tìm thấy file CSDL: {db_path}",
            }

        try:
            with sqlite3.connect(str(db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                existing = {row[0] for row in cursor.fetchall()}

            missing = [t for t in required if t not in existing]
            if missing:
                return {
                    'ok': False,
                    'missing_tables': missing,
                    'counts': {},
                    'error': None,
                }

            # CSDL đầy đủ — đếm bản ghi từng bảng
            counts: Dict[str, int] = {}
            with sqlite3.connect(str(db_path)) as conn:
                cursor = conn.cursor()
                for table in required:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    counts[table] = cursor.fetchone()[0]

            return {
                'ok': True,
                'missing_tables': [],
                'counts': counts,
                'error': None,
            }
        except Exception as exc:
            return {
                'ok': False,
                'missing_tables': required,
                'counts': {},
                'error': str(exc),
            }
