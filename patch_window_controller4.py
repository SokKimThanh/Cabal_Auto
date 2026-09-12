import re

with open('ui/controllers/app_window_controller.py', 'r') as f:
    content = f.read()

content = re.sub(r'hasattr\(self\.root\.state_controller, "_update_window_bounds_display"\):\n\s+self\.root\.state_controller\._update_window_bounds_display\(\)', 'True:\n                self.update_window_bounds_display()', content)
content = re.sub(r'hasattr\(self\.root, "_update_window_bounds_display"\):\n\s+self\.root\.state_controller\._update_window_bounds_display\(\)', 'True:\n            self.update_window_bounds_display()', content)

with open('ui/controllers/app_window_controller.py', 'w') as f:
    f.write(content)
