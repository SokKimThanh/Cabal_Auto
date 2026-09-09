import re

with open("ui/controllers/app_state_controller.py", "r", encoding="utf-8") as f:
    content = f.read()

# Replace the simple_vars dictionary
old_simple_vars = """        simple_vars = {
            "target_key": ("target_key_var", "TAB"),
            "target_cycle_delay": ("target_cycle_var", 0.2),
            "search_interval": ("search_interval_var", 0.25),
            "attack_interval": ("attack_interval_var", 0.15),
            "lost_timeout_sec": ("lost_timeout_var", 1.2),
            "attack_min_duration_sec": ("attack_duration_var", 1.5),
            "attack_press_ms": ("attack_press_var", 60),
        }"""

new_simple_vars = """        simple_vars = {
            "target_key": ("setup_target_key_var", "TAB"),
            "target_cycle_delay": ("setup_target_cycle_var", 0.2),
            "search_interval": ("setup_search_interval_var", 0.25),
            "attack_interval": ("setup_attack_interval_var", 0.15),
            "lost_timeout_sec": ("setup_lost_timeout_var", 1.2),
            "attack_min_duration_sec": ("setup_attack_duration_var", 1.5),
            "attack_press_ms": ("setup_press_ms_var", 60),
        }

        if hasattr(app, "setup_mode_var"):
            cfg["ui_mode"] = app.setup_mode_var.get()

        if hasattr(app, "setup_template_var"):
            cfg["template_path"] = app.setup_template_var.get()
"""

content = content.replace(old_simple_vars, new_simple_vars)

with open("ui/controllers/app_state_controller.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Patched app_state_controller.py")
