with open("ui/tabs/hunt_tab.py", "r") as f:
    content = f.read()

content = content.replace('bg_color=UI.COLOR_DANGER,\n            hover_color=UI.COLOR_WARNING,',
                          'bg_color=UI.BTN_DANGER_BG if hasattr(UI, "BTN_DANGER_BG") else UI.COLOR_DANGER,\n            hover_color=UI.BTN_DANGER_HOVER if hasattr(UI, "BTN_DANGER_HOVER") else UI.COLOR_WARNING,')

with open("ui/tabs/hunt_tab.py", "w") as f:
    f.write(content)
