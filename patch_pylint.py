import re

with open('app_gui.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
skip_next = False
for i, line in enumerate(lines):
    if skip_next:
        skip_next = False
        continue

    # E1101: self.state_controller._update_window_bounds_display()
    if 'self.state_controller._update_window_bounds_display()' in line:
        line = line.replace('self.state_controller._update_window_bounds_display()', 'self.window_controller.update_window_bounds_display()')

    # E1101: self.icon_helper._icon_cache -> self.icon_helper._cache
    if 'self.icon_helper._icon_cache' in line:
        line = line.replace('self.icon_helper._icon_cache', 'self.icon_helper._cache')

    # Remove E1101: _update_monster_estimate_label
    if '_update_monster_estimate_label' in line:
        continue

    # E1101: skill_slot_duration_vars check in _collect_skill_slots
    if 'self.skill_slot_duration_vars' in line or 'self.state_controller.skill_slot_duration_vars' in line:
        if 'if hasattr(self, "skill_slot_duration_vars")' in line:
            # We skip the condition and its body and just use default duration
            # Let's fix this manually with sed later if needed, but wait:
            pass

    new_lines.append(line)

with open('app_gui.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
print("Initial substitutions applied.")
