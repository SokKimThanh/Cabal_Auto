import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from typing import Dict, Any

from lib.ui_style_v2 import UIStyleV2 as UIStyle


class MonsterManagerFrame(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=UIStyle.THEME_BG_APP)
        self.app = app
        self.monsters = []

        self._setup_ui()
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
            self.tree.heading(col, text=self.app._t(f"col_{col.lower()}", default=col))
            self.tree.column(col, width=100, minwidth=80)

        self.tree.pack(fill="both", expand=True)

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

    def _load_monsters(self):
        try:
            self.monsters = self.app.monster_library_service.load_monsters()
            if not isinstance(self.monsters, list):
                self.monsters = []
        except Exception as e:
            self.monsters = []
            print(f"Error loading monsters: {e}")
        self._refresh_tree()

    def _refresh_tree(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for m in self.monsters:
            if isinstance(m, dict):
                values = (
                    m.get("id", ""),
                    m.get("name", "Unknown"),
                    m.get("level", 0),
                    m.get("hp", 0),
                    m.get("defense", 0),
                    m.get("type", ""),
                    m.get("dungeonId", "")
                )
                self.tree.insert("", "end", iid=str(m.get("id", str(id(m)))), values=values)

    def _save_monsters(self):
        try:
            self.app.monster_library_service.save_monsters(self.monsters)
        except Exception as e:
            messagebox.showerror(
                self.app._t("err_title", default="Lỗi"),
                self.app._t("err_save_monsters", default="Không thể lưu danh sách quái: ") + str(e),
                parent=self
            )

    def _add_monster(self):
        prompt = self.app._t("prompt_add_monster", default="Nhập thông tin (Tên, Cấp, HP, Defense, Type, Dungeon):")
        result = simpledialog.askstring(
            self.app._t("title_add_monster", default="Thêm Quái"),
            prompt,
            parent=self
        )
        if result:
            parts = [x.strip() for x in result.split(",")]
            if len(parts) >= 1:
                name = parts[0]
                level = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 1
                hp = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else 100
                defense = int(parts[3]) if len(parts) > 3 and parts[3].isdigit() else 0
                m_type = parts[4] if len(parts) > 4 else "Normal"
                dungeon = parts[5] if len(parts) > 5 else ""

                # generate id
                max_id = 0
                for m in self.monsters:
                    try:
                        m_id = int(m.get("id", 0))
                        if m_id > max_id:
                            max_id = m_id
                    except ValueError:
                        pass
                new_id = max_id + 1

                new_monster = {
                    "id": new_id,
                    "name": name,
                    "level": level,
                    "hp": hp,
                    "defense": defense,
                    "type": m_type,
                    "dungeonId": dungeon
                }

                self.monsters.append(new_monster)
                self._save_monsters()
                self._refresh_tree()

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
        target_monster = None
        for m in self.monsters:
            if str(m.get("id", "")) == m_id:
                target_monster = m
                break

        if target_monster:
            initial = f"{target_monster.get('name', '')}, {target_monster.get('level', 0)}, {target_monster.get('hp', 0)}, {target_monster.get('defense', 0)}, {target_monster.get('type', '')}, {target_monster.get('dungeonId', '')}"
            prompt = self.app._t("prompt_edit_monster", default="Sửa thông tin (Tên, Cấp, HP, Defense, Type, Dungeon):")
            result = simpledialog.askstring(
                self.app._t("title_edit_monster", default="Sửa Quái"),
                prompt,
                initialvalue=initial,
                parent=self
            )

            if result:
                parts = [x.strip() for x in result.split(",")]
                if len(parts) >= 1:
                    target_monster["name"] = parts[0]
                    target_monster["level"] = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else target_monster.get("level", 1)
                    target_monster["hp"] = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else target_monster.get("hp", 100)
                    target_monster["defense"] = int(parts[3]) if len(parts) > 3 and parts[3].isdigit() else target_monster.get("defense", 0)
                    target_monster["type"] = parts[4] if len(parts) > 4 else target_monster.get("type", "Normal")
                    target_monster["dungeonId"] = parts[5] if len(parts) > 5 else target_monster.get("dungeonId", "")

                    self._save_monsters()
                    self._refresh_tree()

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
                self.monsters.remove(target_monster)
                self._save_monsters()
                self._refresh_tree()

    def on_view_shown(self):
        self._load_monsters()

    def on_view_hidden(self):
        pass
