with open("ui/tabs/hunt_tab.py", "r") as f:
    content = f.read()

# Change fg=UI.THEME_TEXT_SECONDARY to fg=UI.THEME_TEXT_PRIMARY for the delete hint
content = content.replace('text=self.app._t("monster_rotation_delete_hint"),\n            fg=UI.THEME_TEXT_SECONDARY,',
                          'text=self.app._t("monster_rotation_delete_hint"),\n            fg=UI.THEME_TEXT_PRIMARY,')

# Change fg=UI.THEME_TEXT_SECONDARY to fg=UI.THEME_TEXT_PRIMARY for create_stat_row
content = content.replace('text=self.app._t(label_key) + ":",\n                bg=UI.THEME_BG_PANEL,\n                fg=UI.THEME_TEXT_SECONDARY,',
                          'text=self.app._t(label_key) + ":",\n                bg=UI.THEME_BG_PANEL,\n                fg=UI.THEME_TEXT_PRIMARY,')

with open("ui/tabs/hunt_tab.py", "w") as f:
    f.write(content)
