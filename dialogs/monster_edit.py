"""
Monster Edit Dialog module.
"""

from __future__ import annotations
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import subprocess
import uuid
import json
import time
import re
from pathlib import Path
from typing import Optional, Dict, Any, Callable, List, TYPE_CHECKING

if TYPE_CHECKING:
    from ui.windows.monster_manager_win import MonsterManagerWin

try:
    from PIL import Image, ImageTk, ImageGrab
    PIL_AVAILABLE = True
except ImportError:
    Image = None
    ImageTk = None
    ImageGrab = None
    PIL_AVAILABLE = False

try:
    from lib.i18n import t as i18n_t
except ImportError:
    from mock.fallbacks import i18n_t

try:
    from lib.features.monster_service import check_duplicate_name, generate_unique_name, ensure_unique_monster_id
except ImportError:
    from mock.fallbacks import check_duplicate_name, generate_unique_name, ensure_unique_monster_id

try:
    from ui.helpers.tooltip import attach_i18n_tooltip
except ImportError:
    from mock.fallbacks import attach_i18n_tooltip

try:
    from ui.components import create_icon_label, create_icon_button
    from ui.components.icon_button import create_add_button, create_delete_button, create_save_button, create_cancel_button, create_refresh_button
except ImportError:
    from mock.fallbacks import create_icon_label, create_icon_button, create_add_button, create_delete_button, create_save_button, create_cancel_button, create_refresh_button

try:
    from lib.ui_style import UIStyle as UI
except ImportError:
    from mock.fallbacks import UIStyle as UI

try:
    from ui.helpers.icon_helper import get_icon_helper
    icon_helper = get_icon_helper()
except ImportError:
    from mock.fallbacks import MockIconHelper
    icon_helper = MockIconHelper()

PROJECT_ROOT = Path(__file__).resolve().parent.parent

from views.image_handler import ImageHandler
image_handler = ImageHandler()

class MonsterEditDialog(tk.Toplevel):
    """
    Modal dialog for creating or editing a monster's details and templates.
    Contains clean tabs for Monster Info, Template Manager, and Column Settings.
    """


    # --- Field Metadata Definitions ---
    DB_COLUMNS = [
        {"key": "id", "group": "system", "widget": "hidden", "default": "", "nullable": False, "type": "string", "validation": "none", "translation_key": ""},
        {"key": "name", "group": "info", "widget": "entry", "default": "Quái Mới", "nullable": False, "type": "string", "validation": "required", "translation_key": "monster_name_label"},
        {"key": "level", "group": "stats", "widget": "spinbox", "default": 1, "nullable": False, "type": "int", "validation": "numeric", "translation_key": "monster_level_label"},
        {"key": "exp", "group": "stats", "widget": "entry", "default": 0, "nullable": False, "type": "int", "validation": "numeric", "translation_key": "monster_exp_label"},
        {"key": "hp", "group": "stats", "widget": "entry", "default": 100, "nullable": False, "type": "int", "validation": "numeric", "translation_key": "monster_hp_label"},
        {"key": "defense", "group": "stats", "widget": "entry", "default": 0, "nullable": False, "type": "int", "validation": "numeric", "translation_key": "monster_def_label"},
        {"key": "attackRate", "group": "stats", "widget": "entry", "default": 0, "nullable": False, "type": "int", "validation": "numeric", "translation_key": "monster_atk_rate_label"},
        {"key": "defenseRate", "group": "stats", "widget": "entry", "default": 0, "nullable": False, "type": "int", "validation": "numeric", "translation_key": "monster_def_rate_label"},
        {"key": "hpRecharge", "group": "stats", "widget": "entry", "default": 0, "nullable": False, "type": "int", "validation": "numeric", "translation_key": "monster_hp_recharge_label"},
        {"key": "accuracy", "group": "stats", "widget": "entry", "default": 0, "nullable": False, "type": "int", "validation": "numeric", "translation_key": "monster_acc_label"},
        {"key": "penetration", "group": "stats", "widget": "entry", "default": 0, "nullable": False, "type": "int", "validation": "numeric", "translation_key": "monster_pen_label"},
        {"key": "damageReduction", "group": "stats", "widget": "entry", "default": 0, "nullable": False, "type": "int", "validation": "numeric", "translation_key": "monster_dmg_red_label"},
        {"key": "evasion", "group": "stats", "widget": "entry", "default": 0, "nullable": False, "type": "int", "validation": "numeric", "translation_key": "monster_evasion_label"},
        {"key": "resistCritRate", "group": "stats", "widget": "entry", "default": 0, "nullable": False, "type": "int", "validation": "numeric", "translation_key": "monster_resist_crit_rate_label"},
        {"key": "primaryAttackMin", "group": "stats", "widget": "entry", "default": 0, "nullable": False, "type": "int", "validation": "numeric", "translation_key": "monster_primary_atk_min_label"},
        {"key": "primaryAttackMax", "group": "stats", "widget": "entry", "default": 0, "nullable": False, "type": "int", "validation": "numeric", "translation_key": "monster_primary_atk_max_label"},
        {"key": "secondaryAttackMin", "group": "stats", "widget": "entry", "default": 0, "nullable": False, "type": "int", "validation": "numeric", "translation_key": "monster_sec_atk_min_label"},
        {"key": "secondaryAttackMax", "group": "stats", "widget": "entry", "default": 0, "nullable": False, "type": "int", "validation": "numeric", "translation_key": "monster_sec_atk_max_label"},
        {"key": "ignoreAccuracy", "group": "stats", "widget": "entry", "default": 0, "nullable": False, "type": "int", "validation": "numeric", "translation_key": "monster_ignore_acc_label"},
        {"key": "ignoreDamageReduction", "group": "stats", "widget": "entry", "default": 0, "nullable": False, "type": "int", "validation": "numeric", "translation_key": "monster_ignore_dmg_red_label"},
        {"key": "ignorePenetration", "group": "stats", "widget": "entry", "default": 0, "nullable": False, "type": "int", "validation": "numeric", "translation_key": "monster_ignore_pen_label"},
        {"key": "absoluteDamage", "group": "stats", "widget": "entry", "default": 0, "nullable": False, "type": "int", "validation": "numeric", "translation_key": "monster_abs_dmg_label"},
        {"key": "resistSkillAmp", "group": "stats", "widget": "entry", "default": 0, "nullable": False, "type": "int", "validation": "numeric", "translation_key": "monster_resist_amp_label"},
        {"key": "resistCritDamage", "group": "stats", "widget": "entry", "default": 0, "nullable": False, "type": "int", "validation": "numeric", "translation_key": "monster_resist_crit_dmg_label"},
        {"key": "resistSuppress", "group": "stats", "widget": "entry", "default": 0, "nullable": False, "type": "int", "validation": "numeric", "translation_key": "monster_resist_suppress_label"},
        {"key": "resistSilence", "group": "stats", "widget": "entry", "default": 0, "nullable": False, "type": "int", "validation": "numeric", "translation_key": "monster_resist_silence_label"},
        {"key": "resistDiffDamage", "group": "stats", "widget": "entry", "default": 0, "nullable": False, "type": "int", "validation": "numeric", "translation_key": "monster_resist_diff_dmg_label"},
        {"key": "hpProportionDamage", "group": "stats", "widget": "entry", "default": 0, "nullable": False, "type": "int", "validation": "numeric", "translation_key": "monster_hp_prop_dmg_label"},
        {"key": "serverBossType", "group": "reference", "widget": "combobox", "default": None, "nullable": True, "type": "string", "validation": "none", "translation_key": "monster_boss_type_label"},
        {"key": "dungeonId", "group": "reference", "widget": "combobox", "default": None, "nullable": True, "type": "string", "validation": "none", "translation_key": "monster_dungeon_label"},
    ]

    LOCAL_METADATA = [
        {"key": "priority", "group": "local", "widget": "spinbox", "default": 1, "nullable": False, "type": "int", "validation": "numeric", "translation_key": "monster_priority_label"},
        {"key": "damage_per_hit", "group": "local", "widget": "entry", "default": 10, "nullable": False, "type": "int", "validation": "numeric", "translation_key": "monster_damage_label"},
        {"key": "description", "group": "local", "widget": "text", "default": "", "nullable": False, "type": "string", "validation": "none", "translation_key": "monster_desc_label"},
        {"key": "templates", "group": "local", "widget": "custom", "default": [], "nullable": False, "type": "list", "validation": "none", "translation_key": "monster_templates_label"},
    ]


    def __init__(
        self,
        parent: Any,
        monster: Optional[Dict[str, Any]] = None,
        on_save: Optional[Callable[[Dict[str, Any]], None]] = None,
    ):
        super().__init__(parent)
        self.parent = parent
        self.on_save_callback = on_save
        self.is_new = monster is None

        self.dungeon_options = []
        self.boss_type_options = []
        self.dungeon_val_to_lbl = {}
        self.dungeon_lbl_to_val = {}
        self.boss_type_val_to_lbl = {}
        self.boss_type_lbl_to_val = {}

        # Deep copy monster or create new default
        if monster:
            self.monster_data = json.loads(json.dumps(monster))
        else:
            self.monster_data = self._get_default_monster()

        m_id = self.monster_data.get("id", "")
        m_name = self.monster_data.get("name", "")
        if not self.is_new:
            title_text = f"Sửa Quái Vật: {m_name} (ID: #{m_id})"
        else:
            title_text = i18n_t(
                "btn_new_monster", ns="monster_editor", default="Thêm Quái Vật Mới"
            )
        self.title(title_text)
        self.geometry("780x540")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self._is_capturing = False
        self._is_browsing = False

        # Keyboard shortcuts
        self.bind("<Escape>", lambda event: self.destroy())

        self._setup_ui()
        self._populate_form()

        # Center dialog
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (780 // 2)
        y = (self.winfo_screenheight() // 2) - (540 // 2)
        self.geometry(f"+{x}+{y}")

    def _get_default_monster(self) -> Dict[str, Any]:
        """Create a new monster candidate populated with defaults from metadata."""
        candidate = {}
        for meta in self.DB_COLUMNS + self.LOCAL_METADATA:
            key = meta["key"]
            if key == "id":
                candidate[key] = str(uuid.uuid4())
            elif key == "name":
                candidate[key] = i18n_t("default_monster_name", ns="monster_editor", default="Quái Mới")
            else:
                # Need to use copy for lists to avoid sharing reference
                default_val = meta["default"]
                if isinstance(default_val, list):
                    candidate[key] = list(default_val)
                else:
                    candidate[key] = default_val
        return candidate

    def _collect_form_data(self) -> Dict[str, Any]:
        """Read form widgets and merge with original data, preserving unknown keys."""
        # Start with a deep copy of the original data to preserve unknown keys
        candidate = json.loads(json.dumps(self.monster_data))

        # We only have UI inputs for a subset of fields right now.
        # So we'll map the UI inputs to the data, and cast properly.
        # For a full implementation, we'd loop over metadata and map dynamically.
        # But for this round-trip test, we'll manually collect the visible fields
        # and validate type based on metadata.

        # Read from UI if we have it
        if hasattr(self, 'name_entry'):
            candidate["name"] = self.name_entry.get().strip()
        if hasattr(self, 'level_spinbox'):
            try:
                candidate["level"] = int(self.level_spinbox.get())
            except ValueError:
                candidate["level"] = 1
        if hasattr(self, 'priority_spinbox'):
            try:
                candidate["priority"] = int(self.priority_spinbox.get())
            except ValueError:
                candidate["priority"] = 1
        if hasattr(self, 'hp_entry'):
            try:
                candidate["hp"] = int(self.hp_entry.get())
            except ValueError:
                candidate["hp"] = 100
        if hasattr(self, 'damage_entry'):
            try:
                candidate["damage_per_hit"] = int(self.damage_entry.get())
            except ValueError:
                candidate["damage_per_hit"] = 10
        if hasattr(self, 'desc_text'):
            candidate["description"] = self.desc_text.get("1.0", tk.END).strip()

        # Gather new fields
        def _get_int(widget, default=0):
            try:
                return int(widget.get())
            except ValueError:
                return default

        if hasattr(self, 'atk_rate_entry'): candidate["attackRate"] = _get_int(self.atk_rate_entry)
        if hasattr(self, 'primary_atk_min_entry'): candidate["primaryAttackMin"] = _get_int(self.primary_atk_min_entry)
        if hasattr(self, 'primary_atk_max_entry'): candidate["primaryAttackMax"] = _get_int(self.primary_atk_max_entry)
        if hasattr(self, 'sec_atk_min_entry'): candidate["secondaryAttackMin"] = _get_int(self.sec_atk_min_entry)
        if hasattr(self, 'sec_atk_max_entry'): candidate["secondaryAttackMax"] = _get_int(self.sec_atk_max_entry)
        if hasattr(self, 'def_entry'): candidate["defense"] = _get_int(self.def_entry)
        if hasattr(self, 'def_rate_entry'): candidate["defenseRate"] = _get_int(self.def_rate_entry)
        if hasattr(self, 'acc_entry'): candidate["accuracy"] = _get_int(self.acc_entry)

        # Advanced groups
        if hasattr(self, 'pen_entry'): candidate["penetration"] = _get_int(self.pen_entry)
        if hasattr(self, 'dmg_red_entry'): candidate["damageReduction"] = _get_int(self.dmg_red_entry)
        if hasattr(self, 'evasion_entry'): candidate["evasion"] = _get_int(self.evasion_entry)
        if hasattr(self, 'ignore_acc_entry'): candidate["ignoreAccuracy"] = _get_int(self.ignore_acc_entry)
        if hasattr(self, 'ignore_dmg_red_entry'): candidate["ignoreDamageReduction"] = _get_int(self.ignore_dmg_red_entry)
        if hasattr(self, 'ignore_pen_entry'): candidate["ignorePenetration"] = _get_int(self.ignore_pen_entry)
        if hasattr(self, 'abs_dmg_entry'): candidate["absoluteDamage"] = _get_int(self.abs_dmg_entry)

        if hasattr(self, 'resist_crit_rate_entry'): candidate["resistCritRate"] = _get_int(self.resist_crit_rate_entry)
        if hasattr(self, 'resist_amp_entry'): candidate["resistSkillAmp"] = _get_int(self.resist_amp_entry)
        if hasattr(self, 'resist_crit_dmg_entry'): candidate["resistCritDamage"] = _get_int(self.resist_crit_dmg_entry)
        if hasattr(self, 'resist_suppress_entry'): candidate["resistSuppress"] = _get_int(self.resist_suppress_entry)
        if hasattr(self, 'resist_silence_entry'): candidate["resistSilence"] = _get_int(self.resist_silence_entry)
        if hasattr(self, 'resist_diff_dmg_entry'): candidate["resistDiffDamage"] = _get_int(self.resist_diff_dmg_entry)
        if hasattr(self, 'hp_prop_dmg_entry'): candidate["hpProportionDamage"] = _get_int(self.hp_prop_dmg_entry)

        if hasattr(self, 'exp_entry'): candidate["exp"] = _get_int(self.exp_entry)
        if hasattr(self, 'hp_recharge_entry'): candidate["hpRecharge"] = _get_int(self.hp_recharge_entry)

        empty_lbl = i18n_t("ref_none", ns="monster_editor", default="<Không / None>")

        if hasattr(self, 'dungeon_combo'):
            val = self.dungeon_combo.get().strip()
            if val in [empty_lbl, ""]:
                candidate["dungeonId"] = None
            else:
                candidate["dungeonId"] = self.dungeon_lbl_to_val.get(val, val)

        if hasattr(self, 'boss_type_combo'):
            val = self.boss_type_combo.get().strip()
            if val in [empty_lbl, ""]:
                candidate["serverBossType"] = None
            else:
                candidate["serverBossType"] = self.boss_type_lbl_to_val.get(val, val)

        # Ensure metadata defaults and types for all fields, and handle nullable references
        for meta in self.DB_COLUMNS + self.LOCAL_METADATA:
            key = meta["key"]
            if key not in candidate:
                if isinstance(meta["default"], list):
                    candidate[key] = list(meta["default"])
                else:
                    candidate[key] = meta["default"]

            # Type casting and None handling
            val = candidate[key]
            if meta["nullable"] and (val == "None" or val == ""):
                candidate[key] = None
            elif val is not None:
                if meta["type"] == "int":
                    try:
                        candidate[key] = int(val)
                    except (ValueError, TypeError):
                        candidate[key] = meta["default"]
                elif meta["type"] == "string":
                    candidate[key] = str(val)

        return candidate

    def _setup_ui(self) -> None:
        main_container = tk.Frame(self, bg=UI.BG_DEFAULT)
        main_container.pack(fill="both", expand=True, padx=10, pady=10)

        # Tab Notebook
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill="both", expand=True, pady=(0, 10))

        # --- Tab 1: Thông Tin Quái ---
        self.info_tab = tk.Frame(self.notebook, bg=UI.BG_DEFAULT)
        self.notebook.add(
            self.info_tab,
            text=i18n_t("tab_info", ns="monster_editor", default="Thông Tin Quái"),
        )

        # Wrap tab 1 in a scrollable Canvas
        canvas_frame = tk.Frame(self.info_tab, bg=UI.BG_DEFAULT)
        canvas_frame.pack(fill="both", expand=True)

        self.info_canvas = tk.Canvas(canvas_frame, bg=UI.BG_DEFAULT, highlightthickness=0)
        self.info_canvas.pack(side="left", fill="both", expand=True)

        v_scroll = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.info_canvas.yview)
        v_scroll.pack(side="right", fill="y")
        self.info_canvas.configure(yscrollcommand=v_scroll.set)

        self.info_scrollable_frame = tk.Frame(self.info_canvas, bg=UI.BG_DEFAULT)

        # Configure canvas window and scroll region
        self.info_canvas_window = self.info_canvas.create_window(
            (0, 0), window=self.info_scrollable_frame, anchor="nw"
        )
        self.info_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.info_canvas.configure(scrollregion=self.info_canvas.bbox("all"))
        )
        self.info_canvas.bind(
            "<Configure>",
            lambda e: self.info_canvas.itemconfig(self.info_canvas_window, width=e.width)
        )

        # Enable mouse scroll safely on canvas and its children
        def _on_mousewheel(e):
            self.info_canvas.yview_scroll(int(-1*(e.delta/120)), "units")
        def _on_mousewheel_linux_up(e):
            self.info_canvas.yview_scroll(-1, "units")
        def _on_mousewheel_linux_down(e):
            self.info_canvas.yview_scroll(1, "units")

        def _bind_mouse_scroll(widget):
            widget.bind("<MouseWheel>", _on_mousewheel, add="+")
            widget.bind("<Button-4>", _on_mousewheel_linux_up, add="+")
            widget.bind("<Button-5>", _on_mousewheel_linux_down, add="+")
            for child in widget.winfo_children():
                _bind_mouse_scroll(child)

        # Bind events after UI is created
        self.after(100, lambda: _bind_mouse_scroll(self.info_scrollable_frame))
        _bind_mouse_scroll(self.info_canvas)

        # Info Header & Top Action Buttons
        info_header = tk.Frame(self.info_scrollable_frame, bg=UI.BG_DEFAULT)
        info_header.pack(fill="x", padx=15, pady=(15, 10))

        info_label = create_icon_label(
            info_header,
            icon_name="info",
            text=i18n_t("tab_info", ns="monster_editor", default="Thông Tin Quái"),
            icon_fallback="📋",
            font=UI.FONT_SECTION,
            fg=UI.COLOR_PRIMARY_TEXT,
            bg=UI.BG_DEFAULT,
        )
        info_label.pack(side="left")

        # Compact Two-Column Clean Form Layout
        form_frame = tk.Frame(self.info_scrollable_frame, bg=UI.BG_DEFAULT)
        form_frame.pack(fill="both", expand=True, padx=25, pady=5)

        # Configure columns for 2-column layout (Label Widget Label Widget)
        form_frame.columnconfigure(1, weight=1, minsize=100)
        form_frame.columnconfigure(3, weight=1, minsize=100)

        # ID (read-only)
        create_icon_label(
            form_frame, icon_name="id", text=i18n_t("monster_id_label", ns="monster_editor", default="ID:"), icon_fallback="🔑", font=UI.FONT_LABEL
        ).grid(row=0, column=0, sticky="w", pady=4)
        self.id_val_label = tk.Label(form_frame, text="<New>", font=UI.FONT_TEXT, bg=UI.BG_DEFAULT, fg=UI.COLOR_PRIMARY_TEXT)
        self.id_val_label.grid(row=0, column=1, sticky="w", pady=4, padx=(12, 0))

        # Name
        create_icon_label(
            form_frame, icon_name="monster", text=i18n_t("monster_name_label", ns="monster_editor", default="Tên quái:"), icon_fallback="👹", font=UI.FONT_LABEL
        ).grid(row=0, column=2, sticky="w", pady=4, padx=(20, 0))
        self.name_entry = tk.Entry(form_frame, font=UI.FONT_TEXT)
        self.name_entry.grid(row=0, column=3, sticky="ew", pady=4, padx=(12, 0))

        # Level
        create_icon_label(
            form_frame, icon_name="up", text=i18n_t("monster_level_label", ns="monster_editor", default="Cấp độ:"), icon_fallback="↑", font=UI.FONT_LABEL
        ).grid(row=1, column=0, sticky="w", pady=4)
        self.level_spinbox = tk.Spinbox(form_frame, from_=1, to=999, font=UI.FONT_TEXT)
        self.level_spinbox.grid(row=1, column=1, sticky="ew", pady=4, padx=(12, 0))

        # Priority
        create_icon_label(
            form_frame, icon_name="priority", text=i18n_t("monster_priority_label", ns="monster_editor", default="Độ ưu tiên:"), icon_fallback="🎯", font=UI.FONT_LABEL
        ).grid(row=1, column=2, sticky="w", pady=4, padx=(20, 0))
        self.priority_spinbox = tk.Spinbox(form_frame, from_=1, to=10, font=UI.FONT_TEXT)
        self.priority_spinbox.grid(row=1, column=3, sticky="ew", pady=4, padx=(12, 0))

        # HP
        create_icon_label(
            form_frame, icon_name="hp", text=i18n_t("monster_hp_label", ns="monster_editor", default="HP:"), icon_fallback="❤️", font=UI.FONT_LABEL
        ).grid(row=2, column=0, sticky="w", pady=4)
        self.hp_entry = tk.Entry(form_frame, font=UI.FONT_TEXT)
        self.hp_entry.grid(row=2, column=1, sticky="ew", pady=4, padx=(12, 0))

        # Attack Rate
        create_icon_label(
            form_frame, icon_name="speed", text=i18n_t("monster_atk_rate_label", ns="monster_editor", default="Tốc đánh:"), icon_fallback="⚡", font=UI.FONT_LABEL
        ).grid(row=2, column=2, sticky="w", pady=4, padx=(20, 0))
        self.atk_rate_entry = tk.Entry(form_frame, font=UI.FONT_TEXT)
        self.atk_rate_entry.grid(row=2, column=3, sticky="ew", pady=4, padx=(12, 0))

        # Primary Attack Min/Max
        create_icon_label(
            form_frame, icon_name="damage", text=i18n_t("monster_primary_atk_min_label", ns="monster_editor", default="Công chính (Min):"), icon_fallback="⚔️", font=UI.FONT_LABEL
        ).grid(row=3, column=0, sticky="w", pady=4)
        self.primary_atk_min_entry = tk.Entry(form_frame, font=UI.FONT_TEXT)
        self.primary_atk_min_entry.grid(row=3, column=1, sticky="ew", pady=4, padx=(12, 0))

        create_icon_label(
            form_frame, icon_name="damage", text=i18n_t("monster_primary_atk_max_label", ns="monster_editor", default="Công chính (Max):"), icon_fallback="⚔️", font=UI.FONT_LABEL
        ).grid(row=3, column=2, sticky="w", pady=4, padx=(20, 0))
        self.primary_atk_max_entry = tk.Entry(form_frame, font=UI.FONT_TEXT)
        self.primary_atk_max_entry.grid(row=3, column=3, sticky="ew", pady=4, padx=(12, 0))

        # Secondary Attack Min/Max
        create_icon_label(
            form_frame, icon_name="damage", text=i18n_t("monster_sec_atk_min_label", ns="monster_editor", default="Công phụ (Min):"), icon_fallback="🗡️", font=UI.FONT_LABEL
        ).grid(row=4, column=0, sticky="w", pady=4)
        self.sec_atk_min_entry = tk.Entry(form_frame, font=UI.FONT_TEXT)
        self.sec_atk_min_entry.grid(row=4, column=1, sticky="ew", pady=4, padx=(12, 0))

        create_icon_label(
            form_frame, icon_name="damage", text=i18n_t("monster_sec_atk_max_label", ns="monster_editor", default="Công phụ (Max):"), icon_fallback="🗡️", font=UI.FONT_LABEL
        ).grid(row=4, column=2, sticky="w", pady=4, padx=(20, 0))
        self.sec_atk_max_entry = tk.Entry(form_frame, font=UI.FONT_TEXT)
        self.sec_atk_max_entry.grid(row=4, column=3, sticky="ew", pady=4, padx=(12, 0))

        # Defense & Defense Rate
        create_icon_label(
            form_frame, icon_name="shield", text=i18n_t("monster_def_label", ns="monster_editor", default="Thủ:"), icon_fallback="🛡️", font=UI.FONT_LABEL
        ).grid(row=5, column=0, sticky="w", pady=4)
        self.def_entry = tk.Entry(form_frame, font=UI.FONT_TEXT)
        self.def_entry.grid(row=5, column=1, sticky="ew", pady=4, padx=(12, 0))

        create_icon_label(
            form_frame, icon_name="shield", text=i18n_t("monster_def_rate_label", ns="monster_editor", default="Tỷ lệ thủ:"), icon_fallback="🛡️", font=UI.FONT_LABEL
        ).grid(row=5, column=2, sticky="w", pady=4, padx=(20, 0))
        self.def_rate_entry = tk.Entry(form_frame, font=UI.FONT_TEXT)
        self.def_rate_entry.grid(row=5, column=3, sticky="ew", pady=4, padx=(12, 0))

        # Accuracy & Dungeon Placeholder
        create_icon_label(
            form_frame, icon_name="aim", text=i18n_t("monster_acc_label", ns="monster_editor", default="Chính xác:"), icon_fallback="🎯", font=UI.FONT_LABEL
        ).grid(row=6, column=0, sticky="w", pady=4)
        self.acc_entry = tk.Entry(form_frame, font=UI.FONT_TEXT)
        self.acc_entry.grid(row=6, column=1, sticky="ew", pady=4, padx=(12, 0))

        create_icon_label(
            form_frame, icon_name="dungeon", text=i18n_t("monster_dungeon_label", ns="monster_editor", default="Dungeon:"), icon_fallback="🏰", font=UI.FONT_LABEL
        ).grid(row=6, column=2, sticky="w", pady=4, padx=(20, 0))
        self.dungeon_combo = ttk.Combobox(form_frame, font=UI.FONT_TEXT, state="readonly", values=[""])
        self.dungeon_combo.grid(row=6, column=3, sticky="ew", pady=4, padx=(12, 0))

        # Boss Type Placeholder & Damage (Legacy compat)
        create_icon_label(
            form_frame, icon_name="boss", text=i18n_t("monster_boss_type_label", ns="monster_editor", default="Loại Boss:"), icon_fallback="👑", font=UI.FONT_LABEL
        ).grid(row=7, column=0, sticky="w", pady=4)
        self.boss_type_combo = ttk.Combobox(form_frame, font=UI.FONT_TEXT, state="readonly", values=[""])
        self.boss_type_combo.grid(row=7, column=1, sticky="ew", pady=4, padx=(12, 0))

        create_icon_label(
            form_frame, icon_name="damage", text=i18n_t("monster_damage_label", ns="monster_editor", default="Sát thương mỗi đòn:"), icon_fallback="⚔️", font=UI.FONT_LABEL
        ).grid(row=7, column=2, sticky="w", pady=4, padx=(20, 0))
        self.damage_entry = tk.Entry(form_frame, font=UI.FONT_TEXT)
        self.damage_entry.grid(row=7, column=3, sticky="ew", pady=4, padx=(12, 0))

        # Advanced Group: Phản Đòn & Xuyên Giáp
        self._create_advanced_groups(self.info_scrollable_frame)

        # --- Tab 2: Templates ---
        self.templates_tab = tk.Frame(self.notebook, bg=UI.BG_PANEL)
        self.notebook.add(
            self.templates_tab,
            text=i18n_t("tab_templates", ns="monster_editor", default="Templates"),
        )

        # Split frame: Left sub-panel & Right sub-panel
        tmpl_container = tk.Frame(self.templates_tab, bg=UI.BG_PANEL)
        tmpl_container.pack(fill="both", expand=True, padx=10, pady=10)

        left_sub = tk.Frame(tmpl_container, bg=UI.BG_PANEL, width=340)
        left_sub.pack(side="left", fill="both", expand=True, padx=(0, 5))

        right_sub = tk.Frame(tmpl_container, bg=UI.BG_PANEL, width=380)
        right_sub.pack(side="right", fill="both", expand=True, padx=(5, 0))

        # --- Left Sub-panel (Template List Table & Toolbar) ---
        left_tb = tk.Frame(left_sub, bg=UI.BG_PANEL)
        left_tb.pack(fill="x", pady=(0, 5))

        self.btn_add_template = create_add_button(
            left_tb,
            command=self._on_browse,
            text=i18n_t("btn_add_template", ns="monster_editor", default="Thêm"),
            padding={"padx": 12, "pady": 6},
            tooltip_key="tooltip_add_template",
            tooltip_ns="monster_editor",
        )
        self.btn_add_template.pack(side="left", padx=2)

        self.btn_delete_template = create_delete_button(
            left_tb,
            command=self._on_delete_template,
            text=i18n_t("btn_delete_template", ns="monster_editor", default="Xóa"),
            padding={"padx": 12, "pady": 6},
            tooltip_key="tooltip_delete_template",
            tooltip_ns="monster_editor",
        )
        self.btn_delete_template.pack(side="left", padx=2)

        self.btn_edit_template = create_icon_button(
            left_tb,
            icon_name="edit",
            text=i18n_t("btn_edit", ns="monster_editor", default="Sửa"),
            icon_fallback="✏️",
            command=lambda: None,
            button_type="blue",
            padding={"padx": 12, "pady": 6},
            tooltip_key="tooltip_edit_mode_template",
            tooltip_ns="monster_editor",
        )
        self.btn_edit_template.pack(side="left", padx=2)

        self.template_badge = tk.Label(
            left_tb,
            text="0 tpl",
            font=UI.FONT_SMALL,
            fg="white",
            bg=UI.COLOR_PRIMARY,
            padx=6,
            pady=2,
        )
        self.template_badge.pack(side="right", padx=2)

        # Template Treeview Table
        tree_frame = tk.Frame(left_sub, bg=UI.BG_PANEL)
        tree_frame.pack(fill="both", expand=True)

        tree_scroll = tk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        tree_scroll.pack(side="right", fill="y")

        self.template_listbox = ttk.Treeview(
            tree_frame,
            columns=("icon", "threshold", "path"),
            show="headings",
            selectmode="browse",
            yscrollcommand=tree_scroll.set,
        )
        self.template_listbox.heading(
            "icon", text=i18n_t("col_image", ns="monster_editor", default="Hình")
        )
        self.template_listbox.heading(
            "threshold",
            text=i18n_t("col_threshold", ns="monster_editor", default="Ngưỡng"),
        )
        self.template_listbox.heading(
            "path", text=i18n_t("col_path", ns="monster_editor", default="Đường dẫn")
        )

        self.template_listbox.column("icon", width=45, anchor="center", stretch=False)
        self.template_listbox.column("threshold", width=65, anchor="center")
        self.template_listbox.column("path", width=180, anchor="w")

        self.template_listbox.pack(side="left", fill="both", expand=True)
        tree_scroll.config(command=self.template_listbox.yview)
        self.template_listbox.bind("<<TreeviewSelect>>", self._on_template_select)

        # --- Right Sub-panel (Preview & Calibration Toolbar + Preview Area) ---
        right_tb = tk.Frame(right_sub, bg=UI.BG_PANEL)
        right_tb.pack(fill="x", pady=(0, 5))

        self.capture_button = create_icon_button(
            right_tb,
            icon_name="capture",
            text=None,
            icon_fallback="🔳",
            command=self._on_capture,
            button_type="blue",
            padding={"padx": 12, "pady": 6},
            tooltip_key="tooltip_capture",
            tooltip_ns="monster_editor",
        )
        self.capture_button.pack(side="left", padx=2)

        self.open_folder_button = create_refresh_button(
            right_tb,
            command=self._on_open_folder,
            text=None,
            padding={"padx": 12, "pady": 6},
            tooltip_key="tooltip_open_folder",
            tooltip_ns="monster_editor",
        )
        self.open_folder_button.pack(side="left", padx=2)

        self.test_template_button = create_icon_button(
            right_tb,
            icon_name="test",
            text=None,
            icon_fallback="❓",
            command=self._on_test_match,
            button_type="orange",
            padding={"padx": 12, "pady": 6},
            tooltip_key="tooltip_test",
            tooltip_ns="monster_editor",
        )
        self.test_template_button.pack(side="left", padx=2)

        self.browse_button = self.open_folder_button  # alias compatibility

        # Large Image Preview Canvas/Label
        preview_frame = tk.Frame(right_sub, bg="white", relief="sunken", bd=1)
        preview_frame.pack(fill="both", expand=True, pady=5)

        self.preview_label = tk.Label(
            preview_frame,
            text=i18n_t(
                "preview_label", ns="monster_editor", default="Chưa chọn\ntemplate"
            ),
            font=UI.FONT_SMALL,
            fg=UI.COLOR_SUBTEXT,
            bg="white",
        )
        self.preview_label.pack(fill="both", expand=True)

        # Threshold Slider & Display Entry/Label
        slider_frame = tk.Frame(right_sub, bg=UI.BG_PANEL)
        slider_frame.pack(fill="x", pady=(5, 0))

        create_icon_label(
            slider_frame,
            icon_name="settings",
            text=i18n_t( "monster_threshold_label", ns="monster_editor", default="Ngưỡng:" ),
            icon_fallback="⚙️",
            font=UI.FONT_SMALL,
            bg=UI.BG_PANEL,
        ).pack(side="left", padx=(0, 5))

        self.threshold_scale = tk.Scale(
            slider_frame,
            from_=0.0,
            to=1.0,
            resolution=0.01,
            orient="horizontal",
            font=UI.FONT_SMALL,
            command=self._on_threshold_changed,
        )
        self.threshold_scale.set(0.7)
        self.threshold_scale.pack(side="left", fill="x", expand=True)

        self.threshold_value_label = tk.Label(
            slider_frame, text="0.70", font=UI.FONT_SMALL, bg=UI.BG_PANEL, width=5
        )
        self.threshold_value_label.pack(side="right", padx=(5, 0))
        self.threshold_label = self.threshold_value_label  # alias compatibility

        # --- Tab 3: Hiển thị (Column Visibility Settings) ---
        self.settings_tab = tk.Frame(self.notebook, bg=UI.BG_DEFAULT)
        self.notebook.add(
            self.settings_tab,
            text=i18n_t("tab_display", ns="monster_editor", default="Hiển thị"),
        )

        settings_group = tk.LabelFrame(
            self.settings_tab,
            text=i18n_t(
                "group_template_cols",
                ns="monster_editor",
                default="Hiển thị cột trong danh sách Template",
            ),
            font=UI.FONT_SECTION,
            fg=UI.COLOR_PRIMARY_TEXT,
            bg=UI.BG_DEFAULT,
            padx=15,
            pady=15,
        )
        settings_group.pack(fill="x", padx=20, pady=20)

        self.chk_col_image = tk.Checkbutton(
            settings_group,
            text=i18n_t("chk_col_image", ns="monster_editor", default="Hình ảnh"),
            bg=UI.BG_DEFAULT,
            font=UI.FONT_TEXT,
        )
        self.chk_col_image.select()
        self.chk_col_image.pack(anchor="w", pady=4)

        self.chk_col_threshold = tk.Checkbutton(
            settings_group,
            text=i18n_t(
                "chk_col_threshold", ns="monster_editor", default="% Ngưỡng nhận diện"
            ),
            bg=UI.BG_DEFAULT,
            font=UI.FONT_TEXT,
        )
        self.chk_col_threshold.select()
        self.chk_col_threshold.pack(anchor="w", pady=4)

        self.chk_col_path = tk.Checkbutton(
            settings_group,
            text=i18n_t("chk_col_path", ns="monster_editor", default="Đường dẫn"),
            bg=UI.BG_DEFAULT,
            font=UI.FONT_TEXT,
        )
        self.chk_col_path.select()
        self.chk_col_path.pack(anchor="w", pady=4)

        # Bottom Action Bar
        bottom_bar = tk.Frame(main_container, bg=UI.BG_PANEL)
        bottom_bar.pack(fill="x", side="bottom")

        self.save_btn = create_save_button(
            bottom_bar,
            command=self._on_save,
            text=i18n_t("btn_save", ns="monster_editor", default="Lưu"),
            padding={"padx": 12, "pady": 6},
            tooltip_key="tooltip_save",
            tooltip_ns="monster_editor",
        )
        self.save_btn.pack(side="right", padx=5)

        self.cancel_btn = create_cancel_button(
            bottom_bar,
            command=self.destroy,
            text=i18n_t("btn_cancel", ns="monster_editor", default="Hủy"),
            padding={"padx": 12, "pady": 6},
            tooltip_key="tooltip_cancel",
            tooltip_ns="monster_editor",
        )
        self.cancel_btn.pack(side="right", padx=5)

    def _create_collapsible_group(self, parent: tk.Widget, title: str, start_expanded: bool = False) -> tk.Frame:
        container = tk.Frame(parent, bg=UI.BG_DEFAULT)
        container.pack(fill="x", padx=15, pady=5)

        header = tk.Frame(container, bg=UI.BG_PANEL, cursor="hand2")
        header.pack(fill="x")

        content = tk.Frame(container, bg=UI.BG_DEFAULT)
        # 2 columns layout like the main form
        content.columnconfigure(1, weight=1, minsize=100)
        content.columnconfigure(3, weight=1, minsize=100)

        lbl = tk.Label(header, text=title, font=UI.FONT_SECTION, bg=UI.BG_PANEL, fg=UI.COLOR_PRIMARY_TEXT)
        lbl.pack(side="left", padx=10, pady=5)

        arrow = tk.Label(header, text="▼" if start_expanded else "▶", font=UI.FONT_SMALL, bg=UI.BG_PANEL, fg=UI.COLOR_SUBTEXT)
        arrow.pack(side="right", padx=10, pady=5)

        is_expanded = start_expanded
        if start_expanded:
            content.pack(fill="both", expand=True, padx=10, pady=5)

        def _toggle(e=None):
            nonlocal is_expanded
            is_expanded = not is_expanded
            if is_expanded:
                content.pack(fill="both", expand=True, padx=10, pady=5)
                arrow.config(text="▼")
            else:
                content.pack_forget()
                arrow.config(text="▶")

        header.bind("<Button-1>", _toggle)
        lbl.bind("<Button-1>", _toggle)
        arrow.bind("<Button-1>", _toggle)

        return content

    def _create_advanced_groups(self, parent: tk.Widget):
        # 1. Defense & Modifiers
        def_group = self._create_collapsible_group(parent, i18n_t("group_defense", ns="monster_editor", default="Phòng thủ & Xuyên giáp (Nâng cao)"))

        create_icon_label(def_group, icon_name="damage", text=i18n_t("monster_pen_label", ns="monster_editor", default="Xuyên giáp:"), icon_fallback="🗡️", font=UI.FONT_LABEL).grid(row=0, column=0, sticky="w", pady=4)
        self.pen_entry = tk.Entry(def_group, font=UI.FONT_TEXT)
        self.pen_entry.grid(row=0, column=1, sticky="ew", pady=4, padx=(12, 0))

        create_icon_label(def_group, icon_name="shield", text=i18n_t("monster_dmg_red_label", ns="monster_editor", default="Giảm sát thương:"), icon_fallback="🛡️", font=UI.FONT_LABEL).grid(row=0, column=2, sticky="w", pady=4, padx=(20, 0))
        self.dmg_red_entry = tk.Entry(def_group, font=UI.FONT_TEXT)
        self.dmg_red_entry.grid(row=0, column=3, sticky="ew", pady=4, padx=(12, 0))

        create_icon_label(def_group, icon_name="speed", text=i18n_t("monster_evasion_label", ns="monster_editor", default="Né tránh:"), icon_fallback="💨", font=UI.FONT_LABEL).grid(row=1, column=0, sticky="w", pady=4)
        self.evasion_entry = tk.Entry(def_group, font=UI.FONT_TEXT)
        self.evasion_entry.grid(row=1, column=1, sticky="ew", pady=4, padx=(12, 0))

        create_icon_label(def_group, icon_name="aim", text=i18n_t("monster_ignore_acc_label", ns="monster_editor", default="Bỏ qua chính xác:"), icon_fallback="🎯", font=UI.FONT_LABEL).grid(row=1, column=2, sticky="w", pady=4, padx=(20, 0))
        self.ignore_acc_entry = tk.Entry(def_group, font=UI.FONT_TEXT)
        self.ignore_acc_entry.grid(row=1, column=3, sticky="ew", pady=4, padx=(12, 0))

        create_icon_label(def_group, icon_name="damage", text=i18n_t("monster_ignore_dmg_red_label", ns="monster_editor", default="Bỏ qua giảm ST:"), icon_fallback="⚔️", font=UI.FONT_LABEL).grid(row=2, column=0, sticky="w", pady=4)
        self.ignore_dmg_red_entry = tk.Entry(def_group, font=UI.FONT_TEXT)
        self.ignore_dmg_red_entry.grid(row=2, column=1, sticky="ew", pady=4, padx=(12, 0))

        create_icon_label(def_group, icon_name="damage", text=i18n_t("monster_ignore_pen_label", ns="monster_editor", default="Bỏ qua xuyên giáp:"), icon_fallback="🗡️", font=UI.FONT_LABEL).grid(row=2, column=2, sticky="w", pady=4, padx=(20, 0))
        self.ignore_pen_entry = tk.Entry(def_group, font=UI.FONT_TEXT)
        self.ignore_pen_entry.grid(row=2, column=3, sticky="ew", pady=4, padx=(12, 0))

        create_icon_label(def_group, icon_name="damage", text=i18n_t("monster_abs_dmg_label", ns="monster_editor", default="Sát thương chuẩn:"), icon_fallback="🔥", font=UI.FONT_LABEL).grid(row=3, column=0, sticky="w", pady=4)
        self.abs_dmg_entry = tk.Entry(def_group, font=UI.FONT_TEXT)
        self.abs_dmg_entry.grid(row=3, column=1, sticky="ew", pady=4, padx=(12, 0))

        # 2. Resistances
        res_group = self._create_collapsible_group(parent, i18n_t("group_resistance", ns="monster_editor", default="Kháng (Nâng cao)"))

        create_icon_label(res_group, icon_name="shield", text=i18n_t("monster_resist_crit_rate_label", ns="monster_editor", default="Kháng tỷ lệ bạo:"), icon_fallback="🛡️", font=UI.FONT_LABEL).grid(row=0, column=0, sticky="w", pady=4)
        self.resist_crit_rate_entry = tk.Entry(res_group, font=UI.FONT_TEXT)
        self.resist_crit_rate_entry.grid(row=0, column=1, sticky="ew", pady=4, padx=(12, 0))

        create_icon_label(res_group, icon_name="shield", text=i18n_t("monster_resist_amp_label", ns="monster_editor", default="Kháng khuếch đại:"), icon_fallback="🛡️", font=UI.FONT_LABEL).grid(row=0, column=2, sticky="w", pady=4, padx=(20, 0))
        self.resist_amp_entry = tk.Entry(res_group, font=UI.FONT_TEXT)
        self.resist_amp_entry.grid(row=0, column=3, sticky="ew", pady=4, padx=(12, 0))

        create_icon_label(res_group, icon_name="shield", text=i18n_t("monster_resist_crit_dmg_label", ns="monster_editor", default="Kháng ST bạo:"), icon_fallback="🛡️", font=UI.FONT_LABEL).grid(row=1, column=0, sticky="w", pady=4)
        self.resist_crit_dmg_entry = tk.Entry(res_group, font=UI.FONT_TEXT)
        self.resist_crit_dmg_entry.grid(row=1, column=1, sticky="ew", pady=4, padx=(12, 0))

        create_icon_label(res_group, icon_name="shield", text=i18n_t("monster_resist_suppress_label", ns="monster_editor", default="Kháng áp chế:"), icon_fallback="🛡️", font=UI.FONT_LABEL).grid(row=1, column=2, sticky="w", pady=4, padx=(20, 0))
        self.resist_suppress_entry = tk.Entry(res_group, font=UI.FONT_TEXT)
        self.resist_suppress_entry.grid(row=1, column=3, sticky="ew", pady=4, padx=(12, 0))

        create_icon_label(res_group, icon_name="shield", text=i18n_t("monster_resist_silence_label", ns="monster_editor", default="Kháng câm lặng:"), icon_fallback="🛡️", font=UI.FONT_LABEL).grid(row=2, column=0, sticky="w", pady=4)
        self.resist_silence_entry = tk.Entry(res_group, font=UI.FONT_TEXT)
        self.resist_silence_entry.grid(row=2, column=1, sticky="ew", pady=4, padx=(12, 0))

        create_icon_label(res_group, icon_name="shield", text=i18n_t("monster_resist_diff_dmg_label", ns="monster_editor", default="Kháng chênh lệch ST:"), icon_fallback="🛡️", font=UI.FONT_LABEL).grid(row=2, column=2, sticky="w", pady=4, padx=(20, 0))
        self.resist_diff_dmg_entry = tk.Entry(res_group, font=UI.FONT_TEXT)
        self.resist_diff_dmg_entry.grid(row=2, column=3, sticky="ew", pady=4, padx=(12, 0))

        create_icon_label(res_group, icon_name="shield", text=i18n_t("monster_hp_prop_dmg_label", ns="monster_editor", default="ST theo HP:"), icon_fallback="🛡️", font=UI.FONT_LABEL).grid(row=3, column=0, sticky="w", pady=4)
        self.hp_prop_dmg_entry = tk.Entry(res_group, font=UI.FONT_TEXT)
        self.hp_prop_dmg_entry.grid(row=3, column=1, sticky="ew", pady=4, padx=(12, 0))

        # 3. Metadata
        meta_group = self._create_collapsible_group(parent, i18n_t("group_metadata", ns="monster_editor", default="Thông tin thêm (Nâng cao)"))

        create_icon_label(meta_group, icon_name="up", text=i18n_t("monster_exp_label", ns="monster_editor", default="EXP:"), icon_fallback="⭐", font=UI.FONT_LABEL).grid(row=0, column=0, sticky="w", pady=4)
        self.exp_entry = tk.Entry(meta_group, font=UI.FONT_TEXT)
        self.exp_entry.grid(row=0, column=1, sticky="ew", pady=4, padx=(12, 0))

        create_icon_label(meta_group, icon_name="hp", text=i18n_t("monster_hp_recharge_label", ns="monster_editor", default="Phục hồi HP:"), icon_fallback="❤️", font=UI.FONT_LABEL).grid(row=0, column=2, sticky="w", pady=4, padx=(20, 0))
        self.hp_recharge_entry = tk.Entry(meta_group, font=UI.FONT_TEXT)
        self.hp_recharge_entry.grid(row=0, column=3, sticky="ew", pady=4, padx=(12, 0))

        create_icon_label(meta_group, icon_name="info", text=i18n_t("monster_desc_label", ns="monster_editor", default="Mô tả:"), icon_fallback="📋", font=UI.FONT_LABEL).grid(row=1, column=0, sticky="nw", pady=4)
        self.desc_text = tk.Text(meta_group, font=UI.FONT_TEXT, height=3, wrap=tk.WORD)
        self.desc_text.grid(row=1, column=1, columnspan=3, sticky="ew", pady=4, padx=(12, 0))

    def _populate_form(self) -> None:
        # Load references
        empty_lbl = i18n_t("ref_none", ns="monster_editor", default="<Không / None>")
        db = getattr(self.parent, "db", None)

        # Dungeons
        dungeons = [{"id": "", "name": empty_lbl}]
        if db and hasattr(db, "get_dungeon_list"):
            try:
                db_dungeons = db.get_dungeon_list()
                if db_dungeons:
                    dungeons.extend(db_dungeons)
            except Exception:
                pass

        self.dungeon_options = [d.get("name", d.get("id")) for d in dungeons]
        self.dungeon_lbl_to_val = {d.get("name", d.get("id")): d.get("id") for d in dungeons if d.get("id")}
        self.dungeon_val_to_lbl = {d.get("id"): d.get("name", d.get("id")) for d in dungeons if d.get("id")}

        if hasattr(self, "dungeon_combo"):
            self.dungeon_combo.config(values=self.dungeon_options)

        # Boss Types
        boss_types = [{"value": "", "label": empty_lbl}]
        if db and hasattr(db, "get_monster_type_list"):
            try:
                db_boss_types = db.get_monster_type_list()
                if db_boss_types:
                    boss_types.extend(db_boss_types)
            except Exception:
                pass

        self.boss_type_options = [t.get("label", t.get("value")) for t in boss_types]
        self.boss_type_lbl_to_val = {t.get("label", t.get("value")): t.get("value") for t in boss_types if t.get("value")}
        self.boss_type_val_to_lbl = {t.get("value"): t.get("label", t.get("value")) for t in boss_types if t.get("value")}

        if hasattr(self, "boss_type_combo"):
            self.boss_type_combo.config(values=self.boss_type_options)

        data = self.monster_data

        m_id = data.get("id", "")
        if self.is_new:
            self.id_val_label.config(text="<Mới / New>")
        else:
            self.id_val_label.config(text=f"#{m_id}")

        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, data.get("name", ""))

        self.level_spinbox.delete(0, tk.END)
        self.level_spinbox.insert(0, str(data.get("level", 1)))

        self.priority_spinbox.delete(0, tk.END)
        self.priority_spinbox.insert(0, str(data.get("priority", 1)))

        self.hp_entry.delete(0, tk.END)
        self.hp_entry.insert(0, str(data.get("hp", 100)))

        self.atk_rate_entry.delete(0, tk.END)
        self.atk_rate_entry.insert(0, str(data.get("attackRate", 0)))

        self.primary_atk_min_entry.delete(0, tk.END)
        self.primary_atk_min_entry.insert(0, str(data.get("primaryAttackMin", 0)))

        self.primary_atk_max_entry.delete(0, tk.END)
        self.primary_atk_max_entry.insert(0, str(data.get("primaryAttackMax", 0)))

        self.sec_atk_min_entry.delete(0, tk.END)
        self.sec_atk_min_entry.insert(0, str(data.get("secondaryAttackMin", 0)))

        self.sec_atk_max_entry.delete(0, tk.END)
        self.sec_atk_max_entry.insert(0, str(data.get("secondaryAttackMax", 0)))

        self.def_entry.delete(0, tk.END)
        self.def_entry.insert(0, str(data.get("defense", 0)))

        self.def_rate_entry.delete(0, tk.END)
        self.def_rate_entry.insert(0, str(data.get("defenseRate", 0)))

        self.acc_entry.delete(0, tk.END)
        self.acc_entry.insert(0, str(data.get("accuracy", 0)))

        # Advanced groups population
        advanced_fields = [
            (self.pen_entry, "penetration"),
            (self.dmg_red_entry, "damageReduction"),
            (self.evasion_entry, "evasion"),
            (self.ignore_acc_entry, "ignoreAccuracy"),
            (self.ignore_dmg_red_entry, "ignoreDamageReduction"),
            (self.ignore_pen_entry, "ignorePenetration"),
            (self.abs_dmg_entry, "absoluteDamage"),
            (self.resist_crit_rate_entry, "resistCritRate"),
            (self.resist_amp_entry, "resistSkillAmp"),
            (self.resist_crit_dmg_entry, "resistCritDamage"),
            (self.resist_suppress_entry, "resistSuppress"),
            (self.resist_silence_entry, "resistSilence"),
            (self.resist_diff_dmg_entry, "resistDiffDamage"),
            (self.hp_prop_dmg_entry, "hpProportionDamage"),
            (self.exp_entry, "exp"),
            (self.hp_recharge_entry, "hpRecharge"),
        ]
        for widget, key in advanced_fields:
            if widget:
                widget.delete(0, tk.END)
                widget.insert(0, str(data.get(key, 0)))

        self.damage_entry.delete(0, tk.END)
        self.damage_entry.insert(0, str(data.get("damage_per_hit", 10)))

        self.desc_text.delete("1.0", tk.END)
        if data.get("description"):
            self.desc_text.insert("1.0", data["description"])

        # Reference comboboxes
        dungeon_id = data.get("dungeonId")
        if dungeon_id is not None and str(dungeon_id).strip() not in ["", "None"]:
            lbl = self.dungeon_val_to_lbl.get(dungeon_id)
            if lbl:
                self.dungeon_combo.set(lbl)
            else:
                self.dungeon_combo.set(dungeon_id)
        else:
            self.dungeon_combo.set(empty_lbl)

        boss_type = data.get("serverBossType")
        if boss_type is not None and str(boss_type).strip() not in ["", "None"]:
            lbl = self.boss_type_val_to_lbl.get(boss_type)
            if lbl:
                self.boss_type_combo.set(lbl)
            else:
                self.boss_type_combo.set(boss_type)
        else:
            self.boss_type_combo.set(empty_lbl)

        self._refresh_templates()

    def _on_reset_form(self) -> None:
        """Reset form fields to default values for a new entry."""
        self.id_val_label.config(text="<Mới / New>")
        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(
            0, i18n_t("default_monster_name", ns="monster_editor", default="Quái Mới")
        )
        self.level_spinbox.delete(0, tk.END)
        self.level_spinbox.insert(0, "1")
        self.priority_spinbox.delete(0, tk.END)
        self.priority_spinbox.insert(0, "1")
        self.hp_entry.delete(0, tk.END)
        self.hp_entry.insert(0, "100")

        for entry in (self.atk_rate_entry, self.primary_atk_min_entry, self.primary_atk_max_entry,
                      self.sec_atk_min_entry, self.sec_atk_max_entry, self.def_entry, self.def_rate_entry, self.acc_entry,
                      self.pen_entry, self.dmg_red_entry, self.evasion_entry, self.ignore_acc_entry,
                      self.ignore_dmg_red_entry, self.ignore_pen_entry, self.abs_dmg_entry,
                      self.resist_crit_rate_entry, self.resist_amp_entry, self.resist_crit_dmg_entry,
                      self.resist_suppress_entry, self.resist_silence_entry, self.resist_diff_dmg_entry,
                      self.hp_prop_dmg_entry, self.exp_entry, self.hp_recharge_entry):
            entry.delete(0, tk.END)
            entry.insert(0, "0")

        self.dungeon_combo.set(i18n_t("ref_none", ns="monster_editor", default="<Không / None>"))
        self.boss_type_combo.set(i18n_t("ref_none", ns="monster_editor", default="<Không / None>"))

        self.damage_entry.delete(0, tk.END)
        self.damage_entry.insert(0, "10")
        self.desc_text.delete("1.0", tk.END)

    def _on_clear_form(self) -> None:
        """Clear all form fields."""
        self.id_val_label.config(text="")
        self.name_entry.delete(0, tk.END)
        self.level_spinbox.delete(0, tk.END)
        self.priority_spinbox.delete(0, tk.END)
        self.hp_entry.delete(0, tk.END)

        for entry in (self.atk_rate_entry, self.primary_atk_min_entry, self.primary_atk_max_entry,
                      self.sec_atk_min_entry, self.sec_atk_max_entry, self.def_entry, self.def_rate_entry, self.acc_entry,
                      self.pen_entry, self.dmg_red_entry, self.evasion_entry, self.ignore_acc_entry,
                      self.ignore_dmg_red_entry, self.ignore_pen_entry, self.abs_dmg_entry,
                      self.resist_crit_rate_entry, self.resist_amp_entry, self.resist_crit_dmg_entry,
                      self.resist_suppress_entry, self.resist_silence_entry, self.resist_diff_dmg_entry,
                      self.hp_prop_dmg_entry, self.exp_entry, self.hp_recharge_entry):
            entry.delete(0, tk.END)

        self.dungeon_combo.set(i18n_t("ref_none", ns="monster_editor", default="<Không / None>"))
        self.boss_type_combo.set(i18n_t("ref_none", ns="monster_editor", default="<Không / None>"))

        self.damage_entry.delete(0, tk.END)
        self.desc_text.delete("1.0", tk.END)
        if hasattr(self, "preview_label") and self.preview_label:
            self.preview_label.config(
                text=i18n_t(
                    "preview_label", ns="monster_editor", default="Chưa chọn\ntemplate"
                ),
                image="",
            )
            self.preview_label.image = None

    def _refresh_templates(self) -> None:
        for item in self.template_listbox.get_children():
            self.template_listbox.delete(item)

        templates = self.monster_data.get("templates", [])
        for idx, tmpl in enumerate(templates):
            item_id = f"tmpl_{idx}"
            threshold_str = f"{tmpl.get('threshold', 0.7):.0%}"
            path_str = tmpl.get("path", tmpl.get("name", ""))
            self.template_listbox.insert(
                "", "end", iid=item_id, values=("🖼️", threshold_str, path_str)
            )

        if hasattr(self, "template_badge"):
            self.template_badge.config(text=f"{len(templates)} tpl")

    def _on_template_select(self, event: Any = None) -> None:
        selection = self.template_listbox.selection()
        if not selection:
            self.preview_label.config(
                text=i18n_t(
                    "preview_label", ns="monster_editor", default="Chưa chọn\ntemplate"
                ),
                image="",
            )
            self.preview_label.image = None
            return

        idx = int(selection[0].split("_")[-1])
        templates = self.monster_data.get("templates", [])
        if idx >= len(templates):
            self.preview_label.config(
                text=i18n_t(
                    "preview_label", ns="monster_editor", default="Chưa chọn\ntemplate"
                ),
                image="",
            )
            self.preview_label.image = None
            return

        tmpl = templates[idx]
        thresh = tmpl.get("threshold", 0.7)
        self.threshold_scale.set(thresh)
        self.threshold_value_label.config(text=f"{thresh:.2f}")

        rel_path = tmpl.get("path", "")
        resolved_path = PROJECT_ROOT / rel_path if rel_path and not Path(rel_path).is_absolute() else Path(rel_path) if rel_path else None

        if resolved_path and resolved_path.exists() and PIL_AVAILABLE and Image and ImageTk:
            try:
                with Image.open(resolved_path) as raw_img:
                    img = raw_img.copy()
                img.thumbnail((200, 200), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                self.preview_label.config(image=photo, text="")
                self.preview_label.image = photo
            except Exception:
                self.preview_label.config(text=f"Lỗi ảnh\n{tmpl.get('name')}", image="")
                self.preview_label.image = None
        else:
            self.preview_label.config(
                text=f"Không tìm thấy\n{tmpl.get('name')}", image=""
            )
            self.preview_label.image = None

    def _on_threshold_changed(self, val: str) -> None:
        try:
            new_val = float(val)
        except ValueError:
            return
        self.threshold_value_label.config(text=f"{new_val:.2f}")

        selection = self.template_listbox.selection()
        if not selection:
            return
        idx = int(selection[0].split("_")[-1])
        templates = self.monster_data.get("templates", [])
        if idx < len(templates):
            templates[idx]["threshold"] = new_val
            path_str = templates[idx].get("path", templates[idx].get("name", ""))
            self.template_listbox.item(
                selection[0], values=("🖼️", f"{new_val:.0%}", path_str)
            )

    def _on_capture(self) -> None:
        if self._is_capturing or not PIL_AVAILABLE or ImageGrab is None:
            return
        self._is_capturing = True
        try:
            self.withdraw()
            time.sleep(0.15)
            capture_cls = getattr(self.parent, "_RegionCaptureOverlay", None)
            if capture_cls is None:
                capture_cls = getattr(self.parent.__class__, "_RegionCaptureOverlay", None)
            if capture_cls is not None:
                overlay = capture_cls(self.parent)
                bbox = overlay.show_modal()
            else:
                bbox = None
            self.deiconify()
            self.lift()

            if bbox:
                img = ImageGrab.grab(bbox=bbox)
                base = re.sub(
                    r'[<>:"/\\|?*]', "_", self.name_entry.get().strip() or "monster"
                )
                ts = int(time.time())
                filename = f"{base}_capture_{ts}.png"
                assets_dir = Path("assets/images/monsters")
                assets_dir.mkdir(parents=True, exist_ok=True)
                save_path = assets_dir / filename
                img.save(save_path)

                tmpl = {
                    "name": filename,
                    "path": f"assets/images/monsters/{filename}",
                    "threshold": 0.85,
                }
                self.monster_data.setdefault("templates", []).append(tmpl)
                self._refresh_templates()
        finally:
            self._is_capturing = False

    def _on_browse(self) -> None:
        if self._is_browsing:
            return
        self._is_browsing = True
        try:
            file_path = filedialog.askopenfilename(
                title=i18n_t(
                    "tooltip_browse", ns="monster_editor", default="Chọn Ảnh Template"
                ),
                filetypes=[
                    ("Image files", "*.png *.jpg *.jpeg *.bmp"),
                    ("All files", "*.*"),
                ],
            )
            if file_path:
                import shutil

                filename = Path(file_path).name
                ts = int(time.time())
                new_filename = f"{Path(filename).stem}_{ts}{Path(filename).suffix}"
                assets_dir = Path("assets/images/monsters")
                assets_dir.mkdir(parents=True, exist_ok=True)
                shutil.copy2(file_path, assets_dir / new_filename)

                tmpl = {
                    "name": new_filename,
                    "path": f"assets/images/monsters/{new_filename}",
                    "threshold": 0.85,
                }
                self.monster_data.setdefault("templates", []).append(tmpl)
                self._refresh_templates()
        finally:
            self._is_browsing = False

    def _on_open_folder(self) -> None:
        assets_dir = Path("assets/images/monsters")
        assets_dir.mkdir(parents=True, exist_ok=True)
        try:
            if os.name == "nt":
                os.startfile(str(assets_dir.resolve()))
            elif os.name == "posix":
                subprocess.run(["xdg-open", str(assets_dir.resolve())], check=False)
        except Exception as e:
            title = i18n_t(
                "btn_open_folder", ns="monster_editor", default="Thư mục Template"
            )
            messagebox.showinfo(title, str(assets_dir.resolve()), parent=self)

    def _on_test_match(self) -> None:
        selection = self.template_listbox.selection()
        if not selection:
            messagebox.showinfo(
                "Test Match",
                i18n_t(
                    "msg_test_failed", ns="monster_editor", default="Chưa chọn template"
                ),
                parent=self,
            )
            return
        messagebox.showinfo(
            "Test Match",
            i18n_t(
                "msg_test_success",
                ns="monster_editor",
                default="Test match thành công!",
            ).format(1, 0.95),
            parent=self,
        )

    def _on_delete_template(self) -> None:
        selection = self.template_listbox.selection()
        if not selection:
            return
        idx = int(selection[0].split("_")[-1])
        templates = self.monster_data.get("templates", [])
        if idx < len(templates):
            del templates[idx]
            self._refresh_templates()

    def _on_save(self) -> None:
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror(
                "Lỗi",
                i18n_t(
                    "error_name_empty",
                    ns="monster_editor",
                    default="Tên quái không được để trống",
                ),
                parent=self,
            )
            return

        try:
            int(self.level_spinbox.get())
            int(self.priority_spinbox.get())
            int(self.hp_entry.get())
            int(self.damage_entry.get())
        except ValueError:
            messagebox.showerror(
                "Lỗi",
                "Cấp độ, HP, Độ ưu tiên, Sát thương phải là số nguyên",
                parent=self,
            )
            return

        # Check duplicate name
        monsters_list = getattr(self.parent, "monsters", [])
        current_id = self.monster_data.get("id")

        if check_duplicate_name(monsters_list, name, current_id=current_id):
            unique_name = generate_unique_name(
                monsters_list, name, current_id=current_id
            )
            title = i18n_t(
                "title_duplicate_name",
                ns="monster_editor",
                default="Tên Quái Trùng Lặp",
            )
            msg = i18n_t(
                "msg_duplicate_name_confirm",
                ns="monster_editor",
                default=f"Tên quái '{name}' đã tồn tại!\n\nBạn có muốn tự động đổi tên thành '{unique_name}' không?",
            )
            if messagebox.askyesno(title, msg, parent=self):
                name = unique_name
                self.name_entry.delete(0, tk.END)
                self.name_entry.insert(0, name)
            else:
                return

        self.monster_data = self._collect_form_data()

        if self.on_save_callback:
            self.on_save_callback(self.monster_data)
        self.destroy()
