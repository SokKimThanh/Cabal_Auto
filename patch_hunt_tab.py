import re

with open("ui/tabs/hunt_tab.py", "r") as f:
    content = f.read()

# Fix the empty lines caused by naive string replacement
lines = content.split('\n')
new_lines = []
for i, line in enumerate(lines):
    if line.strip() == 'UIHelper.create_tooltip(':
        # Let's fix the indent
        spaces = len(line) - len(line.lstrip())
        new_lines.append(" " * (spaces - 4) + 'UIHelper.create_tooltip(')
    elif line.strip() == 'UIHelper.destroy_widget_tooltip(self.hunt_status_label)':
        spaces = len(line) - len(line.lstrip())
        new_lines.append(" " * (spaces - 4) + 'UIHelper.destroy_widget_tooltip(self.hunt_status_label)')
    else:
        new_lines.append(line)

content = '\n'.join(new_lines)
with open("ui/tabs/hunt_tab.py", "w") as f:
    f.write(content)
