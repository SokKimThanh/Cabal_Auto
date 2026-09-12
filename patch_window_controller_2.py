with open('ui/controllers/app_window_controller.py', 'r') as f:
    lines = f.readlines()

new_lines = []
skip = False
for i, line in enumerate(lines):
    if skip:
        skip = False
        continue
    if "if (\"hunt_status\" in self.root.state_controller.ui_vars):" in line:
        pass # we just ignore this line and write the contents with set_ui_var
    elif "self.root.state_controller.ui_vars['hunt_status'].set(" in line:
        new_lines.append(line.replace("self.root.state_controller.ui_vars['hunt_status'].set(", "self.root.state_controller.set_ui_var('hunt_status', "))
    else:
        new_lines.append(line)

with open('ui/controllers/app_window_controller.py', 'w') as f:
    f.writelines(new_lines)
