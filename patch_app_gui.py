import re

with open("app_gui.py", "r", encoding="utf-8") as f:
    content = f.read()

# I will replace the redundant hotkey logic in `on_global_apply` with just reading from `cfg` directly since it's now embedded in `_hunt_from_ui()`
old_logic = """
            # 2. Update hunt config from Hunt tab UI (in-place update)
            cfg = self.state_controller._hunt_from_ui()

            # 2.5. Update global hotkeys from Setup tab UI
            if hasattr(self, "global_hotkey_enabled_var"):
                enabled = self.global_hotkey_enabled_var.get()
                hotkeys = cfg.get("global_hotkeys", {})

                def _hotkey_value(attr_name, config_name, default):
                    variable = getattr(self, attr_name, None)
                    return (
                        variable.get()
                        if variable is not None
                        else hotkeys.get(config_name, default)
                    )

                start_key = _hotkey_value(
                    "global_hotkey_start_var", "start_key", "ctrl+shift+r"
                )
                stop_key = _hotkey_value(
                    "global_hotkey_stop_var", "stop_key", "ctrl+shift+e"
                )
                library_key = _hotkey_value(
                    "global_hotkey_library_var", "library_manager_key", "ctrl+shift+l"
                )

                # Validate: all hotkeys must be unique
                vision_key = _hotkey_value(
                    "global_hotkey_vision_var", "vision_wizard_key", "ctrl+shift+v"
                )
                monster_key = _hotkey_value(
                    "global_hotkey_monster_var", "monster_editor_key", "ctrl+shift+m"
                )
                all_keys = [
                    start_key,
                    stop_key,
                    library_key,
                    vision_key,
                    monster_key,
                ]
                if len(all_keys) != len(set(all_keys)):
                    messagebox.showerror(
                        self._t("error_title"),
                        (
                            "All hotkeys must be different!"
                            if self.lang == "en"
                            else "Tất cả phím tắt phải khác nhau!"
                        ),
                    )
                    return

                # Update config
                cfg["global_hotkeys"] = {
                    "enabled": enabled,
                    "start_key": start_key,
                    "stop_key": stop_key,
                    "library_manager_key": library_key,
                    "vision_wizard_key": vision_key,
                    "monster_editor_key": monster_key,
                }

                # Re-register hotkeys with new settings
                self.hunt_cfg = cfg  # Update instance config first
                self.hotkey_controller.unregister_all()
                self.hotkey_controller.register_all()

            # 3. Save to file ONCE (preserves insertion order in Python 3.7+)
"""

new_logic = """
            # 2. Update hunt config from Hunt tab UI (in-place update)
            cfg = self.state_controller._hunt_from_ui()

            # Validate hotkey uniqueness before applying
            if "global_hotkeys" in cfg:
                hk = cfg["global_hotkeys"]
                all_keys = [
                    hk.get("start_key"),
                    hk.get("stop_key"),
                    hk.get("library_manager_key"),
                    hk.get("vision_wizard_key"),
                    hk.get("monster_editor_key"),
                ]
                # Filter out empty or None hotkeys
                all_keys = [k for k in all_keys if k]
                if len(all_keys) != len(set(all_keys)):
                    messagebox.showerror(
                        self._t("error_title"),
                        (
                            "All hotkeys must be different!"
                            if self.lang == "en"
                            else "Tất cả phím tắt phải khác nhau!"
                        ),
                    )
                    return

                self.hunt_cfg = cfg  # Update instance config first
                self.hotkey_controller.unregister_all()
                self.hotkey_controller.register_all()

            # 3. Save to file ONCE (preserves insertion order in Python 3.7+)
"""

content = content.replace(old_logic, new_logic)

with open("app_gui.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Patched app_gui.py")
