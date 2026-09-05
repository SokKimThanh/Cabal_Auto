with open("app_gui.py", "r") as f:
    content = f.read()

# Modify column 6 configuration in _build_ui
content = content.replace('self.action_bar_frame.columnconfigure(5, minsize=80, weight=0)  # Language',
                          'self.action_bar_frame.columnconfigure(5, minsize=80, weight=0)  # Language\n        self.action_bar_frame.columnconfigure(6, minsize=160, weight=0)  # Global Apply')

# Update _build_global_apply_section
old_apply_code = """    def _build_global_apply_section(self):
        \"\"\"Build global apply button section below tabs.\"\"\"
        # Frame for global apply section (right-aligned)
        self.global_apply_frame = tk.Frame(self, relief="sunken", bd=1, bg=UI.THEME_BG_PANEL)
        apply_frame = self.global_apply_frame
        apply_frame.pack(side="bottom", fill="x", padx=8, pady=(0, 8))"""

new_apply_code = """    def _build_global_apply_section(self):
        \"\"\"Build global apply button section below tabs.\"\"\"
        # Frame for global apply section (right-aligned)
        self.global_apply_frame = tk.Frame(self.action_bar_frame, bg=UI.THEME_BG_APP)
        apply_frame = self.global_apply_frame
        apply_frame.grid(row=0, column=6, sticky="e", padx=(0, 12))"""

content = content.replace(old_apply_code, new_apply_code)

with open("app_gui.py", "w") as f:
    f.write(content)
