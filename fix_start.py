with open("app_gui.py", "r") as f:
    text = f.read()

import_str = "from lib.features.hunt.hunt_config import CONFIG_PATH, HUNT_CONFIG_PATH\n"
idx = text.find("from lib.features.hunt.hunt_config import ")
text = text[:idx] + import_str + text[idx:]

with open("app_gui.py", "w") as f:
    f.write(text)
