with open("ui/tabs/hunt_tab.py", "r") as f:
    content = f.read()

content = content.replace('text="Unknown Target"', 'text=self.app._t("target_card.unknown_mob")')
content = content.replace('update_status("IDLE")', 'update_status(self.app._t("target_card.status_idle"))')
content = content.replace('text="[ NO IMAGE ]"', 'text=self.app._t("target_card.no_image")')
content = content.replace('text="IDLE"', 'text=self.app._t("target_card.status_idle")')

# Fix Combo Chain hardcoding
old_combo_title = """            title_text = (
                f"{t_combo if t_combo != 'skill_strip.combo_lane' else 'Combo Chain'} {col + 1}"
                if is_combo_lane
                else f"{t_buff if t_buff != 'skill_strip.buff_lane' else 'Buff Lane'} {col + 1}"
            )"""
new_combo_title = """            title_text = (
                f"{t_combo} {col + 1}"
                if is_combo_lane
                else f"{t_buff} {col + 1}"
            )"""
content = content.replace(old_combo_title, new_combo_title)

with open("ui/tabs/hunt_tab.py", "w") as f:
    f.write(content)

with open("ui/controllers/app_state_controller.py", "r") as f:
    content2 = f.read()
content2 = content2.replace('app.hunt_target_info = tk.StringVar(master=root, value="Target: None")',
                            'app.hunt_target_info = tk.StringVar(master=root, value=app._t("target_card.target_none"))')
with open("ui/controllers/app_state_controller.py", "w") as f:
    f.write(content2)

with open("app_gui.py", "r") as f:
    content3 = f.read()
content3 = content3.replace('self.hunt_target_info.set("Target: None")',
                            'self.hunt_target_info.set(self._t("target_card.target_none"))')
with open("app_gui.py", "w") as f:
    f.write(content3)
