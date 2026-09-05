with open("app_gui.py", "r") as f:
    content = f.read()

content = content.replace('indicator_frame = tk.Frame(apply_frame, bg=UI.THEME_BG_PANEL)',
                          'indicator_frame = tk.Frame(apply_frame, bg=UI.THEME_BG_APP)')
content = content.replace('indicator_frame, text="", fg=UI.THEME_TEXT_SECONDARY, font=UI.FONT_TEXT, bg=UI.THEME_BG_PANEL',
                          'indicator_frame, text="", fg=UI.THEME_TEXT_SECONDARY, font=UI.FONT_TEXT, bg=UI.THEME_BG_APP')

with open("app_gui.py", "w") as f:
    f.write(content)
