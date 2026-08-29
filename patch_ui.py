import re

with open("dialogs/monster_edit.py", "r") as f:
    content = f.read()

# I will use replace_with_git_merge_diff for this, it's easier. Let's first dump the _setup_ui string.
