import re

with open("app_gui.py", "r", encoding="utf-8") as f:
    content = f.read()

# Add import
import_stmt = "\nfrom dialogs.monster_picker import MonsterPickerDialog"
content = content.replace("from ui.windows.setup_wizard import show_setup_wizard", "from ui.windows.setup_wizard import show_setup_wizard" + import_stmt)

# Replace _on_monster_add_smart
pattern = re.compile(r'    def _on_monster_add_smart\(self\):.*?    def on_skill_slot_changed', re.DOTALL)

replacement = """    def _on_monster_add_smart(self):
        def on_monster_selected(record):
            # Check for duplicate
            monster_id = record["monster_id"]
            dungeon_id = record.get("dungeon_id")

            # Deduplicate by (monster_id, dungeon_id)
            for entry in self.monster_rotation:
                if entry.get("monster_id") == monster_id and entry.get("dungeon_id") == dungeon_id:
                    messagebox.showinfo(
                        self._t("info_title", ns="ui"),
                        self._t("monster_already_in_list").format(name=record["name"]),
                        parent=self
                    )
                    return

            # Add with new priority
            new_priority = len(self.monster_rotation) + 1
            new_entry = {
                "monster_id": monster_id,
                "name": record["name"],
                "priority": new_priority,
                "dungeon_id": dungeon_id
            }

            self.monster_rotation.append(new_entry)
            if hasattr(self, "_mark_unsaved"):
                self._mark_unsaved()

            self._refresh_monster_rotation_list()

        MonsterPickerDialog(self, self.current_lang, on_monster_selected, self._t)

    def on_skill_slot_changed"""

content = pattern.sub(replacement, content)

with open("app_gui.py", "w", encoding="utf-8") as f:
    f.write(content)
