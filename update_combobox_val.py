import re
with open("ui/tabs/hunt_tab.py", "r", encoding="utf-8") as f:
    content = f.read()

# Make sure we reset combobox current value, v.set() updates StringVar but Combobox text might stay if modified
# actually v.set() should correctly update the combobox text as it is tied with textvariable

# To strictly revert dropdown value display if v.set() isn't enough, we could set cmb.set(val)
# But tk.StringVar() is linked to textvariable=var on Combobox, so var.set() works for readonly comboboxes.

# Let's ensure cmb is accessible inside _on_cmb_selected to explicitly update it if needed.
# Let's also check if cmb is passed to the handler

# Change: def _on_cmb_selected(event, v=var, lbl=stats_lbl, is_combo_lane=is_combo_lane, col=col, cmb=cmb):
routing_code = """            def _on_cmb_selected(event, v=var, lbl=stats_lbl, is_combo_lane=is_combo_lane, col=col, cmb=cmb):
                selected_name = v.get().strip()
                if not selected_name:
                    v._previous_value = ""
                    if hasattr(self.app, "on_skill_slot_changed"):
                        self.app.on_skill_slot_changed(event)
                    update_card_stats(lbl, "")
                    return

                # Check skill type
                skills_by_name = {s.get("name"): s for s in getattr(self.app, "skills", []) if isinstance(s, dict) and s.get("name")}
                skill = skills_by_name.get(selected_name)

                if skill:
                    skill_type = skill.get("type", "attack")
                    expected_lane = "combo" if is_combo_lane else "buff"

                    # Ensure skill slots exist and are properly sized
                    skill_slot_vars = self.app.skill_slot_vars
                    combo_vars = skill_slot_vars[:4]
                    buff_vars = skill_slot_vars[4:]

                    if skill_type != "attack" and expected_lane == "combo":
                        # Buff selected in combo lane
                        # Find empty in buff lane
                        empty_idx = -1
                        for i, bv in enumerate(buff_vars):
                            if not bv.get().strip():
                                empty_idx = i
                                break

                        if empty_idx != -1:
                            # Move to empty buff slot
                            buff_vars[empty_idx].set(selected_name)
                            v.set("")
                            cmb.set("")
                            self.show_toast(f"Đã tự động chuyển '{selected_name}' sang Làn Buff", duration_ms=2000, level="info")
                        else:
                            # Lane full
                            prev = getattr(v, "_previous_value", "")
                            v.set(prev)
                            cmb.set(prev)
                            self.show_toast("Làn kỹ năng tương ứng đã đầy", duration_ms=2000, level="error")
                            return

                    elif skill_type == "attack" and expected_lane == "buff":
                        # Attack selected in buff lane
                        # Find empty in combo lane
                        empty_idx = -1
                        for i, cv in enumerate(combo_vars):
                            if not cv.get().strip():
                                empty_idx = i
                                break

                        if empty_idx != -1:
                            combo_vars[empty_idx].set(selected_name)
                            v.set("")
                            cmb.set("")
                            self.show_toast(f"Đã tự động chuyển '{selected_name}' sang Làn Combo", duration_ms=2000, level="info")
                        else:
                            prev = getattr(v, "_previous_value", "")
                            v.set(prev)
                            cmb.set(prev)
                            self.show_toast("Làn kỹ năng tương ứng đã đầy", duration_ms=2000, level="error")
                            return

                # Update previous value for rollback on next conflict
                v._previous_value = v.get().strip()

                if hasattr(self.app, "on_skill_slot_changed"):
                    self.app.on_skill_slot_changed(event)
                update_card_stats(lbl, v.get().strip())

                # If we moved it, also need to update the card stats of the destination
                for idx, slot_var in enumerate(self.app.skill_slot_vars):
                    if hasattr(self.app, "skill_slot_stats_labels") and idx < len(self.app.skill_slot_stats_labels):
                        update_card_stats(self.app.skill_slot_stats_labels[idx], slot_var.get().strip())"""

content = re.sub(r'            def _on_cmb_selected\(event, v=var, lbl=stats_lbl, is_combo_lane=is_combo_lane, col=col\):.*?update_card_stats\(self\.app\.skill_slot_stats_labels\[idx\], slot_var\.get\(\)\.strip\(\)\)', routing_code, content, flags=re.DOTALL)

with open("ui/tabs/hunt_tab.py", "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
