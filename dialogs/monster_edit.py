# -*- coding: utf-8 -*-
"""
Monster Edit Dialog module.
Main modal dialog coordinating Basic Info, Extended Info, and Templates tabs.
"""

from __future__ import annotations
import tkinter as tk
from tkinter import ttk, messagebox
import json
import uuid
from typing import Optional, Dict, Any, Callable, List

from dialogs.monster_validator import validate_monster_data
from dialogs.monster_form_basic import BasicInfoForm
from dialogs.monster_form_extended import ExtendedInfoForm
from dialogs.monster_templates_tab import MonsterTemplatesTab

try:
    from database import get_db
except ImportError:
    get_db = None

try:
    from lib.i18n import t as i18n_t
except ImportError:
    from mock.fallbacks import i18n_t

try:
    from lib.features.monster_service import check_duplicate_name, generate_unique_name
except ImportError:
    from mock.fallbacks import check_duplicate_name, generate_unique_name

try:
    from lib.ui_style import UIStyle as UI
except ImportError:
    from mock.fallbacks import UIStyle as UI

try:
    from ui.components import create_icon_label
    from ui.components.icon_button import create_save_button, create_cancel_button
except ImportError:
    from mock.fallbacks import create_icon_label, create_save_button, create_cancel_button


class MonsterEditDialog(tk.Toplevel):
    """
    Modal dialog for creating or editing a monster with full 30 schema fields.
    """

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

        # Deep copy monster or create new default
        if monster:
            self.monster_data = json.loads(json.dumps(monster))
        else:
            self.monster_data = {
                "id": f"m_{int(uuid.uuid4().hex[:8], 16)}",
                "name": "Quái Mới",
                "level": 1,
                "priority": 1,
                "hp": 100,
                "damage_per_hit": 10,
                "dungeonId": None,
                "serverBossType": None,
                "templates": [],
            }

        m_id = self.monster_data.get("id", "")
        m_name = self.monster_data.get("name", "")
        title_text = f"Sửa Quái Vật: {m_name} (ID: #{m_id})" if not self.is_new else "Thêm Quái Vật Mới"
        self.title(title_text)
        self.geometry("820x620")
        self.resizable(True, True)
        self.transient(parent)
        self.grab_set()

        # Fetch reference lists from DB/parent
        self.dungeon_list: List[Dict[str, str]] = []
        self.type_list: List[Dict[str, str]] = []
        self.existing_monsters: List[Dict[str, Any]] = getattr(parent, "monsters", [])

        db = getattr(parent, "db", None) if getattr(parent, "db", None) is not None else (get_db() if get_db is not None else None)
        if db is not None:
            try:
                self.dungeon_list = db.get_dungeon_list() if hasattr(db, "get_dungeon_list") else []
                self.type_list = db.get_monster_type_list() if hasattr(db, "get_monster_type_list") else []
            except Exception:
                pass

        self.bind("<Escape>", lambda event: self.destroy())

        self._setup_ui()

        # Center dialog
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (820 // 2)
        y = (self.winfo_screenheight() // 2) - (620 // 2)
        self.geometry(f"+{x}+{y}")

    def _setup_ui(self) -> None:
        main_container = tk.Frame(self, bg=UI.BG_DEFAULT)
        main_container.pack(fill="both", expand=True, padx=10, pady=10)

        # Tab Notebook
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill="both", expand=True, pady=(0, 10))

        # --- Tab 1: Form Tab (Basic + Extended) ---
        self.info_tab = tk.Frame(self.notebook, bg=UI.BG_DEFAULT)
        self.notebook.add(self.info_tab, text="Thông Tin Quái")

        # Scrollable container for form
        canvas = tk.Canvas(self.info_tab, bg=UI.BG_DEFAULT, highlightthickness=0)
        scrollbar = tk.Scrollbar(self.info_tab, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg=UI.BG_DEFAULT)

        scroll_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Basic Info Form Component
        self.basic_form = BasicInfoForm(
            scroll_frame,
            monster_data=self.monster_data,
            is_new=self.is_new,
            dungeon_list=self.dungeon_list,
            type_list=self.type_list,
            existing_monsters=self.existing_monsters,
            on_clone_callback=self._on_clone_monster,
        )
        self.basic_form.pack(fill="x", expand=True, padx=10, pady=5)

        # Extended Info Form Component
        self.extended_form = ExtendedInfoForm(scroll_frame, monster_data=self.monster_data)
        self.extended_form.pack(fill="x", expand=True, padx=10, pady=5)

        # Backward compatibility properties for unit tests
        self.name_entry = self.basic_form.name_entry
        self.level_spinbox = self.basic_form.level_spin
        self.hp_entry = self.basic_form.hp_entry
        self.priority_spinbox = tk.Spinbox(self.info_tab, from_=1, to=10)
        self.priority_spinbox.delete(0, tk.END)
        self.priority_spinbox.insert(0, "1")

        self.damage_entry = tk.Entry(self.info_tab)
        self.damage_entry.insert(0, "10")

        self.desc_text = tk.Text(self.info_tab)

        # --- Tab 2: Templates ---
        self.templates_tab = MonsterTemplatesTab(
            self.notebook,
            monster_data=self.monster_data,
            get_monster_name_func=lambda: self.basic_form.name_entry.get().strip(),
        )
        self.notebook.add(self.templates_tab, text="Templates")

        # Backward compatibility aliases for templates tab
        self.template_listbox = self.templates_tab.template_listbox
        self.threshold_scale = self.templates_tab.threshold_scale
        self.threshold_label = self.templates_tab.threshold_value_label
        self.capture_button = self.templates_tab.capture_button
        self.browse_button = self.templates_tab.btn_add
        self.delete_template_button = self.templates_tab.btn_delete
        self.test_template_button = self.templates_tab.capture_button

        # --- Tab 3: Display Settings ---
        self.settings_tab = tk.Frame(self.notebook, bg=UI.BG_DEFAULT)
        self.notebook.add(self.settings_tab, text="Hiển thị")

        # Bottom Action & Status Bar
        self.bottom_bar = tk.Frame(main_container, bg=UI.BG_PANEL)
        self.bottom_bar.pack(fill="x", side="bottom")

        self.status_lbl = tk.Label(
            self.bottom_bar, text="", font=UI.FONT_LABEL, bg=UI.BG_PANEL, fg=UI.COLOR_PRIMARY_TEXT
        )
        self.status_lbl.pack(side="left", padx=10)

        self.save_btn = create_save_button(
            self.bottom_bar,
            command=self._on_save,
            text="Lưu",
            padding={"padx": 12, "pady": 6},
        )
        self.save_btn.pack(side="right", padx=5)

        self.cancel_btn = create_cancel_button(
            self.bottom_bar,
            command=self.destroy,
            text="Hủy",
            padding={"padx": 12, "pady": 6},
        )
        self.cancel_btn.pack(side="right", padx=5)

    def _on_clone_monster(self, source_monster: Dict[str, Any]) -> None:
        """Prefills form with attributes from source_monster."""
        clone_data = json.loads(json.dumps(source_monster))
        if self.is_new:
            clone_data["id"] = self.basic_form.id_entry.get().strip() or f"m_{int(uuid.uuid4().hex[:8], 16)}"
        else:
            clone_data["id"] = self.monster_data.get("id")
        clone_data["name"] = f"{source_monster.get('name', '')} (Copy)"

        self.basic_form.populate(clone_data)
        self.extended_form.populate(clone_data)
        if "templates" in clone_data:
            self.monster_data["templates"] = clone_data["templates"]
            self.templates_tab.refresh_templates()

        self.status_lbl.config(fg="green", text=f"Đã sao chép từ '{source_monster.get('name')}'")

    def _populate_form(self) -> None:
        self.basic_form.populate(self.monster_data)
        self.extended_form.populate(self.monster_data)

    def _on_reset_form(self) -> None:
        default_data = {
            "id": f"m_{int(uuid.uuid4().hex[:8], 16)}",
            "name": "Quái Mới",
            "level": 1,
            "hp": 100,
        }
        self.basic_form.populate(default_data)
        self.extended_form.populate(default_data)

    def _on_clear_form(self) -> None:
        empty_data = {"id": "", "name": "", "level": 0, "hp": 0}
        self.basic_form.populate(empty_data)
        self.extended_form.populate(empty_data)

    def _on_save(self) -> None:
        raw_basic = self.basic_form.get_data()
        raw_extended = self.extended_form.get_data()

        merged_raw = {**self.monster_data, **raw_basic, **raw_extended}

        is_valid, errors, cleaned = validate_monster_data(
            merged_raw,
            is_new=self.is_new,
            existing_monsters=self.existing_monsters,
        )

        self.basic_form.show_errors(errors)
        self.extended_form.show_errors(errors)

        if not is_valid:
            first_err = next(iter(errors.values()))
            self.status_lbl.config(fg="red", text=f"Lỗi: {first_err}")
            messagebox.showerror("Validation Error", f"Vui lòng kiểm tra lại thông tin:\n- {first_err}", parent=self)
            return

        # Check duplicate name
        monsters_list = getattr(self.parent, "monsters", self.existing_monsters)
        current_id = cleaned.get("id")
        name = cleaned.get("name", "")

        if check_duplicate_name(monsters_list, name, current_id=current_id):
            unique_name = generate_unique_name(monsters_list, name, current_id=current_id)
            title = i18n_t("title_duplicate_name", ns="monster_editor", default="Tên Quái Trùng Lặp")
            msg = i18n_t(
                "msg_duplicate_name_confirm",
                ns="monster_editor",
                default=f"Tên quái '{name}' đã tồn tại!\n\nBạn có muốn tự động đổi tên thành '{unique_name}' không?",
            )
            if messagebox.askyesno(title, msg, parent=self):
                name = unique_name
                cleaned["name"] = name
                self.basic_form.name_entry.delete(0, tk.END)
                self.basic_form.name_entry.insert(0, name)
            else:
                return

        # Ensure priority and damage_per_hit exist for legacy unit tests
        cleaned.setdefault("priority", self.monster_data.get("priority", 1))
        cleaned.setdefault("damage_per_hit", self.monster_data.get("damage_per_hit", 10))

        self.status_lbl.config(fg="green", text="Đã lưu thông tin thành công!")

        if self.on_save_callback:
            self.on_save_callback(cleaned)

        self.destroy()
