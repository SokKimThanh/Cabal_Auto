import tkinter as tk
from tkinter import ttk
from lib.ui_style import UIStyle as UI
from lib.features.skills.skill_preset_service import SkillPresetService

class SkillPanel:
    """Full panel with both widgets AND logic"""

    def __init__(self, parent, app_state):
        self.frame = tk.Frame(parent, bg=UI.THEME_BG_APP)
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
        header_frame = tk.Frame(self.frame, bg=UI.THEME_BG_PANEL)
        header_frame.pack(fill='x', pady=2)

        self.widgets['preset_indicator'] = tk.Label(header_frame, text="⭐ Default", bg=UI.THEME_BG_PANEL, fg=UI.THEME_TEXT_PRIMARY)
        self.widgets['preset_indicator'].pack(side='left')

        btn_frame = tk.Frame(header_frame, bg=UI.THEME_BG_PANEL)
        btn_frame.pack(side='right')

        self.widgets['btn_build'] = tk.Button(btn_frame, text="⚙️ Build", command=self.on_build)
        self.widgets['btn_build'].pack(side='left', padx=2)
        self.widgets['btn_presets'] = tk.Button(btn_frame, text="📋 Presets", command=self.on_presets)
        self.widgets['btn_presets'].pack(side='left', padx=2)
        self.widgets['btn_reset'] = tk.Button(btn_frame, text="🔄 Reset", command=self.on_reset)
        self.widgets['btn_reset'].pack(side='left', padx=2)

        # Load available skills for combobox values
        class_id = getattr(self.app_state, '_current_class_id', 1)
        skills = self.skill_service.skill_repo.list_skills(class_id=class_id)
        skill_names = [s.get('name') for s in skills if s.get('name')]

        lanes_frame = tk.Frame(self.frame, bg=UI.THEME_BG_APP)
        lanes_frame.pack(fill='both', expand=True, pady=4)

        # Combo lane section
        tk.Label(lanes_frame, text="Attack Combo", bg=UI.THEME_BG_APP, fg=UI.THEME_TEXT_SECONDARY).grid(row=0, column=0, sticky='w')
        self.widgets['combo_dropdowns'] = []
        for i in range(4):
            dd_var = tk.StringVar()
            dd = ttk.Combobox(lanes_frame, textvariable=dd_var, state='readonly', values=skill_names)
            dd.grid(row=0, column=i+1, padx=2, pady=2)
            dd.bind('<<ComboboxSelected>>', lambda e, idx=i: self._on_skill_changed(e, 'attack_combo', idx))
            self.widgets['combo_dropdowns'].append(dd)

        # Buff lane section
        tk.Label(lanes_frame, text="Buff Lane", bg=UI.THEME_BG_APP, fg=UI.THEME_TEXT_SECONDARY).grid(row=1, column=0, sticky='w')
        self.widgets['buff_dropdowns'] = []
        for i in range(4):
            dd_var = tk.StringVar()
            dd = ttk.Combobox(lanes_frame, textvariable=dd_var, state='readonly', values=skill_names)
            dd.grid(row=1, column=i+1, padx=2, pady=2)
            dd.bind('<<ComboboxSelected>>', lambda e, idx=i: self._on_skill_changed(e, 'buff_lane', idx))
            self.widgets['buff_dropdowns'].append(dd)

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
