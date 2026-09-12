import re

with open('ui/controllers/app_state_controller.py', 'r') as f:
    content = f.read()

# Add get_ui_var and set_ui_var methods
methods = """
    def get_ui_var(self, name: str) -> Any:
        if name in self.ui_vars:
            return self.ui_vars[name].get()
        return None

    def set_ui_var(self, name: str, value: Any) -> None:
        if name in self.ui_vars:
            self.ui_vars[name].set(value)
"""

if "def get_ui_var(" not in content:
    # insert methods at the end of the file
    content += methods

    with open('ui/controllers/app_state_controller.py', 'w') as f:
        f.write(content)
