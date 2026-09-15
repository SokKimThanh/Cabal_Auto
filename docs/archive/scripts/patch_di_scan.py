import re
with open("app_gui.py", "r") as f:
    content = f.read()

# Make sure scan_controller is correctly passed or mocked
di_assign2 = """        if di_container:
            self.monster_library_service = getattr(di_container, "monster_library_service", None)
            self.skill_service = getattr(di_container, "skill_service", None)
            self.db_skill_service = getattr(di_container, "db_skill_service", None)
            self.db_class_service = getattr(di_container, "db_class_service", None)
            self.db_scan_service = getattr(di_container, "db_scan_service", None)
            self.overlay_controller = getattr(di_container, "overlay_controller", None)
            self.skill_caster_service = getattr(di_container, "skill_caster_service", None)
            self.scan_controller = getattr(di_container, "scan_controller", None)"""

content = content.replace('''        if di_container:
            self.monster_library_service = getattr(di_container, "monster_library_service", None)
            self.skill_service = getattr(di_container, "skill_service", None)
            self.db_skill_service = getattr(di_container, "db_skill_service", None)
            self.db_class_service = getattr(di_container, "db_class_service", None)
            self.db_scan_service = getattr(di_container, "db_scan_service", None)
            self.overlay_controller = getattr(di_container, "overlay_controller", None)
            self.skill_caster_service = getattr(di_container, "skill_caster_service", None)''', di_assign2)

with open("app_gui.py", "w") as f:
    f.write(content)
