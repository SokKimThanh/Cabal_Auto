import re

with open("dialogs/monster_picker.py", "r", encoding="utf-8") as f:
    content = f.read()

replacement = """        self.tree.heading("id", text="ID", anchor="w")
        self.tree.heading("name", text=self._t("monster_name") if self._t else "Name", anchor="w")
        self.tree.heading("level", text="Lv", anchor="center")
        self.tree.heading("hp", text="HP", anchor="e")"""

content = content.replace(replacement, replacement)

with open("dialogs/monster_picker.py", "w", encoding="utf-8") as f:
    f.write(content)
