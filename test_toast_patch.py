import re

with open("ui/tabs/hunt_tab.py", "r") as f:
    content = f.read()

print("class HuntTab" in content)
