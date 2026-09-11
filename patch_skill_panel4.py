with open("ui/panels/skill_panel.py", "r") as f:
    content = f.read()

# I see it didn't match the string perfectly. Let's do a more robust approach.
search_str = "    def _build_lanes(self):"

methods_str = """
    def _load_classes(self):
        class_service = ClassService()
        classes = class_service.get_all_classes()
        self._class_list = classes

        values = []
        default_val = ""
        current_class_id = getattr(self.app_state, "_current_class_id", 1)

        for c in classes:
            val = f"{c['id']} - {c['name']}"
            values.append(val)
            if c['id'] == current_class_id:
                default_val = val

        self.widgets["cb_class"].config(values=values)
        if default_val:
            self.widgets["cb_class"].set(default_val)
            self._last_selected_class = default_val
        elif values:
            self.widgets["cb_class"].set(values[0])
            self._last_selected_class = values[0]

    def _on_class_selected(self, event):
        selected_val = self.widgets["cb_class"].get()
        if not selected_val:
            return

        try:
            class_id = int(selected_val.split(" - ")[0])
        except (ValueError, IndexError):
            self.widgets["cb_class"].set(self._last_selected_class)
            return

        if hasattr(self.app_state, "set_current_class"):
            success = self.app_state.set_current_class(class_id)
            if not success:
                self.widgets["cb_class"].set(getattr(self, "_last_selected_class", ""))
            else:
                self._last_selected_class = selected_val
                # Reload skills for dropdowns
                self._show_all_skills = False
                self._update_toggle_button_visuals()

                skills = self.skill_service.skill_repo.list_skills(class_id=class_id, include_all=self._show_all_skills)
                self.skill_names = [s.get("name") for s in skills if s.get("name")]

                for dd in self.widgets.get("combo_dropdowns", []) + self.widgets.get("buff_dropdowns", []):
                    dd.config(values=self.skill_names)

    def _build_lanes(self):"""

content = content.replace(search_str, methods_str)

with open("ui/panels/skill_panel.py", "w") as f:
    f.write(content)
