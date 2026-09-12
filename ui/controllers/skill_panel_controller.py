from lib.db.services.class_service import ClassService
from lib.features.skills.skill_preset_service import SkillPresetService


class SkillPanelController:
    """Controller for SkillPanel to manage class/skill loading and business state."""
    def __init__(self, app_state):
        self.app_state = app_state
        self.skill_service = SkillPresetService()
        self.class_service = ClassService()

        # Business states
        self.show_all_skills = False
        self.class_list = []
        self.skill_names = []
        self.last_selected_class = ""
        self.previous_show_all_skills = None

    def load_classes(self):
        """Loads available classes and returns values list and default value."""
        self.class_list = self.class_service.get_all_classes()
        values = []
        default_val = ""
        current_class_id = getattr(
            self.app_state.root if hasattr(self.app_state, "root") else self.app_state,
            "_current_class_id",
            1
        )

        for c in self.class_list:
            val = f"{c['id']} - {c['name']}"
            values.append(val)
            if c['id'] == current_class_id:
                default_val = val

        if default_val:
            self.last_selected_class = default_val
        elif values:
            self.last_selected_class = values[0]

        return values, default_val

    def load_skills(self):
        """Loads skills based on current state (all or class specific)."""
        class_id = getattr(self.app_state, "_current_class_id", 1)
        skills = self.skill_service.skill_repo.list_skills(
            class_id=class_id, include_all=self.show_all_skills
        )
        self.skill_names = [s.get("name") for s in skills if s.get("name")]
        return self.skill_names

    def on_class_selected(self, selected_val):
        """Handles class selection change."""
        if not selected_val or selected_val == "---":
            return False, self.last_selected_class, self.skill_names

        try:
            class_id = int(selected_val.split(" - ")[0])
        except (ValueError, IndexError):
            return False, self.last_selected_class, self.skill_names

        if hasattr(self.app_state, "set_current_class"):
            # Prepare skills for the newly selected class
            skills = self.skill_service.skill_repo.list_skills(class_id=class_id, include_all=False)
            new_skill_names = [s.get("name") for s in skills if s.get("name")]

            # Change state
            success = self.app_state.set_current_class(class_id)
            if not success:
                # Revert if failed
                old_id = int(self.last_selected_class.split(" - ")[0]) if self.last_selected_class else 1
                skills = self.skill_service.skill_repo.list_skills(class_id=old_id, include_all=False)
                self.skill_names = [s.get("name") for s in skills if s.get("name")]
                return False, self.last_selected_class, self.skill_names
            else:
                self.last_selected_class = selected_val
                self.skill_names = new_skill_names
                return True, self.last_selected_class, self.skill_names

        return False, self.last_selected_class, self.skill_names

    def toggle_skills(self):
        """Toggles between showing all skills and class-specific skills."""
        self.show_all_skills = not self.show_all_skills

        if self.show_all_skills:
            skills = self.skill_service.skill_repo.list_skills(include_all=True)
        else:
            class_id = getattr(self.app_state, "_current_class_id", 1)
            skills = self.skill_service.skill_repo.list_skills(class_id=class_id, include_all=False)

        self.skill_names = [s.get("name") for s in skills if s.get("name")]
        return self.show_all_skills, self.skill_names

    def handle_bot_state_change(self, is_running):
        """Handles bot state changes to lock/unlock UI state."""
        if is_running:
            if self.previous_show_all_skills is None:
                self.previous_show_all_skills = self.show_all_skills
            self.show_all_skills = False

            class_id = getattr(self.app_state, "_current_class_id", 1)
            # Find the corresponding class label for cb_class
            class_label = ""
            for val in [f"{c['id']} - {c['name']}" for c in self.class_list]:
                if val.startswith(f"{class_id} -"):
                    class_label = val
                    self.last_selected_class = val
                    break

            skills = self.skill_service.skill_repo.list_skills(class_id=class_id, include_all=False)
            self.skill_names = [s.get("name") for s in skills if s.get("name")]
            return True, class_label, self.skill_names
        else:
            if self.previous_show_all_skills is not None:
                self.show_all_skills = self.previous_show_all_skills
                self.previous_show_all_skills = None

            # Re-load skills just in case
            if self.show_all_skills:
                skills = self.skill_service.skill_repo.list_skills(include_all=True)
            else:
                class_id = getattr(self.app_state, "_current_class_id", 1)
                skills = self.skill_service.skill_repo.list_skills(class_id=class_id, include_all=False)

            self.skill_names = [s.get("name") for s in skills if s.get("name")]
            return False, self.last_selected_class, self.skill_names

    def get_skill_id_by_name(self, skill_name):
        """Looks up a skill ID by its name."""
        skills = self.skill_service.skill_repo.list_skills(include_all=True)
        for s in skills:
            if s.get("name") == skill_name:
                return s.get("skill_id")
        return None

    def get_skill(self, skill_id):
        """Gets a skill by its ID."""
        return self.skill_service.skill_repo.get_skill(skill_id)
