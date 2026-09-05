import re

with open("ui/tabs/hunt_tab.py", "r") as f:
    content = f.read()

content = content.replace("col+1", "col + 1")
content = content.replace("8*scale_factor", "8 * scale_factor")
content = content.replace("    def clear_target_photo(self):", "    def clear_target_photo(self):")
content = re.sub(r'\n\n\n    def clear_target_photo\(self\):', '\n\n    def clear_target_photo(self):', content)

with open("ui/tabs/hunt_tab.py", "w") as f:
    f.write(content)

with open("lib/features/monsters/monster_repo.py", "r") as f:
    content = f.read()

content = re.sub(r'\n\n\n\nDEFAULT_MONSTER_SCHEMA = {', '\n\nDEFAULT_MONSTER_SCHEMA = {', content)
content = re.sub(r'\n}\n\ndef get_target_monster_info', '\n}\n\n\ndef get_target_monster_info', content)

with open("lib/features/monsters/monster_repo.py", "w") as f:
    f.write(content)
