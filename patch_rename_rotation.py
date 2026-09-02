import re

with open("app_gui.py", "r", encoding="utf-8") as f:
    content = f.read()

# I am changing all references of `self.monster_rotation_list` to `self.monster_rotation`
content = content.replace("self.monster_rotation_list =", "self.monster_rotation =")
content = content.replace("self.monster_rotation_list.append", "self.monster_rotation.append")
content = content.replace("self.monster_rotation_list)", "self.monster_rotation)")
content = content.replace("self.monster_rotation_list,", "self.monster_rotation,")
content = content.replace("self.monster_rotation_list\n", "self.monster_rotation\n")
content = content.replace('getattr(self, "monster_rotation_list"', 'getattr(self, "monster_rotation"')
content = content.replace("not self.monster_rotation_list:", "not self.monster_rotation:")

with open("app_gui.py", "w", encoding="utf-8") as f:
    f.write(content)
