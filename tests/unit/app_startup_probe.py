import time
import traceback
import tkinter as tk
from unittest.mock import MagicMock

try:
    from app_gui import App
except Exception as e:
    print("IMPORT_APP_FAILED:", e)
    traceback.print_exc()
    raise

try:
    from lib.core.app_container import AppContainer
    from lib.features.monsters.monster_library_service import MonsterLibraryService
    from lib.features.skills.skill_runtime_service import SkillRuntimeService
    from lib.db.services.skill_service import SkillService as DbSkillService
    from lib.db.services.class_service import ClassService as DbClassService
    from lib.db.services.scan_service import ScanService
    from lib.features.skills.skill_caster_service import SkillCasterService

    root = tk.Tk()
    container = AppContainer()

    container.monster_library_service = MonsterLibraryService()
    container.skill_service = SkillRuntimeService()
    from lib.db.services.skill_type_service import SkillTypeService
    container.db_skill_service = DbSkillService()
    container.db_skill_type_service = SkillTypeService()
    container.db_class_service = DbClassService()
    container.db_scan_service = ScanService()
    # Mock return value so it unpacks correctly
    container.db_scan_service.get_scans_with_details = MagicMock(return_value=([], 0))
    container.skill_caster_service = SkillCasterService()

    app = App(root=root, di_container=container)
    # wait briefly to allow registration prints to appear
    time.sleep(1)
    try:
        diag = getattr(app, "_failed_hotkeys", {})
        handlers = list(getattr(app, "_registered_hotkey_handlers", {}).keys())
        ok = getattr(app, "_hotkeys_registered_ok", None)
        print("HOTKEYS_FAILED:", diag)
        print("REGISTERED_HANDLERS:", handlers)
        print("HOTKEYS_OK:", ok)
    except Exception as e:
        print("DIAG_CAPTURE_FAILED:", e)
        traceback.print_exc()
    try:
        root.destroy()
    except Exception as e:
        print("APP_DESTROY_FAILED:", e)
    print("PROBE_DONE")
except Exception as e:
    print("PROBE_EXCEPTION:", e)
    traceback.print_exc()
