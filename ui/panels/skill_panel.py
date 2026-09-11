import tkinter as tk
from tkinter import ttk
from lib.ui_style_v2 import UIStyleV2 as UI
from lib.features.skills.skill_preset_service import SkillPresetService
from lib.features.skills.skill_runtime_service import SkillRuntimeService
from lib.db.services.class_service import ClassService
from ui.helpers.icon_helper import IconHelper


class SkillPanel(ttk.LabelFrame):
    """Full panel with both widgets AND logic"""

    def __init__(self, parent, app_state, scale_factor=1.0, hunt_tab=None):
        padding = (int(10 * scale_factor), int(8 * scale_factor))
        super().__init__(parent, text="⚔️ Active Skills", padding=padding)
        self.pack(fill="both", expand=True)
        self.app_state = app_state
        self.scale_factor = scale_factor
        self.hunt_tab = hunt_tab
        self.skill_service = SkillPresetService()
        self.widgets = {}
        self.frame = self  # Alias for backwards compatibility
        self._show_all_skills = False
        self._icon_helper = IconHelper()
        self._build()

        # Register for app state changes
        if hasattr(self.app_state, "register_callback"):
            self.app_state.register_callback(
                "on_skill_slots_changed", self.on_skill_slots_changed
            )
            self.app_state.register_callback(
                "on_bot_state_changed", self.on_bot_state_changed
            )

    def _build(self):
        """Build all widgets for skill panel"""
        header_frame = tk.Frame(self.frame, bg=UI.BG_ELEVATED)
        header_frame.pack(fill="x", pady=0)

        # Class selector
        class_frame = tk.Frame(header_frame, bg=UI.BG_ELEVATED)
        class_frame.pack(side="left", padx=(10, 0))

        lbl_class = tk.Label(class_frame, bg=UI.BG_ELEVATED, fg=UI.TEXT_PRIMARY)
        if hasattr(self.app_state, "bind_text"):
            self.app_state.bind_text(lbl_class, "lbl_class_select")
        else:
            lbl_class.config(text=self.app_state._t("lbl_class_select"))
        lbl_class.pack(side="left")

        self.widgets["cb_class"] = ttk.Combobox(
            class_frame,
            state="readonly",
            width=15,
            font=UI.FONT_BODY
        )
        self.widgets["cb_class"].pack(side="left", padx=5)
        self.widgets["cb_class"].bind("<<ComboboxSelected>>", self._on_class_selected)

        self._load_classes()

        # Combo header with custom checkbox
        cb_var = tk.BooleanVar(value=True)
        self.widgets["auto_combo_var"] = cb_var
        cb = tk.Checkbutton(
            header_frame,
            text="Bật Auto Combo",
            variable=cb_var,
            bg=UI.BG_ELEVATED,
            fg=UI.TEXT_PRIMARY,
            selectcolor=UI.BG_BASE,
            activebackground=UI.BG_ELEVATED,
            activeforeground=UI.TEXT_PRIMARY,
            relief="flat",
            bd=0,
            highlightthickness=0
        )
        self.widgets["auto_combo_cb"] = cb
        cb.pack(side="left", padx=12, pady=10)

        tk.Label(
            header_frame,
            text="[Alt+3]",
            font=UI.FONT_SMALL,
            bg=UI.BG_SURFACE,
            fg=UI.TEXT_MUTED,
        ).pack(side="left")

        self.widgets["preset_indicator"] = tk.Label(
            header_frame, bg=UI.BG_ELEVATED, fg=UI.TEXT_PRIMARY
        )
        if hasattr(self.app_state, "bind_text"):
            self.app_state.bind_text(self.widgets["preset_indicator"], "skill_panel.preset_default")
        else:
            self.widgets["preset_indicator"].config(text=self.app_state._t("skill_panel.preset_default"))
        self.widgets["preset_indicator"].pack(side="left", padx=(10, 0))

        btn_frame = tk.Frame(header_frame, bg=UI.BG_ELEVATED)
        btn_frame.pack(side="right", padx=12)

        self.widgets["btn_toggle_skills"] = tk.Button(
            btn_frame,
            command=self._on_toggle_skills,
            bg=UI.BG_ELEVATED,
            fg=UI.TEXT_MUTED,
            relief="flat",
            bd=0,
            cursor="hand2"
        )
        self._update_toggle_button_visuals()
        self.widgets["btn_toggle_skills"].pack(side="left", padx=10)

        self.widgets["btn_build"] = tk.Button(
            btn_frame,
            text="[⚙️ Build]",
            command=self.on_build,
            bg=UI.BG_ELEVATED,
            fg=UI.TEXT_MUTED,
            relief="flat",
            bd=0,
        )
        self.widgets["btn_build"].pack(side="left", padx=2)
        self.widgets["btn_presets"] = tk.Button(
            btn_frame,
            text="[📋 Presets]",
            command=self.on_presets,
            bg=UI.BG_ELEVATED,
            fg=UI.TEXT_MUTED,
            relief="flat",
            bd=0,
        )
        self.widgets["btn_presets"].pack(side="left", padx=2)
        self.widgets["btn_reset"] = tk.Button(
            btn_frame,
            text="[🔄 Reset]",
            command=self.on_reset,
            bg=UI.BG_ELEVATED,
            fg=UI.TEXT_MUTED,
            relief="flat",
            bd=0,
        )
        self.widgets["btn_reset"].pack(side="left", padx=2)

        self.widgets["btn_save_preset"] = tk.Button(
            btn_frame,
            text="[💾 Save Preset]",
            command=self._on_save_preset_click,
            bg=UI.BG_ELEVATED,
            fg=UI.ACCENT_BLUE,
            relief="flat",
            bd=0,
        )
        self.widgets["btn_save_preset"].pack(side="left", padx=2)

        # Load available skills for combobox values
        class_id = getattr(self.app_state, "_current_class_id", 1)
        skills = self.skill_service.skill_repo.list_skills(class_id=class_id, include_all=self._show_all_skills)
        self.skill_names = [s.get("name") for s in skills if s.get("name")]

        content_frame = tk.Frame(self.frame, bg=UI.BG_BASE)
        content_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Combo lane section (4 cards grid)
        combo_frame = tk.Frame(content_frame, bg=UI.BG_BASE)
        combo_frame.pack(fill="x")
        combo_frame.columnconfigure(0, weight=1)
        combo_frame.columnconfigure(1, weight=1)
        combo_frame.columnconfigure(2, weight=1)
        combo_frame.columnconfigure(3, weight=1)

        self.widgets["combo_dropdowns"] = []
        self.widgets["combo_hotkeys"] = []
        self.widgets["combo_stats"] = []

        for i in range(4):
            card = tk.Frame(
                combo_frame,
                bg=UI.BG_SURFACE,
                highlightbackground=UI.BORDER_PRIMARY,
                highlightthickness=1,
            )
            card.grid(row=0, column=i, sticky="nsew", padx=3, pady=3)

            # Header with title and hotkey entry
            header = tk.Frame(card, bg=UI.BG_SURFACE)
            header.pack(fill="x", padx=8, pady=(8, 2))
            tk.Label(
                header,
                text=f"{getattr(self.app_state, '_t', lambda x: x)('skill_strip.combo_lane')} {i + 1}",
                font=UI.FONT_SMALL,
                bg=UI.BG_SURFACE,
                fg=UI.TEXT_MUTED,
            ).pack(side="left")

            hk_entry = tk.Entry(
                header,
                width=5,
                bg=UI.BG_BASE,
                fg=UI.TEXT_PRIMARY,
                insertbackground=UI.TEXT_PRIMARY,
                relief="flat",
                justify="center"
            )
            hk_entry.pack(side="right")
            hk_entry.bind("<FocusOut>", lambda e, idx=i: self._on_hotkey_changed(e, "attack_combo", idx))
            hk_entry.bind("<Return>", lambda e, idx=i: self._on_hotkey_changed(e, "attack_combo", idx))
            self.widgets["combo_hotkeys"].append(hk_entry)

            dd_var = tk.StringVar()
            dd = ttk.Combobox(
                card, textvariable=dd_var, state="readonly", values=self.skill_names
            )
            dd.pack(fill="x", padx=8, pady=8)
            dd.bind(
                "<<ComboboxSelected>>",
                lambda e, idx=i: self._on_skill_changed(e, "attack_combo", idx),
            )
            self.widgets["combo_dropdowns"].append(dd)

            stats = tk.Frame(card, bg=UI.BG_SURFACE)
            stats.pack(fill="x", padx=8, pady=(2, 8))
            cast_lbl = tk.Label(
                stats,
                text="⏱ -",
                font=UI.FONT_SMALL,
                bg=UI.BG_SURFACE,
                fg=UI.TEXT_MUTED,
            )
            cast_lbl.pack(side="left")
            cd_lbl = tk.Label(
                stats,
                text="🔄 -",
                font=UI.FONT_SMALL,
                bg=UI.BG_SURFACE,
                fg=UI.TEXT_MUTED,
            )
            cd_lbl.pack(side="right")
            self.widgets["combo_stats"].append((cast_lbl, cd_lbl))
        # Divider
        divider = tk.Frame(content_frame, bg=UI.BG_BASE)
        divider.pack(fill="x", pady=16)

        # Use explicit frames to avoid border intersection
        left_line = tk.Frame(divider, height=1, bg=UI.BORDER_PRIMARY)
        left_line.pack(side="left", fill="x", expand=True)

        lbl_container = tk.Frame(divider, bg=UI.BG_BASE, padx=12, pady=4)
        lbl_container.pack(side="left")
        tk.Label(
            lbl_container,
            text=getattr(self.app_state, "_t", lambda x: x)("skill_strip.buff_lane"),
            font=UI.FONT_SMALL,
            bg=UI.BG_BASE,
            fg=UI.TEXT_MUTED,
        ).pack(side="left")

        right_line = tk.Frame(divider, height=1, bg=UI.BORDER_PRIMARY)
        right_line.pack(side="left", fill="x", expand=True)

        # Buff lane section (2 cards grid)
        buff_frame = tk.Frame(content_frame, bg=UI.BG_BASE)
        buff_frame.pack(fill="x")
        buff_frame.columnconfigure(0, weight=1)
        buff_frame.columnconfigure(1, weight=1)
        # Combo Mode Indicator and Controls
        controls_frame = tk.Frame(self.frame, bg=UI.BG_ELEVATED)
        controls_frame.pack(fill="x", padx=10, pady=(0, 10))

        self.widgets["combo_indicator_dot"] = tk.Label(
            controls_frame, text="🔴", bg=UI.BG_ELEVATED, fg=UI.TEXT_PRIMARY
        )
        self.widgets["combo_indicator_dot"].pack(side="left", padx=(10, 5), pady=10)

        self.widgets["combo_indicator_text"] = tk.Label(
            controls_frame, bg=UI.BG_ELEVATED, fg=UI.TEXT_MUTED
        )
        if hasattr(self.app_state, "bind_text"):
            self.app_state.bind_text(self.widgets["combo_indicator_text"], "skill_panel.combo_inactive")
        else:
            self.widgets["combo_indicator_text"].config(text=self.app_state._t("skill_panel.combo_inactive"))
        self.widgets["combo_indicator_text"].pack(side="left", pady=10)

        self.widgets["btn_start_combo"] = tk.Button(
            controls_frame,
            text=self.app_state._t("skill_panel.combo_start"),
            command=self.on_start_combo,
            bg=UI.ACCENT_GREEN_BG,
            fg=UI.ACCENT_GREEN,
            relief="flat",
            font=UI.FONT_BUTTON,
        )
        self.widgets["btn_start_combo"].pack(side="right", padx=10, pady=10)

        self.widgets["btn_stop_combo"] = tk.Button(
            controls_frame,
            text=self.app_state._t("skill_panel.combo_stop"),
            command=self.on_stop_combo,
            bg=UI.DANGER,
            fg=UI.TEXT_PRIMARY,
            relief="flat",
            font=UI.FONT_BUTTON,
        )
        # Initially hidden

        self.widgets["buff_dropdowns"] = []
        self.widgets["buff_hotkeys"] = []
        self.widgets["buff_stats"] = []

        for i in range(2):
            card = tk.Frame(
                buff_frame,
                bg=UI.BG_SURFACE,
                highlightbackground=UI.BORDER_PRIMARY,
                highlightthickness=1,
            )
            card.grid(row=0, column=i, sticky="nsew", padx=3, pady=3)

            header = tk.Frame(card, bg=UI.BG_SURFACE)
            header.pack(fill="x", padx=8, pady=(8, 2))
            tk.Label(
                header,
                text=self.app_state._t("skill_panel.buff_lane").format(num=i + 1),
                font=UI.FONT_SMALL,
                bg=UI.BG_SURFACE,
                fg=UI.TEXT_MUTED,
            ).pack(side="left")

            hk_entry = tk.Entry(
                header,
                width=5,
                bg=UI.BG_BASE,
                fg=UI.TEXT_PRIMARY,
                insertbackground=UI.TEXT_PRIMARY,
                relief="flat",
                justify="center"
            )
            hk_entry.pack(side="right")
            hk_entry.bind("<FocusOut>", lambda e, idx=i: self._on_hotkey_changed(e, "buff_lane", idx))
            hk_entry.bind("<Return>", lambda e, idx=i: self._on_hotkey_changed(e, "buff_lane", idx))
            self.widgets["buff_hotkeys"].append(hk_entry)

            dd_var = tk.StringVar()
            dd = ttk.Combobox(
                card, textvariable=dd_var, state="readonly", values=self.skill_names
            )
            dd.pack(fill="x", padx=8, pady=8)
            dd.bind(
                "<<ComboboxSelected>>",
                lambda e, idx=i: self._on_skill_changed(e, "buff_lane", idx),
            )
            self.widgets["buff_dropdowns"].append(dd)

            stats = tk.Frame(card, bg=UI.BG_SURFACE)
            stats.pack(fill="x", padx=8, pady=(2, 8))
            cast_lbl = tk.Label(
                stats,
                text="⏱ -",
                font=UI.FONT_SMALL,
                bg=UI.BG_SURFACE,
                fg=UI.TEXT_MUTED,
            )
            cast_lbl.pack(side="left")
            cd_lbl = tk.Label(
                stats,
                text="🔄 -",
                font=UI.FONT_SMALL,
                bg=UI.BG_SURFACE,
                fg=UI.TEXT_MUTED,
            )
            cd_lbl.pack(side="right")
            self.widgets["buff_stats"].append((cast_lbl, cd_lbl))

    def on_bot_state_changed(self, state: str):
        if not hasattr(self, "widgets") or "cb_class" not in self.widgets:
            return

        is_running = state == "running"
        # Also double check with controller just in case
        if hasattr(self.app_state, "is_bot_running") and self.app_state.is_bot_running():
            is_running = True

        if is_running:
            self.widgets["cb_class"].config(state="disabled")
        else:
            self.widgets["cb_class"].config(state="readonly")

    def _load_classes(self):
        class_service = ClassService()
        classes = class_service.get_all_classes()
        self._class_list = classes

        values = []
        default_val = ""
        current_class_id = getattr(self.app_state.root if hasattr(self.app_state, "root") else self.app_state, "_current_class_id", 1)

        for c in classes:
            val = f"{c['id']} - {c['name']}"
            values.append(val)
            if c['id'] == current_class_id:
                default_val = val

        self.widgets["cb_class"].config(values=values)
        if default_val:
            self.widgets["cb_class"].set(default_val)
            self._last_selected_class = default_val
        elif values:
            self.widgets["cb_class"].set(values[0])
            self._last_selected_class = values[0]

    def _on_class_selected(self, event):
        selected_val = self.widgets["cb_class"].get()
        if not selected_val:
            return

        try:
            class_id = int(selected_val.split(" - ")[0])
        except (ValueError, IndexError):
            self.widgets["cb_class"].set(getattr(self, "_last_selected_class", ""))
            return

        if hasattr(self.app_state, "set_current_class"):
            success = self.app_state.set_current_class(class_id)
            if not success:
                self.widgets["cb_class"].set(getattr(self, "_last_selected_class", ""))
            else:
                self._last_selected_class = selected_val
                # Reload skills for dropdowns
                self._show_all_skills = False
                self._update_toggle_button_visuals()

                skills = self.skill_service.skill_repo.list_skills(class_id=class_id, include_all=self._show_all_skills)
                self.skill_names = [s.get("name") for s in skills if s.get("name")]

                for dd in self.widgets.get("combo_dropdowns", []) + self.widgets.get("buff_dropdowns", []):
                    dd.config(values=self.skill_names)

    def on_start_combo(self):
        self.widgets["combo_indicator_dot"].config(text="🟢")
        self.widgets["combo_indicator_text"].config(text=self.app_state._t("skill_panel.combo_active"), fg=UI.ACCENT_GREEN)
        self.widgets["btn_start_combo"].pack_forget()
        self.widgets["btn_stop_combo"].pack(side="right", padx=10, pady=10)

        # Lock dropdowns
        for dd in self.widgets.get("combo_dropdowns", []) + self.widgets.get("buff_dropdowns", []):
            dd.config(state="disabled")

    def _update_toggle_button_visuals(self):
        btn = self.widgets.get("btn_toggle_skills")
        if not btn:
            return

        icon_name = "off-button" if self._show_all_skills else "on-button"
        icon_img = self._icon_helper.get_icon(icon_name, size=(32, 16))

        if icon_img and not isinstance(icon_img, str):
            btn.config(image=icon_img, text="")
            btn.image = icon_img
        else:
            # Fallback to text if image not found
            text = "[🌐 All Skills]" if self._show_all_skills else "[🎯 Class Skills]"
            btn.config(text=text, image="")

    def _on_toggle_skills(self):
        self._show_all_skills = not self._show_all_skills
        self._update_toggle_button_visuals()

        # Refresh skill list based on new mode
        class_id = getattr(self.app_state, "_current_class_id", 1)
        skills = self.skill_service.skill_repo.list_skills(class_id=class_id, include_all=self._show_all_skills)
        self.skill_names = [s.get("name") for s in skills if s.get("name")]

        # Update comboboxes
        for dd in self.widgets.get("combo_dropdowns", []) + self.widgets.get("buff_dropdowns", []):
            dd.config(values=self.skill_names)

    def on_stop_combo(self):
        self.widgets["combo_indicator_dot"].config(text="🔴")
        self.widgets["combo_indicator_text"].config(text=self.app_state._t("skill_panel.combo_inactive"), fg=UI.TEXT_MUTED)
        self.widgets["btn_stop_combo"].pack_forget()
        self.widgets["btn_start_combo"].pack(side="right", padx=10, pady=10)

        # Unlock dropdowns
        for dd in self.widgets.get("combo_dropdowns", []) + self.widgets.get("buff_dropdowns", []):
            dd.config(state="readonly")

    def _on_hotkey_changed(self, event, lane, position_idx):
        entry = event.widget
        new_hotkey = entry.get().strip()
        if hasattr(self.app_state, "set_skill_hotkey"):
            self.app_state.set_skill_hotkey(lane, position_idx, new_hotkey)
        # Prevent FocusOut / Return from causing UI weirdness
        if event.keysym == 'Return':
            self.focus_set()

    def on_skill_slots_changed(self, skill_slots=None):
        """Logic moved from HuntTab"""
        if not skill_slots:
            skill_slots = getattr(
                self.app_state, "skill_slots", {"attack_combo": [], "buff_lane": []}
            )

        runtime_srv = SkillRuntimeService()
        all_runtime_skills = runtime_srv.get_all_skills()

        # Update dropdowns, hotkeys, and stats
        for lane_key, dropdown_list, hotkeys_list, stats_list in [
            ("attack_combo", self.widgets.get("combo_dropdowns", []), self.widgets.get("combo_hotkeys", []), self.widgets.get("combo_stats", [])),
            ("buff_lane", self.widgets.get("buff_dropdowns", []), self.widgets.get("buff_hotkeys", []), self.widgets.get("buff_stats", [])),
        ]:
            lane_skills = skill_slots.get(lane_key, [])
            for i, dd in enumerate(dropdown_list):
                hk_entry = hotkeys_list[i] if i < len(hotkeys_list) else None
                cast_lbl, cd_lbl = stats_list[i] if i < len(stats_list) else (None, None)

                if i < len(lane_skills) and lane_skills[i]:
                    # We might have dict (if from app_state.skill_slots) or int (if from old structure)
                    slot_data = lane_skills[i]
                    skill_id = slot_data.get("skill_id") if isinstance(slot_data, dict) else slot_data

                    skill = self.skill_service.skill_repo.get_skill(skill_id)
                    if skill:
                        dd.set(skill.get("name", ""))

                        # Find runtime stats
                        runtime_info = next((s for s in all_runtime_skills if s.get("name") == skill.get("name")), None)

                        # Update Hotkey
                        user_hk = slot_data.get("user_hotkey", "") if isinstance(slot_data, dict) else ""
                        if not user_hk and runtime_info:
                            user_hk = runtime_info.get("key", "")

                        if hk_entry:
                            hk_entry.delete(0, 'end')
                            hk_entry.insert(0, user_hk)

                        # Update Stats
                        if runtime_info:
                            if cast_lbl:
                                cast_lbl.config(text=f"⏱ {runtime_info.get('cast_time', 0)}s")
                            if cd_lbl:
                                cd_lbl.config(text=f"🔄 {runtime_info.get('cooldown', 0)}s")
                        else:
                            if cast_lbl:
                                cast_lbl.config(text="⏱ -")
                            if cd_lbl:
                                cd_lbl.config(text="🔄 -")

                    else:
                        dd.set("")
                        if hk_entry:
                            hk_entry.delete(0, 'end')
                        if cast_lbl:
                            cast_lbl.config(text="⏱ -")
                        if cd_lbl:
                            cd_lbl.config(text="🔄 -")
                else:
                    dd.set("")
                    if hk_entry:
                        hk_entry.delete(0, 'end')
                    if cast_lbl:
                        cast_lbl.config(text="⏱ -")
                    if cd_lbl:
                        cd_lbl.config(text="🔄 -")

        # Update preset indicator
        preset_mode = getattr(self.app_state, "_preset_mode", "default")
        if preset_mode == "default":
            self.widgets["preset_indicator"].config(text=self.app_state._t("skill_panel.preset_default"))
        else:
            self.widgets["preset_indicator"].config(text=self.app_state._t("skill_panel.preset_custom"))

    def _on_skill_changed(self, event, lane, position_idx):
        """Logic extracted from HuntTab"""
        dropdown = event.widget
        skill_name = dropdown.get()
        # Ensure we search across all skills when updating the DB
        skills = self.skill_service.skill_repo.list_skills(include_all=True)
        skill_id = None
        for s in skills:
            if s.get("name") == skill_name:
                skill_id = s.get("skill_id")
                break

        if skill_id is not None and hasattr(self.app_state, "set_skill_slot"):
            self.app_state.set_skill_slot(lane, position_idx, skill_id)

    def on_build(self):
        """Open skill build tab"""
        pass

    def on_presets(self):
        """Open preset dialog"""
        from ui.dialogs.preset_dialog import PresetDialog

        PresetDialog(self.frame, self.app_state)

    def on_reset(self):
        """Revert to default preset"""
        class_id = getattr(self.app_state, "_current_class_id", 1)
        if hasattr(self.app_state, "apply_default_preset"):
            self.app_state.apply_default_preset(class_id)

    def _on_save_preset_click(self):
        from ui.dialogs.create_preset_dialog import CreatePresetDialog
        import tkinter.messagebox as messagebox

        # Disable button to prevent multiple clicks
        self.widgets["btn_save_preset"].config(state="disabled")

        class_id = getattr(self.app_state, "_current_class_id", 1)

        # Prepare skill summary
        skill_slots = getattr(self.app_state, "skill_slots", {"attack_combo": [], "buff_lane": []})
        skill_summary = {}
        for lane, skills in skill_slots.items():
            lane_names = []
            for slot_data in skills:
                if not slot_data:
                    continue
                skill_id = slot_data.get("skill_id") if isinstance(slot_data, dict) else slot_data
                if skill_id is not None:
                    skill = self.skill_service.skill_repo.get_skill(skill_id)
                    if skill:
                        lane_names.append(skill.get("name", f"Unknown ID {skill_id}"))
            skill_summary[lane] = lane_names

        def _on_save(preset_name):
            parsed_slots = {}
            for lane, skills in skill_slots.items():
                parsed_lane = []
                for slot_data in skills:
                    if not slot_data:
                        continue
                    skill_id = slot_data.get("skill_id") if isinstance(slot_data, dict) else slot_data
                    if skill_id is not None:
                        parsed_lane.append(skill_id)
                parsed_slots[lane] = parsed_lane

            res = self.skill_service.create_custom_preset(class_id, preset_name, parsed_slots)
            if res.get("success"):
                messagebox.showinfo("Success", f"Đã lưu preset '{preset_name}' thành công!", parent=self.frame)
                # Refresh indicator
                self.on_skill_slots_changed(skill_slots)
            else:
                messagebox.showerror("Error", f"Lỗi khi lưu preset: {res.get('error')}", parent=self.frame)

        dialog = CreatePresetDialog(
            parent=self.winfo_toplevel(),
            class_id=class_id,
            skill_summary=skill_summary,
            on_save_callback=_on_save
        )
        self.wait_window(dialog)

        # Safely re-enable button
        if self.winfo_exists() and "btn_save_preset" in self.widgets:
            self.widgets["btn_save_preset"].config(state="normal")

    def get_frame(self):
        return self.frame
