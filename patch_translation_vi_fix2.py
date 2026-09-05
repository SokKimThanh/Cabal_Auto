with open("lib/i18n/translations.py", "r") as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if "'target_card.status_idle': 'Đang rảnh'," in line:
        lines[i] = "        'target_card.status_idle': 'IDLE',\n"
    if "'target_card.no_image': '[ KHÔNG CÓ ẢNH ]'," in line:
        lines[i] = "        'target_card.no_image': '[ NO IMAGE ]',\n"
    if "'target_card.target_none': 'Mục tiêu: Không'," in line:
        lines[i] = "        'target_card.target_none': 'Target: None',\n"

for i, line in enumerate(lines):
    if i > 400: # Assuming Vietnamese section starts later
        if "'target_card.status_idle': 'IDLE'," in line:
            lines[i] = "        'target_card.status_idle': 'IDLE',\n"
        if "'target_card.no_image': '[ NO IMAGE ]'," in line:
            lines[i] = "        'target_card.no_image': '[ NO IMAGE ]',\n"
        if "'target_card.target_none': 'Target: None'," in line:
            lines[i] = "        'target_card.target_none': 'Target: None',\n"

with open("lib/i18n/translations.py", "w") as f:
    f.writelines(lines)
