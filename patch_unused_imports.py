import re

with open('app_gui.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []

for idx, line in enumerate(lines):
    # W0404: Reimport 'DialogService'
    if line.strip() == "from lib.ui.dialog_service import DialogService" and idx > 100:
        continue # skip re-imports further down
    # W0404: Reimport 'WindowSelectionService'
    if line.strip() == "from lib.features.hunt.window_selection_service import WindowSelectionService" and idx > 100:
        continue
    # W0404: Reimport HuntRunner, HuntOrchestrator, SkillCasterService, TargetLocatorService, tkinter (lines 3088+)
    if idx > 2750:
        if line.strip() == "from lib.features.hunt.hunt_runner import HuntRunner": continue
        if line.strip() == "from lib.features.hunt.hunt_orchestrator import HuntOrchestrator": continue
        if line.strip() == "from lib.features.skills.skill_caster_service import SkillCasterService": continue
        if line.strip() == "from lib.features.hunt.target_locator import TargetLocatorService": continue
        if line.strip() == "import tkinter as tk": continue
        if line.strip() == "from ui.icon_library import Icons": continue

    # W0611 unused imports (top of file 1-50)
    if idx < 60:
        if "from lib.features.skills.skill_caster_service import SkillCasterService" in line: continue
        if "from lib.features.hunt.target_locator import TargetLocatorService" in line: continue
        if "from lib.features.hunt.hunt_orchestrator import HuntOrchestrator" in line: continue
        if "from lib.features.hunt.hunt_runner import HuntRunner" in line: continue
        if "from ui.helpers.tooltip import attach_i18n_tooltip" in line: continue
        if "from typing import Any" in line: continue
        if "from dataclasses import dataclass" in line: continue

    # Unused in App.__init__
    if idx > 250 and idx < 320:
        if "getter" in line and "def getter():" in line:
            continue
        if "return self._vision_engine" in line or "return get_vision_engine()" in line:
            # We'll just remove the getter function and its calls
            continue
        if "from lib.features.hunt.scan_controller import ScanController" in line: continue
        if "from ui.icon_library import Icons" in line: continue
        if "from ui.controllers.overlay_controller import (" in line: continue
        if "OverlayController as AppOverlayController," in line: continue
        if "from lib.features.monsters.monster_library_service import MonsterLibraryService" in line: continue
        if "from lib.features.skills.skill_runtime_service import SkillRuntimeService" in line: continue
        if "from lib.db.services.skill_service import SkillService as DbSkillService" in line: continue
        if "from lib.db.services.class_service import ClassService as DbClassService" in line: continue
        if "self.scan_controller = di_container.scan_controller if di_container else None" in line: continue

    # Unused module at line 1295
    if "import importlib" in line and idx > 1200 and idx < 1320:
        pass # wait, let me check where 'module' is defined in line 1295

    new_lines.append(line)

with open('app_gui.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
print("Unused imports patched.")
