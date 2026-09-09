import re

with open("ui/controllers/app_state_controller.py", "r", encoding="utf-8") as f:
    content = f.read()

# Make sure we replace the mode reading with a hardcoded advanced mode
old_mode = """        if hasattr(app, "setup_mode_var"):
            cfg["ui_mode"] = app.setup_mode_var.get()"""

new_mode = """        # Force advanced mode since mode selection is removed
        cfg["ui_mode"] = "advanced\""""

content = content.replace(old_mode, new_mode)

with open("ui/controllers/app_state_controller.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Patched app_state_controller.py part 2")
