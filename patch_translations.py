with open("lib/i18n/translations.py", "r") as f:
    lines = f.readlines()

new_en = []
new_vi = []

for i, line in enumerate(lines):
    if "'target_card.unknown_mob': 'Unknown Target'," in line:
        pass
    new_en.append(line)

# Let's use string replacement to add the keys reliably

with open("lib/i18n/translations.py", "r") as f:
    content = f.read()

# For English
content = content.replace("'target_card.unknown_mob': 'Unknown Target',",
                          "'target_card.unknown_mob': 'Unknown Target',\n        'target_card.status_idle': 'IDLE',\n        'target_card.no_image': '[ NO IMAGE ]',\n        'target_card.target_none': 'Target: None',")

# For Vietnamese
content = content.replace("'target_card.unknown_mob': 'Unknown Target',",
                          "'target_card.unknown_mob': 'Unknown Target',\n        'target_card.status_idle': 'IDLE',\n        'target_card.no_image': '[ NO IMAGE ]',\n        'target_card.target_none': 'Target: None',")

with open("lib/i18n/translations.py", "w") as f:
    f.write(content)
