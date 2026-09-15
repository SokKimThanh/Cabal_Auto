import re
with open("app_gui.py", "r") as f:
    content = f.read()
if "app.protocol" in content:
    print("app.protocol exists")
else:
    print("app.protocol NOT exists")
