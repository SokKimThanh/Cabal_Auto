import re

with open("dialogs/monster_edit.py", "r", encoding="utf-8") as f:
    content = f.read()

content_new = content.replace("UI.COLOR_SECONDARY_TEXT", "UI.COLOR_PRIMARY_TEXT") # Or just default it

with open("dialogs/monster_edit.py", "w", encoding="utf-8") as f:
    f.write(content_new)

print("Fixed color attribute.")
