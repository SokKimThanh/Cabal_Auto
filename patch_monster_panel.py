import re

def update_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()

    # Replaces
    content = content.replace('message="Danh sách mục tiêu trống"', 'message=self.app._t("monster_target.empty_list")')
    content = content.replace('submessage="Thêm quái vật vào danh sách để bắt đầu săn."', 'submessage=self.app._t("monster_target.empty_list_submessage")')

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)

update_file('ui/panels/monster_target_panel.py')
