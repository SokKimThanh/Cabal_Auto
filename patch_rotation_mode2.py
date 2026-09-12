with open('app_gui.py', 'r') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if "self.state_controller.set_ui_var('hunt_status', " in line and line.strip().endswith("mode}\")"):
        lines[i] = line.replace("mode}\")", "mode}\")\n")

with open('app_gui.py', 'w') as f:
    f.writelines(lines)
