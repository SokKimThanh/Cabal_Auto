with open("lib/i18n/translations.py", "r") as f:
    lines = f.readlines()

out_lines = []
for line in lines:
    out_lines.append(line)
    if "'target_card.unknown_mob': 'Unknown Target'," in line:
        out_lines.append("        'target_card.status_idle': 'IDLE',\n")
        out_lines.append("        'target_card.no_image': '[ NO IMAGE ]',\n")
        out_lines.append("        'target_card.target_none': 'Target: None',\n")
    if "'target_card.unknown_mob': 'Mục Tiêu Không Xác Định'," in line:
        out_lines.append("        'target_card.status_idle': 'IDLE',\n")
        out_lines.append("        'target_card.no_image': '[ NO IMAGE ]',\n")
        out_lines.append("        'target_card.target_none': 'Target: None',\n")

with open("lib/i18n/translations.py", "w") as f:
    f.writelines(out_lines)
