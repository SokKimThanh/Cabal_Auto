import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Any, List

from lib.ui_style_v2 import UIStyleV2 as UIStyle
from database import get_db, get_all_monsters_api
from dialogs.monster_edit import MonsterEditDialog

class MonsterManagerFrame(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=UIStyle.THEME_BG_APP)
        self.app = app
        self.monsters = []
        self.db = get_db()
        self.dungeon_map = {}
        self.type_map = {}

        self._setup_ui()
        self._load_reference_data()
        self._load_monsters()

    def _setup_ui(self):
        # Title Label
        title_lbl = tk.Label(
            self,
            text=self.app._t("monster_manager_title", default="Quản lý Quái vật"),
            font=(UIStyle.resolve_font_family("title"), 16, "bold"),
            bg=UIStyle.THEME_BG_APP,
            fg=UIStyle.TEXT_PRIMARY
        )
        title_lbl.pack(pady=UIStyle.SPACE_MD)

        # Treeview Area
        table_frame = tk.Frame(self, bg=UIStyle.THEME_BG_APP)
        table_frame.pack(fill="both", expand=True, padx=UIStyle.SPACE_MD, pady=UIStyle.SPACE_MD)

        self.tree_scroll_y = ttk.Scrollbar(table_frame, orient=tk.VERTICAL)
        self.tree_scroll_y.pack(side="right", fill="y")

        self.tree_scroll_x = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL)
        self.tree_scroll_x.pack(side="bottom", fill="x")

        self.columns = ("ID", "Name", "Level", "HP", "Defense", "Type", "Dungeon")
        self.tree = ttk.Treeview(
            table_frame,
            columns=self.columns,
            show="headings",
            selectmode="browse",
            yscrollcommand=self.tree_scroll_y.set,
            xscrollcommand=self.tree_scroll_x.set
        )

        self.tree_scroll_y.config(command=self.tree.yview)
        self.tree_scroll_x.config(command=self.tree.xview)

        for col in self.columns:
            self.tree.heading(col, text=self.app._t(f"col_{col.lower()}", default=col), command=lambda c=col: self._sort_treeview(c, False))
            self.tree.column(col, width=100, minwidth=80)

        self.tree.pack(fill="both", expand=True)

        self.tree.bind("<Double-1>", lambda e: self._edit_monster())

        # Bottom Bar for Actions
        bottom_bar = tk.Frame(self, bg=UIStyle.THEME_BG_PANEL, height=50)
        bottom_bar.pack(side="bottom", fill="x", pady=UIStyle.SPACE_SM)

        add_btn = tk.Button(
            bottom_bar,
            text=self.app._t("btn_add_monster", default=" Thêm"),
            command=self._add_monster,
            bg=UIStyle.ACCENT_GREEN,
            fg="white",
            relief="flat"
        )
        add_btn.pack(side="left", padx=UIStyle.SPACE_MD, pady=UIStyle.SPACE_SM)

        edit_btn = tk.Button(
            bottom_bar,
            text=self.app._t("btn_edit_monster", default=" Sửa"),
            command=self._edit_monster,
            bg=UIStyle.ACCENT_GREEN,
            fg="white",
            relief="flat"
        )
        edit_btn.pack(side="left", padx=UIStyle.SPACE_MD, pady=UIStyle.SPACE_SM)

        del_btn = tk.Button(
            bottom_bar,
            text=self.app._t("btn_del_monster", default=" Xóa"),
            command=self._delete_monster,
            bg="#dc3545",
            fg="white",
            relief="flat"
        )
        del_btn.pack(side="left", padx=UIStyle.SPACE_MD, pady=UIStyle.SPACE_SM)

        ref_btn = tk.Button(
            bottom_bar,
            text=self.app._t("btn_refresh_monster", default=" Làm mới"),
            command=self._load_monsters,
            bg=UIStyle.BG_ELEVATED,
            fg=UIStyle.TEXT_PRIMARY,
            relief="flat"
        )
        ref_btn.pack(side="right", padx=UIStyle.SPACE_MD, pady=UIStyle.SPACE_SM)

    def _sort_treeview(self, col, reverse):
        l = [(self.tree.set(k, col), k) for k in self.tree.get_children('')]
        try:
            l.sort(key=lambda t: float(t[0]), reverse=reverse)
        except ValueError:
            l.sort(reverse=reverse)

        for index, (val, k) in enumerate(l):
            self.tree.move(k, '', index)

        self.tree.heading(col, command=lambda: self._sort_treeview(col, not reverse))

    def _load_reference_data(self):
        try:
            types = self.db.get_monster_types()
            for t in types:
                self.type_map[str(t['value'])] = t['label']

            dungeons = self.db.get_dungeons()
            for d in dungeons:
                self.dungeon_map[str(d['id'])] = d['name']
        except Exception as e:
            print(f"Error loading reference data: {e}")

    def _load_monsters(self):
        try:
            res = self.db.get_filtered_monsters(limit=5000)
            self.monsters = res.get('items', [])
        except Exception as e:
            self.monsters = []
            print(f"Error loading monsters: {e}")
        self._refresh_tree()

    def _refresh_tree(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for m in self.monsters:
            if isinstance(m, dict):
                m_type = m.get("serverBossType")
                type_label = self.type_map.get(str(m_type), "Normal") if m_type is not None else "Normal"

                dungeon_id = m.get("dungeonId")
                dungeon_name = self.dungeon_map.get(str(dungeon_id), str(dungeon_id)) if dungeon_id else ""

                values = (
                    m.get("id", ""),
                    m.get("name", "Unknown"),
                    m.get("level", 0),
                    m.get("hp", 0),
                    m.get("defense", 0),
                    type_label,
                    dungeon_name
                )
                self.tree.insert("", "end", iid=str(m.get("id", str(id(m)))), values=values)

    def get_all_monsters_for_validation(self) -> List[Dict[str, Any]]:
        return self.monsters

    def _save_monster_callback(self, data: Dict[str, Any]):
        try:
            success = self.db.insert_or_update_monster(data)
            if success:
                self._load_monsters()
            else:
                messagebox.showerror(
                    self.app._t("err_title", default="Lỗi"),
                    self.app._t("err_save_monsters", default="Không thể lưu quái vật vào CSDL."),
                    parent=self
                )
        except Exception as e:
            messagebox.showerror(
                self.app._t("err_title", default="Lỗi"),
                f"Exception saving monster: {e}",
                parent=self
            )

    def _add_monster(self):
        new_data = {
            "id": "",
            "name": "",
            "level": 1,
            "hp": 100,
            "defense": 0
        }
        MonsterEditDialog(self, new_data, self._save_monster_callback)

    def _edit_monster(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning(
                self.app._t("warn_title", default="Cảnh báo"),
                self.app._t("warn_no_sel", default="Vui lòng chọn quái vật để sửa"),
                parent=self
            )
            return

        m_id = selected[0]
        target_monster = self.db.get_monster_by_id(m_id)

        if target_monster:
            MonsterEditDialog(self, target_monster, self._save_monster_callback)
        else:
            messagebox.showerror(
                self.app._t("err_title", default="Lỗi"),
                f"Không tìm thấy quái vật ID: {m_id} trong cơ sở dữ liệu.",
                parent=self
            )

    def _delete_monster(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning(
                self.app._t("warn_title", default="Cảnh báo"),
                self.app._t("warn_no_sel", default="Vui lòng chọn quái vật để xóa"),
                parent=self
            )
            return

        m_id = selected[0]
        target_monster = None
        for m in self.monsters:
            if str(m.get("id", "")) == m_id:
                target_monster = m
                break

        if target_monster:
            name = target_monster.get('name', 'Unknown')
            confirm = messagebox.askyesno(
                self.app._t("confirm_del_title", default="Xác nhận xóa"),
                self.app._t("confirm_del_msg", default=f"Bạn có chắc muốn xóa quái vật '{name}' không?"),
                parent=self
            )

            if confirm:
                success = self.db.delete_monster(m_id)
                if success:
                    self._load_monsters()
                else:
                    messagebox.showerror(
                        self.app._t("err_title", default="Lỗi"),
                        "Không thể xóa quái vật từ CSDL.",
                        parent=self
                    )

    def on_view_shown(self):
        self._load_monsters()

    def on_view_hidden(self):
        pass
