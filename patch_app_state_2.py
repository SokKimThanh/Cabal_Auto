import re

with open("ui/controllers/app_state_controller.py", "r", encoding="utf-8") as f:
    content = f.read()

hotkey_snippet = """
        # Extract hotkey settings if they are available on the app object
        if hasattr(app, "global_hotkey_enabled_var"):
            enabled = app.global_hotkey_enabled_var.get()
            hotkeys = cfg.get("global_hotkeys", {})

            def _hotkey_value(attr_name, config_name, default):
                variable = getattr(app, attr_name, None)
                return (
                    variable.get()
                    if variable is not None
                    else hotkeys.get(config_name, default)
                )

            cfg["global_hotkeys"] = {
                "enabled": enabled,
                "start_key": _hotkey_value("global_hotkey_start_var", "start_key", "ctrl+shift+r"),
                "stop_key": _hotkey_value("global_hotkey_stop_var", "stop_key", "ctrl+shift+e"),
                "library_manager_key": _hotkey_value("global_hotkey_library_var", "library_manager_key", "ctrl+shift+l"),
                "vision_wizard_key": _hotkey_value("global_hotkey_vision_var", "vision_wizard_key", "ctrl+shift+v"),
                "monster_editor_key": _hotkey_value("global_hotkey_monster_var", "monster_editor_key", "ctrl+shift+m"),
            }
"""

# Insert the snippet right before returning cfg
return_cfg_str = "return cfg"
content = content.replace(return_cfg_str, hotkey_snippet + "\n        " + return_cfg_str)

with open("ui/controllers/app_state_controller.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Patched app_state_controller.py part 2")
