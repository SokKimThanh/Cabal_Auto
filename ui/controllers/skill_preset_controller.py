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
        if hasattr(self.app_state, "apply_default_preset"):
            self.app_state.apply_default_preset(class_id)

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
