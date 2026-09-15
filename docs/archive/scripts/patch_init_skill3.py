with open("app_gui.py", "r") as f:
    content = f.read()

content = content.replace("        if hasattr(self.state_controller, \"register_callback\"):\n            # Move to SkillPanelController logic\n            # Move to SkillPanelController logic\n", "")

with open("app_gui.py", "w") as f:
    f.write(content)
