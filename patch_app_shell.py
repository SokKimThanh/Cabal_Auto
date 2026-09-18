import re

with open("ui/components/app_shell.py", "r") as f:
    content = f.read()

# Remove minsize=int(96 * scale_factor) from row 0
content = re.sub(r'self\.main_shell\.rowconfigure\(0,\s*minsize=int\(96\s*\*\s*scale_factor\),\s*weight=0\)',
                 'self.main_shell.rowconfigure(0, weight=0)', content)

# Remove height=int(96 * scale_factor) from shell_zone_a
content = re.sub(r'self\.shell_zone_a = tk\.Frame\(self\.main_shell,\s*bg=UI\.BG_BASE,\s*height=int\(96\s*\*\s*scale_factor\)\)',
                 'self.shell_zone_a = tk.Frame(self.main_shell, bg=UI.BG_BASE)', content)

# Remove grid_propagate(False) from shell_zone_a
content = re.sub(r'\s*self\.shell_zone_a\.grid_propagate\(False\)\n', '\n', content)

with open("ui/components/app_shell.py", "w") as f:
    f.write(content)
