import tkinter as tk
from tkinter import ttk
from lib.ui_style_v2 import UIStyleV2 as UI
from lib.features.skills.skill_preset_service import SkillPresetService

class SkillPanel:
    """Full panel with both widgets AND logic"""

    def __init__(self, parent, app_state):
        self.frame = tk.Frame(parent, bg=UI.BG_BASE)
        self.frame.pack(fill="both", expand=True)
        self.app_state = app_state
        self.skill_service = SkillPresetService()
        self.widgets = {}
        self._build()

        # Register for app state changes
        if hasattr(self.app_state, 'register_callback'):
            self.app_state.register_callback('on_skill_slots_changed', self.on_skill_slots_changed)

    def _build(self):
        """Build all widgets for skill panel"""
        header_frame = tk.Frame(self.frame, bg=UI.BG_ELEVATED)
        header_frame.pack(fill='x', pady=0)

        # Combo header with custom checkbox
        cb_var = tk.BooleanVar(value=True)
        self.widgets['auto_combo_var'] = cb_var
        cb = tk.Checkbutton(
            header_frame,
            text="Bật Auto Combo",
            variable=cb_var,
            bg=UI.BG_ELEVATED,
            fg=UI.TEXT_PRIMARY,
            selectcolor=UI.BG_ELEVATED,
            activebackground=UI.BG_ELEVATED,
            activeforeground=UI.TEXT_PRIMARY,
        )
        self.widgets['auto_combo_cb'] = cb
        cb.pack(side='left', padx=12, pady=10)

        tk.Label(header_frame, text="[Alt+3]", font=UI.FONT_SMALL, bg=UI.BG_SURFACE, fg=UI.TEXT_MUTED).pack(side='left')

        self.widgets['preset_indicator'] = tk.Label(header_frame, text="⭐ Default", bg=UI.BG_ELEVATED, fg=UI.TEXT_PRIMARY)
        self.widgets['preset_indicator'].pack(side='left', padx=(10,0))

        btn_frame = tk.Frame(header_frame, bg=UI.BG_ELEVATED)
        btn_frame.pack(side='right', padx=12)

        self.widgets['btn_build'] = tk.Button(btn_frame, text="⚙️", command=self.on_build, bg=UI.BG_ELEVATED, fg=UI.TEXT_MUTED, relief="flat", bd=0)
        self.widgets['btn_build'].pack(side='left', padx=2)
        self.widgets['btn_presets'] = tk.Button(btn_frame, text="📋", command=self.on_presets, bg=UI.BG_ELEVATED, fg=UI.TEXT_MUTED, relief="flat", bd=0)
        self.widgets['btn_presets'].pack(side='left', padx=2)
        self.widgets['btn_reset'] = tk.Button(btn_frame, text="🔄", command=self.on_reset, bg=UI.BG_ELEVATED, fg=UI.TEXT_MUTED, relief="flat", bd=0)
        self.widgets['btn_reset'].pack(side='left', padx=2)

        # Load available skills for combobox values
        class_id = getattr(self.app_state, '_current_class_id', 1)
        skills = self.skill_service.skill_repo.list_skills(class_id=class_id)
        skill_names = [s.get('name') for s in skills if s.get('name')]

        content_frame = tk.Frame(self.frame, bg=UI.BG_BASE)
        content_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Combo lane section (4 cards grid)
        combo_frame = tk.Frame(content_frame, bg=UI.BG_BASE)
        combo_frame.pack(fill='x')
        combo_frame.columnconfigure(0, weight=1)
        combo_frame.columnconfigure(1, weight=1)
        combo_frame.columnconfigure(2, weight=1)
        combo_frame.columnconfigure(3, weight=1)

        self.widgets['combo_dropdowns'] = []
        for i in range(4):
            card = tk.Frame(combo_frame, bg=UI.BG_ELEVATED, highlightbackground=UI.BORDER_PRIMARY, highlightthickness=1)
            card.grid(row=0, column=i, sticky="nsew", padx=3, pady=3)

            tk.Label(card, text=f"CHAIN {i+1}", font=UI.FONT_SMALL, bg=UI.BG_ELEVATED, fg=UI.TEXT_MUTED).pack(anchor="w", padx=8, pady=(8,2))

            dd_var = tk.StringVar()
            dd = ttk.Combobox(card, textvariable=dd_var, state='readonly', values=skill_names)
            dd.pack(fill='x', padx=6, pady=4)
            dd.bind('<<ComboboxSelected>>', lambda e, idx=i: self._on_skill_changed(e, 'attack_combo', idx))
            self.widgets['combo_dropdowns'].append(dd)

            stats = tk.Frame(card, bg=UI.BG_ELEVATED)
            stats.pack(fill='x', padx=8, pady=(2,8))
            tk.Label(stats, text="⏱ 0.5s", font=UI.FONT_SMALL, bg=UI.BG_ELEVATED, fg=UI.TEXT_MUTED).pack(side='left')
            tk.Label(stats, text="🔄 5s", font=UI.FONT_SMALL, bg=UI.BG_ELEVATED, fg=UI.TEXT_MUTED).pack(side='right')

        # Divider
        divider = tk.Frame(content_frame, bg=UI.BG_BASE)
        divider.pack(fill='x', pady=12)
        tk.Frame(divider, height=1, bg=UI.BORDER_PRIMARY).pack(side='left', fill='x', expand=True)
        tk.Label(divider, text="BUFF LANES", font=UI.FONT_SMALL, bg=UI.BG_BASE, fg=UI.TEXT_MUTED).pack(side='left', padx=8)
        tk.Frame(divider, height=1, bg=UI.BORDER_PRIMARY).pack(side='left', fill='x', expand=True)

        # Buff lane section (2 cards grid)
        buff_frame = tk.Frame(content_frame, bg=UI.BG_BASE)
        buff_frame.pack(fill='x')
        buff_frame.columnconfigure(0, weight=1)
        buff_frame.columnconfigure(1, weight=1)

        self.widgets['buff_dropdowns'] = []
        for i in range(2):
            card = tk.Frame(buff_frame, bg="#161616", highlightbackground=UI.BORDER_PRIMARY, highlightthickness=1)
            card.grid(row=0, column=i, sticky="nsew", padx=3, pady=3)

            tk.Label(card, text=f"BUFF LANE {i+1}", font=UI.FONT_SMALL, bg="#161616", fg=UI.TEXT_MUTED).pack(anchor="w", padx=8, pady=(8,2))

            dd_var = tk.StringVar()
            dd = ttk.Combobox(card, textvariable=dd_var, state='readonly', values=skill_names)
            dd.pack(fill='x', padx=6, pady=4)
            dd.bind('<<ComboboxSelected>>', lambda e, idx=i: self._on_skill_changed(e, 'buff_lane', idx))
            self.widgets['buff_dropdowns'].append(dd)

            stats = tk.Frame(card, bg="#161616")
            stats.pack(fill='x', padx=8, pady=(2,8))
            tk.Label(stats, text="⏱ 2.0s", font=UI.FONT_SMALL, bg="#161616", fg=UI.TEXT_MUTED).pack(side='left')
            tk.Label(stats, text="🔄 20s", font=UI.FONT_SMALL, bg="#161616", fg=UI.TEXT_MUTED).pack(side='right')

    def on_skill_slots_changed(self, skill_slots=None):
        """Logic moved from HuntTab"""
        if not skill_slots:
            skill_slots = getattr(self.app_state, 'skill_slots', {'attack_combo': [], 'buff_lane': []})

        # Update dropdowns
        for lane_key, dropdown_list in [('attack_combo', self.widgets['combo_dropdowns']), ('buff_lane', self.widgets['buff_dropdowns'])]:
            lane_skills = skill_slots.get(lane_key, [])
            for i, dd in enumerate(dropdown_list):
                if i < len(lane_skills) and lane_skills[i]:
                    skill = self.skill_service.skill_repo.get_skill(lane_skills[i])
                    if skill:
                        dd.set(skill.get('name', ''))
                else:
                    dd.set('')

        # Update preset indicator
        preset_mode = getattr(self.app_state, '_preset_mode', 'default')
        if preset_mode == 'default':
            self.widgets['preset_indicator'].config(text="⭐ Default")
        else:
            self.widgets['preset_indicator'].config(text="✏️ Custom")

    def _on_skill_changed(self, event, lane, position_idx):
        """Logic extracted from HuntTab"""
        dropdown = event.widget
        skill_name = dropdown.get()
        skills = self.skill_service.skill_repo.list_skills()
        skill_id = None
        for s in skills:
            if s.get('name') == skill_name:
                skill_id = s.get('skill_id')
                break

        if skill_id is not None and hasattr(self.app_state, 'set_skill_slot'):
            self.app_state.set_skill_slot(lane, position_idx, skill_id)

    def on_build(self):
        """Open skill build tab"""
        pass

    def on_presets(self):
        """Open preset dialog"""
        from ui.dialogs.preset_dialog import PresetDialog
        dialog = PresetDialog(self.frame, self.app_state)

    def on_reset(self):
        """Revert to default preset"""
        class_id = getattr(self.app_state, '_current_class_id', 1)
        if hasattr(self.app_state, 'apply_default_preset'):
            self.app_state.apply_default_preset(class_id)

    def get_frame(self):
        return self.frame
