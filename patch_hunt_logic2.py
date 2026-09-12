with open('ui/controllers/app_state_controller.py', 'r') as f:
    content = f.read()

content = content.replace("self.ui_vars[\"global_hotkey_enabled\"].get()", "self.get_ui_var(\"global_hotkey_enabled\")")
content = content.replace("\"global_hotkey_enabled\" in self.ui_vars", "self.get_ui_var(\"global_hotkey_enabled\") is not None")

content = content.replace("variable = self.ui_vars.get(attr_name.replace(\"_var\", \"\"))\n                return (\n                    variable.get()\n                    if variable is not None\n                    else hotkeys.get(config_name, default)\n                )", "val = self.get_ui_var(attr_name.replace(\"_var\", \"\"))\n                return val if val is not None else hotkeys.get(config_name, default)")

content = content.replace("self.ui_vars[\"monster_estimate\"].set(\"\")", "self.set_ui_var(\"monster_estimate\", \"\")")
content = content.replace("self.ui_vars[\"monster_estimate\"].set(", "self.set_ui_var(\"monster_estimate\", ")
content = content.replace("\"monster_estimate\" not in self.ui_vars", "self.get_ui_var(\"monster_estimate\") is None")

content = content.replace("self.ui_vars['template'].set(first_path)", "self.set_ui_var('template', first_path)")
content = content.replace("\"template\" in self.ui_vars", "self.get_ui_var(\"template\") is not None")

content = content.replace("self.ui_vars['attack_duration'].set(f\"{attack_min:.2f}\")", "self.set_ui_var('attack_duration', f\"{attack_min:.2f}\")")
content = content.replace("\"attack_duration\" in self.ui_vars", "self.get_ui_var(\"attack_duration\") is not None")

content = content.replace("self.ui_vars['lost_timeout'].set(f\"{lost_timeout:.2f}\")", "self.set_ui_var('lost_timeout', f\"{lost_timeout:.2f}\")")
content = content.replace("\"lost_timeout\" in self.ui_vars", "self.get_ui_var(\"lost_timeout\") is not None")

content = content.replace("\"window_bounds_display\" not in self.ui_vars", "self.get_ui_var(\"window_bounds_display\") is None")
content = content.replace("self.ui_vars[\"window_bounds_display\"].set(\n                f\"{bounds[0]}, {bounds[1]}, {bounds[2]}, {bounds[3]}\"\n            )", "self.set_ui_var(\"window_bounds_display\", f\"{bounds[0]}, {bounds[1]}, {bounds[2]}, {bounds[3]}\")")
content = content.replace("self.ui_vars[\"window_bounds_display\"].set(\"\")", "self.set_ui_var(\"window_bounds_display\", \"\")")

content = content.replace("self.ui_vars[\"hunt_status\"].set(text)", "self.set_ui_var(\"hunt_status\", text)")
content = content.replace("\"bounds_status\" in self.ui_vars", "self.get_ui_var(\"bounds_status\") is not None")

content = content.replace("self.ui_vars[\"win_combo\"].get()", "self.get_ui_var(\"win_combo\")")
content = content.replace("\"win_combo\" in self.ui_vars", "self.get_ui_var(\"win_combo\") is not None")

with open('ui/controllers/app_state_controller.py', 'w') as f:
    f.write(content)
