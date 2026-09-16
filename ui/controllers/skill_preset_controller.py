from lib.i18n import GLOBAL_NS as I18N_GLOBAL
from lib.i18n import t as i18n_t
from typing import Optional
class SkillPresetController:
    """Controller for SkillPanel to manage preset operations."""
    def __init__(self, parent_frame, app_state):
        self.parent_frame = parent_frame
        self.app_state = app_state
        from lib.features.skills.skill_preset_service import SkillPresetService
        self.skill_service = SkillPresetService()

    def on_presets(self):
        """Opens preset dialog."""
        from ui.services.dialog_service import DialogService
        DialogService.open_preset_dialog(self.parent_frame, self.app_state)

    def on_reset(self, class_id):
        """Reverts to default preset."""
        self.apply_default_preset(class_id)

    def prepare_skill_summary(self, skill_slots):
        """Prepares a summary of skills by name for the save dialog."""
        skill_summary = {}
        for lane, skills in skill_slots.items():
            lane_names = []
            for slot_data in skills:
                if not slot_data:
                    continue
                skill_id = slot_data.get("skill_id") if isinstance(slot_data, dict) else slot_data
                if skill_id is not None:
                    skill = self.skill_service.skill_repo.get_skill(skill_id)
                    if skill:
                        lane_names.append(skill.get("name", f"Unknown ID {skill_id}"))
            skill_summary[lane] = lane_names
        return skill_summary

    def parse_skill_slots(self, skill_slots):
        """Parses skill slots dict/int structure to a plain list of IDs."""
        parsed_slots = {}
        for lane, skills in skill_slots.items():
            parsed_lane = []
            for slot_data in skills:
                if not slot_data:
                    continue
                skill_id = slot_data.get("skill_id") if isinstance(slot_data, dict) else slot_data
                if skill_id is not None:
                    parsed_lane.append(skill_id)
            parsed_slots[lane] = parsed_lane
        return parsed_slots

    def on_save_preset_click(self, class_id, btn_widget, on_slots_changed_callback):
        """Handles the save preset click flow."""
        from ui.services.dialog_service import DialogService

        # Disable button to prevent multiple clicks
        if btn_widget:
            btn_widget.config(state="disabled")

        skill_slots = getattr(self.app_state, "skill_slots", {"attack_combo": [], "buff_lane": []})
        skill_summary = self.prepare_skill_summary(skill_slots)

        def _on_save(preset_name):
            parsed_slots = self.parse_skill_slots(skill_slots)

            res = self.skill_service.create_custom_preset(class_id, preset_name, parsed_slots)
            if res.get("success"):
                DialogService.show_info("Success", f"Đã lưu preset '{preset_name}' thành công!", parent=self.parent_frame)

                # Update root state with new preset ID and mode via app_state
                new_preset_id = res.get("preset_id")
                if new_preset_id and hasattr(self.app_state, "update_preset_state"):
                    self.app_state.update_preset_state(new_preset_id, "custom")

                # Refresh indicator
                if on_slots_changed_callback:
                    on_slots_changed_callback(skill_slots)
            else:
                DialogService.show_error("Error", f"Lỗi khi lưu preset: {res.get('error')}", parent=self.parent_frame)

        DialogService.open_create_preset_dialog(
            parent=self.parent_frame,
            class_id=class_id,
            skill_summary=skill_summary,
            on_save_callback=_on_save
        )

        # Safely re-enable button
        if btn_widget and hasattr(btn_widget, "winfo_exists") and btn_widget.winfo_exists():
            btn_widget.config(state="normal")

    def set_current_class(self, class_id: int) -> bool:
        """
        Safely changes the current class, prompting for unsaved changes if necessary.
        Returns True if the class was changed, False if the user cancelled.
        """
        import tkinter.messagebox as messagebox

        if getattr(self.app_state, "has_unsaved_changes", False):
            title = i18n_t("warning_title", ns=I18N_GLOBAL)
            msg = i18n_t("msg_unsaved_class_change", ns=I18N_GLOBAL)

            if not messagebox.askyesno(title, msg, parent=self.app_state.root):
                return False

        self.app_state._current_class_id = class_id

        # Save to hunt_cfg
        if hasattr(self.app_state.root, "hunt_cfg"):
            self.app_state.hunt_cfg["last_active_class_id"] = class_id
            from lib.features.hunt.hunt_config import save_hunt_config
            save_hunt_config(self.app_state.hunt_cfg)

        # Clear unsaved changes since we are loading a fresh preset from DB
        self.app_state._clear_unsaved_changes()

        # Auto load preset for the new class
        self.load_preset_for_class(class_id)

        return True

    def apply_default_preset(self, class_id: int) -> None:
        self.load_preset_for_class(class_id)

    def set_custom_mode(self) -> None:
        self.app_state._preset_mode = "custom"
        self.app_state._emit_event("on_preset_changed")

    def update_preset_state(self, preset_id: int, mode: str) -> None:
        """Encapsulates preset state updates."""
        self.app_state._active_preset_id = preset_id
        self.app_state._preset_mode = mode
        self.app_state._emit_event("on_preset_changed")

    def save_custom_preset(self, preset_name: str) -> None:
        from lib.features.skills.skill_preset_service import SkillPresetService

        if self.app_state._preset_mode == "custom" and self.app_state._active_preset_id:
            service = SkillPresetService()
            preset = service.preset_repo.get_preset(self.app_state._active_preset_id)
            if preset and not preset.get("is_default"):
                skill_slots_for_db = {
                    lane: [s["skill_id"] for s in self.app_state.skill_slots.get(lane, [])]
                    for lane in self.app_state.skill_slots
                }
                service.update_custom_preset(
                    self.app_state._active_preset_id, skill_slots_for_db
                )
            else:
                # Need to create new custom preset
                skill_slots_for_db = {
                    lane: [s["skill_id"] for s in self.app_state.skill_slots.get(lane, [])]
                    for lane in self.app_state.skill_slots
                }
                res = service.create_custom_preset(
                    self.app_state._current_class_id, preset_name, skill_slots_for_db
                )
                if res.get("success"):
                    self.app_state._active_preset_id = res.get("preset_id")
        else:
            # Need to create new custom preset
            service = SkillPresetService()
            skill_slots_for_db = {
                lane: [s["skill_id"] for s in self.app_state.skill_slots.get(lane, [])]
                for lane in self.app_state.skill_slots
            }
            res = service.create_custom_preset(
                self.app_state._current_class_id, preset_name, skill_slots_for_db
            )
            if res.get("success"):
                self.app_state._active_preset_id = res.get("preset_id")
                self.app_state._preset_mode = "custom"

        self.app_state._emit_event("on_preset_changed")

    def get_available_presets(self, class_id: int) -> list:
        from lib.features.skills.skill_preset_service import SkillPresetService

        service = SkillPresetService()
        return service.list_presets_by_class(class_id)

    def set_skill_slot(self, lane: str, position: int, skill_id: int) -> None:
        if lane not in self.app_state.skill_slots:
            self.app_state.skill_slots[lane] = []
        while len(self.app_state.skill_slots[lane]) <= position:
            self.app_state.skill_slots[lane].append(
                {
                    "position": len(self.app_state.skill_slots[lane]),
                    "lane_type": lane,
                    "skill_id": None,
                    "skill_name": "",
                    "user_hotkey": "",
                    "assigned": False,
                    "is_ready": True,
                    "cooldown_remaining": 0.0,
                }
            )
        self.app_state.skill_slots[lane][position]["skill_id"] = skill_id
        self.app_state.skill_slots[lane][position]["assigned"] = skill_id is not None

        # If changing a slot in default mode, automatically switch to custom mode
        if self.app_state._preset_mode == "default":
            self.set_custom_mode()

        self.app_state._emit_event("on_skill_slots_changed")

    def set_skill_hotkey(self, lane: str, position: int, hotkey: str) -> None:
        if lane in self.app_state.skill_slots and position < len(
            self.app_state.skill_slots[lane]
        ):
            self.app_state.skill_slots[lane][position]["user_hotkey"] = hotkey
            self.app_state._emit_event("on_hotkey_changed")

    def update_skill_cooldown(self, lane: str, position: int, remaining: float) -> None:
        if lane in self.app_state.skill_slots and position < len(
            self.app_state.skill_slots[lane]
        ):
            self.app_state.skill_slots[lane][position]["cooldown_remaining"] = remaining
            self.app_state.skill_slots[lane][position]["is_ready"] = remaining <= 0.0
            self.app_state._emit_event("on_cooldown_updated")

    def load_preset_for_class(
        self, class_id: int, preset_id: Optional[int] = None
    ) -> None:
        self.app_state._current_class_id = class_id
        from lib.features.skills.skill_preset_service import SkillPresetService

        service = SkillPresetService()
        if preset_id is None:
            # Try to load default preset
            presets = service.list_presets_by_class(class_id)
            default_preset = next((p for p in presets if p["is_default"]), None)
            if default_preset:
                preset_id = default_preset["preset_id"]
            elif presets:
                preset_id = presets[0]["preset_id"]

        if preset_id is not None:
            result = service.apply_preset(preset_id, class_id)
            if result.get("success"):
                self.app_state._active_preset_id = preset_id
                mode = "default" if result["preset"].get("is_default") else "custom"
                self.app_state._preset_mode = mode

                # Transform to app state structure
                self.app_state.skill_slots = {"attack_combo": [], "buff_lane": []}
                for lane, skill_ids in result.get("skill_slots", {}).items():
                    for idx, skill_id in enumerate(skill_ids):
                        self.app_state.skill_slots[lane].append(
                            {
                                "position": idx,
                                "lane_type": lane,
                                "skill_id": skill_id,
                                "skill_name": "Unknown",  # Will populate later or via UI
                                "user_hotkey": "",
                                "assigned": False,
                                "is_ready": True,
                                "cooldown_remaining": 0.0,
                            }
                        )
                self.app_state._emit_event("on_preset_changed")
                self.app_state._emit_event("on_skill_slots_changed")
        else:
            # When the class has no presets at all, clear the skill slots
            self.app_state._active_preset_id = None
            self.app_state._preset_mode = "custom"
            self.app_state.skill_slots = {"attack_combo": [], "buff_lane": []}
            self.app_state._emit_event("on_preset_changed")
            self.app_state._emit_event("on_skill_slots_changed")
