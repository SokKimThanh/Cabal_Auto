with open("ui/views/icon_manager_frame.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

new_lines = []
for i, line in enumerate(lines):
    if "def _on_refresh(self):" in line:
        new_lines.append("    def apply_filters(self):\n")
        new_lines.append("        if hasattr(self, 'tree_component') and hasattr(self.tree_component, 'apply_filters'):\n")
        new_lines.append("            self.tree_component.apply_filters()\n\n")
        new_lines.append(line)
    elif "self.tree_component.apply_filters()" in line and "def _on_refresh" not in line:
        new_lines.append(line.replace("self.tree_component.apply_filters()", "self.apply_filters()"))
    else:
        new_lines.append(line)

with open("ui/views/icon_manager_frame.py", "w", encoding="utf-8") as f:
    f.writelines(new_lines)
