with open("ui/panels/skill_panel.py", "r") as f:
    content = f.read()

# Add logic for populating the combobox
# Inside _build, after cb_class is created
cb_class_search = """        self.widgets["cb_class"].bind("<<ComboboxSelected>>", self._on_class_selected)

        # Combo header with custom checkbox"""

cb_class_replace = """        self.widgets["cb_class"].bind("<<ComboboxSelected>>", self._on_class_selected)

        self._load_classes()

        # Combo header with custom checkbox"""

content = content.replace(cb_class_search, cb_class_replace)

with open("ui/panels/skill_panel.py", "w") as f:
    f.write(content)
