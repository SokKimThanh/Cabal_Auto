import re

with open("ui/tabs/hunt_tab.py", "r", encoding="utf-8") as f:
    content = f.read()

replacement = """        # Remove right-click binding, App no longer has _show_monster_context_menu"""

content = re.sub(r'        self\.app\.monster_rotation_listbox\.bind\(\n            "<Button-3>", self\.app\._show_monster_context_menu\n        \)', replacement, content, flags=re.DOTALL)

with open("ui/tabs/hunt_tab.py", "w", encoding="utf-8") as f:
    f.write(content)
