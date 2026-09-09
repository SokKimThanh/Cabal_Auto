import re

def update_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()

    # Replaces
    content = content.replace('text="✅ Đã cập nhật scan"', 'text=t("screen_state.scan_updated", default="✅ Đã cập nhật scan")')
    content = content.replace('"⏳ Đang theo dõi..."', 't("screen_state.tracking", default="⏳ Đang theo dõi...")')
    content = content.replace('"📍 Unknown"', 't("screen_state.location_unknown", default="📍 Unknown")')

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)

update_file('ui/panels/screen_state_panel.py')
