import sqlite3
from typing import List, Dict, Any, Optional
from lib.db.connection import get_connection

class ScanService:
    def __init__(self):
        pass

    def create_scan(self, data: Dict[str, Any]) -> Optional[int]:
        conn, is_local = get_connection()
        if not conn:
            return None
        try:
            conn.execute("BEGIN TRANSACTION")
            cursor = conn.cursor()

            # Constraints checking
            if 'monster_id' in data and data['monster_id']:
                cursor.execute("SELECT 1 FROM monsters WHERE id = ?", (str(data['monster_id']),))
                if not cursor.fetchone():
                    raise ValueError(f"monster_id {data['monster_id']} does not exist.")
            if 'skill_id' in data and data['skill_id']:
                cursor.execute("SELECT 1 FROM skills WHERE skill_id = ?", (data['skill_id'],))
                if not cursor.fetchone():
                    raise ValueError(f"skill_id {data['skill_id']} does not exist.")
            if 'class_id' in data and data['class_id']:
                cursor.execute("SELECT 1 FROM classes WHERE class_id = ?", (data['class_id'],))
                if not cursor.fetchone():
                    raise ValueError(f"class_id {data['class_id']} does not exist.")

            cursor.execute(
                """
                INSERT INTO scans (monster_id, skill_id, class_id, status)
                VALUES (:monster_id, :skill_id, :class_id, :status)
                """,
                {
                    "monster_id": str(data.get("monster_id")) if data.get("monster_id") else None,
                    "skill_id": data.get("skill_id"),
                    "class_id": data.get("class_id"),
                    "status": data.get("status", "pending"),
                }
            )
            scan_id = cursor.lastrowid
            conn.commit()
            return scan_id
        except Exception as e:
            try: conn.rollback()
            except: pass
            print(f"[ScanService] Create scan error: {e}")
            return None
        finally:
            if is_local and conn:
                try: conn.close()
                except: pass

    def get_scan_by_id(self, scan_id: int) -> Optional[Dict[str, Any]]:
        conn, is_local = get_connection()
        if not conn:
            return None
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM scans WHERE scan_id = ?", (scan_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        except Exception as e:
            print(f"[ScanService] Read error: {e}")
            return None
        finally:
            if is_local and conn:
                try: conn.close()
                except: pass

    def get_scans(self) -> List[Dict[str, Any]]:
        conn, is_local = get_connection()
        if not conn:
            return []
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM scans ORDER BY timestamp DESC")
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"[ScanService] Read all error: {e}")
            return []
        finally:
            if is_local and conn:
                try: conn.close()
                except: pass

    def update_scan_status(self, scan_id: int, status: str) -> bool:
        conn, is_local = get_connection()
        if not conn:
            return False
        try:
            conn.execute("BEGIN TRANSACTION")
            cursor = conn.cursor()
            cursor.execute("UPDATE scans SET status = ? WHERE scan_id = ?", (status, scan_id))
            updated = cursor.rowcount > 0
            conn.commit()
            return updated
        except Exception as e:
            try: conn.rollback()
            except: pass
            print(f"[ScanService] Update status error: {e}")
            return False
        finally:
            if is_local and conn:
                try: conn.close()
                except: pass

    def delete_scan(self, scan_id: int) -> bool:
        conn, is_local = get_connection()
        if not conn:
            return False
        try:
            conn.execute("BEGIN TRANSACTION")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM scans WHERE scan_id = ?", (scan_id,))
            deleted = cursor.rowcount > 0
            conn.commit()
            return deleted
        except Exception as e:
            try: conn.rollback()
            except: pass
            print(f"[ScanService] Delete scan error: {e}")
            return False
        finally:
            if is_local and conn:
                try: conn.close()
                except: pass
