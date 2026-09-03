import re

with open("app_gui.py", "r", encoding="utf-8") as f:
    content = f.read()

replacement_refresh = """    def _refresh_monster_rotation_list(self):
        \"\"\"Refresh the configured monster rotation UI queue.\"\"\"
        if not hasattr(self, "monster_rotation_listbox"):
            return

        self.monster_rotation_listbox.delete(0, tk.END)

        from database import get_monster_by_id_api, find_monster_by_name_api

        # In-memory cache for DB queries during this panel's lifetime
        if not hasattr(self, "_monster_metadata_cache"):
            self._monster_metadata_cache = {}

        # Re-sort list just to be safe
        self.monster_rotation.sort(key=lambda x: x.get("priority", 999))

        for idx, entry in enumerate(self.monster_rotation):
            monster_id = entry.get("monster_id")
            name = entry.get("name")
            dungeon_id = entry.get("dungeon_id")

            cache_key = f"{monster_id}_{name}_{dungeon_id}"

            if cache_key not in self._monster_metadata_cache:
                # 1. Try by ID
                db_record = get_monster_by_id_api(str(monster_id)) if monster_id else None
                # 2. Try by Name fallback
                if not db_record and name:
                    db_record = find_monster_by_name_api(name, dungeon_id)
                self._monster_metadata_cache[cache_key] = db_record
            else:
                db_record = self._monster_metadata_cache[cache_key]

            if db_record:
                # Resolved metadata
                level = db_record.get("level", "--")
                hp = db_record.get("hp", "--")
                display_str = f"[#{monster_id}] {name} - Lv.{level} | HP: {hp}"
            else:
                # Missing metadata
                display_str = f"[{self._t('monster_rotation.unknown_badge')}] {name} - Lv.-- | HP: --"

            self.monster_rotation_listbox.insert(tk.END, display_str)"""

content = re.sub(r'    def _refresh_monster_rotation_list\(self\):.*?    def _on_monster_move_up\(self\):', replacement_refresh + "\n\n    def _on_monster_move_up(self):", content, flags=re.DOTALL)

with open("app_gui.py", "w", encoding="utf-8") as f:
    f.write(content)
