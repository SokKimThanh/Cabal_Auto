import sqlite3
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class IconService:
    def __init__(self, db_connection: sqlite3.Connection):
        self.conn = db_connection

    def _row_to_dict(self, cursor: sqlite3.Cursor, row: tuple) -> Optional[Dict]:
        if not row:
            return None
        return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}

    def get_all_icons(self, search_term: str = "", category: str = "", status_filter: str = "") -> List[Dict]:
        try:
            cursor = self.conn.cursor()
            query = "SELECT * FROM icons WHERE 1=1"
            params = []

            if search_term:
                query += " AND (icon_key LIKE ? OR name LIKE ?)"
                search_like = f"%{search_term}%"
                params.extend([search_like, search_like])

            if category:
                query += " AND category = ?"
                params.append(category)

            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [self._row_to_dict(cursor, row) for row in rows]
        except sqlite3.Error as e:
            logger.error(f"Error in get_all_icons: {e}")
            return []

    def get_icon_by_key(self, icon_key: str) -> Optional[Dict]:
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM icons WHERE icon_key = ?", (icon_key,))
            row = cursor.fetchone()
            if row:
                return self._row_to_dict(cursor, row)
            return None
        except sqlite3.Error as e:
            logger.error(f"Error in get_icon_by_key: {e}")
            return None

    def upsert_icon(self, icon_data: Dict) -> bool:
        try:
            cursor = self.conn.cursor()

            cursor.execute("""
                INSERT INTO icons (
                    icon_key, name, filepath, fallback_emoji,
                    tooltip_translation_key, category, description
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(icon_key) DO UPDATE SET
                    name = excluded.name,
                    filepath = excluded.filepath,
                    fallback_emoji = excluded.fallback_emoji,
                    tooltip_translation_key = excluded.tooltip_translation_key,
                    category = excluded.category,
                    description = excluded.description
            """, (
                icon_data.get('icon_key'),
                icon_data.get('name'),
                icon_data.get('filepath'),
                icon_data.get('fallback_emoji'),
                icon_data.get('tooltip_translation_key'),
                icon_data.get('category', 'General'),
                icon_data.get('description')
            ))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            logger.error(f"Error in upsert_icon: {e}")
            self.conn.rollback()
            return False

    def delete_icon(self, icon_key: str) -> bool:
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM icons WHERE icon_key = ?", (icon_key,))
            self.conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            logger.error(f"Error in delete_icon: {e}")
            self.conn.rollback()
            return False

    def register_usage(self, icon_key: str, module_name: str, component_type: str, element_id: str) -> bool:
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO icon_usages (icon_key, module_name, ui_component_type, ui_element_id)
                VALUES (?, ?, ?, ?)
            """, (icon_key, module_name, component_type, element_id))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            logger.error(f"Error in register_usage: {e}")
            self.conn.rollback()
            return False

    def get_usages(self, icon_key: str) -> List[Dict]:
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM icon_usages WHERE icon_key = ?", (icon_key,))
            rows = cursor.fetchall()
            return [self._row_to_dict(cursor, row) for row in rows]
        except sqlite3.Error as e:
            logger.error(f"Error in get_usages: {e}")
            return []

    def clear_usages(self, icon_key: str) -> bool:
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM icon_usages WHERE icon_key = ?", (icon_key,))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            logger.error(f"Error in clear_usages: {e}")
            self.conn.rollback()
            return False
