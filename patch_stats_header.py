with open("ui/tabs/hunt_tab.py", "r") as f:
    content = f.read()

content = content.replace('self.app.skill_stats_frame = tk.LabelFrame(\n            self.skill_strip_frame,\n            text=self.app._t("skill_stats_title"),\n            padx=10,\n            pady=8,\n        )',
                          'self.app.skill_stats_frame = tk.LabelFrame(\n            self.skill_strip_frame,\n            text=self.app._t("skill_stats_title"),\n            padx=10,\n            pady=(12, 8),\n        )')

with open("ui/tabs/hunt_tab.py", "w") as f:
    f.write(content)
