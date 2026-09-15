import re

with open("app_gui.py", "r") as f:
    content = f.read()

def replace_body(method_name, new_body, content):
    pattern = rf"def {method_name}\(self.*?\):\n(?:    +.*\n)*"
    match = re.search(pattern, content)
    if match:
        content = content[:match.start()] + new_body + content[match.end():]
    return content

# Methods to extract to MonsterRotationController
methods_to_extract = [
    "_load_monster_rotation_list",
    "_refresh_monster_select_options",
    "_update_monster_frame_title",
    "_update_monster_status",
    "on_monster_select_change",
    "on_monster_apply_from_select",
    "on_monster_use_for_hunt"
]

for method in methods_to_extract:
    clean_name = method.lstrip('_')
    body = f"""def {method}(self, *args, **kwargs):
        if hasattr(self, 'monster_rotation_controller') and self.monster_rotation_controller:
            return self.monster_rotation_controller.{clean_name}(*args, **kwargs)
\n"""
    content = replace_body(method, body, content)

with open("app_gui.py", "w") as f:
    f.write(content)
