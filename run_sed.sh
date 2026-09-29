sed -i 's/self\.app\.state_controller\.hunt_cfg\.get/self.app.state_controller.get_hunt_config_value/g' ui/tabs/hunt_tab.py
sed -i 's/self\.app\.state_controller\.hunt_cfg\.get/self.app.state_controller.get_hunt_config_value/g' ui/tabs/setup_tab.py
sed -i 's/self\.app\.state_controller\.hunt_cfg\.get/self.app.state_controller.get_hunt_config_value/g' ui/panels/monster_target_panel.py
sed -i 's/self\.app_state\.hunt_cfg\.get/self.app_state.get_hunt_config_value/g' ui/controllers/skill_panel_controller.py
sed -i 's/self\.root\.state_controller\.hunt_cfg\.get/self.root.state_controller.get_hunt_config_value/g' ui/controllers/app_window_controller.py
sed -i 's/self\.app\.state_controller\.hunt_cfg\.get/self.app.state_controller.get_hunt_config_value/g' ui/controllers/app_lifecycle_controller.py
sed -i 's/self\.parent\.state_controller\.hunt_cfg\.get/self.parent.state_controller.get_hunt_config_value/g' ui/controllers/hotkey_controller.py
sed -i 's/self\.parent\.hunt_cfg\.get/self.parent.state_controller.get_hunt_config_value/g' ui/controllers/overlay_controller.py
sed -i 's/self\.hunt_cfg\.get/self._get_cfg_val/g' ui/windows/library_manager.py
sed -i 's/hunt_cfg\.get("overlay"/self.get_hunt_config_value("overlay"/g' ui/controllers/overlay_controller.py
sed -i 's/self\.parent\.hunt_cfg\["overlay"\] = new_config/self.parent.state_controller.set_hunt_config_value("overlay", new_config)/g' ui/controllers/overlay_controller.py
sed -i 's/self\.parent\.hunt_cfg\["window_hwnd"\] = target_hwnd/self.parent.state_controller.set_hunt_config_value("window_hwnd", target_hwnd)/g' ui/controllers/overlay_controller.py
sed -i 's/self\.parent\.hunt_cfg\["window_title"\] = cabal_window.title/self.parent.state_controller.set_hunt_config_value("window_title", cabal_window.title)/g' ui/controllers/overlay_controller.py
sed -i 's/self\.root\.state_controller\.hunt_cfg\["window_title"\] = selected\["title"\]/self.root.state_controller.set_hunt_config_value("window_title", selected["title"])/g' ui/controllers/app_window_controller.py
sed -i 's/self\.root\.state_controller\.hunt_cfg\["window_pid"\] = selected\["pid"\]/self.root.state_controller.set_hunt_config_value("window_pid", selected["pid"])/g' ui/controllers/app_window_controller.py
sed -i 's/self\.root\.state_controller\.hunt_cfg\["window_hwnd"\] = selected\["hwnd"\]/self.root.state_controller.set_hunt_config_value("window_hwnd", selected["hwnd"])/g' ui/controllers/app_window_controller.py
sed -i 's/self\.app_state\.hunt_cfg\["last_active_class_id"\] = class_id/self.app_state.set_hunt_config_value("last_active_class_id", class_id)/g' ui/controllers/skill_preset_controller.py
sed -i 's/self\.app\.state_controller\.hunt_cfg\["is_configured"\] = True/self.app.state_controller.set_hunt_config_value("is_configured", True)/g' ui/controllers/app_lifecycle_controller.py
sed -i 's/self\.state_controller\.hunt_cfg\["window_pid"\] = window_dict\.get("pid")/self.state_controller.set_hunt_config_value("window_pid", window_dict.get("pid"))/g' ui/components/action_bar_view.py
sed -i 's/self\.state_controller\.hunt_cfg\["window_hwnd"\] = window_dict\.get("hwnd")/self.state_controller.set_hunt_config_value("window_hwnd", window_dict.get("hwnd"))/g' ui/components/action_bar_view.py
sed -i 's/self\.state_controller\.hunt_cfg\["window_title"\] = window_dict\.get("title")/self.state_controller.set_hunt_config_value("window_title", window_dict.get("title"))/g' ui/components/action_bar_view.py
sed -i 's/self\.app\.state_controller\.hunt_cfg\["target_policy"\] = new_policy/self.app.state_controller.set_hunt_config_value("target_policy", new_policy)/g' ui/panels/monster_target_panel.py
sed -i 's/self\.hunt_cfg\["window_bounds"\]/self._get_cfg_val("window_bounds")/g' ui/windows/library_manager.py
sed -i 's/self\.hunt_cfg\["skill_slots"\]/self._get_cfg_val("skill_slots", [])/g' ui/windows/library_manager.py
sed -i 's/save_hunt_config(self\.parent\.hunt_cfg)/self.parent.state_controller.save_hunt_config()/g' ui/controllers/overlay_controller.py
sed -i 's/save_hunt_config(self\.root\.state_controller\.hunt_cfg)/self.root.state_controller.save_hunt_config()/g' ui/controllers/app_window_controller.py
sed -i 's/save_hunt_config(self\.app\.state_controller\.hunt_cfg)/self.app.state_controller.save_hunt_config()/g' ui/controllers/library_manager_controller.py
sed -i 's/save_hunt_config(self\.app_state\.hunt_cfg)/self.app_state.save_hunt_config()/g' ui/controllers/skill_preset_controller.py
sed -i 's/save_hunt_config(self\.app\.state_controller\.hunt_cfg)/self.app.state_controller.save_hunt_config()/g' ui/controllers/app_lifecycle_controller.py
sed -i 's/save_hunt_config(self\.state_controller\.hunt_cfg)/self.state_controller.save_hunt_config()/g' ui/components/action_bar_view.py
sed -i '/from lib\.features\.hunt\.hunt_config import save_hunt_config/d' ui/controllers/overlay_controller.py
sed -i 's/from lib\.features\.hunt\.hunt_config import save_hunt_config, CONFIG_PATH/from lib.features.hunt.hunt_config import CONFIG_PATH/g' ui/controllers/app_window_controller.py
sed -i '/from lib\.features\.hunt\.hunt_config import save_hunt_config/d' ui/controllers/library_manager_controller.py
sed -i '/from lib\.features\.hunt\.hunt_config import save_hunt_config/d' ui/controllers/skill_preset_controller.py
sed -i '/from lib\.features\.hunt\.hunt_config import save_hunt_config/d' ui/controllers/app_lifecycle_controller.py
sed -i '/from lib\.features\.hunt\.hunt_config import save_hunt_config/d' ui/components/action_bar_view.py
sed -i 's/WindowSelectionService.update_bounds(self.root.state_controller.hunt_cfg, bounds)/WindowSelectionService.update_bounds(self.root.state_controller.get_all_hunt_config(), bounds)/g' ui/controllers/app_window_controller.py
sed -i 's/self\.parent\.state_controller\.get_hunt_config_value/self.parent.state_controller.get_hunt_config_value/g' ui/controllers/overlay_controller.py
sed -i 's/save_hunt_config(self\.app\.state_controller\.hunt_cfg)/self.app.state_controller.save_hunt_config()/g' ui/panels/monster_target_panel.py
sed -i '/from lib\.features\.hunt\.hunt_config import save_hunt_config/d' ui/panels/monster_target_panel.py
sed -i 's/self\.app\.state_controller\.get_hunt_config_value("window_hwnd")/self.app.state_controller.get_hunt_config_value("window_hwnd")/g' ui/tabs/hunt_tab.py
sed -i 's/self\.app\.state_controller\.get_hunt_config_value("global_hotkeys", {})/self.app.state_controller.get_hunt_config_value("global_hotkeys", {})/g' ui/tabs/setup_tab.py
sed -i 's/self\.app\.state_controller\.get_hunt_config_value("template_path", "assets\/images\/target_frame\.png")/self.app.state_controller.get_hunt_config_value("template_path", "assets\/images\/target_frame.png")/g' ui/tabs/setup_tab.py
sed -i '/self\.app\.state_controller\.hunt_cfg\["rois"\] = {}/d' ui/panels/monster_target_panel.py
sed -i 's/self\.app\.state_controller\.hunt_cfg\["rois"\]\["hunt_area"\] = list(region)/rois = self.app.state_controller.get_hunt_config_value("rois", {}); rois["hunt_area"] = list(region); self.app.state_controller.set_hunt_config_value("rois", rois)/g' ui/panels/monster_target_panel.py
