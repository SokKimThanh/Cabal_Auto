with open("ui/panels/skill_panel.py", "r") as f:
    content = f.read()

# Fix the trailing whitespaces and remove unused variable
lines = content.split('\n')
for i, line in enumerate(lines):
    lines[i] = line.rstrip()

new_content = '\n'.join(lines)
new_content = new_content.replace('dialog = PresetDialog(self.frame, self.app_state)', 'PresetDialog(self.frame, self.app_state)')

with open("ui/panels/skill_panel.py", "w") as f:
    f.write(new_content)
