import re

with open("app_gui.py", "r") as f:
    content = f.read()

# Replace any lingering self.tk or self.after with self.root.tk and self.root.after in specific files if needed
content = content.replace("self.tk", "self.root.tk")
content = content.replace("self.after", "self.root.after")

with open("app_gui.py", "w") as f:
    f.write(content)

with open("lib/system/task_scheduler.py", "r") as f:
    task_content = f.read()

task_content = task_content.replace("self.root.after", "self.root.root.after if hasattr(self.root, 'root') else self.root.after")
with open("lib/system/task_scheduler.py", "w") as f:
    f.write(task_content)
