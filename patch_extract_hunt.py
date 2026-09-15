import re

with open("app_gui.py", "r") as f:
    content = f.read()

# Replace these methods logic to call controllers

def replace_body(method_name, new_body, content):
    pattern = rf"def {method_name}\(self.*?\):\n(?:    +.*\n)*"
    # Find match to know if it exists
    match = re.search(pattern, content)
    if match:
        content = content[:match.start()] + new_body + content[match.end():]
    return content

start_stop_body = """def on_start_stop_clicked(self):
        if hasattr(self, 'hunt_controller') and self.hunt_controller:
            self.hunt_controller.on_start_stop_clicked()
\n"""
content = replace_body("on_start_stop_clicked", start_stop_body, content)

refresh_start_stop_body = """def _refresh_start_stop_visual(self):
        if hasattr(self, 'hunt_controller') and self.hunt_controller:
            self.hunt_controller.refresh_start_stop_visual()
\n"""
content = replace_body("_refresh_start_stop_visual", refresh_start_stop_body, content)

reenable_body = """def _reenable_start_stop_btn(self):
        if hasattr(self, 'hunt_controller') and self.hunt_controller:
            self.hunt_controller.reenable_start_stop_btn()
\n"""
content = replace_body("_reenable_start_stop_btn", reenable_body, content)

# Write back
with open("app_gui.py", "w") as f:
    f.write(content)
