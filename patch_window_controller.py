with open('ui/controllers/app_window_controller.py', 'r') as f:
    content = f.read()

content = content.replace("if (\"hunt_status\" in self.root.state_controller.ui_vars):\n                self.root.state_controller.ui_vars['hunt_status'].set", "self.root.state_controller.set_ui_var('hunt_status', ")
content = content.replace("if (\"hunt_status\" in self.root.state_controller.ui_vars):\n            self.root.state_controller.ui_vars['hunt_status'].set", "self.root.state_controller.set_ui_var('hunt_status', ")
content = content.replace("self.root.state_controller.ui_vars['win_combo'].get()", "self.root.state_controller.get_ui_var('win_combo')")
content = content.replace("if (\"win_combo\" in self.root.state_controller.ui_vars)\n                else \"\"", "if True else \"\"")
content = content.replace("if (\"win_combo\" in self.root.state_controller.ui_vars):\n                        self.root.state_controller.ui_vars['win_combo'].set", "self.root.state_controller.set_ui_var('win_combo', ")
content = content.replace("if (\"setup_lost_timeout\" in self.root.state_controller.ui_vars):\n                self.root.state_controller.ui_vars['setup_lost_timeout'].set", "self.root.state_controller.set_ui_var('setup_lost_timeout', ")

with open('ui/controllers/app_window_controller.py', 'w') as f:
    f.write(content)
