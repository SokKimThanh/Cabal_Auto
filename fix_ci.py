with open("app_gui.py", "r") as f:
    text = f.read()

# Fix show_setup_wizard missing
text = text.replace("from ui.windows.hotkey_diag_dialog import show_hotkey_diagnostics_modal\n", "from ui.windows.hotkey_diag_dialog import show_hotkey_diagnostics_modal\nfrom ui.windows.setup_wizard import show_setup_wizard\n")

# Fix CONFIG_PATH and HUNT_CONFIG_PATH missing
# We can import them from lib.features.hunt.hunt_config
import_str = "from lib.features.hunt.hunt_config import CONFIG_PATH, HUNT_CONFIG_PATH\n"
idx = text.find("from lib.features.hunt.hunt_config import load_config")
text = text[:idx] + import_str + text[idx:]

with open("app_gui.py", "w") as f:
    f.write(text)
