# -*- coding: utf-8 -*-
"""
Module quản lý CSDL SQLite cho ứng dụng Auto Bot.
Xử lý schema setup, data import, và các query hỗ trợ UI.
Sử dụng bảng `dungeons` và khóa ngoại `dungeonId` trong bảng `monsters`.
"""

import sqlite3
import json
import math
import re
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional

# Đảm bảo encoding utf-8 cho console output trên Windows
if sys.stdout.encoding != "utf-8":
    import io

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")


class MonsterDatabase:
    """Quản lý kết nối và thao tác với database monsters.db"""

    DB_PATH = Path(__file__).parent / "monsters.db"
    DATA_FILE = Path(__file__).parent / "lib" / "data" / "monster-db-cabal.txt"
    LOCATION_FILE = Path(__file__).parent / "lib" / "data" / "location-db-cabal.txt"
    MONSTER_TYPE_FILE = (
        Path(__file__).parent / "lib" / "data" / "type-monster-db-cabal.txt"
    )

    REQUIRED_TABLES = ["monsters", "dungeons", "monster_type"]

    MONSTER_COLUMNS = [
        "id",
        "name",
        "level",
        "exp",
        "hp",
        "defense",
        "attackRate",
        "defenseRate",
        "hpRecharge",
        "accuracy",
        "penetration",
        "damageReduction",
        "evasion",
        "resistCritRate",
        "primaryAttackMin",
        "primaryAttackMax",
        "secondaryAttackMin",
        "secondaryAttackMax",
        "ignoreAccuracy",
        "ignoreDamageReduction",
        "ignorePenetration",
        "absoluteDamage",
        "resistSkillAmp",
        "resistCritDamage",
        "resistSuppress",
        "resistSilence",
        "resistDiffDamage",
        "hpProportionDamage",
        "serverBossType",
        "dungeonId",
    ]

    def __init__(self):
        """Khởi tạo database connection"""
        self.conn = None
        self._connect()

    def _connect(self) -> None:
        """Kết nối tới SQLite database và thiết lập Pragma"""
        self.conn = sqlite3.connect(str(self.DB_PATH))
        self.conn.row_factory = sqlite3.Row  # Cho phép truy cập column theo tên
        cursor = self.conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON;")
        self.conn.commit()

    def setup_schema(self) -> None:
        """Tạo schema bảng với bảng dungeons và dungeonId trong monsters"""
        cursor = self.conn.cursor()

        try:
            from lib.db.schema import setup_skills_schema

            setup_skills_schema(self.conn)
        except ImportError as e:
            print(f"[DB] Could not setup skills schema: {e}")

        # Bảng translations
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS translations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                namespace TEXT NOT NULL,
                key TEXT NOT NULL,
                lang TEXT NOT NULL,
                text TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                UNIQUE(namespace, key, lang)
            )
        """)

        # Bảng dungeons (thay thế cho locations cũ)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS dungeons (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL
            )
        """)

        # Bảng monster_type sử dụng 'value' làm PRIMARY KEY theo nguyên bản
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS monster_type (
                value TEXT PRIMARY KEY,
                label TEXT NOT NULL
            )
        """)

        # Bảng monsters với dungeonId là khóa ngoại liên kết tới bảng dungeons
        cursor.execute("""
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
                serverBossType TEXT,
                dungeonId TEXT,
                FOREIGN KEY (dungeonId) REFERENCES dungeons(id) ON DELETE SET NULL,
                FOREIGN KEY (serverBossType) REFERENCES monster_type(value) ON DELETE SET NULL
            )
        """)

        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_monsters_dungeonId ON monsters(dungeonId);"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_monsters_serverBossType ON monsters(serverBossType);"
        )

        self.conn.commit()

    def _seed_dungeons(self) -> None:
        """Đọc file location-db-cabal.txt và chèn dữ liệu vào bảng dungeons."""
        if not self.LOCATION_FILE.exists():
            print(f"[DB] Bỏ qua seed dungeons: không tìm thấy {self.LOCATION_FILE}")
            return

        with open(self.LOCATION_FILE, "r", encoding="utf-8") as f:
            content = f.read()

        entries = re.findall(r'(\w+):\s*"([^"]+)"', content)
        if not entries:
            print("[DB] Không tìm thấy dữ liệu dungeons trong file.")
            return

        cursor = self.conn.cursor()
        cursor.executemany(
            "INSERT OR IGNORE INTO dungeons (id, name) VALUES (?, ?)",
            [(str(loc_id), name) for loc_id, name in entries],
        )
        self.conn.commit()
        print(f"[DB] Seed dungeons: đã xử lý {len(entries)} bản ghi.")

    def _seed_monster_type(self) -> None:
        """Đọc file type-monster-db-cabal.txt và chèn dữ liệu vào bảng monster_type."""
        if not self.MONSTER_TYPE_FILE.exists():
            print(
                f"[DB] Bỏ qua seed monster_type: không tìm thấy {self.MONSTER_TYPE_FILE}"
            )
            return

        with open(self.MONSTER_TYPE_FILE, "r", encoding="utf-8") as f:
            content = f.read()

        entries = re.findall(r'value:\s*"([^"]+)"[^}]*label:\s*"([^"]+)"', content)
        if not entries:
            print("[DB] Không tìm thấy dữ liệu monster_type trong file.")
            return

        filtered = [(v, label) for v, label in entries if v != "all"]

        cursor = self.conn.cursor()
        default_types = [("0", "Normal"), ("1", "Boss")]
        cursor.executemany(
            "INSERT OR IGNORE INTO monster_type (value, label) VALUES (?, ?)",
            default_types + filtered,
        )
        self.conn.commit()
        print(f"[DB] Seed monster_type: đã xử lý {len(filtered)} bản ghi.")

    def seed_reference_data(self) -> None:
        """Seed dữ liệu tham chiếu cho dungeons và monster_type nếu bảng còn trống."""
        cursor = self.conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM dungeons")
        if cursor.fetchone()[0] == 0:
            self._seed_dungeons()

        cursor.execute("SELECT COUNT(*) FROM monster_type")
        if cursor.fetchone()[0] == 0:
            self._seed_monster_type()

    def init_db(self) -> None:
        """Khởi tạo database schema và seed dữ liệu tham chiếu."""
        self.setup_schema()
        self.seed_reference_data()

    def _extract_json_from_webpack(self, content: str) -> str:
        start = content.find("JSON.parse('")
        if start == -1:
            return ""
        start += len("JSON.parse('")
        # Tìm vị trí của dấu nháy đơn + dấu đóng ngoặc (')
        # Lưu ý: Tìm từ vị trí start để không nhầm với JSON bên trong
        end = content.find("')", start)
        if end == -1:
            return ""
        json_str = content[start:end]
        # Thay thế escape sequences
        json_str = json_str.replace("\\'", "'").replace('\\"', '"')
        return json_str

    def load_monsters_data(self) -> List[Dict[str, Any]]:
        """Load dữ liệu quái vật từ file JSON."""
        if not self.DATA_FILE.exists():
            raise FileNotFoundError(f"File dữ liệu không tồn tại: {self.DATA_FILE}")

        with open(self.DATA_FILE, "r", encoding="utf-8") as f:
            content = f.read()

        json_str = self._extract_json_from_webpack(content)
        if not json_str:
            raise ValueError("Không thể trích xuất JSON hợp lệ từ file dữ liệu.")

        try:
            monsters = json.loads(json_str)
        except json.JSONDecodeError as e:
            raise ValueError(f"Lỗi parse JSON: {e}")

        if not isinstance(monsters, list):
            raise ValueError("Dữ liệu JSON gốc phải là danh sách (list/array).")

        return monsters

    def import_dungeons_from_monsters(
        self, monsters_data: List[Dict[str, Any]]
    ) -> None:
        """Import tự động các dungeonId phát sinh từ danh sách monsters nếu chưa có trong bảng dungeons."""
        cursor = self.conn.cursor()
        dungeon_ids = set()

        for monster in monsters_data:
            d_id = monster.get("dungeonId") or monster.get("locationId")
            if d_id and str(d_id).strip():
                dungeon_ids.add(str(d_id).strip())

        cursor.executemany(
            """
            INSERT OR IGNORE INTO dungeons (id, name)
            VALUES (?, ?)
        """,
            ((d_id, d_id) for d_id in dungeon_ids),
        )

        self.conn.commit()

    def import_monsters(self, monsters_data: List[Dict[str, Any]]) -> None:
        """Import danh sách quái vật vào bảng monsters sử dụng dungeonId."""
        cursor = self.conn.cursor()
        insert_data = []

        for monster in monsters_data:
            row_data = {}
            for col in self.MONSTER_COLUMNS:
                val = monster.get(col)

                # Fallback: nếu dungeonId trống, thử lấy từ locationId
                if not val and col == "dungeonId":
                    val = monster.get("locationId")

                if col == "dungeonId":
                    # Giữ giá trị nếu không phải None và không rỗng, kể cả '0'
                    if val is not None and str(val).strip() != "":
                        row_data[col] = str(val).strip()
                    else:
                        row_data[col] = None

                elif col == "serverBossType":
                    # Giữ giá trị nếu không phải None và không rỗng, kể cả '0'
                    if val is not None and str(val).strip() != "":
                        row_data[col] = str(val).strip()
                    else:
                        row_data[col] = None

                else:
                    if col in ("name", "id") and not val:
                        row_data[col] = ""
                    else:
                        row_data[col] = val if val is not None else 0

            row = tuple(row_data.get(col) for col in self.MONSTER_COLUMNS)
            insert_data.append(row)

        placeholders = ",".join(["?"] * len(self.MONSTER_COLUMNS))
        columns_str = ",".join(self.MONSTER_COLUMNS)
        query = (
            f"INSERT OR REPLACE INTO monsters ({columns_str}) VALUES ({placeholders})"
        )

        cursor.executemany(query, insert_data)
        self.conn.commit()
        print(
            f"[DB] Đã import thành công {len(insert_data)} quái vật vào bảng monsters."
        )

    def get_monster_types(self) -> List[Any]:
        """Lấy danh sách các serverBossType distinct."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT DISTINCT serverBossType
            FROM monsters
            WHERE serverBossType IS NOT NULL AND serverBossType != ''
            ORDER BY serverBossType
        """)
        return [row[0] for row in cursor.fetchall()]

    def get_monster_type_list(self) -> List[Dict[str, str]]:
        """Trả về danh sách loại quái dạng [{'value': '1', 'label': 'Boss'}, ...]"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT value, label FROM monster_type ORDER BY value")
        return [{"value": row[0], "label": row[1]} for row in cursor.fetchall()]

    def get_dungeons(self) -> List[Any]:
        """Lấy danh sách dungeonId từ bảng dungeons."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id
            FROM dungeons
            ORDER BY id
        """)
        return [row[0] for row in cursor.fetchall()]

    def get_filtered_monsters(
        self,
        keyword: str = "",
        monster_type: Optional[str] = None,
        dungeon_id: Optional[str] = None,
        page: int = 1,
        page_size: int = 25,
        sort_column: str = "name",
        sort_order: str = "ASC",
    ) -> Dict[str, Any]:
        """Lấy danh sách quái vật theo filter sử dụng dungeonId có phân trang."""
        safe_page = max(1, int(page or 1))
        safe_page_size = max(1, int(page_size or 25))
        allowed_columns = {
            "name",
            "level",
            "hp",
            "defense",
            "defenseRate",
            "ignorePenetration",
            "resistCritRate",
            "resistSkillAmp",
            "resistCritDamage",
        }
        safe_sort_column = sort_column if sort_column in allowed_columns else "name"
        safe_sort_order = str(sort_order or "ASC").upper()
        if safe_sort_order not in {"ASC", "DESC"}:
            safe_sort_order = "ASC"

        filters: List[str] = []
        params: List[Any] = []

        if keyword and str(keyword).strip():
            filters.append("name LIKE ?")
            params.append(f"%{str(keyword).strip()}%")

        if monster_type and str(monster_type).strip() not in (
            "All Monsters",
            "All",
            "",
        ):
            filters.append("serverBossType = ?")
            params.append(str(monster_type).strip())

        if dungeon_id and str(dungeon_id).strip() not in ("All Dungeons", "All", ""):
            filters.append("dungeonId = ?")
            params.append(str(dungeon_id).strip())

        where_clause = f" WHERE {' AND '.join(filters)}" if filters else ""

        cursor = self.conn.cursor()

        count_query = (
            f"SELECT COUNT(*) AS total FROM monsters{where_clause}"  # nosec B608
        )
        cursor.execute(count_query, params)
        total_records = int(cursor.fetchone()["total"] or 0)
        total_pages = (
            max(1, math.ceil(total_records / safe_page_size)) if total_records else 1
        )

        offset = (safe_page - 1) * safe_page_size
        sql = f"SELECT * FROM monsters{where_clause} ORDER BY {safe_sort_column} {safe_sort_order} LIMIT ? OFFSET ?"  # nosec B608
        cursor.execute(sql, params + [safe_page_size, offset])

        return {
            "items": [dict(row) for row in cursor.fetchall()],
            "total_records": total_records,
            "total_pages": total_pages,
        }

    def get_all_monsters(self, limit: int = 100) -> List[Dict[str, Any]]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, name, level, hp FROM monsters LIMIT ?", (limit,))
        return [dict(row) for row in cursor.fetchall()]

    def get_monster_by_id(self, monster_id: str) -> Optional[Dict[str, Any]]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM monsters WHERE id = ?", (monster_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def search_monsters(self, keyword: str, limit: int = 50) -> List[Dict[str, Any]]:
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT id, name, level, hp FROM monsters
            WHERE name LIKE ? LIMIT ?
        """,
            (f"%{keyword}%", limit),
        )
        return [dict(row) for row in cursor.fetchall()]

    def close(self) -> None:
        if self.conn:
            self.conn.close()

    def get_dungeon_list(self) -> List[Dict[str, str]]:
        """Trả về danh sách dungeon dạng [{'id': '1', 'name': 'Bloody Ice'}, ...]"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, name FROM dungeons ORDER BY id")
        return [{"id": row[0], "name": row[1]} for row in cursor.fetchall()]

    # Thêm
    def insert_or_update_monster(self, monster: Dict[str, Any]) -> bool:
        """Chèn hoặc cập nhật một quái vật (INSERT OR REPLACE)"""
        columns = self.MONSTER_COLUMNS
        # Lọc các trường có trong bảng
        data = {k: v for k, v in monster.items() if k in columns}
        # Xử lý giá trị rỗng cho dungeonId và serverBossType
        for col in ("dungeonId", "serverBossType"):
            if col in data and (data[col] is None or str(data[col]).strip() == ""):
                data[col] = None
        if not data.get("id"):
            print("[DB] Lỗi insert/update monster: missing 'id'")
            return False
        # Đảm bảo các trường số có giá trị mặc định
        for col in columns:
            if col not in data:
                data[col] = "" if col == "name" else 0
        placeholders = ",".join(["?" for _ in data])
        columns_str = ",".join(data.keys())
        values = list(data.values())
        sql = f"INSERT OR REPLACE INTO monsters ({columns_str}) VALUES ({placeholders})"
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql, values)
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"[DB] Lỗi insert/update monster: {e}")
            return False

    def delete_monster(self, monster_id: str) -> bool:
        """Xóa quái vật theo ID"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM monsters WHERE id = ?", (monster_id,))
            deleted = cursor.rowcount > 0
            self.conn.commit()
            return deleted
        except sqlite3.Error as e:
            print(f"[DB] Lỗi xóa monster: {e}")
            return False


_db_instance: Optional[MonsterDatabase] = None


def get_db() -> MonsterDatabase:
    global _db_instance
    if _db_instance is None:
        _db_instance = MonsterDatabase()
        _db_instance.init_db()
    return _db_instance


def close_db() -> None:
    global _db_instance
    if _db_instance:
        _db_instance.close()
        _db_instance = None


def init_database() -> None:
    get_db()


def get_all_monsters_api(limit: int = 100) -> List[Dict[str, Any]]:
    return get_db().get_all_monsters(limit)


def get_monster_by_id_api(monster_id: str) -> Optional[Dict[str, Any]]:
    return get_db().get_monster_by_id(monster_id)


def search_monsters_api(keyword: str, limit: int = 50) -> List[Dict[str, Any]]:
    return get_db().search_monsters(keyword, limit)


def get_monster_types_api() -> List[Any]:
    return get_db().get_monster_types()


def get_dungeons_api() -> List[Any]:
    return get_db().get_dungeons()


def get_filtered_monsters_api(**kwargs) -> Dict[str, Any]:
    return get_db().get_filtered_monsters(**kwargs)


def check_db_health() -> Dict[str, Any]:
    db_path = MonsterDatabase.DB_PATH
    required = MonsterDatabase.REQUIRED_TABLES

    if not db_path.exists():
        return {
            "ok": False,
            "missing_tables": required,
            "counts": {},
            "error": f"Không tìm thấy file CSDL: {db_path}",
        }

    try:
        with sqlite3.connect(str(db_path)) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            existing = {row[0] for row in cursor.fetchall()}

        missing = [t for t in required if t not in existing]
        if missing:
            return {"ok": False, "missing_tables": missing, "counts": {}, "error": None}

        counts: Dict[str, int] = {}
        with sqlite3.connect(str(db_path)) as conn:
            cursor = conn.cursor()
            for table in required:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")  # nosec B608
                counts[table] = cursor.fetchone()[0]

        return {"ok": True, "missing_tables": [], "counts": counts, "error": None}
    except Exception as exc:
        return {
            "ok": False,
            "missing_tables": required,
            "counts": {},
            "error": str(exc),
        }


if __name__ == "__main__":
    """
    KỊCH BẢN TẠO DATABASE (DB CREATION SCRIPT)
    """
    print("\n" + "=" * 50)
    print(" SCRIPT TẠO DATABASE (MONSTER DB - DUNGEON TABLE & DUNGEON ID FOCUS)")
    print("=" * 50)

    db = MonsterDatabase()
    print("[1] Khởi tạo cấu trúc bảng (Schema với bảng dungeons)...")
    db.init_db()

    print("[2] Bắt đầu đọc dữ liệu từ Webpack/JSON...")
    try:
        monsters_data = db.load_monsters_data()
        print(f"    -> Đã phân tích thành công {len(monsters_data)} thực thể.")

        print("[3] Nhập dữ liệu Dungeons từ dungeonId...")
        db.import_dungeons_from_monsters(monsters_data)

        print("[4] Nhập dữ liệu Monsters chính...")
        db.import_monsters(monsters_data)

        print("\n" + "-" * 50)
        print(" TÓM TẮT TÌNH TRẠNG DATABASE ")
        print("-" * 50)

        health = check_db_health()
        if health["ok"]:
            for table, count in health["counts"].items():
                print(f" [OK] Bảng {table.ljust(15)}: {count} bản ghi")
            print(
                "\n>> HOÀN TẤT: CSDL `monsters.db` đã cập nhật bảng `dungeons` và khóa ngoại `dungeonId`!"
            )
        else:
            print(f">> CẢNH BÁO: {health['error']}")

    except Exception as e:
        print(f"\n[LỖI] {e}")
    finally:
        db.close()
        print("=" * 50 + "\n")
