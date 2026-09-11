import re

with open("ui/panels/skill_panel.py", "r") as f:
    content = f.read()

# Add DbClassService import
import_str = "from lib.features.skills.skill_runtime_service import SkillRuntimeService\nfrom lib.db.services.class_service import ClassService"
content = content.replace("from lib.features.skills.skill_runtime_service import SkillRuntimeService", import_str)

# In _build, add the combobox before auto_combo_var
build_search = """        header_frame = tk.Frame(self.frame, bg=UI.BG_ELEVATED)
        header_frame.pack(fill="x", pady=0)

        # Combo header with custom checkbox"""

build_replace = """        header_frame = tk.Frame(self.frame, bg=UI.BG_ELEVATED)
        header_frame.pack(fill="x", pady=0)

        # Class selector
        class_frame = tk.Frame(header_frame, bg=UI.BG_ELEVATED)
        class_frame.pack(side="left", padx=(10, 0))

        lbl_class = tk.Label(class_frame, bg=UI.BG_ELEVATED, fg=UI.TEXT_PRIMARY)
        if hasattr(self.app_state, "bind_text"):
            self.app_state.bind_text(lbl_class, "lbl_class_select")
        else:
            lbl_class.config(text=self.app_state._t("lbl_class_select"))
        lbl_class.pack(side="left")

        self.widgets["cb_class"] = ttk.Combobox(
            class_frame,
            state="readonly",
            width=15,
            font=UI.FONT_BODY
        )
        self.widgets["cb_class"].pack(side="left", padx=5)
        self.widgets["cb_class"].bind("<<ComboboxSelected>>", self._on_class_selected)

        # Combo header with custom checkbox"""

content = content.replace(build_search, build_replace)


with open("ui/panels/skill_panel.py", "w") as f:
    f.write(content)

