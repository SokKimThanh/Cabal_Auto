with open('app_gui.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_duration = """            if skill_type == "buff":
                duration = 300
                if hasattr(self, "skill_slot_duration_vars") and i < len(
                    self.state_controller.skill_slot_duration_vars
                ):
                    try:
                        duration = int(self.state_controller.skill_slot_duration_vars[i].get())
                    except ValueError:
                        pass
                slot_data["duration_sec"] = duration
                buff_slots.append(slot_data)"""

new_duration = """            if skill_type == "buff":
                duration = 300
                slot_data["duration_sec"] = duration
                buff_slots.append(slot_data)"""

content = content.replace(old_duration, new_duration)

old_calc = """        try:
            stats = self.state_controller._calculate_monster_estimate(monster)
        except Exception as e:
            DialogService.show_error(
                self._t("monster_section"), self._t("monster_invalid").format(e=e)
            )
            return
        kill_time = stats["kill_time"]
        attack_min, lost_timeout = self.state_controller._recommend_attack_settings(
            stats
        )"""

new_calc = """        try:
            from lib.features.hunt.hunt_setup_service import HuntSetupService
            stats = HuntSetupService.calculate_monster_estimate(monster)
        except Exception as e:
            DialogService.show_error(
                self._t("monster_section"), self._t("monster_invalid").format(e=e)
            )
            return
        kill_time = stats["kill_time"]
        from lib.features.hunt.hunt_setup_service import HuntSetupService
        attack_min, lost_timeout = HuntSetupService.recommend_attack_settings(
            stats
        )"""

content = content.replace(old_calc, new_calc)

with open('app_gui.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Duration and estimate patches applied.")
