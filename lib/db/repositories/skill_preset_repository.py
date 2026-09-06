import sqlite3
import logging
from typing import Optional, List, Dict, Any
from lib.db.connection import get_connection

logger = logging.getLogger(__name__)

class SkillPresetRepository:
    def create_preset(self, class_id: int, name: str, is_default: int = 0) -> int:
        conn, is_local = get_connection()
        if not conn:
            return -1
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO skill_presets (class_id, name, is_default) VALUES (?, ?, ?)",
                (class_id, name, is_default),
            )
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            logger.error(f"Error creating preset for class_id {class_id}: {e}")
            conn.rollback()
            return -1
        finally:
            if is_local and conn:
                try:
                    conn.close()
                except Exception:
                    pass

    def get_preset_skills(self, preset_id: int) -> Dict[str, List[int]]:
        conn, is_local = get_connection()
        if not conn:
            return {}
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT lane_type, skill_id FROM preset_skills WHERE preset_id = ? ORDER BY lane_type, position",
                (preset_id,)
            )
            rows = cursor.fetchall()

            result = {}
            for row in rows:
                lane = row['lane_type']
                skill_id = row['skill_id']
                if lane not in result:
                    result[lane] = []
                result[lane].append(skill_id)

            return result
        except Exception as e:
            logger.error(f"Error getting preset skills for preset_id {preset_id}: {e}")
            return {}
        finally:
            if is_local and conn:
                try:
                    conn.close()
                except Exception:
                    pass

    def set_preset_skills(self, preset_id: int, skills_by_lane: Dict[str, List[int]]) -> bool:
        conn, is_local = get_connection()
        if not conn:
            return False
        try:
            cursor = conn.cursor()

            cursor.execute("DELETE FROM preset_skills WHERE preset_id = ?", (preset_id,))

            for lane, skill_ids in skills_by_lane.items():
                for position, skill_id in enumerate(skill_ids):
                    cursor.execute(
                        "INSERT INTO preset_skills (preset_id, skill_id, lane_type, position) VALUES (?, ?, ?, ?)",
                        (preset_id, skill_id, lane, position)
                    )

            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error setting preset skills for preset_id {preset_id}: {e}")
            conn.rollback()
            return False
        finally:
            if is_local and conn:
                try:
                    conn.close()
                except Exception:
                    pass

    def delete_preset(self, preset_id: int) -> bool:
        conn, is_local = get_connection()
        if not conn:
            return False
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM skill_presets WHERE preset_id = ?", (preset_id,))
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error deleting preset {preset_id}: {e}")
            conn.rollback()
            return False
        finally:
            if is_local and conn:
                try:
                    conn.close()
                except Exception:
                    pass

    def get_presets_by_class(self, class_id: int) -> List[Dict[str, Any]]:
        conn, is_local = get_connection()
        if not conn:
            return []
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM skill_presets WHERE class_id = ?", (class_id,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error getting presets by class_id {class_id}: {e}")
            return []
        finally:
            if is_local and conn:
                try:
                    conn.close()
                except Exception:
                    pass

    def get_preset(self, preset_id: int) -> Optional[Dict[str, Any]]:
        conn, is_local = get_connection()
        if not conn:
            return None
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM skill_presets WHERE preset_id = ?", (preset_id,))
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
        except Exception as e:
            logger.error(f"Error getting preset {preset_id}: {e}")
            return None
        finally:
            if is_local and conn:
                try:
                    conn.close()
                except Exception:
                    pass
