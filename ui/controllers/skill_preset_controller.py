class SkillPresetController:
    """Controller for SkillPanel to manage preset operations."""
    def __init__(self, parent_frame, app_state):
        self.parent_frame = parent_frame
        self.app_state = app_state
        from lib.features.skills.skill_preset_service import SkillPresetService
        self.skill_service = SkillPresetService()

    def on_presets(self):
        """Opens preset dialog."""
        from ui.dialogs.preset_dialog import PresetDialog
        PresetDialog(self.parent_frame, self.app_state)

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
        from ui.dialogs.create_preset_dialog import CreatePresetDialog
        import tkinter.messagebox as messagebox

        # Disable button to prevent multiple clicks
        if btn_widget:
            btn_widget.config(state="disabled")

        skill_slots = getattr(self.app_state, "skill_slots", {"attack_combo": [], "buff_lane": []})
        skill_summary = self.prepare_skill_summary(skill_slots)

        def _on_save(preset_name):
            parsed_slots = self.parse_skill_slots(skill_slots)

            res = self.skill_service.create_custom_preset(class_id, preset_name, parsed_slots)
            if res.get("success"):
                messagebox.showinfo("Success", f"Đã lưu preset '{preset_name}' thành công!", parent=self.parent_frame)

                # Update root state with new preset ID and mode
                new_preset_id = res.get("preset_id")
                if new_preset_id and hasattr(self.app_state, "root"):
                    self.app_state.root._active_preset_id = new_preset_id
                    self.app_state.root._preset_mode = "custom"

                # Refresh indicator
                if on_slots_changed_callback:
                    on_slots_changed_callback(skill_slots)
            else:
                messagebox.showerror("Error", f"Lỗi khi lưu preset: {res.get('error')}", parent=self.parent_frame)

        # Assuming winfo_toplevel is available on parent_frame
        try:
            toplevel = self.parent_frame.winfo_toplevel()
        except AttributeError:
            toplevel = self.parent_frame

        dialog = CreatePresetDialog(
            parent=toplevel,
            class_id=class_id,
            skill_summary=skill_summary,
            on_save_callback=_on_save
        )

        # Need a way to wait for the dialog. If parent_frame is a widget:
        if hasattr(self.parent_frame, "wait_window"):
            self.parent_frame.wait_window(dialog)

        # Safely re-enable button
        if btn_widget and hasattr(btn_widget, "winfo_exists") and btn_widget.winfo_exists():
            btn_widget.config(state="normal")
