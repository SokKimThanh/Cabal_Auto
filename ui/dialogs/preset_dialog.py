import tkinter as tk
from tkinter import ttk
from lib.ui_style import UIStyle as UI
from lib.features.skills.skill_preset_service import SkillPresetService

class PresetDialog(tk.Toplevel):
    def __init__(self, parent, app, **kwargs):
        super().__init__(parent, **kwargs)
        self.app = app
        self.service = SkillPresetService()
        self.title("Presets")
        self.geometry("400x300")
        self.transient(parent)
        self.grab_set()

        app_root = getattr(self.app, "root", self.app)
        self.class_id = getattr(app_root, "_current_class_id", 1)

        self._build_ui()
        self._load_presets()

    def _build_ui(self):
        main_frame = tk.Frame(self, bg=UI.THEME_BG_APP, padx=10, pady=10)
        main_frame.pack(fill='both', expand=True)

        self.listbox = tk.Listbox(main_frame, bg=UI.THEME_BG_PANEL, fg=UI.THEME_TEXT_PRIMARY, selectmode='single')
        self.listbox.pack(fill='both', expand=True, pady=5)

        btn_frame = tk.Frame(main_frame, bg=UI.THEME_BG_APP)
        btn_frame.pack(fill='x', pady=5)

        tk.Button(btn_frame, text="Cancel", command=self.destroy).pack(side='right', padx=2)
        self.apply_btn = tk.Button(btn_frame, text="Apply", command=self._on_apply)
        self.apply_btn.pack(side='right', padx=2)

        self.delete_btn = tk.Button(btn_frame, text="Delete", command=self._on_delete)
        self.delete_btn.pack(side='left', padx=2)

        self.listbox.bind('<<ListboxSelect>>', self._on_select)

    def _load_presets(self):
        self.presets = self.service.list_presets_by_class(self.class_id)
        self.listbox.delete(0, tk.END)
        for preset in self.presets:
            icon = "⭐" if preset['is_default'] else "✏️"
            self.listbox.insert(tk.END, f"{icon} {preset['name']}")

        self._update_buttons()

    def _on_select(self, event):
        self._update_buttons()

    def _update_buttons(self):
        selection = self.listbox.curselection()
        if not selection:
            self.apply_btn.config(state='disabled')
            self.delete_btn.config(state='disabled')
            return

        self.apply_btn.config(state='normal')

        idx = selection[0]
        preset = self.presets[idx]
        if preset['is_default']:
            self.delete_btn.config(state='disabled')
        else:
            self.delete_btn.config(state='normal')

    def _on_apply(self):
        selection = self.listbox.curselection()
        if selection:
            idx = selection[0]
            preset = self.presets[idx]
            if hasattr(self.app, 'load_preset_for_class'):
                self.app.load_preset_for_class(self.class_id, preset['preset_id'])
            self.destroy()

    def _on_delete(self):
        selection = self.listbox.curselection()
        if selection:
            idx = selection[0]
            preset = self.presets[idx]
            if not preset['is_default']:
                self.service.delete_custom_preset(preset['preset_id'])
                self._load_presets()
