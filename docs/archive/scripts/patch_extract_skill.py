import re
with open("app_gui.py", "r") as f:
    content = f.read()

methods_to_remove = [
    "_update_skill_keys",
    "_update_duplicate_colors",
    "on_skill_slot_changed",
]

for method in methods_to_remove:
    pattern = rf"def {method}\(self.*?\):\n(?:    +.*\n)*"
    content = re.sub(pattern, "", content)

with open("app_gui.py", "w") as f:
    f.write(content)
