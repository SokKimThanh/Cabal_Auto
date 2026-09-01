import re

with open("lib/features/hunt/hunt_orchestrator.py", "r") as f:
    content = f.read()

# Add TargetBarDetector import if not present
if "TargetBarDetector" not in content:
    content = content.replace(
        "from lib.features.hunt.window_selection_service import validate_selected_cabal_window",
        "from lib.features.hunt.window_selection_service import validate_selected_cabal_window\nfrom lib.vision.target_bar_detector import TargetBarDetector"
    )

# Find the start of the worker function and add detector initialization
worker_def_idx = content.find("def worker():")
if worker_def_idx != -1:
    logger_init_idx = content.find("logger = get_hunt_logger()", worker_def_idx)

    # insert detector
    insert_str = """
            target_bar_detector = TargetBarDetector()
            consecutive_false_readings = 0
            """
    content = content[:logger_init_idx] + insert_str + content[logger_init_idx:]

with open("lib/features/hunt/hunt_orchestrator.py", "w") as f:
    f.write(content)
