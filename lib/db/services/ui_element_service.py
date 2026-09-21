import sqlite3
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class UIElementService:
    def __init__(self, db_conn: sqlite3.Connection):
        self.conn = db_conn

    def _row_to_dict(self, cursor: sqlite3.Cursor, row: tuple) -> Dict:
        """Chuyển đổi một dòng kết quả thành dictionary."""
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    def get_all_elements(self) -> List[Dict]:
        """Lấy tất cả UI elements từ DB."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM ui_elements")
            rows = cursor.fetchall()
            return [self._row_to_dict(cursor, row) for row in rows]
        except sqlite3.Error as e:
            logger.error(f"Error in get_all_elements: {e}")
            return []

    def bulk_upsert_elements(self, elements: List[Dict]) -> bool:
        """Thêm hoặc cập nhật hàng loạt UI elements (Bulk Insert/Upsert) để tối ưu hiệu năng."""
        if not elements:
            return True

        try:
            cursor = self.conn.cursor()

            # Sử dụng INSERT OR REPLACE với composite key UNIQUE(module_name, screen_name, element_id)
            query = """
                INSERT OR REPLACE INTO ui_elements (
                    element_id, module_name, screen_name, component_type, is_exclusive, description
                ) VALUES (?, ?, ?, ?, ?, ?)
            """

            data = [
                (
                    el.get("element_id"),
                    el.get("module_name"),
                    el.get("screen_name"),
                    el.get("component_type"),
                    1 if el.get("is_exclusive") else 0,
                    el.get("description", "")
                )
                for el in elements
            ]

            cursor.executemany(query, data)
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            logger.error(f"Error in bulk_upsert_elements: {e}")
            self.conn.rollback()
            return False

    def get_element_by_id(self, module_name: str, screen_name: str, element_id: str) -> Optional[Dict]:
        """Lấy một UI element cụ thể dựa trên composite key."""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT * FROM ui_elements WHERE module_name = ? AND screen_name = ? AND element_id = ?",
                (module_name, screen_name, element_id)
            )
            row = cursor.fetchone()
            if row:
                return self._row_to_dict(cursor, row)
            return None
        except sqlite3.Error as e:
            logger.error(f"Error in get_element_by_id: {e}")
            return None

    def delete_element(self, module_name: str, screen_name: str, element_id: str) -> bool:
        """Xoá một UI element cụ thể."""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT id FROM ui_elements WHERE module_name = ? AND screen_name = ? AND element_id = ?",
                (module_name, screen_name, element_id)
            )
            row = cursor.fetchone()
            if not row:
                return False

            element_db_id = row[0]
            cursor.execute("DELETE FROM ui_elements WHERE id = ?", (element_db_id,))
            self.conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            logger.error(f"Error in delete_element: {e}")
            self.conn.rollback()
            return False
