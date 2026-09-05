import re

with open("lib/features/monsters/monster_repo.py", "r") as f:
    content = f.read()

content = re.sub(r'    }\n\nDEFAULT_MONSTER_SCHEMA = {', '    }\n\n\nDEFAULT_MONSTER_SCHEMA = {', content)

with open("lib/features/monsters/monster_repo.py", "w") as f:
    f.write(content)
