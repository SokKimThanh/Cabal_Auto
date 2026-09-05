with open("ui/tabs/hunt_tab.py", "r") as f:
    lines = f.readlines()

out_lines = []
skip = False
for i, line in enumerate(lines):
    if "hover_color=(" in line and "BTN_NEUTRAL_HOVER" in lines[i-1]:
        skip = True
        continue
    if skip and ")," in line and "UI.COLOR_PRIMARY" in lines[i-1]:
        skip = False
        continue
    if skip:
        continue
    out_lines.append(line)

with open("ui/tabs/hunt_tab.py", "w") as f:
    f.writelines(out_lines)
