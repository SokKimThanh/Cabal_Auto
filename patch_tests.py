import re

with open("tests/unit/ui/tabs/test_hunt_target_modes.py", "r") as f:
    content = f.read()

content = content.replace('app._create_tooltip = lambda *args, **kwargs: None', '')
# Maybe replace UIHelper instead if it is needed? Actually tests usually patch at the import location.
# We'll just remove the assignment since the method is no longer there.

with open("tests/unit/ui/tabs/test_hunt_target_modes.py", "w") as f:
    f.write(content)
