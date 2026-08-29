import re

with open("dialogs/monster_edit.py", "r", encoding="utf-8") as f:
    content = f.read()

new_populate = """    def _populate_form(self) -> None:
        data = self.monster_data

        m_id = data.get("id", "")
        if self.is_new:
            self.id_val_label.config(text="<Mới / New>")
        else:
            self.id_val_label.config(text=f"#{m_id}")

        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, data.get("name", ""))

        self.level_spinbox.delete(0, tk.END)
        self.level_spinbox.insert(0, str(data.get("level", 1)))

        self.priority_spinbox.delete(0, tk.END)
        self.priority_spinbox.insert(0, str(data.get("priority", 1)))

        self.hp_entry.delete(0, tk.END)
        self.hp_entry.insert(0, str(data.get("hp", 100)))

        self.atk_rate_entry.delete(0, tk.END)
        self.atk_rate_entry.insert(0, str(data.get("attackRate", 0)))

        self.primary_atk_min_entry.delete(0, tk.END)
        self.primary_atk_min_entry.insert(0, str(data.get("primaryAttackMin", 0)))

        self.primary_atk_max_entry.delete(0, tk.END)
        self.primary_atk_max_entry.insert(0, str(data.get("primaryAttackMax", 0)))

        self.sec_atk_min_entry.delete(0, tk.END)
        self.sec_atk_min_entry.insert(0, str(data.get("secondaryAttackMin", 0)))

        self.sec_atk_max_entry.delete(0, tk.END)
        self.sec_atk_max_entry.insert(0, str(data.get("secondaryAttackMax", 0)))

        self.def_entry.delete(0, tk.END)
        self.def_entry.insert(0, str(data.get("defense", 0)))

        self.def_rate_entry.delete(0, tk.END)
        self.def_rate_entry.insert(0, str(data.get("defenseRate", 0)))

        self.acc_entry.delete(0, tk.END)
        self.acc_entry.insert(0, str(data.get("accuracy", 0)))

        self.damage_entry.delete(0, tk.END)
        self.damage_entry.insert(0, str(data.get("damage_per_hit", 10)))

        self.desc_text.delete("1.0", tk.END)
        if data.get("description"):
            self.desc_text.insert("1.0", data["description"])

        # Reference comboboxes (empty options for now)
        dungeon_id = data.get("dungeonId")
        if dungeon_id:
            self.dungeon_combo.set(dungeon_id)
        else:
            self.dungeon_combo.set("")

        boss_type = data.get("serverBossType")
        if boss_type:
            self.boss_type_combo.set(boss_type)
        else:
            self.boss_type_combo.set("")

        self._refresh_templates()"""

search_pattern = r"    def _populate_form\(self\) -> None:.*?self\._refresh_templates\(\)"
content_new = re.sub(search_pattern, new_populate, content, flags=re.DOTALL)

with open("dialogs/monster_edit.py", "w", encoding="utf-8") as f:
    f.write(content_new)

print("Updated _populate_form")
