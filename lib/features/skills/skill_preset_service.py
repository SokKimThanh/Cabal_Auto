from typing import Dict, List, Any, Optional
from lib.db.repositories.skill_repository import SkillRepository
from lib.db.repositories.skill_preset_repository import SkillPresetRepository
from lib.db.repositories.preset_state_manager import PresetStateManager
import logging

logger = logging.getLogger(__name__)

class SkillPresetService:
    def __init__(self):
        self.skill_repo = SkillRepository()
        self.preset_repo = SkillPresetRepository()
        self.state_manager = PresetStateManager()

    def apply_preset(self, preset_id: int, class_name: str) -> Dict[str, Any]:
        """Applies a specific preset and updates state"""
        preset = self.preset_repo.get_preset(preset_id)
        if not preset:
            return {"success": False, "error": f"Preset {preset_id} not found", "skill_slots": {}}

        # Update user state
        self.state_manager.set_active_preset(class_name, preset_id, 'default')

        skills = self.preset_repo.get_preset_skills(preset_id)
        return {"success": True, "skill_slots": skills, "preset": preset}

    def create_custom_preset(self, class_name: str, name: str, skill_slots: Dict[str, List[int]]) -> Dict[str, Any]:
        """Creates a new custom preset and sets it as active"""
        try:
            preset_id = self.preset_repo.create_preset(class_name, name, is_default=0)
            if preset_id <= 0:
                return {"success": False, "error": "Failed to create preset"}

            success = self.preset_repo.set_preset_skills(preset_id, skill_slots)
            if not success:
                # Cleanup if skill insertion fails
                self.preset_repo.delete_preset(preset_id)
                return {"success": False, "error": "Failed to add skills to preset"}

            self.state_manager.set_active_preset(class_name, preset_id, 'default')
            return {"success": True, "preset_id": preset_id}
        except Exception as e:
            logger.error(f"Error creating custom preset: {e}")
            return {"success": False, "error": str(e)}

    def update_custom_preset(self, preset_id: int, skill_slots: Dict[str, List[int]]) -> bool:
        """Updates an existing custom preset (fails if trying to update default)"""
        preset = self.preset_repo.get_preset(preset_id)
        if not preset:
            return False
        if preset['is_default']:
            # Never overwrite a default preset directly
            return False

        return self.preset_repo.set_preset_skills(preset_id, skill_slots)

    def delete_custom_preset(self, preset_id: int) -> bool:
        preset = self.preset_repo.get_preset(preset_id)
        if not preset or preset['is_default']:
            return False
        return self.preset_repo.delete_preset(preset_id)

    def list_presets_by_class(self, class_name: str) -> List[Dict[str, Any]]:
        return self.preset_repo.get_presets_by_class(class_name)

    def migrate_legacy_presets(self, legacy_cfg: dict, class_name: str) -> None:
        """Migrates legacy JSON config skill_slots into the database as a default preset"""
        skill_slots_list = legacy_cfg.get("skill_slots", [])
        if not skill_slots_list:
            return

        # Check if default preset already exists for this class
        existing = self.list_presets_by_class(class_name)
        has_default = any(p['is_default'] for p in existing)

        if not has_default:
            preset_id = self.preset_repo.create_preset(class_name, "Migrated Legacy Preset", is_default=1)

            # Convert legacy array format to dictionary of lanes
            # We map attack skills to 'attack_combo' and buff skills to 'buff_lane'
            lanes = {'attack_combo': [], 'buff_lane': []}

            for slot in skill_slots_list:
                if isinstance(slot, dict) and 'id' in slot:
                    skill_id = slot['id']
                    # Look up skill type
                    skill_info = self.skill_repo.get_skill(skill_id)
                    if skill_info:
                        if skill_info['type'] == 'buff':
                            lanes['buff_lane'].append(skill_id)
                        else:
                            lanes['attack_combo'].append(skill_id)
                    else:
                        # Fallback to attack_combo
                        lanes['attack_combo'].append(skill_id)

            self.preset_repo.set_preset_skills(preset_id, lanes)
            self.state_manager.set_active_preset(class_name, preset_id, 'default')
            logger.info(f"Migrated legacy preset for {class_name}")
