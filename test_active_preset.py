import os
import sys

# Setup paths
sys.path.insert(0, os.path.abspath('.'))

from lib.features.skills.skill_preset_service import SkillPresetService
from lib.db.repositories.preset_state_manager import PresetStateManager
from lib.db.repositories.skill_preset_repository import SkillPresetRepository

def test():
    service = SkillPresetService()
    state_manager = PresetStateManager()
    preset_repo = SkillPresetRepository()

    # Create a dummy class and preset
    class_id = 1

    presets = preset_repo.get_presets_by_class(class_id)
    print(f"Presets for class {class_id}: {presets}")

    if not presets:
        print("No presets found. Let's create one.")
        res = service.create_custom_preset(class_id, "Test Preset", {})
        print(f"Created preset: {res}")
        presets = preset_repo.get_presets_by_class(class_id)

    if presets:
        preset_id = presets[0]["preset_id"]
        print(f"Applying preset {preset_id}")
        service.apply_preset(preset_id, class_id)

        active_preset_id = state_manager.get_active_preset(class_id)
        print(f"Active preset ID: {active_preset_id}")

        assert active_preset_id == preset_id, f"Expected {preset_id}, got {active_preset_id}"
        print("Test passed: Active preset correctly stored in DB.")

if __name__ == "__main__":
    test()
