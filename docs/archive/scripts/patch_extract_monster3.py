import re

with open("app_gui.py", "r") as f:
    content = f.read()

# Completely remove the wrappers now that we verified logic exists in MRC
# For methods like _load_monster_rotation_list, we simply delete them.

methods_to_remove = [
    "_load_monster_rotation_list",
    "_refresh_monster_select_options",
    "_update_monster_frame_title",
    "on_monster_select_change",
    "on_monster_apply_from_select",
    "on_monster_use_for_hunt",
    "on_start_stop_clicked",
    "_refresh_start_stop_visual",
    "_reenable_start_stop_btn",
]

for method in methods_to_remove:
    pattern = rf"def {method}\(self.*?\):\n(?:    +.*\n)*"
    content = re.sub(pattern, "", content)

with open("app_gui.py", "w") as f:
    f.write(content)
