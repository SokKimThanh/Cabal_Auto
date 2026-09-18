with open('ui/views/icon_manager_frame.py', 'r') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if line.startswith('        def _build_categories_panel(self, parent_frame):'):
        new_lines.append('    def _build_categories_panel(self, parent_frame):\n')
    else:
        new_lines.append(line)

with open('ui/views/icon_manager_frame.py', 'w') as f:
    f.writelines(new_lines)
