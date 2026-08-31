from typing import Dict, Any, Optional
from lib.db.connection import get_connection

class MonsterCatalogueLookup:
    """
    Lookup adapter for Monsters.
    Input: stable monster ID or name from user config.
    Output: immutable reference stats/metadata.
    Fallback: return None, preserve user monster untouched.
    """

    @classmethod
    def get_reference_by_id(cls, monster_id: str) -> Optional[Dict[str, Any]]:
        conn, is_local = get_connection()
        if not conn:
            return None

        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM monsters WHERE id = ?", (monster_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        except Exception:
            return None
        finally:
            if is_local and conn:
                try:
                    conn.close()
                except Exception:
                    pass

    @classmethod
    def get_reference_by_name(cls, monster_name: str) -> Optional[Dict[str, Any]]:
        conn, is_local = get_connection()
        if not conn:
            return None

        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM monsters WHERE name = ? LIMIT 1", (monster_name,))
            row = cursor.fetchone()
            return dict(row) if row else None
        except Exception:
            return None
        finally:
            if is_local and conn:
                try:
                    conn.close()
                except Exception:
                    pass


class SkillCatalogueLookup:
    """
    Lookup adapter for Skills.
    Input: skill_name or skill_code.
    Output: icon/category/class references.
    Fallback: return None.
    """

    @classmethod
    def get_reference_by_name(cls, skill_name: str) -> Optional[Dict[str, Any]]:
        conn, is_local = get_connection()
        if not conn:
            return None

        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM skills WHERE name = ? OR alias = ? LIMIT 1", (skill_name, skill_name))
            row = cursor.fetchone()
            if not row:
                return None

            skill_data = dict(row)

            # Enrich with class data if possible
            if skill_data.get("class_id"):
                cursor.execute("SELECT * FROM classes WHERE class_id = ?", (skill_data["class_id"],))
                class_row = cursor.fetchone()
                if class_row:
                    skill_data["class_data"] = dict(class_row)

            return skill_data
        except Exception:
            return None
        finally:
            if is_local and conn:
                try:
                    conn.close()
                except Exception:
                    pass


class SkillRuntimeView:
    """
    Combines user skill library record + optional catalogue record.
    Emits runtime fields strictly from user JSON and reference fields from DB.
    Never infers/guesses key, cooldown, cast_time, or image.
    """

    @classmethod
    def build_view(cls, user_skill: Dict[str, Any], catalogue_record: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        view = dict(user_skill)

        # Optional catalogue enrichment
        if catalogue_record:
            # We ONLY enrich metadata. We DO NOT overwrite the runtime user configurations.
            view["catalogue_alias"] = catalogue_record.get("alias")
            view["catalogue_icon"] = {
                "x": catalogue_record.get("icon_x"),
                "y": catalogue_record.get("icon_y"),
                "w": catalogue_record.get("icon_w"),
                "h": catalogue_record.get("icon_h")
            }
            if catalogue_record.get("class_data"):
                view["class_name"] = catalogue_record["class_data"].get("name")
                view["class_code"] = catalogue_record["class_data"].get("class_code")
                view["class_icon_path"] = catalogue_record["class_data"].get("icon_path")

        return view
