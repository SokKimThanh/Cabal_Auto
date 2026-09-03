import re

with open("dialogs/monster_picker.py", "r", encoding="utf-8") as f:
    content = f.read()

replacement = """        for r in records:
            id_val = r.get("id")
            name_val = r.get("name", "Unknown")
            lvl_val = r.get("level", "--")
            hp_val = r.get("hp", "--")
            dungeon_id = r.get("dungeonId")

            try:
                monster_id = int(id_val) if id_val is not None else 0
            except (ValueError, TypeError):
                monster_id = 0

            item_id = self.tree.insert("", "end", values=(f"#{id_val}", name_val, lvl_val, hp_val))
            # Attach canonical record to the item for retrieval later
            canonical_record = {
                "monster_id": monster_id,
                "name": str(name_val).strip(),
                "dungeon_id": str(dungeon_id) if dungeon_id else None
            }
            # Store canonical mapping
            self._item_map[item_id] = canonical_record"""

content = re.sub(r'        for r in records:.*?            self\._item_map\[item_id\] = canonical_record', replacement, content, flags=re.DOTALL)

with open("dialogs/monster_picker.py", "w", encoding="utf-8") as f:
    f.write(content)
