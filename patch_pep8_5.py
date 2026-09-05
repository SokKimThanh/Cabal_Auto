import re

def fix_file(filepath):
    with open(filepath, "r") as f:
        content = f.read()
    lines = content.split('\n')
    lines = [re.sub(r'^\s+$', '', line) if line.strip() == '' else line for line in lines]
    with open(filepath, "w") as f:
        f.write('\n'.join(lines))

fix_file("lib/features/monsters/monster_repo.py")
fix_file("lib/i18n/translations.py")
fix_file("ui/tabs/hunt_tab.py")

with open("lib/features/monsters/monster_repo.py", "r") as f:
    content = f.read()
content = content.replace("\nDEFAULT_MONSTER_SCHEMA", "\n\nDEFAULT_MONSTER_SCHEMA")
with open("lib/features/monsters/monster_repo.py", "w") as f:
    f.write(content)
