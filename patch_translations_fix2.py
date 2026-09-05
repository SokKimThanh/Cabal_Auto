with open("lib/i18n/translations.py", "r") as f:
    lines = f.readlines()

out_lines = []
skip = False
for line in lines:
    if "'target_card.status_idle': 'IDLE'," in line or "'target_card.no_image': '[ NO IMAGE ]'," in line or "'target_card.target_none': 'Target: None'," in line:
        continue
    out_lines.append(line)

with open("lib/i18n/translations.py", "w") as f:
    f.writelines(out_lines)
