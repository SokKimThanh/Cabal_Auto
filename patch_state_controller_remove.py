with open('ui/controllers/app_state_controller.py', 'r') as f:
    lines = f.readlines()

new_lines = []
skip = False
for line in lines:
    if "def _update_window_bounds_display" in line or "def _validate_hunt_prerequisites" in line:
        skip = True

    if skip and ("def _clear_unsaved_changes" in line or "def build_hunt_config_from_state" in line or "def update_preset_state" in line or "def get_ui_var" in line):
        skip = False

    if not skip:
        new_lines.append(line)

with open('ui/controllers/app_state_controller.py', 'w') as f:
    f.writelines(new_lines)
