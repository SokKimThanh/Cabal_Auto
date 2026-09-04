import re

with open("ui/controllers/app_state_controller.py", "r", encoding="utf-8") as f:
    content = f.read()

validate_code = """    def _validate_slot_key_duplicates(self) -> None:
        app = self.root
        labels = getattr(app, "skill_slot_key_labels", [])
        vars_ = getattr(app, "skill_slot_vars", [])
        boxes_ = getattr(app, "skill_slot_boxes", [])

        skills_by_name = {
            skill.get("name"): skill
            for skill in getattr(app, "skills", [])
            if isinstance(skill, dict) and skill.get("name")
        }

        seen = {}
        conflicts = {}  # idx -> conflict reason

        combo_key = app.hunt_cfg.get("combo", {}).get("combo_start_key", "").lower()

        for idx, var in enumerate(vars_):
            skill_name = var.get().strip()
            if not skill_name:
                continue

            key = str(skills_by_name.get(skill_name, {}).get("key", "") or "").lower()
            if not key:
                continue

            if combo_key and key == combo_key:
                conflicts[idx] = "Trùng với Combo Start Key"
                continue

            if key in seen:
                prev_idx = seen[key]
                conflicts[prev_idx] = "Trùng lặp phím kỹ năng"
                conflicts[idx] = "Trùng lặp phím kỹ năng"
            else:
                seen[key] = idx

        for idx, label in enumerate(labels):
            box = boxes_[idx] if idx < len(boxes_) else None

            if idx in conflicts:
                label.config(fg="#C62828")
                if box:
                    # Depending on widget type, config border might not work perfectly on ttk.Combobox,
                    # but we can place a tooltip over the widget frame (its parent card)
                    card = box.master
                    card.config(highlightbackground="#FFA500", highlightthickness=2)
                    if hasattr(app, "_create_tooltip"):
                        app._create_tooltip(card, f"[!] Cảnh báo: {conflicts[idx]}")
            else:
                label.config(fg="#333333")
                if box:
                    card = box.master
                    card.config(highlightbackground="#D0D0D0", highlightthickness=1)
                    if hasattr(app, "_create_tooltip"):
                        app._create_tooltip(card, app._t("skill_strip.tooltip_placeholder"))
"""

content = re.sub(r'    def _validate_slot_key_duplicates\(self\) -> None:\n(?:.*\n)*?            label\.config\(fg="#C62828" if idx in duplicate_indices else "#333333"\)', validate_code.strip(), content)

with open("ui/controllers/app_state_controller.py", "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
