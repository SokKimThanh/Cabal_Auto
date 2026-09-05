with open("app_gui.py", "r") as f:
    content = f.read()

content = content.replace('self.action_bar_frame.columnconfigure(\n            0, minsize=380, weight=1\n        )  # Window Selection',
                          'self.action_bar_frame.columnconfigure(\n            0, minsize=380, weight=2\n        )  # Window Selection')

with open("app_gui.py", "w") as f:
    f.write(content)
