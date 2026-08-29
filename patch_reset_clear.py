import re

with open("dialogs/monster_edit.py", "r", encoding="utf-8") as f:
    content = f.read()

new_reset = """    def _on_reset_form(self) -> None:
        \"\"\"Reset form fields to default values for a new entry.\"\"\"
        self.id_val_label.config(text="<Mới / New>")
        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(
            0, i18n_t("default_monster_name", ns="monster_editor", default="Quái Mới")
        )
        self.level_spinbox.delete(0, tk.END)
        self.level_spinbox.insert(0, "1")
        self.priority_spinbox.delete(0, tk.END)
        self.priority_spinbox.insert(0, "1")
        self.hp_entry.delete(0, tk.END)
        self.hp_entry.insert(0, "100")

        for entry in (self.atk_rate_entry, self.primary_atk_min_entry, self.primary_atk_max_entry,
                      self.sec_atk_min_entry, self.sec_atk_max_entry, self.def_entry, self.def_rate_entry, self.acc_entry):
            entry.delete(0, tk.END)
            entry.insert(0, "0")

        self.dungeon_combo.set("")
        self.boss_type_combo.set("")

        self.damage_entry.delete(0, tk.END)
        self.damage_entry.insert(0, "10")
        self.desc_text.delete("1.0", tk.END)

    def _on_clear_form(self) -> None:
        \"\"\"Clear all form fields.\"\"\"
        self.id_val_label.config(text="")
        self.name_entry.delete(0, tk.END)
        self.level_spinbox.delete(0, tk.END)
        self.priority_spinbox.delete(0, tk.END)
        self.hp_entry.delete(0, tk.END)

        for entry in (self.atk_rate_entry, self.primary_atk_min_entry, self.primary_atk_max_entry,
                      self.sec_atk_min_entry, self.sec_atk_max_entry, self.def_entry, self.def_rate_entry, self.acc_entry):
            entry.delete(0, tk.END)

        self.dungeon_combo.set("")
        self.boss_type_combo.set("")

        self.damage_entry.delete(0, tk.END)
        self.desc_text.delete("1.0", tk.END)
        if hasattr(self, "preview_label") and self.preview_label:"""

search_pattern = r"    def _on_reset_form\(self\) -> None:.*?if hasattr\(self, \"preview_label\"\) and self\.preview_label:"
content_new = re.sub(search_pattern, new_reset, content, flags=re.DOTALL)

with open("dialogs/monster_edit.py", "w", encoding="utf-8") as f:
    f.write(content_new)

print("Updated _on_reset_form and _on_clear_form")
