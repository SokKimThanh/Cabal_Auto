import re

for filepath in ["tests/unit/test_target_hp_recovery.py", "tests/unit/test_skill_strip_logic.py", "tests/unit/ui/tabs/test_hunt_tab_layout.py"]:
    with open(filepath, "r") as f:
        content = f.read()

    # The tests mock `_create_tooltip` inside MockApp. We can safely remove it.
    content = re.sub(r'def _create_tooltip\([^\)]+\):[\s\S]*?pass\n', '', content)
    content = re.sub(r'def _create_tooltip\([^\)]+\):[\s\S]*?return\n', '', content)

    with open(filepath, "w") as f:
        f.write(content)
