import tkinter as tk
from tkinter import ttk
from lib.ui_style_v2 import UIStyleV2 as UI
from lib.features.skills.skill_runtime_service import SkillRuntimeService
from ui.helpers.icon_helper import IconHelper
from ui.controllers.skill_panel_controller import SkillPanelController
from ui.controllers.skill_preset_controller import SkillPresetController


class SkillPanel(ttk.LabelFrame):
    MODULE_NAME = "skill_panel"
    SCREEN_NAME = "main"

    """Full panel with both widgets AND logic"""

    def _t(self, key, **kwargs):
        if hasattr(self.app_state, "_t"):
            return self.app_state._t(key, **kwargs)
        from lib.i18n import t as i18n_t
        return i18n_t(key, **kwargs)

    def __init__(self, parent, app_state, scale_factor=1.0, hunt_tab=None):
        self.app_state = app_state
        padding = (int(10 * scale_factor), int(8 * scale_factor))
        super().__init__(parent, text=self._t("skill_panel.title", default="Active Skills"), padding=padding)
        # Fix typography hierarchy per Task 10
        self.configure(labelanchor="n")
        from ui.components.icon_button import create_icon_label
        lbl = create_icon_label(
            self,
            icon_name="skill",
            text=self._t("skill_panel.title", default="Active Skills"),
            font=UI.get_font("title", weight="bold"),
            bg=UI.BG_BASE,
            fg=UI.TEXT_PRIMARY
        )
        self.configure(labelwidget=lbl)
        self.pack(fill="both", expand=True)
        self.scale_factor = scale_factor
        self.hunt_tab = hunt_tab
        self.controller = SkillPanelController(self.app_state)
        self.preset_controller = SkillPresetController(self, self.app_state)
        self.widgets = {}
        self.frame = self  # Alias for backwards compatibility
        self._icon_helper = IconHelper()

        # Initial load from controller
        self.controller.load_skills()

        self._build()

        # Register for app state changes
        if hasattr(self.app_state, "register_callback"):
            self.app_state.register_callback(
                "on_skill_slots_changed", self.on_skill_slots_changed
            )
            self.app_state.register_callback(
                "on_bot_state_changed", self.on_bot_state_changed
            )

    def _map_skills_to_timeline_format(self, slots):
        """Helper to map raw slot data to what SkillTimelineStrip expects"""
        mapped = []
        for slot in slots:
            if not slot:
                continue
            skill_id = slot.get("skill_id") if isinstance(slot, dict) else slot
            skill_info = self.controller.get_skill(skill_id)
            if skill_info:
                mapped.append({
                    "name": skill_info.get("name", "Unknown"),
                    "icon_key": skill_info.get("icon_key", "unknown"),
                    "hotkey": slot.get("user_hotkey", "") if isinstance(slot, dict) else ""
                })
        return mapped

    def _build(self):
        """Build all widgets for skill panel"""
        self._build_header()

        from ui.components.combo_rhythm_bar import ComboRhythmBar
        from ui.components.skill_timeline_strip import SkillTimelineStrip

        # Top Element: Combo Rhythm Bar
        self.combo_rhythm_bar = ComboRhythmBar(self.frame)
        self.combo_rhythm_bar.pack(fill="x", padx=10, pady=(10, 0))

        # Bottom Element: Toggle Button Section
        self._build_toggle_section()

        # Middle Content: SkillTimelineStrips
        self.content_frame = tk.Frame(self.frame, bg=UI.BG_BASE)
        self.content_frame.pack(fill="both", expand=True, padx=10, pady=(10, 0))

        # We keep these initialized to prevent breaking Automation Tests
        self.widgets["combo_dropdowns"] = []
        self.widgets["combo_hotkeys"] = []
        self.widgets["combo_stats"] = []
        self.widgets["buff_dropdowns"] = []
        self.widgets["buff_hotkeys"] = []
        self.widgets["buff_stats"] = []

        # Title for attack combo
        tk.Label(
            self.content_frame,
            text=self._t('skill_strip.combo_lane'),
            font=UI.FONT_SMALL,
            bg=UI.BG_BASE,
            fg=UI.TEXT_MUTED,
            anchor="w"
        ).pack(fill="x", pady=(0, 5))

        combo_seq = self._map_skills_to_timeline_format(self.controller.get_combo_sequence())
        self.attack_timeline = SkillTimelineStrip(self.content_frame, skills=combo_seq)
        self.attack_timeline.pack(fill="x", pady=(0, 10))

        # Title for buff lane
        tk.Label(
            self.content_frame,
            text=self._t('skill_strip.buff_lane'),
            font=UI.FONT_SMALL,
            bg=UI.BG_BASE,
            fg=UI.TEXT_MUTED,
            anchor="w"
        ).pack(fill="x", pady=(10, 5))

        buff_seq = self._map_skills_to_timeline_format(self.controller.get_buff_sequence())
        self.buff_timeline = SkillTimelineStrip(self.content_frame, skills=buff_seq)
        self.buff_timeline.pack(fill="x", pady=(0, 10))

    def _build_toggle_section(self):
        # Combo Mode Controls pinned to bottom
        controls_frame = tk.Frame(self.frame, bg=UI.BG_ELEVATED)
        controls_frame.pack(side="bottom", fill="x", padx=10, pady=10)

        # Ensure auto_combo_var exists for backward compat and Automation
        if "auto_combo_var" not in self.widgets:
            self.widgets["auto_combo_var"] = tk.BooleanVar(value=True)

        from ui.components.icon_button import create_icon_button

        self.btn_toggle_combo = create_icon_button(
            parent=controls_frame,
            element_id="btn_skill_toggle_combo",
            icon_name="play", # Initial icon, will be updated
            command=self.on_toggle_combo,
            button_type="neutral"
        )
        self.btn_toggle_combo.pack(fill="x", padx=10, pady=10)
        self._update_combo_toggle_ui()

    def on_toggle_combo(self):
        current_state = self.widgets["auto_combo_var"].get()
        new_state = not current_state
        self.widgets["auto_combo_var"].set(new_state)

        # Save to backend config
        if hasattr(self.app_state, "hunt_cfg"):
            if "combo" not in self.app_state.hunt_cfg:
                self.app_state.hunt_cfg["combo"] = {}
            self.app_state.hunt_cfg["combo"]["enabled"] = new_state

            # Optional: Call save config if state controller has one
            # Relying on controllers to pick this up, but marking as unsaved if possible
            if hasattr(self.app_state, "_mark_unsaved"):
                self.app_state._mark_unsaved()

        self._update_combo_toggle_ui()

    def _update_combo_toggle_ui(self):
        if not hasattr(self, "btn_toggle_combo"):
            return

        from ui.components.icon_button import update_button_state
        is_enabled = self.widgets["auto_combo_var"].get()
        if is_enabled:
            update_button_state(
                self.btn_toggle_combo,
                enabled=True,
                icon_name="stop",
                tooltip_text=self._t("skill_panel.combo_stop")
            )
            self.btn_toggle_combo.config(bg=UI.ACCENT_GREEN_BG, fg=UI.ACCENT_GREEN, text=self._t("skill_panel.combo_stop"))
        else:
            update_button_state(
                self.btn_toggle_combo,
                enabled=True,
                icon_name="play",
                tooltip_text=self._t("skill_panel.combo_start")
            )
            self.btn_toggle_combo.config(bg=UI.BG_SURFACE, fg=UI.TEXT_MUTED, text=self._t("skill_panel.combo_start"))

    def _build_header(self):
        header_frame = tk.Frame(self.frame, bg=UI.BG_ELEVATED)
        header_frame.pack(fill="x", pady=0)

        # Class selector
        class_frame = tk.Frame(header_frame, bg=UI.BG_ELEVATED)
        class_frame.pack(side="left", padx=(10, 0))

        lbl_class = tk.Label(class_frame, bg=UI.BG_ELEVATED, fg=UI.TEXT_PRIMARY)
        if hasattr(self.app_state, "bind_text"):
            self.app_state.bind_text(lbl_class, "lbl_class_select")
        else:
            lbl_class.config(text=self._t("lbl_class_select"))
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

        # Ensure auto_combo_var exists, but we removed the Checkbutton
        # It's now driven entirely by the _build_toggle_section button
        if "auto_combo_var" not in self.widgets:
            self.widgets["auto_combo_var"] = tk.BooleanVar(value=True)

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
            self.widgets["preset_indicator"].config(text=self._t("skill_panel.preset_default"))
        self.widgets["preset_indicator"].pack(side="left", padx=(10, 0))

        btn_frame = tk.Frame(header_frame, bg=UI.BG_ELEVATED)
        btn_frame.pack(side="right", padx=12)

        from ui.components.icon_button import create_icon_button

        self.widgets["btn_toggle_skills"] = create_icon_button(
            parent=btn_frame,
            element_id="btn_skill_toggle_view",
            icon_name="list",
            command=self._on_toggle_skills,
            button_type="neutral"
        )
        self._update_toggle_button_visuals()
        self.widgets["btn_toggle_skills"].pack(side="left", padx=10)

        self.widgets["btn_build"] = create_icon_button(
            parent=btn_frame,
            element_id="btn_skill_build",
            icon_name="settings",
            text="Build",
            command=self.on_build,
            button_type="neutral"
        )
        self.widgets["btn_build"].pack(side="left", padx=2)

        self.widgets["btn_presets"] = create_icon_button(
            parent=btn_frame,
            element_id="btn_skill_presets",
            icon_name="list",
            text="Presets",
            command=self.on_presets,
            button_type="neutral"
        )
        self.widgets["btn_presets"].pack(side="left", padx=2)

        self.widgets["btn_reset"] = create_icon_button(
            parent=btn_frame,
            element_id="btn_skill_reset",
            icon_name="refresh",
            text="Reset",
            command=self.on_reset,
            button_type="neutral"
        )
        self.widgets["btn_reset"].pack(side="left", padx=2)

        self.widgets["btn_save_preset"] = create_icon_button(
            parent=btn_frame,
            element_id="btn_skill_save_preset",
            icon_name="save",
            text="Save Preset",
            command=self._on_save_preset_click,
            button_type="default"
        )
        self.widgets["btn_save_preset"].pack(side="left", padx=2)

        # Initial load from controller is handled in __init__

    def on_bot_state_changed(self, state: str):
        if not hasattr(self, "widgets") or "cb_class" not in self.widgets:
            return

        is_running = state == "running"
        if hasattr(self.app_state, "is_bot_running") and self.app_state.is_bot_running():
            is_running = True

        locked, class_label, skill_names = self.controller.handle_bot_state_change(is_running)

        if locked:
            self._update_toggle_button_visuals()
            self.widgets["cb_class"].config(state="disabled")
            if class_label:
                self.widgets["cb_class"].set(class_label)

            for dd in self.widgets.get("combo_dropdowns", []) + self.widgets.get("buff_dropdowns", []):
                dd.config(values=skill_names)
        else:
            self._update_toggle_button_visuals()
            if self.controller.show_all_skills:
                self.widgets["cb_class"].config(state="disabled")
                self.widgets["cb_class"].set("---")
            else:
                self.widgets["cb_class"].config(state="readonly")
                if class_label:
                    self.widgets["cb_class"].set(class_label)

            for dd in self.widgets.get("combo_dropdowns", []) + self.widgets.get("buff_dropdowns", []):
                dd.config(values=skill_names)

    def _load_classes(self):
        values, default_val = self.controller.load_classes()
        self.widgets["cb_class"].config(values=values)
        if default_val:
            self.widgets["cb_class"].set(default_val)
        elif values:
            self.widgets["cb_class"].set(values[0])

    def _on_class_selected(self, event):
        selected_val = self.widgets["cb_class"].get()
        success, last_selected, skill_names = self.controller.on_class_selected(selected_val)

        if not success:
            self.widgets["cb_class"].set(last_selected)
        else:
            for dd in self.widgets.get("combo_dropdowns", []) + self.widgets.get("buff_dropdowns", []):
                dd.config(values=skill_names)

    def _update_toggle_button_visuals(self):
        btn = self.widgets.get("btn_toggle_skills")
        if not btn:
            return

        from ui.components.icon_button import set_button_icon
        icon_name = "list" if self.controller.show_all_skills else "target"
        set_button_icon(btn, icon_name=icon_name)

    def _on_toggle_skills(self):
        show_all, skill_names = self.controller.toggle_skills()
        self._update_toggle_button_visuals()

        if show_all:
            # Mode ON (All Skills): Disable Class Dropdown, set to '---'
            self.widgets["cb_class"].set("---")
            self.widgets["cb_class"].config(state="disabled")
        else:
            # Mode OFF (Class Skills): Enable Class Dropdown, restore value
            self.widgets["cb_class"].config(state="readonly")
            self.widgets["cb_class"].set(self.controller.last_selected_class)

        # Update comboboxes
        for dd in self.widgets.get("combo_dropdowns", []) + self.widgets.get("buff_dropdowns", []):
            dd.config(values=skill_names)

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

        # First, ensure combobox values are up to date
        for dd in self.widgets.get("combo_dropdowns", []) + self.widgets.get("buff_dropdowns", []):
            dd.config(values=self.controller.skill_names)

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

                    skill = self.controller.get_skill(skill_id)
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
                                cast_lbl.config(text=f"{runtime_info.get('cast_time', 0)}s")
                            if cd_lbl:
                                cd_lbl.config(text=f"{runtime_info.get('cooldown', 0)}s")
                        else:
                            if cast_lbl:
                                cast_lbl.config(text="-")
                            if cd_lbl:
                                cd_lbl.config(text="-")

                    else:
                        dd.set("")
                        if hk_entry:
                            hk_entry.delete(0, 'end')
                        if cast_lbl:
                            cast_lbl.config(text="-")
                        if cd_lbl:
                            cd_lbl.config(text="-")
                else:
                    dd.set("")
                    if hk_entry:
                        hk_entry.delete(0, 'end')
                    if cast_lbl:
                        cast_lbl.config(text="-")
                    if cd_lbl:
                        cd_lbl.config(text="-")

        # Also sync SkillTimelineStrips
        if hasattr(self, "attack_timeline") and self.attack_timeline.winfo_exists():
            self.attack_timeline.update_skills(self._map_skills_to_timeline_format(self.controller.get_combo_sequence()))
        if hasattr(self, "buff_timeline") and self.buff_timeline.winfo_exists():
            self.buff_timeline.update_skills(self._map_skills_to_timeline_format(self.controller.get_buff_sequence()))

        # Update preset indicator
        preset_mode = getattr(self.app_state, "_preset_mode", "default")
        if preset_mode == "default":
            self.widgets["preset_indicator"].config(text=self._t("skill_panel.preset_default"))
        else:
            self.widgets["preset_indicator"].config(text=self._t("skill_panel.preset_custom"))

    def _on_skill_changed(self, event, lane, position_idx):
        """Logic extracted from HuntTab"""
        dropdown = event.widget
        skill_name = dropdown.get()

        skill_id = self.controller.get_skill_id_by_name(skill_name)

        if skill_id is not None and hasattr(self.controller.preset_controller, "set_skill_slot"):
            self.controller.preset_controller.set_skill_slot(lane, position_idx, skill_id)

    def on_build(self):
        """Open skill build tab"""
        pass

    def on_presets(self):
        """Open preset dialog"""
        self.preset_controller.on_presets()

    def on_reset(self):
        """Revert to default preset"""
        class_id = getattr(self.app_state, "_current_class_id", 1)
        self.preset_controller.on_reset(class_id)

    def _on_save_preset_click(self):
        class_id = getattr(self.app_state, "_current_class_id", 1)
        btn_widget = self.widgets.get("btn_save_preset")
        self.preset_controller.on_save_preset_click(class_id, btn_widget, self.on_skill_slots_changed)

    def get_frame(self):
        return self.frame
