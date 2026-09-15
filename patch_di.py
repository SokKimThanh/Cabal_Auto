import re

with open("app_gui.py", "r") as f:
    content = f.read()

# Move the di_container assignment to the beginning of __init__
init_def = "def __init__(self, root, di_container=None):\n        self.root = root"

di_assign = '''
        if di_container:
            self.monster_library_service = getattr(di_container, "monster_library_service", None)
            self.skill_service = getattr(di_container, "skill_service", None)
            self.db_skill_service = getattr(di_container, "db_skill_service", None)
            self.db_class_service = getattr(di_container, "db_class_service", None)
            self.db_scan_service = getattr(di_container, "db_scan_service", None)
            self.overlay_controller = getattr(di_container, "overlay_controller", None)
            self.skill_caster_service = getattr(di_container, "skill_caster_service", None)
'''

# We need to remove the existing DI assignments that are lower down.
# Then insert them near the top.
# Using a simpler strategy: replace the first occurrence of `self.root = root`
# and delete the original DI block later.

new_init = init_def + di_assign
content = content.replace("def __init__(self, root, di_container=None):\n        self.root = root", new_init, 1)

# Now remove the old block
old_block_regex = r"        if di_container:\s*self\.monster_library_service = di_container\.monster_library_service\s*self\.skill_service = di_container\.skill_service\s*self\.db_skill_service = di_container\.db_skill_service\s*self\.db_class_service = di_container\.db_class_service\s*self\.db_scan_service = di_container\.db_scan_service\s*self\.overlay_controller = di_container\.overlay_controller\s*self\.skill_caster_service = di_container\.skill_caster_service"
content = re.sub(old_block_regex, "", content)

with open("app_gui.py", "w") as f:
    f.write(content)
