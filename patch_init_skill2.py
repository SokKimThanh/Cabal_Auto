import re
with open("app_gui.py", "r") as f:
    content = f.read()

content = content.replace("self.state_controller.register_callback(\"on_skill_key_duplicates_detected\", self._update_duplicate_colors)", "# Move to SkillPanelController logic")

with open("app_gui.py", "w") as f:
    f.write(content)
