import re
with open('ui/controllers/app_window_controller.py', 'r') as f:
    content = f.read()

# Replace the other occurrences
content = content.replace("if True:\n            self.update_window_bounds_display()", "self.update_window_bounds_display()")
content = content.replace("if True:\n                self.update_window_bounds_display()", "self.update_window_bounds_display()")

with open('ui/controllers/app_window_controller.py', 'w') as f:
    f.write(content)
