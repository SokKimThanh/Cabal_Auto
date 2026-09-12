with open('ui/panels/monster_target_panel.py', 'r') as f:
    content = f.read()

content = content.replace("self.app.state_controller.ui_vars['target_policy'].get()", "self.app.state_controller.get_ui_var('target_policy')")
content = content.replace("self.app.state_controller.ui_vars['target_policy'] = tk.StringVar(", "self.app.state_controller.ui_vars['target_policy'] = tk.StringVar(")
content = content.replace("self.app.state_controller.ui_vars['target_policy'].set(", "self.app.state_controller.set_ui_var('target_policy', ")
content = content.replace("hasattr(self.app.state_controller.ui_vars['target_policy'], \"trace_add\")", "hasattr(self.app.state_controller.ui_vars.get('target_policy'), \"trace_add\")")
content = content.replace("self.app.state_controller.ui_vars['target_policy'].trace_add", "self.app.state_controller.ui_vars['target_policy'].trace_add")
content = content.replace("variable=self.app.state_controller.ui_vars['target_policy']", "variable=self.app.state_controller.ui_vars['target_policy']")


with open('ui/panels/monster_target_panel.py', 'w') as f:
    f.write(content)
