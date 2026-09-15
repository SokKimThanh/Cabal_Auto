import re

with open("app_gui.py", "r") as f:
    content = f.read()

# Replace any lingering self.bind or self.protocol with self.root.bind / self.root.protocol
content = content.replace("self.bind", "self.root.bind")
content = content.replace("self.protocol", "self.root.protocol")
content = content.replace("self.title", "self.root.title")
content = content.replace("self.geometry", "self.root.geometry")
content = content.replace("self.winfo_width", "self.root.winfo_width")
content = content.replace("self.winfo_height", "self.root.winfo_height")
content = content.replace("self.config", "self.root.config")
content = content.replace("self.tk", "self.root.tk")

with open("app_gui.py", "w") as f:
    f.write(content)
