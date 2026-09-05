with open("lib/i18n/translations.py", "r") as f:
    content = f.read()

# Revert the double replace issue, then properly insert
import re
content = re.sub(r"'target_card.status_idle': 'IDLE',\n        'target_card.no_image': '\[ NO IMAGE \]',\n        'target_card.target_none': 'Target: None',\n        ", "", content)

with open("lib/i18n/translations.py", "w") as f:
    f.write(content)
