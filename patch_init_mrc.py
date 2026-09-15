import re
with open("app_gui.py", "r") as f:
    content = f.read()

content = content.replace("self._load_monster_rotation_list()", "self.monster_rotation_controller.load_monster_rotation_list() if hasattr(self, 'monster_rotation_controller') and self.monster_rotation_controller else None")

with open("app_gui.py", "w") as f:
    f.write(content)
