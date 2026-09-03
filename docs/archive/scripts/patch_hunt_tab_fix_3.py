import re

with open("ui/tabs/hunt_tab.py", "r", encoding="utf-8") as f:
    content = f.read()

replacement = """        # Replaced _load_skill_slots_from_cfg with equivalent logic inline
        saved = (
            self.app.hunt_cfg.get("skill_slots", []) if hasattr(self.app, "hunt_cfg") else []
        )

        normalized_slots = []
        for slot in saved:
            if isinstance(slot, dict):
                normalized_slots.append(slot.get("name", ""))
            elif isinstance(slot, str):
                normalized_slots.append(slot)
            else:
                normalized_slots.append("")

        self.app.skill_slot_saved_names = [name for name in normalized_slots if name]

        if hasattr(self.app, "_refresh_skill_slots_options"):
            self.app._refresh_skill_slots_options()

        if hasattr(self.app, "skill_slot_vars"):
            for idx, var in enumerate(self.app.skill_slot_vars):
                name = ""
                if idx < len(normalized_slots):
                    name = normalized_slots[idx]
                var.set(name)

        if hasattr(self.app, "_update_attack_keys_from_slots"):
            self.app._update_attack_keys_from_slots()"""

content = re.sub(r'        self\.app\._load_skill_slots_from_cfg\(\)', replacement, content)

with open("ui/tabs/hunt_tab.py", "w", encoding="utf-8") as f:
    f.write(content)
