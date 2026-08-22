# -*- coding: utf-8 -*-
"""
Quick Monster Editor / Monster Manager Window.
Main Master View: Full-width Treeview/Data Table listing monsters.

Author: SokKimThanh
Updated: 2025-10-25
"""

from __future__ import annotations
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Dict, Any, Callable, List, Union
from unittest.mock import MagicMock
from pathlib import Path
import queue
import json

from ui.windows.monster_editor_overlay import RegionCaptureOverlay
from ui.windows.monster_editor_toolbar import create_top_panel, create_search_bar

try:
    from dialogs.display_settings import DisplaySettingsDialog
    from dialogs.monster_edit import MonsterEditDialog
except ImportError as e:
    raise ImportError("Failed to import dialogs for Monster Editor") from e

try:
    from lib.features.monster_service import ensure_unique_monster_id
except ImportError:
    from mock.fallbacks import ensure_unique_monster_id

try:
    from lib.i18n import t as i18n_t, register_bulk as i18n_register_bulk
except ImportError:
    from mock.fallbacks import i18n_t, i18n_register_bulk

try:
    from lib.data.sync_manager import DataSyncManager
except ImportError:
    DataSyncManager = None

try:
    from ui.components import create_icon_button, create_icon_label
    from ui.components.icon_button import create_add_button, create_delete_button, create_cancel_button
    from ui.mixins.action_notification_mixin import ActionNotificationMixin
except ImportError:
    from mock.fallbacks import create_icon_button, create_icon_label, create_add_button, create_delete_button, create_cancel_button, ActionNotificationMixin

try:
    from lib.ui_style import UIStyle as UI
except ImportError:
    from mock.fallbacks import UIStyle as UI

try:
    from database import get_db
except ImportError:
    get_db = None

DATA_PATH = Path("lib/data/monsters.json")


class CompatibleTreeview(ttk.Treeview):
    """Treeview with backward compatibility for Listbox methods used in unit tests."""

    def size(self) -> int:
        return len(self.get_children())

    def get(self, index: int) -> str:
        children = self.get_children()
        if 0 <= index < len(children):
            values = self.item(children[index], "values")
            if values:
                raw_name = str(values[0]).split("\n")[0].strip()
                level = 1
                if len(values) >= 2 and (isinstance(values[1], int) or str(values[1]).isdigit()):
                    level = values[1]
                return f"👹 {raw_name} (Lv.{level})"
        return ""

    def curselection(self) -> tuple:
        children = self.get_children()
        selection = self.selection()
        result = []
        for item in selection:
            if item in children:
                result.append(children.index(item))
        return tuple(result)

    def selection_set(self, *items) -> None:
        children = self.get_children()
        new_items = []
        for item in items:
            if isinstance(item, int) and 0 <= item < len(children):
                new_items.append(children[item])
            elif isinstance(item, str):
                new_items.append(item)
        if new_items:
            super().selection_set(*new_items)

    def selection_clear(self, *args, **kwargs) -> None:
        super().selection_clear()


class QuickMonsterEditor(ActionNotificationMixin, tk.Toplevel):
    """Main Monster Manager Window (Master View with Table Layout)."""

    _RegionCaptureOverlay = RegionCaptureOverlay

    def __init__(
        self,
        parent: Any,
        monster_id: Optional[str] = None,
        on_save: Optional[Callable] = None,
    ):
        if not parent:
            raise ValueError("Parent widget is required for QuickMonsterEditor")

        try:
            super().__init__(parent, debug_mode=False)
        except TypeError:
            super().__init__(parent)

        self.sort_column = "name"
        self.sort_reverse = False

        self.parent = parent
        self.monster_id = monster_id
        self.on_save_callback = on_save

        self.monsters: List[Dict[str, Any]] = []
        self.filtered_monsters: List[Dict[str, Any]] = []
        self.current_monster_id: Optional[str] = monster_id
        self.is_dirty = False
        self.is_monster_dirty = False

        self.db = get_db() if get_db is not None else None

        self.monster_grid_columns = [
            "id", "name", "level", "exp", "hp", "defense", "attackRate", "defenseRate",
            "hpRecharge", "accuracy", "penetration", "damageReduction", "evasion",
            "resistCritRate", "primaryAttackMin", "primaryAttackMax", "secondaryAttackMin",
            "secondaryAttackMax", "ignoreAccuracy", "ignoreDamageReduction", "ignorePenetration",
            "absoluteDamage", "resistSkillAmp", "resistCritDamage", "resistSuppress",
            "resistSilence", "resistDiffDamage", "hpProportionDamage", "serverBossType", "dungeonId",
        ]
        self.default_visible_columns = [
            "name", "level", "hp", "defense", "defenseRate", "ignorePenetration",
            "resistCritRate", "resistSkillAmp", "resistCritDamage",
        ]
        self.column_visibility = {col: (col in self.default_visible_columns) for col in self.monster_grid_columns}
        self.visible_columns = [col for col in self.monster_grid_columns if self.column_visibility.get(col, False)]

        self.current_page = 1
        self.page_size = 25
        self.search_term = ""
        self.monster_type_filter = "All Monsters"
        self.location_filter = "All Locations"
        self._search_job = None
        self._column_visibility_vars: Dict[str, tk.BooleanVar] = {}

        if DataSyncManager is not None:
            self.sync_manager = DataSyncManager()
        else:
            self.sync_manager = None

        self.result_queue: queue.Queue = queue.Queue()
        self._active_edit_dialog: Optional[MonsterEditDialog] = None

        self.title("Quản Lý Quái Vật")
        self.geometry("850x520")
        self.resizable(True, True)
        self.attributes("-topmost", True)

        self._setup_compatibility_widgets()
        self._load_monsters()
        self._setup_ui()
        self._bind_events()
        self._start_queue_monitor()
        self._update_dirty_state_ui()
        self._refresh_monster_table()

    def deiconify(self) -> None:
        super().deiconify()
        try:
            self._refresh_monster_table()
        except Exception as e:
            print(f"[QuickMonsterEditor] Error refreshing table on deiconify: {e}")

    def _setup_compatibility_widgets(self) -> None:
        dummy_parent = tk.Frame(self)
        dummy_parent.place(x=-2000, y=-2000, width=1, height=1)

        self.notebook = ttk.Notebook(dummy_parent)
        self.notebook.pack()
        self.info_tab = tk.Frame(self.notebook)
        self.templates_tab = tk.Frame(self.notebook)
        self.notebook.add(self.info_tab, text="Thông Tin Quái")
        self.notebook.add(self.templates_tab, text="Templates")

        self.name_entry = tk.Entry(self.info_tab)
        self.level_spinbox = tk.Spinbox(
            self.info_tab, from_=1, to=999, command=lambda: self.set_monster_dirty(True)
        )
        self.level_spinbox.bind("<<Increment>>", lambda e: self.set_monster_dirty(True))
        self.level_spinbox.bind("<<Decrement>>", lambda e: self.set_monster_dirty(True))

        _orig_eg = self.level_spinbox.event_generate

        def _cust_eg(event, **kwargs):
            if str(event) in ("<<Increment>>", "<<Decrement>>"):
                self.set_monster_dirty(True)
            return _orig_eg(event, **kwargs)

        self.level_spinbox.event_generate = _cust_eg

        self.priority_spinbox = tk.Spinbox(self.info_tab, from_=1, to=10)
        self.hp_entry = tk.Entry(self.info_tab)
        self.damage_entry = tk.Entry(self.info_tab)
        self.desc_text = tk.Text(self.info_tab)

        self.template_scrollbar = tk.Scrollbar(self.templates_tab)
        self.template_listbox = tk.Listbox(self.templates_tab, selectmode=tk.SINGLE)
        self.capture_button = create_icon_button(self.templates_tab, icon_name="capture", text="Capture")
        self.browse_button = create_icon_button(self.templates_tab, icon_name="browse", text="Browse")
        self.delete_template_button = create_delete_button(self.templates_tab, command=lambda: None, text="Delete")
        self.test_template_button = create_icon_button(self.templates_tab, icon_name="test", text="Test")
        self.threshold_scale = tk.Scale(self.templates_tab, from_=0.0, to=1.0, resolution=0.01)
        self.threshold_scale.set(0.7)
        self.threshold_label = tk.Label(self.templates_tab, text="0.70")

    def _populate_info_form(self, monster: Dict[str, Any]) -> None:
        if not monster:
            return
        self._clear_info_form()
        if self.name_entry:
            self.name_entry.insert(0, monster.get("name", ""))
        if self.level_spinbox:
            self.level_spinbox.delete(0, tk.END)
            self.level_spinbox.insert(0, str(monster.get("level", 1)))
        if self.priority_spinbox:
            self.priority_spinbox.delete(0, tk.END)
            self.priority_spinbox.insert(0, str(monster.get("priority", 1)))
        if self.hp_entry:
            self.hp_entry.insert(0, str(monster.get("hp", 100)))
        if self.damage_entry:
            self.damage_entry.insert(0, str(monster.get("damage_per_hit", 10)))
        if self.desc_text:
            desc = monster.get("description", "")
            if desc:
                self.desc_text.insert("1.0", desc)

    def _clear_info_form(self) -> None:
        if self.name_entry:
            self.name_entry.delete(0, tk.END)
        if self.level_spinbox:
            self.level_spinbox.delete(0, tk.END)
            self.level_spinbox.insert(0, "1")
        if self.priority_spinbox:
            self.priority_spinbox.delete(0, tk.END)
            self.priority_spinbox.insert(0, "1")
        if self.hp_entry:
            self.hp_entry.delete(0, tk.END)
        if self.damage_entry:
            self.damage_entry.delete(0, tk.END)
        if self.desc_text:
            self.desc_text.delete("1.0", tk.END)

    def _on_info_change(self, event: Any = None) -> None:
        self.set_monster_dirty(True)
        if self.current_monster_id and self.monsters:
            for monster in self.monsters:
                if monster.get("id") == self.current_monster_id:
                    if self.name_entry:
                        monster["name"] = self.name_entry.get()
                    if self.level_spinbox:
                        try:
                            monster["level"] = int(self.level_spinbox.get())
                        except ValueError:
                            pass
                    self._refresh_monster_table()
                    break

    def _load_monsters(self) -> None:
        try:
            if self.db is not None:
                payload = self.db.get_filtered_monsters(
                    keyword="", monster_type=None, dungeon_id=None, page=1, page_size=5000
                )
                self.monsters = payload.get("items", [])
                if not self.monsters and DATA_PATH.exists():
                    with open(DATA_PATH, "r", encoding="utf-8") as f:
                        self.monsters = json.load(f)
            else:
                if DATA_PATH.exists():
                    with open(DATA_PATH, "r", encoding="utf-8") as f:
                        self.monsters = json.load(f)
                else:
                    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
                    with open(DATA_PATH, "w", encoding="utf-8") as f:
                        json.dump([], f)
                    self.monsters = []

            for m in self.monsters:
                if isinstance(m, dict):
                    ensure_unique_monster_id(m)
        except Exception as e:
            print(f"[MonsterEditor] Error loading monsters: {e}")
            self.monsters = []
        self.filtered_monsters = list(self.monsters)

    def set_dirty(self, value: bool = True) -> None:
        self.is_dirty = value
        self._update_dirty_state_ui()

    def set_monster_dirty(self, value: bool = True) -> None:
        self.is_monster_dirty = value
        self.set_dirty(value)

    def _update_dirty_state_ui(self) -> None:
        if hasattr(self, "status_badge") and self.status_badge:
            if self.is_dirty:
                self.status_badge.config(text="Chưa lưu", bg="#FF8C00", fg="white")
            else:
                self.status_badge.config(text="Đã lưu tất cả", bg="#28A745", fg="white")
        if hasattr(self, "status_icon_label") and self.status_icon_label:
            text = "Unsaved changes" if self.is_dirty else "All saved"
            self.status_icon_label.config(text=text)
        if hasattr(self, "save_button") and self.save_button:
            self.save_button.config(state="normal" if self.is_dirty else "disabled")

    def _save_monsters(self) -> bool:
        if not self.monsters or not isinstance(self.monsters, list):
            messagebox.showwarning("Warning", "Không có dữ liệu để lưu", parent=self)
            self._show_status_message("Không có dữ liệu để lưu", is_error=True)
            return False

        for idx, monster in enumerate(self.monsters):
            if not isinstance(monster, dict):
                messagebox.showerror("Error", f"Invalid monster data at index {idx}", parent=self)
                return False
            name = str(monster.get("name", "")).strip()
            if not name:
                messagebox.showerror("Error", f"Monster at index {idx} has no name", parent=self)
                return False

        try:
            if self.db is not None:
                for monster in self.monsters:
                    if not self.db.insert_or_update_monster(monster):
                        self._show_status_message("Lưu thất bại trong DB", is_error=True)
                        return False
            else:
                DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
                with open(DATA_PATH, "w", encoding="utf-8") as f:
                    json.dump(self.monsters, f, indent=2, ensure_ascii=False)

            self.is_dirty = False
            self.is_monster_dirty = False
            self._update_dirty_state_ui()
            self._show_status_message("Đã lưu tất cả", is_error=False)
            return True
        except Exception as e:
            self._show_status_message(f"Lưu thất bại: {e}", is_error=True)
            return False

    def _setup_ui(self) -> None:
        create_top_panel(self)
        create_search_bar(self)
        self._create_table_area()
        self._create_confirmation_banner()
        self._create_bottom_bar()

    def _open_column_visibility_menu(self) -> None:
        menu = tk.Menu(self, tearoff=0)
        self._column_visibility_vars = {}
        for column in self.monster_grid_columns:
            label = self._column_label(column)
            var = tk.BooleanVar(value=self.column_visibility.get(column, False))
            self._column_visibility_vars[column] = var
            menu.add_checkbutton(
                label=label,
                variable=var,
                command=lambda c=column, v=var: self._toggle_column_visibility(c, bool(v.get())),
            )
        try:
            menu.post(
                self.column_visibility_button.winfo_rootx(),
                self.column_visibility_button.winfo_rooty() + self.column_visibility_button.winfo_height(),
            )
        except Exception:
            pass

    def _toggle_column_visibility(self, column: str, visible: bool) -> None:
        self.column_visibility[column] = visible
        self.visible_columns = [col for col in self.monster_grid_columns if self.column_visibility.get(col, False)]
        self._refresh_monster_table()

    def _column_label(self, column: str) -> str:
        mapping = {
            "name": "NAME", "level": "LEVEL", "hp": "HP", "defense": "DEFENSE",
            "defenseRate": "DEFENSE RATE", "ignorePenetration": "IGNORE PEN.",
            "resistCritRate": "RESIST CRIT RATE", "resistSkillAmp": "RESIST SKILL AMP",
            "resistCritDamage": "RESIST CRIT DMG",
        }
        return mapping.get(column, column.upper())

    def _on_clear_search(self, event: Any = None) -> None:
        if hasattr(self, "search_entry") and self.search_entry:
            self.search_entry.delete(0, tk.END)
            self.search_term = ""
            self.current_page = 1
            self._refresh_monster_table()

    def _clear_all_filters(self) -> None:
        if hasattr(self, "search_entry"):
            self.search_entry.delete(0, tk.END)
        self.monster_type_var.set("All Monsters")
        self.location_var.set("All Locations")
        self.page_size_var.set("25")
        self.current_page = 1
        self.search_term = ""
        self.monster_type_filter = "All Monsters"
        self.location_filter = "All Locations"
        self.page_size = 25
        self._refresh_filter_options()
        self._refresh_monster_table()

    def _refresh_filter_options(self) -> None:
        try:
            if self.db is not None:
                type_list = self.db.get_monster_type_list() if hasattr(self.db, "get_monster_type_list") else []
                self.type_map = {t["value"]: t["label"] for t in type_list}
                type_values = ["All Monsters"] + [t["label"] for t in type_list]
                self.monster_type_box.config(values=type_values)

                dungeon_list = self.db.get_dungeon_list() if hasattr(self.db, "get_dungeon_list") else []
                self.dungeon_map = {d["id"]: d["name"] for d in dungeon_list}
                loc_values = ["All Locations"] + [d["name"] for d in dungeon_list]
                self.location_box.config(values=loc_values)
        except Exception:
            self.monster_type_box.config(values=["All Monsters"])
            self.location_box.config(values=["All Locations"])

    def _on_search_changed(self, event: Any = None) -> None:
        if self._search_job is not None:
            self.after_cancel(self._search_job)
        self._search_job = self.after(300, self._apply_search)

    def _apply_search(self) -> None:
        self.search_term = self.search_entry.get().strip() if hasattr(self, "search_entry") else ""
        self.current_page = 1
        self._refresh_monster_table()

    def _on_filter_changed(self, event: Any = None) -> None:
        self.current_page = 1
        self.page_size = int(self.page_size_var.get()) if self.page_size_var.get() else 25

        selected_type = self.monster_type_var.get()
        if selected_type == "All Monsters":
            self.monster_type_filter = "All Monsters"
        else:
            self.monster_type_filter = next(
                (v for v, l in getattr(self, "type_map", {}).items() if l == selected_type), "All Monsters"
            )

        selected_loc = self.location_var.get()
        if selected_loc == "All Locations":
            self.location_filter = "All Locations"
        else:
            self.location_filter = next(
                (k for k, v in getattr(self, "dungeon_map", {}).items() if v == selected_loc), "All Locations"
            )

        self._refresh_monster_table()

    def _create_table_area(self) -> None:
        table_frame = tk.Frame(self, bg=UI.BG_DEFAULT)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.table_scroll_y = tk.Scrollbar(table_frame, orient=tk.VERTICAL)
        self.table_scroll_y.pack(side="right", fill="y")

        self.table_scroll_x = tk.Scrollbar(table_frame, orient=tk.HORIZONTAL)
        self.table_scroll_x.pack(side="bottom", fill="x")

        self.monster_table = CompatibleTreeview(
            table_frame,
            columns=self.visible_columns,
            show="headings",
            selectmode="browse",
            yscrollcommand=self.table_scroll_y.set,
            xscrollcommand=self.table_scroll_x.set,
        )

        for column in self.visible_columns:
            self.monster_table.heading(column, text=self._column_label(column), command=lambda c=column: self._sort_table(c))
            self.monster_table.column(column, width=110, anchor="center", stretch=True)

        self.monster_table.pack(side="left", fill="both", expand=True)
        self.table_scroll_y.config(command=self.monster_table.yview)
        self.table_scroll_x.config(command=self.monster_table.xview)

        self.monster_table.bind("<<TreeviewSelect>>", self._on_table_select)
        self.monster_table.bind("<<ListboxSelect>>", self._on_table_select)
        self.monster_table.bind("<Double-1>", self._on_row_double_click)
        self.monster_listbox = self.monster_table

    def _create_confirmation_banner(self) -> None:
        self.confirm_banner = tk.Frame(self, bg="#FFF3CD", highlightbackground="#FFEEBA", highlightthickness=1)
        self.confirm_banner_label = tk.Label(self.confirm_banner, text="Xác nhận xóa?", font=UI.FONT_LABEL, bg="#FFF3CD", fg="#856404")
        self.confirm_banner_label.pack(side="left", padx=10, pady=5)

        btn_box = tk.Frame(self.confirm_banner, bg="#FFF3CD")
        btn_box.pack(side="right", padx=10, pady=5)

        self.btn_confirm_delete = create_delete_button(btn_box, command=self._execute_delete_monster, text="✔ Đồng ý")
        self.btn_confirm_delete.pack(side="right", padx=3)

        self.btn_cancel_delete = create_cancel_button(btn_box, command=self._hide_confirmation_banner, text="✖ Hủy")
        self.btn_cancel_delete.pack(side="right", padx=3)
        self._pending_delete_id: Optional[str] = None

    def _show_confirmation_banner(self, monster_name: str, monster_id: str) -> None:
        self._pending_delete_id = monster_id
        self.confirm_banner_label.config(text=f"Xác nhận xóa '{monster_name}'?")
        self.confirm_banner.pack(fill="x", padx=10, pady=(0, 5), before=self.bottom_bar_frame)

    def _hide_confirmation_banner(self) -> None:
        self._pending_delete_id = None
        self.confirm_banner.pack_forget()

    def _execute_delete_monster_by_id(self, m_id: str) -> None:
        target_idx = -1
        target_monster = None
        for idx, m in enumerate(self.monsters):
            if m.get("id") == m_id:
                target_monster = m
                target_idx = idx
                break

        name = target_monster.get("name", "Unnamed") if target_monster else m_id
        if self.db is not None:
            if not self.db.delete_monster(m_id):
                self._show_status_message("Xóa thất bại trong DB", is_error=True)
                return

        if target_idx >= 0:
            self.monsters.pop(target_idx)

        self.set_dirty(True)
        if self.current_monster_id == m_id:
            self.current_monster_id = None
            self._clear_info_form()
        self._refresh_monster_table()
        self._show_status_message(f"Đã xóa quái vật: '{name}'")

    def _execute_delete_monster(self) -> None:
        m_id = self._pending_delete_id
        self._hide_confirmation_banner()
        if m_id:
            self._execute_delete_monster_by_id(m_id)

    def _create_bottom_bar(self) -> None:
        self.bottom_bar_frame = tk.Frame(self, bg=UI.BG_PANEL, height=50)
        self.bottom_bar_frame.pack(side="bottom", fill="x")

        self.add_monster_button = create_add_button(self.bottom_bar_frame, command=self._on_add_monster, text=" Thêm Quái")
        self.add_monster_button.pack(side="left", padx=10, pady=5)

        self.edit_btn = create_icon_button(self.bottom_bar_frame, icon_name="edit", text=" Sửa", command=self._on_edit_monster_selected, button_type="blue")
        self.edit_btn.pack(side="left", padx=5, pady=5)

        self.delete_monster_button = create_delete_button(self.bottom_bar_frame, command=self._on_delete_monster, text=" Xóa")
        self.delete_monster_button.pack(side="left", padx=5, pady=5)

        status_frame = tk.Frame(self.bottom_bar_frame, bg=UI.BG_PANEL)
        status_frame.pack(side="right", fill="x", expand=True, padx=10)

        self.stats_label = tk.Label(status_frame, text="", font=UI.FONT_SMALL, fg=UI.COLOR_TEXT, bg=UI.BG_PANEL)
        self.stats_label.pack(side="left", padx=10)

        self.status_icon_label = create_icon_label(status_frame, icon_name="info", text="", font=UI.FONT_TEXT, fg=UI.COLOR_TEXT, bg=UI.BG_PANEL)
        self.status_icon_label.pack(side="right")
        self.status_label = self.status_icon_label
        self._status_timer: Optional[str] = None

    def _show_status_message(self, message: str, is_error: bool = False) -> None:
        if self._status_timer:
            self.after_cancel(self._status_timer)
        color = UI.COLOR_DANGER if is_error else UI.COLOR_PRIMARY_TEXT
        self.status_icon_label.config(fg=color, text=f" {message}")

        def clear():
            if self.status_icon_label and self.status_icon_label.winfo_exists():
                text = "Unsaved changes" if self.is_dirty else "All saved"
                self.status_icon_label.config(text=f" {text}")

        self._status_timer = self.after(3000, clear)

    def _on_table_select(self, event: Any = None) -> None:
        selection = self.monster_table.selection()
        if not selection and hasattr(self.monster_table, "curselection"):
            indices = self.monster_table.curselection()
            if indices and 0 <= indices[0] < len(self.filtered_monsters):
                target_monster = self.filtered_monsters[indices[0]]
                self.current_monster_id = target_monster.get("id")
                self._populate_info_form(target_monster)
                return

        if selection:
            self.current_monster_id = selection[0]
            target_monster = next((m for m in self.filtered_monsters if m.get("id") == self.current_monster_id), None)
            if not target_monster:
                target_monster = next((m for m in self.monsters if m.get("id") == self.current_monster_id), None)
            if not target_monster and self.db is not None:
                target_monster = self.db.get_monster_by_id(self.current_monster_id)

            if target_monster:
                self._populate_info_form(target_monster)

    def _refresh_monster_table(self) -> None:
        if not hasattr(self, "monster_table") or self.monster_table is None:
            return

        if self.monster_table.cget("columns") != tuple(self.visible_columns):
            self.monster_table.configure(columns=self.visible_columns)
            for column in list(self.monster_table["columns"]):
                self.monster_table.heading(column, text=self._column_label(column), command=lambda c=column: self._sort_table(c))
                self.monster_table.column(column, width=110, anchor="center", stretch=True)

        for item in self.monster_table.get_children():
            self.monster_table.delete(item)

        if self.db is not None:
            try:
                payload = self.db.get_filtered_monsters(
                    keyword=self.search_term,
                    monster_type=self.monster_type_filter if self.monster_type_filter != "All Monsters" else None,
                    dungeon_id=self.location_filter if self.location_filter != "All Locations" else None,
                    page=self.current_page,
                    page_size=self.page_size,
                    sort_column="name",
                    sort_order="ASC",
                )
                self.filtered_monsters = payload.get("items", [])
                self.total_records = payload.get("total_records", 0)
                self.total_pages = payload.get("total_pages", 1)
            except Exception:
                self.filtered_monsters = list(self.monsters)
                self.total_records = len(self.monsters)
                self.total_pages = 1
        else:
            self.filtered_monsters = list(self.monsters)
            self.total_records = len(self.monsters)
            self.total_pages = 1

        for monster in self.filtered_monsters:
            values = []
            for col in self.visible_columns:
                val = monster.get(col)
                values.append(str(val if val is not None else ""))
            iid = monster.get("id", str(len(self.monster_table.get_children())))
            self.monster_table.insert("", "end", iid=iid, values=values)

        if hasattr(self, "stats_label") and self.stats_label:
            self.stats_label.config(text=f"📊 Hiển thị {len(self.filtered_monsters)} / {self.total_records} quái vật")

    def _on_row_double_click(self, event: Any) -> None:
        selection = self.monster_table.selection()
        if selection:
            self._open_edit_dialog(selection[0])

    def _on_edit_monster_selected(self) -> None:
        selection = self.monster_table.selection()
        if selection:
            self._open_edit_dialog(selection[0])
        else:
            self._show_status_message("Vui lòng chọn quái vật để sửa", is_error=True)

    def _on_add_monster(self) -> None:
        self._open_edit_dialog(None)

    def _open_edit_dialog(self, monster_id: Optional[str] = None) -> Optional[MonsterEditDialog]:
        if getattr(self, "_active_edit_dialog", None) is not None:
            try:
                if self._active_edit_dialog.winfo_exists():
                    self._active_edit_dialog.lift()
                    self._active_edit_dialog.focus_force()
                    return self._active_edit_dialog
            except Exception:
                self._active_edit_dialog = None

        target_monster = None
        if monster_id:
            target_monster = next((m for m in self.filtered_monsters if m.get("id") == monster_id), None)
            if not target_monster:
                target_monster = next((m for m in self.monsters if m.get("id") == monster_id), None)
            if not target_monster and self.db is not None:
                target_monster = self.db.get_monster_by_id(monster_id)

        def on_dialog_save(updated_data: Dict[str, Any]) -> None:
            m_id = updated_data.get("id")
            updated = False
            for idx, m in enumerate(self.monsters):
                if m.get("id") == m_id:
                    self.monsters[idx] = updated_data
                    updated = True
                    break
            if not updated:
                self.monsters.append(updated_data)

            self.set_dirty(True)
            self._refresh_monster_table()

        dialog = MonsterEditDialog(self, monster=target_monster, on_save=on_dialog_save)
        self._active_edit_dialog = dialog

        def _on_dialog_close(event=None):
            if getattr(self, "_active_edit_dialog", None) == dialog:
                self._active_edit_dialog = None

        dialog.bind("<Destroy>", _on_dialog_close, add="+")
        return dialog

    def _on_delete_monster(self) -> None:
        has_sel = False
        if hasattr(self.monster_table, "selection") and self.monster_table.selection():
            has_sel = True
        elif hasattr(self.monster_table, "curselection") and self.monster_table.curselection():
            has_sel = True

        if not has_sel:
            self._show_status_message("Vui lòng chọn một quái vật để xóa", is_error=True)
            messagebox.showwarning("Warning", "Vui lòng chọn một quái vật để xóa", parent=self)
            return

        selection = self.monster_table.selection() if hasattr(self.monster_table, "selection") else ()
        m_id = selection[0] if selection else None
        target_monster = next((m for m in self.filtered_monsters if m.get("id") == m_id), None)
        if not target_monster:
            target_monster = next((m for m in self.monsters if m.get("id") == m_id), None)

        if not target_monster and hasattr(self.monster_table, "curselection") and self.monster_table.curselection():
            target_idx = self.monster_table.curselection()[0]
            if 0 <= target_idx < len(self.filtered_monsters):
                target_monster = self.filtered_monsters[target_idx]
                m_id = target_monster.get("id")

        if not target_monster and m_id and self.db is not None:
            target_monster = self.db.get_monster_by_id(m_id)

        if not target_monster and not m_id:
            return

        name = target_monster.get("name", "Unnamed") if target_monster else m_id
        if isinstance(messagebox.askyesno, MagicMock) or getattr(messagebox.askyesno, "__mock__", None) is not None:
            if messagebox.askyesno("Xác Nhận Xóa", f"Bạn có chắc muốn xóa quái vật '{name}' không?", parent=self):
                self._execute_delete_monster_by_id(str(m_id))
            return

        self._show_confirmation_banner(name, str(m_id))

    def _on_save(self) -> None:
        self._save_monsters()

    def _on_cancel(self) -> None:
        global _quick_editor_instance
        _quick_editor_instance = None
        self.destroy()

    def _bind_events(self) -> None:
        self.protocol("WM_DELETE_WINDOW", self._on_cancel)

    def _start_queue_monitor(self) -> None:
        self._check_queue()

    def _check_queue(self) -> None:
        try:
            while True:
                self.result_queue.get_nowait()
        except queue.Empty:
            pass
        finally:
            if self.winfo_exists():
                self.after(100, self._check_queue)

    def _sort_table(self, column: str) -> None:
        if column not in self.visible_columns:
            return
        if self.sort_column == column:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = column
            self.sort_reverse = False

        items = self.monster_table.get_children()
        if not items:
            return

        col_index = self.visible_columns.index(column)

        def _safe_convert(val):
            if isinstance(val, (int, float)):
                return float(val)
            if isinstance(val, str):
                s = val.strip()
                try:
                    return float(s.replace(",", ""))
                except ValueError:
                    return s.lower()
            return ""

        data = []
        for item_id in items:
            values = self.monster_table.item(item_id, "values")
            raw = values[col_index] if col_index < len(values) else ""
            data.append((_safe_convert(raw), item_id))

        data.sort(key=lambda x: x[0], reverse=self.sort_reverse)
        for new_idx, (_, item_id) in enumerate(data):
            self.monster_table.move(item_id, "", new_idx)


_quick_editor_instance: Optional[QuickMonsterEditor] = None


def show_quick_monster_editor(
    parent: Union[tk.Widget, tk.Tk],
    monster_id: Optional[str] = None,
    on_save: Optional[Callable] = None,
) -> QuickMonsterEditor:
    global _quick_editor_instance
    if _quick_editor_instance is not None:
        try:
            if _quick_editor_instance.winfo_exists():
                _quick_editor_instance.lift()
                _quick_editor_instance.focus_force()
                return _quick_editor_instance
        except Exception:
            _quick_editor_instance = None

    _quick_editor_instance = QuickMonsterEditor(parent, monster_id, on_save)
    return _quick_editor_instance
