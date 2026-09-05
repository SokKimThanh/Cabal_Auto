import sqlite3
from typing import Optional, Dict, Any, Tuple
from lib.db.connection import get_connection
from lib.db.repositories.skill_preset_repository import SkillPresetRepository

class PresetStateManager:
    def get_active_preset(self, class_name: str) -> Optional[int]:
        conn, is_local = get_connection()
        if not conn:
            return None
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT active_preset_id FROM user_preset_state WHERE class_name = ?",
                (class_name,),
            )
            row = cursor.fetchone()
            if row:
                return row["active_preset_id"]
            return None
        finally:
            if is_local and conn:
                try:
                    conn.close()
                except Exception:
                    pass

    def set_active_preset(self, class_name: str, preset_id: int, mode: str = 'default') -> bool:
        conn, _ = get_connection()
        if not conn:
            return False
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO user_preset_state (class_name, active_preset_id, preset_mode)
                VALUES (?, ?, ?)
                ON CONFLICT(class_name) DO UPDATE SET
                active_preset_id = excluded.active_preset_id,
                preset_mode = excluded.preset_mode
                """,
                (class_name, preset_id, mode)
            )
            conn.commit()
            return True
        finally:
            conn.close()

    def get_preset_mode(self, class_name: str) -> str:
        conn, _ = get_connection()
        if not conn:
            return 'default'
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT preset_mode FROM user_preset_state WHERE class_name = ?", (class_name,))
            row = cursor.fetchone()
            if row and row['preset_mode']:
                return row['preset_mode']
            return 'default'
        finally:
            conn.close()

    def reset_to_default(self, class_name: str) -> Optional[int]:
        """Resets to default preset, updates state, and returns the default preset_id"""
        preset_repo = SkillPresetRepository()
        presets = preset_repo.get_presets_by_class(class_name)

        default_preset_id = None
        for preset in presets:
            if preset['is_default']:
                default_preset_id = preset['preset_id']
                break

        if default_preset_id is not None:
            self.set_active_preset(class_name, default_preset_id, 'default')

        return default_preset_id
