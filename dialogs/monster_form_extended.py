# -*- coding: utf-8 -*-
"""
Extended Monster Information Form Component.
Collapsible panel containing Stats, Attack, and Resistance sub-tabs.
"""

from __future__ import annotations
import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, List

try:
    from lib.ui_style import UIStyle as UI
except ImportError:
    from mock.fallbacks import UIStyle as UI

try:
    from ui.components import create_icon_label, create_icon_button
except ImportError:
    from mock.fallbacks import create_icon_label, create_icon_button


class ExtendedInfoForm(tk.Frame):
    """Component hiển thị nhóm 'Thông tin mở rộng' (Collapsible Panel với sub-tabs)."""

    def __init__(self, parent: tk.Widget, monster_data: Dict[str, Any]):
        super().__init__(parent, bg=UI.BG_DEFAULT)
        self.monster_data = monster_data
        self.is_expanded = False
        self.entries: Dict[str, tk.Entry] = {}
        self.error_labels: Dict[str, tk.Label] = {}

        self._setup_ui()
        self.populate(monster_data)

    def _setup_ui(self) -> None:
        # Header bar for toggle
        header_frame = tk.Frame(self, bg=UI.BG_PANEL, relief="groove", bd=1)
        header_frame.pack(fill="x", padx=5, pady=(5, 0))

        self.btn_toggle = create_icon_button(
            header_frame,
            icon_name="down",
            text="▶ Thông tin mở rộng (Stats, Attack, Resistance)",
            command=self.toggle_expand,
            button_type="gray",
        )
        self.btn_toggle.pack(side="left", fill="x", expand=True)

        # Content container (hidden by default)
        self.content_frame = tk.Frame(self, bg=UI.BG_DEFAULT)

        # Notebook for Sub-tabs
        self.notebook = ttk.Notebook(self.content_frame)
        self.notebook.pack(fill="both", expand=True, padx=5, pady=5)

        # --- Tab 1: Stats ---
        self.tab_stats = tk.Frame(self.notebook, bg=UI.BG_DEFAULT)
        self.notebook.add(self.tab_stats, text="Stats")
        self._build_stats_tab()

        # --- Tab 2: Attack ---
        self.tab_attack = tk.Frame(self.notebook, bg=UI.BG_DEFAULT)
        self.notebook.add(self.tab_attack, text="Attack")
        self._build_attack_tab()

        # --- Tab 3: Resistance ---
        self.tab_resistance = tk.Frame(self.notebook, bg=UI.BG_DEFAULT)
        self.notebook.add(self.tab_resistance, text="Resistance")
        self._build_resistance_tab()

    def toggle_expand(self) -> None:
        if self.is_expanded:
            self.content_frame.pack_forget()
            self.is_expanded = False
            self.btn_toggle.config(text="▶ Thông tin mở rộng (Stats, Attack, Resistance)")
        else:
            self.content_frame.pack(fill="both", expand=True, padx=5, pady=5)
            self.is_expanded = True
            self.btn_toggle.config(text="▼ Thông tin mở rộng (Stats, Attack, Resistance)")

    def _create_field_row(self, parent: tk.Widget, field: str, label_text: str, r: int, c: int) -> None:
        lbl = tk.Label(parent, text=f"{label_text}:", font=UI.FONT_LABEL, bg=UI.BG_DEFAULT)
        lbl.grid(row=r, column=c * 2, sticky="w", padx=5, pady=3)

        entry = tk.Entry(parent, font=UI.FONT_TEXT, width=12)
        entry.grid(row=r, column=c * 2 + 1, sticky="ew", padx=5, pady=3)
        self.entries[field] = entry

        err_lbl = tk.Label(parent, text="", fg="red", font=UI.FONT_SMALL, bg=UI.BG_DEFAULT)
        err_lbl.grid(row=r + 1, column=c * 2 + 1, sticky="w")
        err_lbl.grid_remove()
        self.error_labels[field] = err_lbl

    def _build_stats_tab(self) -> None:
        f = self.tab_stats
        fields = [
            ("exp", "EXP"),
            ("defense", "Defense"),
            ("attackRate", "Attack Rate"),
            ("defenseRate", "Defense Rate"),
            ("hpRecharge", "HP Recharge"),
            ("accuracy", "Accuracy"),
            ("penetration", "Penetration"),
            ("damageReduction", "Damage Red."),
            ("evasion", "Evasion"),
            ("hpProportionDamage", "HP Prop. Dmg"),
            ("absoluteDamage", "Absolute Dmg"),
        ]
        f.columnconfigure(1, weight=1)
        f.columnconfigure(3, weight=1)

        for i, (field, label) in enumerate(fields):
            r = (i // 2) * 2
            c = i % 2
            self._create_field_row(f, field, label, r, c)

    def _build_attack_tab(self) -> None:
        f = self.tab_attack
        fields = [
            ("primaryAttackMin", "Primary Atk Min"),
            ("primaryAttackMax", "Primary Atk Max"),
            ("secondaryAttackMin", "Secondary Atk Min"),
            ("secondaryAttackMax", "Secondary Atk Max"),
            ("ignoreAccuracy", "Ignore Acc."),
            ("ignoreDamageReduction", "Ignore Dmg Red."),
            ("ignorePenetration", "Ignore Pen."),
        ]
        f.columnconfigure(1, weight=1)
        f.columnconfigure(3, weight=1)

        for i, (field, label) in enumerate(fields):
            r = (i // 2) * 2
            c = i % 2
            self._create_field_row(f, field, label, r, c)

    def _build_resistance_tab(self) -> None:
        f = self.tab_resistance
        fields = [
            ("resistCritRate", "Resist Crit Rate"),
            ("resistSkillAmp", "Resist Skill Amp"),
            ("resistCritDamage", "Resist Crit Dmg"),
            ("resistSuppress", "Resist Suppress"),
            ("resistSilence", "Resist Silence"),
            ("resistDiffDamage", "Resist Diff Dmg"),
        ]
        f.columnconfigure(1, weight=1)
        f.columnconfigure(3, weight=1)

        for i, (field, label) in enumerate(fields):
            r = (i // 2) * 2
            c = i % 2
            self._create_field_row(f, field, label, r, c)

    def populate(self, data: Dict[str, Any]) -> None:
        for field, entry in self.entries.items():
            val = data.get(field, 0)
            entry.delete(0, tk.END)
            entry.insert(0, str(val if val is not None else 0))

    def get_data(self) -> Dict[str, Any]:
        result = {}
        for field, entry in self.entries.items():
            result[field] = entry.get().strip()
        return result

    def show_errors(self, errors: Dict[str, str]) -> None:
        has_err = False
        for field, lbl in self.error_labels.items():
            if field in errors:
                lbl.config(text=errors[field])
                lbl.grid()
                has_err = True
            else:
                lbl.grid_remove()

        if has_err and not self.is_expanded:
            self.toggle_expand()
