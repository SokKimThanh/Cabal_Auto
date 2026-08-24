for filename in ["ui/tabs/setup_tab.py", "ui/tabs/stats_tab.py", "ui/tabs/help_tab.py"]:
    with open(filename, "r") as f:
        text = f.read()

    import re
    text = re.sub(r"^[ \t]+$", "", text, flags=re.MULTILINE)
    text = text.replace("import tkinter as tk\nfrom tkinter import ttk\n", "from tkinter import ttk\nimport tkinter as tk\n")

    with open(filename, "w") as f:
        f.write(text)
