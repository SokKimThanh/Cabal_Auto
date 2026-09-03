import re

with open("dialogs/monster_picker.py", "r", encoding="utf-8") as f:
    content = f.read()

# Remove the minsize call
content = re.sub(r'        self\.minsize\(400, 300\)\n', '', content)

with open("dialogs/monster_picker.py", "w", encoding="utf-8") as f:
    f.write(content)
