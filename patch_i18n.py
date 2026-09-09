import re

def update_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()

    en_addition = """
        'target_status.no_target': 'No target',
        'target_status.no_target_submessage': 'Start hunting to show target information here.',
        'target_status.level': 'LEVEL',
        'target_status.defense': 'DEFENSE',
        'target_status.type': 'TYPE',
        'target_status.drop': 'DROP',
        'target_status.unknown': 'Unknown',
        'target_status.badge_waiting': '● WAITING',
        'target_status.badge_ready': '● TARGET LOCKED',
        'target_status.badge_hunting': '● IN COMBAT',
        'skill_panel.combo_inactive': 'COMBO MODE: INACTIVE',
        'skill_panel.combo_start': '▶️ START COMBO MODE',
        'skill_panel.combo_stop': '⏹️ STOP COMBO MODE',
        'skill_panel.combo_active': 'COMBO MODE: ACTIVE',
        'skill_panel.buff_lane': 'BUFF LANE {num}',
        'skill_panel.preset_default': '⭐ Default',
        'skill_panel.preset_custom': '✏️ Custom',
        'monster_target.empty_list': 'Target list is empty',
        'monster_target.empty_list_submessage': 'Add monsters to the list to start hunting.',
        'screen_state.scan_updated': '✅ Scan updated',
        'screen_state.tracking': '⏳ Tracking...',
        'screen_state.location_unknown': '📍 Unknown',
"""

    vi_addition = """
        'target_status.no_target': 'Chưa có mục tiêu',
        'target_status.no_target_submessage': 'Bắt đầu săn để hiển thị thông tin mục tiêu ở đây.',
        'target_status.level': 'CẤP',
        'target_status.defense': 'PHÒNG THỦ',
        'target_status.type': 'LOẠI',
        'target_status.drop': 'DROP',
        'target_status.unknown': 'Chưa rõ',
        'target_status.badge_waiting': '● CHỜ',
        'target_status.badge_ready': '● KHÓA MỤC TIÊU',
        'target_status.badge_hunting': '● ĐANG CHIẾN ĐẤU',
        'skill_panel.combo_inactive': 'COMBO MODE: INACTIVE',
        'skill_panel.combo_start': '▶️ BẮT ĐẦU COMBO',
        'skill_panel.combo_stop': '⏹️ DỪNG COMBO',
        'skill_panel.combo_active': 'COMBO MODE: ACTIVE',
        'skill_panel.buff_lane': 'BUFF LANE {num}',
        'skill_panel.preset_default': '⭐ Mặc định',
        'skill_panel.preset_custom': '✏️ Tùy chỉnh',
        'monster_target.empty_list': 'Danh sách mục tiêu trống',
        'monster_target.empty_list_submessage': 'Thêm quái vật vào danh sách để bắt đầu săn.',
        'screen_state.scan_updated': '✅ Đã cập nhật scan',
        'screen_state.tracking': '⏳ Đang theo dõi...',
        'screen_state.location_unknown': '📍 Chưa rõ',
"""

    parts = content.split("'vi': {")
    en_part = parts[0]
    vi_part = parts[1]

    # insert at the end of 'en' part
    # Find the last '},' or similar? actually it is before "'vi': {"
    en_part = en_part.rstrip()
    if en_part.endswith(','):
        en_part += en_addition
    else:
        en_part += "," + en_addition

    # insert at the beginning of 'vi' part
    vi_part = vi_addition + vi_part

    new_content = en_part + "\n    'vi': {" + vi_part

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(new_content)

update_file('lib/i18n/translations.py')
