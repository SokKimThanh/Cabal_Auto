import re

with open("ui/tabs/hunt_tab.py", "r", encoding="utf-8") as f:
    content = f.read()

# We need to make sure _previous_value is updated when we load from config
config_load_code = """        if hasattr(self.app, "skill_slot_vars"):
            for idx, var in enumerate(self.app.skill_slot_vars):
                name = ""
                if idx < len(normalized_slots):
                    name = normalized_slots[idx]
                var.set(name)
                var._previous_value = name
"""
content = re.sub(r'        if hasattr\(self\.app, "skill_slot_vars"\):\n            for idx, var in enumerate\(self\.app\.skill_slot_vars\):\n                name = ""\n                if idx < len\(normalized_slots\):\n                    name = normalized_slots\[idx\]\n                var\.set\(name\)', config_load_code.strip(), content)

with open("ui/tabs/hunt_tab.py", "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
