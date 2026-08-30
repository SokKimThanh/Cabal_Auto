import re
from typing import Tuple, List, Dict
import sqlite3
import database
from lib.db.connection import get_connection

class SeedClassesService:
    def __init__(self, filepath: str = 'lib/data/color-skill-character-db-cabal.txt'):
        self.filepath = filepath

    def parse_classes(self) -> Tuple[List[Dict], int]:
        with open(self.filepath, 'r') as f:
            content = f.read()

        classes = {}

        # Block 1: Classes with id, name, icon
        for match in re.finditer(r'([a-z_]+):\s*\{\s*id:\s*"([^"]+)",\s*name:\s*"([^"]+)",\s*description:\s*"[^"]*",\s*icon:\s*"([^"]+)"\s*\}', content):
            cls_slug, cls_id, name, icon = match.groups()
            normalized_code = cls_id.replace('_', '-')
            classes[cls_slug] = {
                'class_code': normalized_code,
                'name': name,
                'icon_path': icon
            }

        # Block 2: Base stats
        stats_match = re.search(r'm\s*=\s*\{([\s\S]*?)\};', content)
        if stats_match:
            stats_block = stats_match.group(1)
            for match in re.finditer(r'([a-z_]+):\s*\{\s*str:\s*(\d+),\s*int:\s*(\d+),\s*dex:\s*(\d+)\s*\}', stats_block):
                cls_slug, str_val, int_val, dex_val = match.groups()
                if cls_slug in classes:
                    classes[cls_slug]['str_base'] = int(str_val)
                    classes[cls_slug]['int_base'] = int(int_val)
                    classes[cls_slug]['dex_base'] = int(dex_val)
                else:
                    normalized_code = cls_slug.replace('_', '-')
                    classes[cls_slug] = {
                        'class_code': normalized_code,
                        'str_base': int(str_val),
                        'int_base': int(int_val),
                        'dex_base': int(dex_val)
                    }

        valid_classes = []
        rejected_count = 0
        for slug, data in classes.items():
            if all(k in data for k in ['class_code', 'name', 'icon_path', 'str_base', 'int_base', 'dex_base']):
                valid_classes.append(data)
            else:
                rejected_count += 1

        return valid_classes, rejected_count

    def apply_schema_migrations(self):
        conn, is_local = get_connection()
        if not conn:
            return

        try:
            cursor = conn.cursor()

            try:
                cursor.execute("ALTER TABLE classes ADD COLUMN class_code TEXT")
            except sqlite3.OperationalError:
                pass # column likely exists

            cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_classes_class_code ON classes(class_code) WHERE class_code IS NOT NULL")
            conn.commit()
        finally:
            if is_local and conn:
                try: conn.close()
                except: pass

    def seed_classes(self) -> Tuple[int, int, int]:
        self.apply_schema_migrations()
        valid_classes, rejected_count = self.parse_classes()

        conn, is_local = get_connection()
        if not conn:
            return len(valid_classes), 0, rejected_count

        try:
            cursor = conn.cursor()
            conn.execute("BEGIN TRANSACTION")
            accepted_count = 0

            for cls in valid_classes:
                cursor.execute("SELECT class_id FROM classes WHERE class_code = ?", (cls['class_code'],))
                row = cursor.fetchone()
                if row:
                    cursor.execute(
                        """
                        UPDATE classes SET
                            name=:name,
                            icon_path=:icon_path,
                            str_base=:str_base,
                            int_base=:int_base,
                            dex_base=:dex_base
                        WHERE class_code=:class_code
                        """,
                        cls
                    )
                else:
                    cursor.execute(
                        """
                        INSERT INTO classes (class_code, name, icon_path, str_base, int_base, dex_base)
                        VALUES (:class_code, :name, :icon_path, :str_base, :int_base, :dex_base)
                        """,
                        cls
                    )
                accepted_count += 1

            conn.commit()
            return len(valid_classes), accepted_count, rejected_count
        except Exception as e:
            try: conn.rollback()
            except: pass
            raise e
        finally:
            if is_local and conn:
                try: conn.close()
                except: pass

if __name__ == '__main__':
    service = SeedClassesService()
    src, acc, rej = service.seed_classes()
    print(f"Source count: {src}, Accepted: {acc}, Rejected: {rej}")
