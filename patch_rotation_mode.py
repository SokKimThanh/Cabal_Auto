with open('app_gui.py', 'r') as f:
    content = f.read()

content = content.replace("display_mode = self.state_controller.ui_vars['rotation_mode'].get()", "display_mode = self.state_controller.get_ui_var('rotation_mode')")
content = content.replace("self.hunt_cfg[\"rotation_mode\"] = mode", "self.state_controller.hunt_cfg[\"rotation_mode\"] = mode")
content = content.replace("self.state_controller.ui_vars['hunt_status'].set", "self.state_controller.set_ui_var('hunt_status', ")

with open('app_gui.py', 'w') as f:
    f.write(content)
