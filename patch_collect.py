import re

with open("dialogs/monster_edit.py", "r", encoding="utf-8") as f:
    content = f.read()

new_collect = """        if hasattr(self, 'desc_text'):
            candidate["description"] = self.desc_text.get("1.0", tk.END).strip()

        # Gather new fields
        def _get_int(widget, default=0):
            try:
                return int(widget.get())
            except ValueError:
                return default

        if hasattr(self, 'atk_rate_entry'): candidate["attackRate"] = _get_int(self.atk_rate_entry)
        if hasattr(self, 'primary_atk_min_entry'): candidate["primaryAttackMin"] = _get_int(self.primary_atk_min_entry)
        if hasattr(self, 'primary_atk_max_entry'): candidate["primaryAttackMax"] = _get_int(self.primary_atk_max_entry)
        if hasattr(self, 'sec_atk_min_entry'): candidate["secondaryAttackMin"] = _get_int(self.sec_atk_min_entry)
        if hasattr(self, 'sec_atk_max_entry'): candidate["secondaryAttackMax"] = _get_int(self.sec_atk_max_entry)
        if hasattr(self, 'def_entry'): candidate["defense"] = _get_int(self.def_entry)
        if hasattr(self, 'def_rate_entry'): candidate["defenseRate"] = _get_int(self.def_rate_entry)
        if hasattr(self, 'acc_entry'): candidate["accuracy"] = _get_int(self.acc_entry)

        if hasattr(self, 'dungeon_combo'):
            val = self.dungeon_combo.get().strip()
            candidate["dungeonId"] = val if val else None

        if hasattr(self, 'boss_type_combo'):
            val = self.boss_type_combo.get().strip()
            candidate["serverBossType"] = val if val else None"""

search_pattern = r"        if hasattr\(self, 'desc_text'\):\n            candidate\[\"description\"\] = self\.desc_text\.get\(\"1\.0\", tk\.END\)\.strip\(\)"
content_new = re.sub(search_pattern, new_collect, content)

with open("dialogs/monster_edit.py", "w", encoding="utf-8") as f:
    f.write(content_new)

print("Updated _collect_form_data")
