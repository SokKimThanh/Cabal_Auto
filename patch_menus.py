import re

with open('app_gui.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_menu_1 = """            # Toggle Overlay (Ctrl+Shift+O) - using translations
            vision_menu.add_command(
                label=self._t("vision_toggle_overlay"),
                accelerator="Ctrl+Shift+O",
                command=self.overlay_controller.toggle_overlay,
            )"""

new_menu_1 = """            # Toggle Overlay (Ctrl+Shift+O) - using translations
            vision_menu.add_command(
                label=self._t("vision_toggle_overlay"),
                accelerator="Ctrl+Shift+O",
                command=lambda: getattr(self, "overlay_controller").toggle_overlay() if hasattr(self, "overlay_controller") and getattr(self, "overlay_controller") else None,
            )"""

old_menu_2 = """            # Overlay Settings - using translations
            overlay_settings_label = (
                "Overlay Settings..." if self.lang == "en" else "Cài Đặt Overlay..."
            )
            vision_menu.add_command(
                label=overlay_settings_label,
                command=self.overlay_controller.open_settings,
            )"""

new_menu_2 = """            # Overlay Settings - using translations
            overlay_settings_label = (
                "Overlay Settings..." if self.lang == "en" else "Cài Đặt Overlay..."
            )
            vision_menu.add_command(
                label=overlay_settings_label,
                command=lambda: getattr(self, "overlay_controller").open_settings() if hasattr(self, "overlay_controller") and getattr(self, "overlay_controller") else None,
            )"""

content = content.replace(old_menu_1, new_menu_1)
content = content.replace(old_menu_2, new_menu_2)

with open('app_gui.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Patch applied to menus.")
