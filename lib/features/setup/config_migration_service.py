from lib.features.hunt.hunt_config import save_hunt_config
from lib.ui.dialog_service import DialogService

class ConfigMigrationService:
    @staticmethod
    def migrate_legacy_attack_keys(state_controller, skill_service, t_func):
        try:
            slots = state_controller.hunt_cfg.get("skill_slots", [])
            anon_indices = [
                i for i, s in enumerate(slots)
                if isinstance(s, dict) and not s.get("name") and s.get("key")
            ]
            if anon_indices:
                try:
                    DialogService.show_info(
                        t_func("migration_legacy_attack_keys_title"),
                        t_func("migration_legacy_attack_keys_message"),
                    )
                except Exception:
                    pass

            skills = skill_service.get_all_skills() if skill_service else []
            if anon_indices and skills:
                assigned = {
                    s.get("name") for s in slots
                    if isinstance(s, dict) and s.get("name")
                }
                attack_names = [
                    sk.get("name", "Unknown") for sk in skills
                    if sk.get("type", "attack") == "attack"
                    and sk.get("name") and sk.get("name") not in assigned
                ]
                changed = False
                for idx in anon_indices:
                    if not attack_names: break
                    name = attack_names.pop(0)
                    slots[idx]["name"] = name
                    changed = True
                if changed:
                    state_controller.hunt_cfg["skill_slots"] = slots
                    try:
                        save_hunt_config(state_controller.hunt_cfg)
                        try:
                            mapped = ", ".join([slots[i].get("name", "") for i in anon_indices if slots[i].get("name")])
                            info_msg = t_func("migration_legacy_attack_keys_auto_mapped").format(mapped=mapped)
                            DialogService.show_info(t_func("skill_section"), info_msg)
                        except Exception:
                            pass
                        state_controller.set_ui_var('hunt_status', t_func("migration_mapped_slots_short"))
                    except Exception:
                        pass
        except Exception:
            pass
