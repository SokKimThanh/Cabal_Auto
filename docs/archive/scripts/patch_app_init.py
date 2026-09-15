import re

with open("app_gui.py", "r") as f:
    content = f.read()

# Replace __init__ signature and super().__init__()
content = re.sub(
    r"def __init__\(self, di_container=None\):",
    r"def __init__(self, root, di_container=None):\n        self.root = root",
    content
)

content = re.sub(
    r"super\(\)\.__init__\(\)\s*self\._is_destroyed = False\s*DialogService\.set_default_parent\(self\)",
    r"self._is_destroyed = False\n            DialogService.set_default_parent(self.root)",
    content
)

with open("app_gui.py", "w") as f:
    f.write(content)
