with open('app_gui.py', 'r') as f:
    content = f.read()

content = content.replace("self.state_controller._apply_monster_to_hunt_quick(monster)", "from lib.features.hunt.hunt_setup_service import HuntSetupService\n            HuntSetupService.apply_monster_to_hunt_quick(monster, self.state_controller)")

with open('app_gui.py', 'w') as f:
    f.write(content)

with open('ui/controllers/app_state_controller.py', 'r') as f:
    lines = f.readlines()

new_lines = []
skip = False
for line in lines:
    if "def _calculate_monster_estimate" in line or "def _recommend_attack_settings" in line or "def _update_monster_estimate_label" in line or "def _apply_monster_to_hunt_quick" in line:
        skip = True

    if skip and ("def _refresh_slot_key_labels" in line or "def _update_window_bounds_display" in line):
        skip = False

    if not skip:
        new_lines.append(line)

with open('ui/controllers/app_state_controller.py', 'w') as f:
    f.writelines(new_lines)
