import re
with open("app_gui.py", "r") as f:
    content = f.read()

content = content.replace("self.state_controller.register_callback(\"on_skill_keys_updated\", self._update_skill_keys)", "# Move to SkillPanelController logic")
content = content.replace("self.state_controller.register_callback(\"on_duplicate_colors_updated\", self._update_duplicate_colors)", "# Move to SkillPanelController logic")

with open("app_gui.py", "w") as f:
    f.write(content)
