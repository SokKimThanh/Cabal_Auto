import re

with open("lib/features/hunt/hunt_orchestrator.py", "r") as f:
    content = f.read()

# Fix the messy import generated earlier
content = content.replace(
    """                    from lib.features.hunt.window_selection_service import validate_selected_cabal_window\nfrom lib.vision.target_bar_detector import TargetBarDetector\n\n                    hunt_selected = self.get_hunt_selected()""",
    """                    from lib.features.hunt.window_selection_service import validate_selected_cabal_window\n\n                    hunt_selected = self.get_hunt_selected()"""
)

# And make sure target_bar_detector is imported at the top of the file
import_stmt = "from lib.vision.target_bar_detector import TargetBarDetector"
if import_stmt not in content:
    content = import_stmt + "\n" + content

with open("lib/features/hunt/hunt_orchestrator.py", "w") as f:
    f.write(content)
