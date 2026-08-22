# -*- coding: utf-8 -*-
"""
Basic Monster Information Form Component.
Handles required fields: id, name, level, hp, dungeonId, serverBossType.
Includes "Generate ID", ID read-only on Edit, and "Clone from Monster" feature.
"""

from __future__ import annotations
import tkinter as tk
from tkinter import ttk
import uuid
from typing import Dict, Any, List, Optional, Callable

try:
    from lib.ui_style import UIStyle as UI
except ImportError:
    from mock.fallbacks import UIStyle as UI

try:
    from ui.components import create_icon_label, create_icon_button
except ImportError:
    from mock.fallbacks import create_icon_label, create_icon_button


class BasicInfoForm(tk.Frame):
    """Component hiển thị nhóm 'Thông tin cơ bản' (Bắt buộc)."""

    def __init__(
        self,
        parent: tk.Widget,
        monster_data: Dict[str, Any],
        is_new: bool,
        dungeon_list: List[Dict[str, str]],
        type_list: List[Dict[str, str]],
        existing_monsters: List[Dict[str, Any]],
        on_clone_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
    ):
        super().__init__(parent, bg=UI.BG_DEFAULT)
        self.monster_data = monster_data
        self.is_new = is_new
        self.dungeon_list = dungeon_list
        self.type_list = type_list
        self.existing_monsters = existing_monsters
        self.on_clone_callback = on_clone_callback

        self.error_labels: Dict[str, tk.Label] = {}
        self._setup_ui()
        self.populate(monster_data)

    def _setup_ui(self) -> None:
        # Group Frame
        group = tk.LabelFrame(
            self,
            text="📌 Thông Tin Cơ Bản (Bắt buộc)",
            font=UI.FONT_SECTION,
            fg=UI.COLOR_PRIMARY_TEXT,
            bg=UI.BG_DEFAULT,
            padx=12,
            pady=8,
        )
        group.pack(fill="x", expand=True, padx=5, pady=5)
        group.columnconfigure(1, weight=1)

        row = 0

        # Clone Feature row (only in Add or always available to copy stats)
        if self.existing_monsters:
            create_icon_label(
                group,
                icon_name="copy",
                text="Sao chép từ:",
                icon_fallback="📋",
                font=UI.FONT_LABEL,
            ).grid(row=row, column=0, sticky="w", pady=4)

            clone_frame = tk.Frame(group, bg=UI.BG_DEFAULT)
            clone_frame.grid(row=row, column=1, sticky="ew", pady=4, padx=(10, 0))

            clone_names = ["-- Chọn quái vật để sao chép --"] + [
                f"{m.get('name', '')} (ID: {m.get('id', '')})"
                for m in self.existing_monsters
            ]
            self.clone_combo = ttk.Combobox(
                clone_frame, values=clone_names, state="readonly", font=UI.FONT_TEXT
            )
            self.clone_combo.current(0)
            self.clone_combo.pack(side="left", fill="x", expand=True)

            btn_clone = create_icon_button(
                clone_frame,
                icon_name="copy",
                text="Clone",
                command=self._on_clone_selected,
                button_type="blue",
            )
            btn_clone.pack(side="left", padx=(5, 0))
            row += 1

        # 1. ID
        create_icon_label(
            group,
            icon_name="key",
            text="Monster ID (*):",
            icon_fallback="🔑",
            font=UI.FONT_LABEL,
        ).grid(row=row, column=0, sticky="w", pady=4)

        id_frame = tk.Frame(group, bg=UI.BG_DEFAULT)
        id_frame.grid(row=row, column=1, sticky="ew", pady=4, padx=(10, 0))

        self.id_entry = tk.Entry(id_frame, font=UI.FONT_TEXT)
        self.id_entry.pack(side="left", fill="x", expand=True)

        if not self.is_new:
            self.id_entry.config(state="disabled")
        else:
            btn_gen = create_icon_button(
                id_frame,
                icon_name="refresh",
                text="Tạo ID",
                command=self._generate_id,
                button_type="refresh",
            )
            btn_gen.pack(side="left", padx=(5, 0))

        self._add_error_label(group, "id", row + 1, 1)
        row += 2

        # 2. Name
        create_icon_label(
            group,
            icon_name="monster",
            text="Tên quái vật (*):",
            icon_fallback="👹",
            font=UI.FONT_LABEL,
        ).grid(row=row, column=0, sticky="w", pady=4)

        self.name_entry = tk.Entry(group, font=UI.FONT_TEXT)
        self.name_entry.grid(row=row, column=1, sticky="ew", pady=4, padx=(10, 0))
        self._add_error_label(group, "name", row + 1, 1)
        row += 2

        # 3. Level & HP (placed side by side)
        lh_frame = tk.Frame(group, bg=UI.BG_DEFAULT)
        lh_frame.grid(row=row, column=0, columnspan=2, sticky="ew", pady=4)

        create_icon_label(
            lh_frame,
            icon_name="up",
            text="Cấp độ (*):",
            icon_fallback="↑",
            font=UI.FONT_LABEL,
        ).pack(side="left")

        self.level_spin = tk.Spinbox(lh_frame, from_=0, to=999, font=UI.FONT_TEXT, width=8)
        self.level_spin.pack(side="left", padx=(5, 20))

        create_icon_label(
            lh_frame,
            icon_name="hp",
            text="HP (*):",
            icon_fallback="❤️",
            font=UI.FONT_LABEL,
        ).pack(side="left")

        self.hp_entry = tk.Entry(lh_frame, font=UI.FONT_TEXT, width=12)
        self.hp_entry.pack(side="left", padx=(5, 0))

        row += 1
        self._add_error_label(group, "level", row, 1)
        self._add_error_label(group, "hp", row, 1)
        row += 1

        # 4. Dungeon ID (FK)
        create_icon_label(
            group,
            icon_name="location",
            text="Dungeon/Map (*):",
            icon_fallback="🏰",
            font=UI.FONT_LABEL,
        ).grid(row=row, column=0, sticky="w", pady=4)

        dungeon_display_values = ["(None / Unassigned)"] + [
            f"{d['id']} - {d['name']}" for d in self.dungeon_list
        ]
        self.dungeon_combo = ttk.Combobox(
            group, values=dungeon_display_values, state="readonly", font=UI.FONT_TEXT
        )
        self.dungeon_combo.grid(row=row, column=1, sticky="ew", pady=4, padx=(10, 0))
        self.dungeon_combo.current(0)
        row += 1

        # 5. Server Boss Type (FK)
        create_icon_label(
            group,
            icon_name="boss",
            text="Monster Type (*):",
            icon_fallback="👾",
            font=UI.FONT_LABEL,
        ).grid(row=row, column=0, sticky="w", pady=4)

        type_display_values = ["(None / Unassigned)"] + [
            f"{t['value']} - {t['label']}" for t in self.type_list
        ]
        self.type_combo = ttk.Combobox(
            group, values=type_display_values, state="readonly", font=UI.FONT_TEXT
        )
        self.type_combo.grid(row=row, column=1, sticky="ew", pady=4, padx=(10, 0))
        self.type_combo.current(0)
        row += 1

    def _add_error_label(self, parent: tk.Widget, field: str, r: int, c: int) -> None:
        err_lbl = tk.Label(parent, text="", fg="red", font=UI.FONT_SMALL, bg=UI.BG_DEFAULT)
        err_lbl.grid(row=r, column=c, sticky="w")
        err_lbl.grid_remove()
        self.error_labels[field] = err_lbl

    def _generate_id(self) -> None:
        new_id = f"m_{int(uuid.uuid4().hex[:8], 16)}"
        self.id_entry.delete(0, tk.END)
        self.id_entry.insert(0, new_id)

    def _on_clone_selected(self) -> None:
        idx = self.clone_combo.current()
        if idx > 0 and self.existing_monsters and idx - 1 < len(self.existing_monsters):
            selected = self.existing_monsters[idx - 1]
            if self.on_clone_callback:
                self.on_clone_callback(selected)

    def populate(self, data: Dict[str, Any]) -> None:
        # ID
        self.id_entry.config(state="normal")
        self.id_entry.delete(0, tk.END)
        self.id_entry.insert(0, str(data.get("id", "")))
        if not self.is_new:
            self.id_entry.config(state="disabled")

        # Name
        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, str(data.get("name", "")))

        # Level
        self.level_spin.delete(0, tk.END)
        self.level_spin.insert(0, str(data.get("level", 1)))

        # HP
        self.hp_entry.delete(0, tk.END)
        self.hp_entry.insert(0, str(data.get("hp", 100)))

        # Dungeon Combo
        curr_d = str(data.get("dungeonId", "") or "").strip()
        matched = False
        for i, d in enumerate(self.dungeon_list):
            if d["id"] == curr_d or f"{d['id']} - {d['name']}" == curr_d:
                self.dungeon_combo.current(i + 1)
                matched = True
                break
        if not matched:
            self.dungeon_combo.current(0)

        # Type Combo
        curr_t = str(data.get("serverBossType", "") or "").strip()
        matched_t = False
        for i, t in enumerate(self.type_list):
            if t["value"] == curr_t or f"{t['value']} - {t['label']}" == curr_t:
                self.type_combo.current(i + 1)
                matched_t = True
                break
        if not matched_t:
            self.type_combo.current(0)

    def get_data(self) -> Dict[str, Any]:
        dungeon_idx = self.dungeon_combo.current()
        d_val = self.dungeon_list[dungeon_idx - 1]["id"] if dungeon_idx > 0 else None

        type_idx = self.type_combo.current()
        t_val = self.type_list[type_idx - 1]["value"] if type_idx > 0 else None

        return {
            "id": self.id_entry.get().strip(),
            "name": self.name_entry.get().strip(),
            "level": self.level_spin.get().strip(),
            "hp": self.hp_entry.get().strip(),
            "dungeonId": d_val,
            "serverBossType": t_val,
        }

    def show_errors(self, errors: Dict[str, str]) -> None:
        for field, lbl in self.error_labels.items():
            if field in errors:
                lbl.config(text=errors[field])
                lbl.grid()
            else:
                lbl.grid_remove()
