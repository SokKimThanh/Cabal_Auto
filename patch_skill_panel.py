import re

def update_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()

    # Replaces
    content = content.replace('text="COMBO MODE: INACTIVE"', 'text=self.app._t("skill_panel.combo_inactive")')
    content = content.replace('text="▶️ START COMBO MODE"', 'text=self.app._t("skill_panel.combo_start")')
    content = content.replace('text="⏹️ STOP COMBO MODE"', 'text=self.app._t("skill_panel.combo_stop")')

    # We need to handle `text=f"BUFF LANE {i+1}"` carefully
    content = content.replace('text=f"BUFF LANE {i+1}"', 'text=self.app._t("skill_panel.buff_lane").format(num=i+1)')

    content = content.replace('text="COMBO MODE: ACTIVE"', 'text=self.app._t("skill_panel.combo_active")')
    content = content.replace('text="⭐ Default"', 'text=self.app._t("skill_panel.preset_default")')
    content = content.replace('text="✏️ Custom"', 'text=self.app._t("skill_panel.preset_custom")')

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)

update_file('ui/panels/skill_panel.py')
