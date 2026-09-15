import re

with open("app_gui.py", "r") as f:
    content = f.read()

content = re.sub(
    r"super\(\)\.destroy\(\)",
    r"self.root.destroy()",
    content
)

with open("app_gui.py", "w") as f:
    f.write(content)
