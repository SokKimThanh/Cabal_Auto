import sys
import os

# Ensure project root is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

if __name__ == "__main__":
    import app_gui

    app = app_gui.App()
    print(app.monster_selected_name)
