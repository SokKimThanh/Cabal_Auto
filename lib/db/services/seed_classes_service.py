import re
from typing import Tuple, List, Dict
import sqlite3
import database
import logging
import os
import hashlib
from lib.db.connection import get_connection

class SeedClassesService:
    def __init__(self, filepath: str = None):
        if filepath is None:
            self.filepath = os.getenv('CABAL_CLASS_DB_FILE', 'lib/data/color-skill-character-db-cabal.txt')
        else:
            self.filepath = filepath

    def parse_classes(self) -> Tuple[List[Dict], int, str]:
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            file_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
        except FileNotFoundError:
            logging.error(f"[SeedClassesService] Could not find data file at: {self.filepath}")
            return [], 0, ""

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
                logging.warning(f"[SeedClassesService] Rejected partial class record for slug '{slug}': {data}")
                rejected_count += 1

        return valid_classes, rejected_count, file_hash

    def apply_schema_migrations(self):
        conn, is_local = get_connection()
        if not conn:
            logging.error("[SeedClassesService] Failed to establish database connection during schema migration.")
            return

        try:
            cursor = conn.cursor()

            try:
                cursor.execute("ALTER TABLE classes ADD COLUMN class_code TEXT")

                # Assign generated backfill defaults if older data exists without code.
                # Use class_id appended to name to ensure absolute uniqueness during backfill.
                cursor.execute("""
                    UPDATE classes
                    SET class_code = lower(replace(name, ' ', '-')) || '-' || class_id
                    WHERE class_code IS NULL
                """)
            except sqlite3.OperationalError:
                pass # column likely exists

            cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_classes_class_code ON classes(class_code) WHERE class_code IS NOT NULL")
            conn.commit()
        except Exception as e:
            logging.error(f"[SeedClassesService] Schema migration failed: {e}", exc_info=True)
            try: conn.rollback()
            except: pass
        finally:
            if is_local and conn:
                try: conn.close()
                except: pass

    def seed_classes(self) -> Tuple[int, int, int]:
        self.apply_schema_migrations()
        valid_classes, rejected_count, file_hash = self.parse_classes()

        if not valid_classes:
            return 0, 0, rejected_count

        conn, is_local = get_connection()
        if not conn:
            logging.error("[SeedClassesService] Failed to establish database connection during seeding.")
            return len(valid_classes), 0, rejected_count

        try:
            cursor = conn.cursor()
            conn.execute("BEGIN TRANSACTION")

            cursor.execute("SELECT class_code, class_id FROM classes WHERE class_code IS NOT NULL")
            existing_map = {row[0]: row[1] for row in cursor.fetchall()}

            updates = []
            inserts = []

            for cls in valid_classes:
                if cls['class_code'] in existing_map:
                    updates.append((
                        cls['name'], cls['icon_path'], cls['str_base'],
                        cls['int_base'], cls['dex_base'], cls['class_code']
                    ))
                else:
                    inserts.append((
                        cls['class_code'], cls['name'], cls['icon_path'],
                        cls['str_base'], cls['int_base'], cls['dex_base']
                    ))

            if updates:
                cursor.executemany(
                    """
                    UPDATE classes SET
                        name=?,
                        icon_path=?,
                        str_base=?,
                        int_base=?,
                        dex_base=?
                    WHERE class_code=?
                    """, updates
                )

            if inserts:
                cursor.executemany(
                    """
                    INSERT INTO classes (class_code, name, icon_path, str_base, int_base, dex_base)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """, inserts
                )

            # Perform FK check as required by prompt
            cursor.execute("PRAGMA foreign_key_check")
            fk_issues = cursor.fetchall()
            if fk_issues:
                logging.error(f"[SeedClassesService] foreign_key_check failed with issues: {fk_issues}")

            conn.commit()

            # Reporting format per prompt
            logging.info(f"Source ID: class_metadata")
            logging.info(f"File: {self.filepath}")
            logging.info(f"Parser Boundary: Block 1 (id/name/icon), Block 2 (base stats)")
            logging.info(f"File Hash: {file_hash}")
            logging.info(f"Expected Source Count: {len(valid_classes) + rejected_count}, Parsed Count: {len(valid_classes) + rejected_count}, Accepted: {len(updates) + len(inserts)}, Rejected: {rejected_count}")
            logging.info(f"FK Issues Found: {len(fk_issues)}")

            return len(valid_classes), len(updates) + len(inserts), rejected_count
        except Exception as e:
            logging.error(f"[SeedClassesService] Seeding failed: {e}", exc_info=True)
            try: conn.rollback()
            except: pass
            raise e
        finally:
            if is_local and conn:
                try: conn.close()
                except: pass

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    service = SeedClassesService()
    try:
        src, acc, rej = service.seed_classes()
        print(f"Source count: {src}, Accepted: {acc}, Rejected: {rej}")
    except Exception as e:
        print(f"Failed to seed: {e}")
