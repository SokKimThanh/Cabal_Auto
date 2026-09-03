import re

with open("app_gui.py", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace("m in self.monster_rotation_list", "m in self.monster_rotation")
content = content.replace("len(self.monster_rotation_list)", "len(self.monster_rotation)")

with open("app_gui.py", "w", encoding="utf-8") as f:
    f.write(content)
