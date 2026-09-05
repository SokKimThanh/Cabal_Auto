with open("ui/tabs/hunt_tab.py", "r") as f:
    content = f.read()

content = content.replace('bg_color=(\n                UI.BTN_ACCENT_BG if hasattr(UI, "BTN_ACCENT_BG") else UI.COLOR_PRIMARY\n            ),',
                          'bg_color=getattr(UI, "BTN_NEUTRAL_BG", "#757575"),\n            hover_color=getattr(UI, "BTN_NEUTRAL_HOVER", "#616161"),')

content = content.replace('bg_color=UI.BTN_INFO_BG if hasattr(UI, "BTN_INFO_BG") else UI.COLOR_INFO,\n            hover_color=(\n                UI.BTN_INFO_HOVER if hasattr(UI, "BTN_INFO_HOVER") else UI.COLOR_PRIMARY\n            ),',
                          'bg_color=getattr(UI, "BTN_NEUTRAL_BG", "#757575"),\n            hover_color=getattr(UI, "BTN_NEUTRAL_HOVER", "#616161"),')

with open("ui/tabs/hunt_tab.py", "w") as f:
    f.write(content)
