import re

def update_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()

    # Replaces
    content = content.replace('text="Chưa có mục tiêu"', 'text=self.app._t("target_status.no_target")')
    content = content.replace('message="Chưa có mục tiêu"', 'message=self.app._t("target_status.no_target")')
    content = content.replace('submessage="Bắt đầu săn để hiển thị thông tin mục tiêu ở đây."', 'submessage=self.app._t("target_status.no_target_submessage")')
    content = content.replace('text="CẤP"', 'text=self.app._t("target_status.level")')
    content = content.replace('self._make_stat_pill(stats_row, "PHÒNG THỦ", 0)', 'self._make_stat_pill(stats_row, self.app._t("target_status.defense"), 0)')
    content = content.replace('self._make_stat_pill(stats_row, "LOẠI", 1)', 'self._make_stat_pill(stats_row, self.app._t("target_status.type"), 1)')
    content = content.replace('self._make_stat_pill(stats_row, "DROP", 2)', 'self._make_stat_pill(stats_row, self.app._t("target_status.drop"), 2)')

    content = content.replace('badge_text = "● CHỜ"', 'badge_text = self.app._t("target_status.badge_waiting")')
    content = content.replace('badge_text = "● KHÓA MỤC TIÊU"', 'badge_text = self.app._t("target_status.badge_ready")')
    content = content.replace('badge_text = "● ĐANG CHIẾN ĐẤU"', 'badge_text = self.app._t("target_status.badge_hunting")')

    content = content.replace('self.type_val_lbl.config(text="Unknown")', 'self.type_val_lbl.config(text=self.app._t("target_status.unknown"))')

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)

update_file('ui/panels/target_status_panel.py')
