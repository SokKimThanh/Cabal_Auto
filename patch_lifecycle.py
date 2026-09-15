import re
with open("ui/controllers/app_lifecycle_controller.py", "r") as f:
    content = f.read()

# Replace self.app.root.after(100, lambda: self.app.attributes("-topmost", False))
# with self.app.root.attributes("-topmost", False) where applicable
content = content.replace("self.app.attributes", "self.app.root.attributes")
content = content.replace("self.app.deiconify", "self.app.root.deiconify")
content = content.replace("self.app.state()", "self.app.root.state()")
content = content.replace("self.app.lift", "self.app.root.lift")
content = content.replace("self.app.focus_force", "self.app.root.focus_force")
content = content.replace("self.app.update_idletasks", "self.app.root.update_idletasks")
content = content.replace("self.app.destroy", "self.app.root.destroy")

with open("ui/controllers/app_lifecycle_controller.py", "w") as f:
    f.write(content)
