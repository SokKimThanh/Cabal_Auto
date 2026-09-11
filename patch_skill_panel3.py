with open("ui/panels/skill_panel.py", "r") as f:
    content = f.read()

# Add _load_classes and _on_class_selected methods
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
                self.widgets["cb_class"].set(self._last_selected_class)
            else:
                self._last_selected_class = selected_val
                # Reload skills for dropdowns
                self._show_all_skills = False
                self._update_toggle_button_visuals()

                skills = self.skill_service.skill_repo.list_skills(class_id=class_id, include_all=self._show_all_skills)
                self.skill_names = [s.get("name") for s in skills if s.get("name")]

                for dd in self.widgets.get("combo_dropdowns", []) + self.widgets.get("buff_dropdowns", []):
                    dd.config(values=self.skill_names)

"""

build_end_search = """        self.widgets["btn_presets"] = tk.Button(
            btn_frame,
            text="[📋 Presets]",
            command=self.on_presets,
            bg=UI.BG_ELEVATED,
            fg=UI.TEXT_MUTED,
            relief="flat",
            bd=0,
        )
        self.widgets["btn_presets"].pack(side="left", padx=2)

        self.widgets["btn_save_preset"] = tk.Button(
            btn_frame,
            text="[💾 Save]",
            command=self._on_save_preset_click,
            bg=UI.BG_ELEVATED,
            fg=UI.TEXT_MUTED,
            relief="flat",
            bd=0,
        )
        self.widgets["btn_save_preset"].pack(side="left", padx=2)

        self.widgets["btn_reset"] = tk.Button(
            btn_frame,
            text="[↺ Reset]",
            command=self.on_reset,
            bg=UI.BG_ELEVATED,
            fg=UI.TEXT_MUTED,
            relief="flat",
            bd=0,
        )
        self.widgets["btn_reset"].pack(side="left", padx=2)

        self._build_lanes()"""


content = content.replace(build_end_search, build_end_search + "\n" + methods_str)


with open("ui/panels/skill_panel.py", "w") as f:
    f.write(content)
