with open("ui/views/icon_manager_frame.py", "r") as f:
    lines = f.readlines()

new_lines = []
for i, line in enumerate(lines):
    if line.strip() == "def _check_scrollbar(self, event=None):" and i > 0 and lines[i-1].strip() != "":
        new_lines.append("\n")
    new_lines.append(line)

with open("ui/views/icon_manager_frame.py", "w") as f:
    f.writelines(new_lines)
