import re
with open("ui/controllers/app_lifecycle_controller.py", "r") as f:
    content = f.read()
content = content.replace("self.app.after", "self.app.root.after")
with open("ui/controllers/app_lifecycle_controller.py", "w") as f:
    f.write(content)

with open("ui/controllers/hotkey_controller.py", "r") as f:
    content = f.read()
content = content.replace("self.app.bind_all", "self.app.root.bind_all")
with open("ui/controllers/hotkey_controller.py", "w") as f:
    f.write(content)
