import re

for filename in ["ui/tabs/setup_tab.py", "ui/tabs/stats_tab.py", "ui/tabs/help_tab.py", "ui/tabs/hunt_tab.py"]:
    with open(filename, "r") as f:
        text = f.read()

    text = text.replace("import tkinter as tk\n", "")
    text = text.replace("from ui.components import create_icon_button as _create_icon_btn_component\n", "")
    text = text.replace("from lib.ui_style import UIStyle as UI\n", "")
    text = text.replace("class", "\nclass")

    with open(filename, "w") as f:
        f.write(text)
