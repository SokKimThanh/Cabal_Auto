import re

with open("ui/controllers/app_state_controller.py", "r") as f:
    content = f.read()

search = """        simple_vars = {
            "target_key": ("target_key_var", "TAB"),"""

replace = """        if hasattr(app, "target_policy_var"):
            cfg["target_policy"] = app.target_policy_var.get()

        simple_vars = {
            "target_key": ("target_key_var", "TAB"),"""

content = content.replace(search, replace)

with open("ui/controllers/app_state_controller.py", "w") as f:
    f.write(content)
