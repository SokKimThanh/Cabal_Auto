import sqlite3
import logging
from typing import List, Dict, Optional
from lib.events.event_bus import EventBus, IconUpdatedEvent, IconManagerSyncEvent
from lib.managers.icon_file_manager import delete_icon_file

logger = logging.getLogger(__name__)


class IconService:
    def __init__(self, db_connection: sqlite3.Connection):
        self.conn = db_connection

    def _row_to_dict(self, cursor: sqlite3.Cursor, row: tuple) -> Optional[Dict]:
        if not row:
            return None
        return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}

    def _check_and_delete_orphaned_file(self, filepath: str) -> bool:
        if not filepath:
            return False
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM icons WHERE filepath = ?", (filepath,))
            count = cursor.fetchone()[0]
            if count == 0:
                return delete_icon_file(filepath)
            return False
        except sqlite3.Error as e:
            logger.error(f"Error checking orphaned file {filepath}: {e}")
            return False

    def get_all_icons(
        self, search_term: str = "", category: str = "", status_filter: str = ""
    ) -> List[Dict]:
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

    def insert_ignore_icon(self, icon_data: Dict) -> bool:
        """Thêm icon mới, bỏ qua nếu đã tồn tại."""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                """
                INSERT INTO icons (
                    icon_key, name, filepath, fallback_emoji,
                    tooltip_translation_key, category, description
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(icon_key) DO NOTHING
            """,
                (
                    icon_data.get("icon_key"),
                    icon_data.get("name"),
                    icon_data.get("filepath"),
                    icon_data.get("fallback_emoji"),
                    icon_data.get("tooltip_translation_key"),
                    icon_data.get("category", "General"),
                    icon_data.get("description"),
                ),
            )
            inserted = cursor.rowcount > 0
            self.conn.commit()

            if inserted:
                # Lúc nạp từ file JSON, không cần thiết phải kích hoạt sync ngược, nhưng có thể cần refresh UI
                icon_key = icon_data.get("icon_key")
                if icon_key:
                    EventBus.trigger(IconUpdatedEvent(icon_key=icon_key))

            return True
        except sqlite3.Error as e:
            logger.error(f"Error in insert_ignore_icon: {e}")
            self.conn.rollback()
            return False

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

            icon_key = icon_data.get("icon_key")
            old_icon = self.get_icon_by_key(icon_key) if icon_key else None
            old_filepath = old_icon.get('filepath') if old_icon else None

            cursor.execute(
                """
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
            """,
                (
                    icon_data.get("icon_key"),
                    icon_data.get("name"),
                    icon_data.get("filepath"),
                    icon_data.get("fallback_emoji"),
                    icon_data.get("tooltip_translation_key"),
                    icon_data.get("category", "General"),
                    icon_data.get("description"),
                ),
            )
            self.conn.commit()

            new_filepath = icon_data.get('filepath')
            if old_filepath and old_filepath != new_filepath:
                self._check_and_delete_orphaned_file(old_filepath)

            # Kích hoạt sự kiện để đồng bộ hóa và làm mới giao diện
            icon_key = icon_data.get("icon_key")
            if icon_key:
                EventBus.trigger(IconUpdatedEvent(icon_key=icon_key))
                EventBus.trigger(IconManagerSyncEvent())

            return True
        except sqlite3.Error as e:
            logger.error(f"Error in upsert_icon: {e}")
            self.conn.rollback()
            return False

    def delete_icon(self, icon_key: str) -> bool:
        try:
            cursor = self.conn.cursor()

            # Check usages first
            cursor.execute("SELECT COUNT(*) FROM icon_usages WHERE icon_key = ?", (icon_key,))
            usages = cursor.fetchone()[0]
            if usages > 0:
                raise ValueError("icon_in_use_error")

            # Lấy thông tin trước khi xoá để biết tên file
            old_icon = self.get_icon_by_key(icon_key)
            old_filepath = old_icon.get('filepath') if old_icon else None

            cursor.execute("DELETE FROM icons WHERE icon_key = ?", (icon_key,))
            deleted = cursor.rowcount > 0
            self.conn.commit()

            if deleted:
                if old_filepath:
                    self._check_and_delete_orphaned_file(old_filepath)
                EventBus.trigger(IconManagerSyncEvent())

            return deleted
        except ValueError as ve:
            raise ve
        except sqlite3.Error as e:
            logger.error(f"Error in delete_icon: {e}")
            self.conn.rollback()
            return False

    def register_usage(
        self, icon_key: str, module_name: str, component_type: str, element_id: str
    ) -> bool:
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                """
                INSERT INTO icon_usages (icon_key, module_name, ui_component_type, ui_element_id)
                VALUES (?, ?, ?, ?)
            """,
                (icon_key, module_name, component_type, element_id),
            )
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
