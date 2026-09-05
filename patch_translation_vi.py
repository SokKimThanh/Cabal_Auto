with open("lib/i18n/translations.py", "r") as f:
    content = f.read()

content = content.replace("'target_card.status_idle': 'IDLE',", "'target_card.status_idle': 'Đang rảnh',", 1)
content = content.replace("'target_card.no_image': '[ NO IMAGE ]',", "'target_card.no_image': '[ KHÔNG CÓ ẢNH ]',", 1)
content = content.replace("'target_card.target_none': 'Target: None',", "'target_card.target_none': 'Mục tiêu: Không',", 1)

with open("lib/i18n/translations.py", "w") as f:
    f.write(content)
