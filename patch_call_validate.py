import re

with open("ui/tabs/hunt_tab.py", "r", encoding="utf-8") as f:
    content = f.read()

# Trigger validation on combo start key change
combo_key_change_code = """        def on_combo_key_change(event):
            self.app.hunt_cfg["combo"]["combo_start_key"] = self.app.combo_start_key_cmb.get()
            if hasattr(self.app, "state_controller") and hasattr(self.app.state_controller, "_validate_slot_key_duplicates"):
                self.app.state_controller._validate_slot_key_duplicates()
"""

content = re.sub(r'        def on_combo_key_change\(event\):\n            self\.app\.hunt_cfg\["combo"\]\["combo_start_key"\] = self\.app\.combo_start_key_cmb\.get\(\)', combo_key_change_code.strip(), content)

with open("ui/tabs/hunt_tab.py", "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
