from typing import List, Tuple
from ui.controllers.app_state_controller import AppStateController

class SkillConfigView:
    """
    View component responsible for the core logic related to UI skill configurations
    such as collecting, clearing, and refreshing attack keys from skill slots.
    """

    def __init__(self, state_controller: AppStateController):
        self.state_controller = state_controller

    def _refresh_skill_slots_options(self):
        if not hasattr(self.state_controller, "skill_slot_boxes"):
            return
        names = []
        skills = getattr(self.state_controller, "skills", [])
        for skill in skills:
            if skill.get("name", "Unknown") not in names:
                names.append(skill.get("name", "Unknown"))

        saved_names = getattr(self.state_controller, "skill_slot_saved_names", [])
        for saved in saved_names:
            if saved and saved not in names:
                names.append(saved)

        values = [""] + names
        for cmb in self.state_controller.skill_slot_boxes:
            cmb["values"] = values

        # Also refresh key labels next to each slot
        try:
            self.state_controller._refresh_slot_key_labels()
        except Exception:
            pass

    def _clear_skill_slot(self, var):
        var.set("")
        self._update_attack_keys_from_slots()

    def _update_attack_keys_from_slots(self):
        saved_names = [
            v.get().strip() for v in getattr(self.state_controller, "skill_slot_vars", []) if v.get().strip()
        ]
        self.state_controller.skill_slot_saved_names = saved_names
        self._refresh_skill_slots_options()

    def _collect_skill_slots(self) -> Tuple[List[dict], List[dict]]:
        if not hasattr(self.state_controller, "skill_slot_vars") or not self.state_controller.skill_slot_vars:
            self.state_controller.skill_slot_saved_names = []
            return [], []

        skills = getattr(self.state_controller, "skills", [])
        mapping = {skill.get("name", "Unknown"): skill for skill in skills}

        skill_slots = []
        buff_slots = []
        saved_names = []

        for i, var in enumerate(self.state_controller.skill_slot_vars):
            name = var.get().strip()
            if not name:
                continue
            skill = mapping.get(name)
            if not skill:
                continue
            saved_names.append(name)

            # The first 4 slots are attack (combo chain), next 4 are buff
            is_combo_lane = i < 4

            skill_type = skill.get("type", "attack")
            if is_combo_lane:
                skill_type = "attack"
            else:
                skill_type = "buff"

            slot_data = {
                "name": skill.get("name", "Unknown"),
                "key": skill.get("key", ""),
                "type": skill_type,
                "cooldown": float(skill.get("cooldown", 0.0)),
                "cast_time": float(skill.get("cast_time", 0.0)),
                "image": skill.get("image", ""),
            }

            if skill_type == "buff":
                duration = 300
                slot_data["duration_sec"] = duration
                buff_slots.append(slot_data)
            else:
                skill_slots.append(slot_data)

        self.state_controller.skill_slot_saved_names = saved_names
        return skill_slots, buff_slots
