import re

with open('app_gui.py', 'r') as f:
    content = f.read()

app_gui_search = """            # Optionally update state with scanner results if needed
            if "class" in results and results["class"] != "Unknown":
                state["character_class"] = results["class"]

            self.screen_state_panel.update_from_scan(state)"""

app_gui_replace = """            # Optionally update state with scanner results if needed
            if "class" in results and results["class"] != "Unknown":
                state["character_class"] = results["class"]

            self.screen_state_panel.update_from_scan(state)

            if "thumbnail" in results:
                self.screen_state_panel.update_thumbnail(results["thumbnail"])"""

content = content.replace(app_gui_search, app_gui_replace)

with open('app_gui.py', 'w') as f:
    f.write(content)
