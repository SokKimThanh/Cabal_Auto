with open("ui/tabs/hunt_tab.py", "r") as f:
    content = f.read()

content = content.replace('self.grid_rowconfigure(0, weight=1)\n        self.grid_rowconfigure(1, weight=0)',
                          'self.grid_rowconfigure(0, weight=0)\n        self.grid_rowconfigure(1, weight=1)')

with open("ui/tabs/hunt_tab.py", "w") as f:
    f.write(content)
