with open('app_gui.py', 'r') as f:
    content = f.read()

content = content.replace("self.state_controller.set_ui_var('hunt_status',  if (\"hunt_status\" in self.state_controller.ui_vars) else lambda _: None", "lambda v: self.state_controller.set_ui_var('hunt_status', v)")
content = content.replace("self.state_controller.ui_vars['hunt_target_info'].set\n                if (\"hunt_target_info\" in self.state_controller.ui_vars)\n                else lambda _: None", "lambda v: self.state_controller.set_ui_var('hunt_target_info', v)")

with open('app_gui.py', 'w') as f:
    f.write(content)
