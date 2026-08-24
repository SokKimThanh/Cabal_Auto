with open("app_gui.py", "r") as f:
    text = f.read()

text = text.replace("    main()from lib.features.hunt.hunt_config import CONFIG_PATH, HUNT_CONFIG_PATH", "    main()\n")

with open("app_gui.py", "w") as f:
    f.write(text)
