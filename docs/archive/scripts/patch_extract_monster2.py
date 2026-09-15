import re

with open("app_gui.py", "r") as f:
    content = f.read()

content = re.sub(
    r"def _update_monster_status\(self.*?\):\n(?:    +.*\n)*",
    "",
    content
)

with open("app_gui.py", "w") as f:
    f.write(content)
