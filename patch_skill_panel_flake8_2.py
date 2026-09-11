with open("ui/panels/skill_panel.py", "r") as f:
    content = f.read()

content = content.replace('\n\n\n    def _load_classes(self):', '\n\n    def _load_classes(self):')

with open("ui/panels/skill_panel.py", "w") as f:
    f.write(content)
