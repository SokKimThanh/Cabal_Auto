import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Dict, Any, Callable, List
import queue
import json
from pathlib import Path

from ui.components.base.responsive_grid_base import ResponsiveGridBase
from lib.ui_style_v2 import UIStyleV2 as UIStyle

# Import module dependencies from monster_manager_win where possible
# This prevents code duplication and relies on the existing mature functions
try:
    from ui.windows.monster_manager_win import (
        ensure_unique_monster_id, i18n_t, get_lang, DataSyncManager, attach_i18n_tooltip,
        get_button_config, create_icon_button, create_icon_label, create_add_button,
        create_delete_button, create_save_button, create_cancel_button, create_refresh_button,
        set_button_enabled, get_db, DB_MANAGER
    )
except ImportError:
    pass

try:
    from dialogs.display_settings import DisplaySettingsDialog
    from dialogs.monster_edit import MonsterEditDialog
except ImportError:
    pass


class MonsterManagerFrame(ResponsiveGridBase):
    """
    Main Monster Manager Workspace View.
    Migrated from MonsterManagerWin to act as a seamless workspace component.
    """

    def __init__(self, parent, app, **kwargs):
        kwargs.setdefault("bg", UIStyle.BG_BASE)
        super().__init__(parent, **kwargs)
        self.app = app

        # State variables
        self.sort_column = "name"
        self.sort_reverse = False
        self.monsters: List[Dict[str, Any]] = []
        self.filtered_monsters: List[Dict[str, Any]] = []
        self.current_monster_id: Optional[str] = None
        self.is_dirty = False
        self.is_monster_dirty = False

        self.db = get_db() if 'get_db' in globals() and get_db is not None else None

        # Pagination & Filtering
        self.current_page = 1
        self.items_per_page = 100
        self.search_var = tk.StringVar()
        self.filter_var = tk.StringVar(value="all")

        self.monster_grid_columns = [
            "id", "name", "level", "exp", "hp", "defense",
            "damage_per_hit", "priority", "template_count"
        ]

        self.visible_columns = {col: True for col in self.monster_grid_columns}
        self.visible_columns["id"] = False

        self._load_monsters()
        self._build_ui()
        self._bind_events()
        self._refresh_monster_table()

    def _load_monsters(self) -> None:
        if self.db:
            try:
                monsters_data = self.db.execute_query("SELECT * FROM monsters")
                if monsters_data:
                    self.monsters = [dict(m) for m in monsters_data]
                    for m in self.monsters:
                        ensure_unique_monster_id(m)

                    self.filtered_monsters = self.monsters.copy()
                    return
            except Exception as e:
                print(f"[MonsterManagerFrame] DB Load Error: {e}")

        # Fallback to app monsters if db is unavailable
        if hasattr(self.app, 'monsters') and self.app.monsters:
            self.monsters = [m.copy() for m in self.app.monsters]
            for m in self.monsters:
                ensure_unique_monster_id(m)
            self.filtered_monsters = self.monsters.copy()

    def _save_monsters(self) -> bool:
        try:
            if hasattr(self.app, 'monsters'):
                self.app.monsters = [m.copy() for m in self.monsters]
                if hasattr(self.app, 'monster_service'):
                    self.app.monster_service.save_monsters(self.app.monsters)

            self.set_dirty(False)
            self._show_status_message(self.app._t("save_success", default="Lưu thành công"))
            return True
        except Exception as e:
            self._show_status_message(f"Error: {e}", is_error=True)
            return False

    def set_dirty(self, value: bool = True) -> None:
        self.is_dirty = value
        self._update_dirty_state_ui()

    def _update_dirty_state_ui(self) -> None:
        if not hasattr(self, 'btn_save'): return

        if self.is_dirty:
            self.status_badge.config(
                text="⚠️ Unsaved Changes",
                fg=UIStyle.COLOR_WARNING,
            )
            set_button_enabled(self.btn_save, True)
        else:
            self.status_badge.config(
                text="✓ All Saved",
                fg=UIStyle.COLOR_SUCCESS,
            )
            set_button_enabled(self.btn_save, False)

    def _build_ui(self) -> None:
        content = self.get_content_frame()
        content.grid_rowconfigure(2, weight=1)
        content.grid_columnconfigure(0, weight=1)

        self._create_top_panel(content)
        self._create_search_bar(content)
        self._create_table_area(content)
        self._create_confirmation_banner(content)
        self._create_bottom_bar(content)

    def _create_top_panel(self, parent) -> None:
        top_frame = tk.Frame(parent, bg=UIStyle.BG_BASE, height=50)
        top_frame.grid(row=0, column=0, sticky="ew")
        top_frame.pack_propagate(False)

        header_title = tk.Label(
            top_frame,
            text=f"👹 {self.app._t('quick_editor_title', default='Quản Lý Quái Vật')}",
            font=UIStyle.FONT_TITLE,
            fg=UIStyle.TEXT_PRIMARY,
            bg=UIStyle.BG_BASE,
        )
        header_title.pack(side="left", padx=15, pady=10)

        btn_frame = tk.Frame(top_frame, bg=UIStyle.BG_BASE)
        btn_frame.pack(side="right", padx=15, pady=10)

        self.status_badge = tk.Label(
            btn_frame,
            text="",
            font=UIStyle.FONT_SMALL,
            bg=UIStyle.BG_BASE,
            fg=UIStyle.TEXT_PRIMARY,
        )
        self.status_badge.pack(side="left", padx=(0, 15))

        self.btn_save = create_save_button(
            btn_frame,
            command=self._on_save,
            text=self.app._t("btn_save_all", default="Lưu Tất Cả"),
        )
        self.btn_save.pack(side="left", padx=5)
        set_button_enabled(self.btn_save, False)

    def _create_search_bar(self, parent) -> None:
        search_frame = tk.Frame(parent, bg=UIStyle.BG_SURFACE)
        search_frame.grid(row=1, column=0, sticky="ew", padx=UIStyle.SPACE_MD, pady=UIStyle.SPACE_SM)

        tk.Label(
            search_frame,
            text="🔍",
            bg=UIStyle.BG_SURFACE,
            fg=UIStyle.TEXT_MUTED,
            font=UIStyle.FONT_BODY,
        ).pack(side="left", padx=(10, 5))

        self.search_entry = ttk.Entry(
            search_frame, textvariable=self.search_var, width=40, font=UIStyle.FONT_BODY
        )
        self.search_entry.pack(side="left", padx=(0, 10), pady=8)
        self.search_var.trace_add("write", self._on_search_changed)

        clear_btn = ttk.Button(
            search_frame,
            text="✕",
            width=3,
            command=self._on_clear_search,
        )
        clear_btn.pack(side="left", padx=(0, 15))

        tk.Label(
            search_frame,
            text=self.app._t("filter_level", default="Cấp độ:"),
            bg=UIStyle.BG_SURFACE,
            fg=UIStyle.TEXT_SECONDARY,
            font=UIStyle.FONT_BODY,
        ).pack(side="left", padx=(10, 5))

        self.filter_combo = ttk.Combobox(
            search_frame,
            textvariable=self.filter_var,
            state="readonly",
            width=15,
            font=UIStyle.FONT_BODY,
        )
        self.filter_combo.pack(side="left", padx=(0, 10))
        self.filter_var.trace_add("write", self._on_filter_changed)
        self._refresh_filter_options()

    def _create_table_area(self, parent) -> None:
        table_frame = tk.Frame(parent, bg=UIStyle.BG_BASE)
        table_frame.grid(row=2, column=0, sticky="nsew", padx=UIStyle.SPACE_MD)

        # In a ResponsiveGridBase, the outer container already scrolls, but a treeview
        # can also scroll independently. We allow it to expand.
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        style = ttk.Style()
        style.configure(
            "Monster.Treeview",
            font=UIStyle.FONT_BODY,
            rowheight=30,
            background=UIStyle.BG_SURFACE,
            foreground=UIStyle.TEXT_PRIMARY,
            fieldbackground=UIStyle.BG_SURFACE,
        )
        style.configure(
            "Monster.Treeview.Heading",
            font=UIStyle.FONT_SECTION,
            background=UIStyle.BG_BASE,
            foreground=UIStyle.TEXT_PRIMARY,
        )
        style.map("Monster.Treeview", background=[("selected", UIStyle.COLOR_PRIMARY)])

        self.tree_scroll = ttk.Scrollbar(table_frame)
        self.tree_scroll.grid(row=0, column=1, sticky="ns")

        self.tree = ttk.Treeview(
            table_frame,
            columns=self.monster_grid_columns,
            show="headings",
            style="Monster.Treeview",
            yscrollcommand=self.tree_scroll.set,
        )
        self.tree.grid(row=0, column=0, sticky="nsew")
        self.tree_scroll.config(command=self.tree.yview)

        self._update_column_headers()
        self.tree.bind("<<TreeviewSelect>>", self._on_table_select)
        self.tree.bind("<Double-1>", self._on_row_double_click)
        self.tree.bind("<Delete>", lambda e: self._on_delete_monster())

    def _create_confirmation_banner(self, parent) -> None:
        self.confirm_banner = tk.Frame(parent, bg="#ffebee", height=40)
        self.confirm_banner.pack_propagate(False)
        self.confirm_banner_label = tk.Label(
            self.confirm_banner,
            text="",
            bg="#ffebee",
            fg="#c62828",
            font=UIStyle.FONT_BODY,
        )
        self.confirm_banner_label.pack(side="left", padx=15, pady=10)

        btn_frame = tk.Frame(self.confirm_banner, bg="#ffebee")
        btn_frame.pack(side="right", padx=15)

        ttk.Button(btn_frame, text="Yes, Delete", command=self._execute_delete_monster).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Cancel", command=self._hide_confirmation_banner).pack(side="left", padx=5)

    def _create_bottom_bar(self, parent) -> None:
        bottom_frame = tk.Frame(parent, bg=UIStyle.BG_SURFACE, height=60)
        bottom_frame.grid(row=4, column=0, sticky="ew", padx=UIStyle.SPACE_MD, pady=UIStyle.SPACE_SM)
        bottom_frame.pack_propagate(False)

        action_frame = tk.Frame(bottom_frame, bg=UIStyle.BG_SURFACE)
        action_frame.pack(side="left", padx=15, pady=12)

        self.btn_add = create_add_button(
            action_frame,
            command=self._on_add_monster,
            text=self.app._t("btn_add_monster", default="Thêm Quái"),
        )
        self.btn_add.pack(side="left", padx=5)

        self.btn_edit = create_add_button(
            action_frame,
            command=self._on_edit_monster_selected,
            text=self.app._t("btn_edit", default="Sửa"),
        )
        self.btn_edit.pack(side="left", padx=5)
        set_button_enabled(self.btn_edit, False)

        self.btn_delete = create_delete_button(
            action_frame,
            command=self._on_delete_monster,
            text=self.app._t("btn_delete", default="Xóa"),
        )
        self.btn_delete.pack(side="left", padx=5)
        set_button_enabled(self.btn_delete, False)

        self.status_bar_label = tk.Label(
            bottom_frame,
            text="Ready",
            bg=UIStyle.BG_SURFACE,
            fg=UIStyle.TEXT_MUTED,
            font=UIStyle.FONT_SMALL,
        )
        self.status_bar_label.pack(side="right", padx=15, pady=20)

    def _update_column_headers(self) -> None:
        display_columns = []
        for col in self.monster_grid_columns:
            if self.visible_columns.get(col, True):
                display_columns.append(col)
                self.tree.heading(
                    col,
                    text=self._column_label(col) + (" ▼" if self.sort_column == col and not self.sort_reverse else " ▲" if self.sort_column == col else ""),
                    command=lambda c=col: self._sort_table(c),
                )
                width = 150 if col == "name" else 100
                self.tree.column(col, width=width, minwidth=50, anchor="w" if col == "name" else "center")

        self.tree["displaycolumns"] = display_columns

    def _column_label(self, column: str) -> str:
        mapping = {
            "id": "ID",
            "name": self.app._t("col_name", default="Tên"),
            "level": self.app._t("col_level", default="Cấp độ"),
            "exp": "EXP",
            "hp": "HP",
            "defense": "DEF",
            "damage_per_hit": "DMG",
            "priority": self.app._t("col_priority", default="Ưu tiên"),
            "template_count": "Templates",
        }
        return mapping.get(column, column)

    def _refresh_filter_options(self) -> None:
        levels = set()
        for m in self.monsters:
            lv = m.get("level")
            if lv: levels.add(str(lv))

        options = ["all"] + sorted(list(levels))
        self.filter_combo["values"] = options

    def _on_search_changed(self, *args):
        self._apply_search()

    def _on_filter_changed(self, *args):
        self._apply_search()

    def _on_clear_search(self):
        self.search_var.set("")

    def _apply_search(self):
        term = self.search_var.get().lower()
        flt = self.filter_var.get()

        self.filtered_monsters = []
        for m in self.monsters:
            match_term = term in str(m.get("name", "")).lower() or term in str(m.get("id", "")).lower()
            match_flt = flt == "all" or str(m.get("level", "")) == flt

            if match_term and match_flt:
                self.filtered_monsters.append(m)

        self._refresh_monster_table()

    def _refresh_monster_table(self) -> None:
        self.tree.delete(*self.tree.get_children())

        for m in self.filtered_monsters:
            values = []
            for col in self.monster_grid_columns:
                if col == "template_count":
                    count = len(m.get("templates", []))
                    values.append(str(count))
                else:
                    values.append(str(m.get(col, "")))

            self.tree.insert("", "end", iid=m.get("id"), values=values)

        self._update_column_headers()

    def _sort_table(self, column: str) -> None:
        if self.sort_column == column:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = column
            self.sort_reverse = False

        def sort_key(m):
            val = m.get(column, "")
            if column == "template_count":
                return len(m.get("templates", []))
            try:
                return float(val) if val else 0
            except ValueError:
                return str(val).lower()

        self.filtered_monsters.sort(key=sort_key, reverse=self.sort_reverse)
        self._refresh_monster_table()

    def _on_table_select(self, event=None) -> None:
        selection = self.tree.selection()
        if selection:
            set_button_enabled(self.btn_edit, True)
            set_button_enabled(self.btn_delete, True)
            self.current_monster_id = selection[0]
        else:
            set_button_enabled(self.btn_edit, False)
            set_button_enabled(self.btn_delete, False)
            self.current_monster_id = None

    def _on_row_double_click(self, event) -> None:
        self._on_edit_monster_selected()

    def _on_add_monster(self) -> None:
        if 'MonsterEditDialog' in globals():
            dialog = MonsterEditDialog(self, monster=None, title=self.app._t("btn_add_monster", default="Thêm Quái"))
            if dialog.result:
                ensure_unique_monster_id(dialog.result)
                self.monsters.append(dialog.result)
                self.set_dirty(True)
                self._apply_search()
                self._refresh_filter_options()
        else:
            messagebox.showinfo("Not Available", "Monster Edit Dialog module not found.")

    def _on_edit_monster_selected(self) -> None:
        if not self.current_monster_id: return

        monster_to_edit = None
        for m in self.monsters:
            if m.get("id") == self.current_monster_id:
                monster_to_edit = m
                break

        if monster_to_edit and 'MonsterEditDialog' in globals():
            dialog = MonsterEditDialog(self, monster=monster_to_edit.copy(), title=self.app._t("btn_edit", default="Sửa"))
            if dialog.result:
                # Update existing
                for i, m in enumerate(self.monsters):
                    if m.get("id") == self.current_monster_id:
                        self.monsters[i] = dialog.result
                        break
                self.set_dirty(True)
                self._apply_search()

    def _on_delete_monster(self) -> None:
        if not self.current_monster_id: return

        monster_name = "Unknown"
        for m in self.monsters:
            if m.get("id") == self.current_monster_id:
                monster_name = m.get("name", "Unknown")
                break

        self._show_confirmation_banner(monster_name, self.current_monster_id)

    def _show_confirmation_banner(self, monster_name: str, monster_id: str) -> None:
        self.monster_to_delete = monster_id
        self.confirm_banner_label.config(text=f"Xóa quái vật '{monster_name}'? Hành động này không thể hoàn tác.")
        self.confirm_banner.grid(row=3, column=0, sticky="ew", padx=UIStyle.SPACE_MD)

    def _hide_confirmation_banner(self) -> None:
        self.confirm_banner.grid_remove()
        self.monster_to_delete = None

    def _execute_delete_monster(self) -> None:
        if hasattr(self, 'monster_to_delete') and self.monster_to_delete:
            self.monsters = [m for m in self.monsters if m.get("id") != self.monster_to_delete]
            self.set_dirty(True)
            self._apply_search()
            self._hide_confirmation_banner()
            self._show_status_message("Monster deleted.")

    def _on_save(self) -> None:
        self._save_monsters()

    def _show_status_message(self, message: str, is_error: bool = False) -> None:
        if hasattr(self, 'status_bar_label'):
            self.status_bar_label.config(text=message, fg=UIStyle.COLOR_ERROR if is_error else UIStyle.TEXT_PRIMARY)
            self.after(3000, lambda: self.status_bar_label.config(text="Ready", fg=UIStyle.TEXT_MUTED))

    def _bind_events(self) -> None:
        pass

    def on_view_shown(self):
        """Lifecycle hook called when view becomes visible."""
        # Refresh to sync with any changes made outside
        self._load_monsters()
        self._refresh_filter_options()
        self._apply_search()
        self._update_dirty_state_ui()

    def on_view_hidden(self):
        """Lifecycle hook called when view becomes hidden."""
        # Optional: Ask to save if dirty
        if self.is_dirty:
            pass
