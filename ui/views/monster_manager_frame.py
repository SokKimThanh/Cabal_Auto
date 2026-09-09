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

        # State phân trang và lọc
        self.current_page = 1
        self.page_size = 25
        self.total_pages = 1
        self.total_records = 0
        self.keyword = ""
        self.monster_type_filter = "All Monsters"
        self.dungeon_filter = "All Locations"

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

        self._create_search_bar()

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

        self._create_pagination_bar()

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
            command=self._on_refresh,
            bg=UIStyle.BG_ELEVATED,
            fg=UIStyle.TEXT_PRIMARY,
            relief="flat"
        )
        ref_btn.pack(side="right", padx=UIStyle.SPACE_MD, pady=UIStyle.SPACE_SM)

    def _create_search_bar(self) -> None:
        search_frame = tk.Frame(self, bg=UIStyle.THEME_BG_PANEL)
        search_frame.pack(fill="x", padx=UIStyle.SPACE_MD, pady=(UIStyle.SPACE_SM, 0))

        # Keyword Search
        lbl_search = tk.Label(search_frame, text=self.app._t("search_label", default="Tìm kiếm:"), bg=UIStyle.THEME_BG_PANEL, fg=UIStyle.TEXT_PRIMARY)
        lbl_search.grid(row=0, column=0, padx=(5, 5), pady=5, sticky="w")

        self.search_entry = tk.Entry(search_frame, font=(UIStyle.resolve_font_family("text"), 10))
        self.search_entry.grid(row=0, column=1, sticky="ew", padx=(0, 5), pady=5)
        self.search_entry.bind("<KeyRelease>", self._on_search_changed)
        self.search_entry.bind("<Escape>", self._on_clear_search)

        # Monster Type
        self.monster_type_var = tk.StringVar(value="All Monsters")
        self.monster_type_box = ttk.Combobox(search_frame, textvariable=self.monster_type_var, state="readonly", width=15)
        self.monster_type_box.grid(row=0, column=2, sticky="ew", padx=(0, 5), pady=5)
        self.monster_type_box.bind("<<ComboboxSelected>>", self._on_filter_changed)

        # Location / Dungeon
        self.location_var = tk.StringVar(value="All Locations")
        self.location_box = ttk.Combobox(search_frame, textvariable=self.location_var, state="readonly", width=15)
        self.location_box.grid(row=0, column=3, sticky="ew", padx=(0, 5), pady=5)
        self.location_box.bind("<<ComboboxSelected>>", self._on_filter_changed)

        # Page size
        self.page_size_var = tk.StringVar(value="25")
        self.page_size_box = ttk.Combobox(search_frame, textvariable=self.page_size_var, state="readonly", width=5, values=["25", "50", "100", "200"])
        self.page_size_box.grid(row=0, column=4, sticky="ew", padx=(0, 5), pady=5)
        self.page_size_box.bind("<<ComboboxSelected>>", self._on_filter_changed)

        search_frame.columnconfigure(1, weight=1)

    def _create_pagination_bar(self) -> None:
        page_frame = tk.Frame(self, bg=UIStyle.THEME_BG_PANEL)
        page_frame.pack(fill="x", padx=UIStyle.SPACE_MD, pady=(0, UIStyle.SPACE_SM))

        self.stats_label = tk.Label(page_frame, text="", bg=UIStyle.THEME_BG_PANEL, fg=UIStyle.TEXT_SECONDARY)
        self.stats_label.pack(side="left", padx=5, pady=5)

        # Controls on right
        controls_frame = tk.Frame(page_frame, bg=UIStyle.THEME_BG_PANEL)
        controls_frame.pack(side="right", padx=5)

        self.btn_prev_page = tk.Button(controls_frame, text="<", command=self._on_prev_page, bg=UIStyle.BG_ELEVATED, fg=UIStyle.TEXT_PRIMARY)
        self.btn_prev_page.pack(side="left", padx=2)

        self.page_entry = tk.Entry(controls_frame, width=4, justify="center")
        self.page_entry.pack(side="left", padx=2)
        self.page_entry.bind("<Return>", lambda e: self._go_to_page_from_entry())

        self.btn_next_page = tk.Button(controls_frame, text=">", command=self._on_next_page, bg=UIStyle.BG_ELEVATED, fg=UIStyle.TEXT_PRIMARY)
        self.btn_next_page.pack(side="left", padx=2)

    def _sort_treeview(self, col, reverse):
        l = [(self.tree.set(k, col), k) for k in self.tree.get_children('')]
        try:
            l.sort(key=lambda t: float(t[0]), reverse=reverse)
        except ValueError:
            l.sort(reverse=reverse)

        for index, (val, k) in enumerate(l):
            self.tree.move(k, '', index)

        self.tree.heading(col, command=lambda: self._sort_treeview(col, not reverse))


    def _on_search_changed(self, event=None) -> None:
        if hasattr(self, "_search_timer"):
            self.after_cancel(self._search_timer)
        self._search_timer = self.after(500, self._apply_search)

    def _apply_search(self) -> None:
        self.keyword = self.search_entry.get().strip()
        self.current_page = 1
        self._load_monsters()

    def _on_clear_search(self, event=None) -> None:
        self.search_entry.delete(0, tk.END)
        self.keyword = ""
        self.current_page = 1
        self._load_monsters()

    def _on_refresh(self) -> None:
        self.search_entry.delete(0, tk.END)
        self.keyword = ""
        self.monster_type_var.set("All Monsters")
        self.location_var.set("All Locations")
        self.page_size_var.set("25")
        self.monster_type_filter = "All Monsters"
        self.dungeon_filter = "All Locations"
        self.page_size = 25
        self.current_page = 1
        self._load_monsters()

    def _on_filter_changed(self, event=None) -> None:
        self.monster_type_filter = self.monster_type_var.get()
        self.dungeon_filter = self.location_var.get()
        self.page_size = int(self.page_size_var.get())
        self.current_page = 1
        self._load_monsters()

    def _on_prev_page(self) -> None:
        if self.current_page > 1:
            self.current_page -= 1
            self._load_monsters()

    def _on_next_page(self) -> None:
        if self.current_page < self.total_pages:
            self.current_page += 1
            self._load_monsters()

    def _go_to_page_from_entry(self) -> None:
        try:
            page = int(self.page_entry.get().strip())
            if page < 1:
                page = 1
            elif page > self.total_pages:
                page = self.total_pages
            if page != self.current_page:
                self.current_page = page
                self._load_monsters()
            else:
                self._update_page_ui()
        except ValueError:
            self._update_page_ui()

    def _update_page_ui(self) -> None:
        self.page_entry.delete(0, tk.END)
        self.page_entry.insert(0, str(self.current_page))

        displayed = len(self.monsters)
        stats_text = f"Hiển thị {displayed} / {self.total_records} (Trang {self.current_page}/{self.total_pages})"
        self.stats_label.config(text=stats_text)

        self.btn_prev_page.config(state="normal" if self.current_page > 1 else "disabled")
        self.btn_next_page.config(state="normal" if self.current_page < self.total_pages else "disabled")

    def _load_reference_data(self):
        try:
            type_list = self.db.get_monster_type_list() if hasattr(self.db, "get_monster_type_list") else []
            self.type_map = {str(t['value']): t['label'] for t in type_list}
            type_values = ["All Monsters"] + [t['label'] for t in type_list]
            if hasattr(self, "monster_type_box"):
                self.monster_type_box.config(values=type_values)

            dungeon_list = self.db.get_dungeon_list() if hasattr(self.db, "get_dungeon_list") else []
            self.dungeon_map = {str(d['id']): d['name'] for d in dungeon_list}
            dungeon_values = ["All Locations"] + [d['name'] for d in dungeon_list]
            if hasattr(self, "location_box"):
                self.location_box.config(values=dungeon_values)

        except Exception as e:
            print(f"Error loading reference data: {e}")

    def _load_monsters(self):
        try:
            m_type = self.monster_type_filter if self.monster_type_filter != "All Monsters" else None
            d_id = self.dungeon_filter if self.dungeon_filter != "All Locations" else None

            # Map values back to IDs for the database query
            if m_type:
                for k, v in self.type_map.items():
                    if v == m_type:
                        m_type = k
                        break
            if d_id:
                for k, v in self.dungeon_map.items():
                    if v == d_id:
                        d_id = k
                        break

            res = self.db.get_filtered_monsters(
                keyword=self.keyword,
                monster_type=m_type,
                dungeon_id=d_id,
                page=self.current_page,
                page_size=self.page_size,
                sort_column="id",
                sort_order="ASC"
            )
            self.monsters = res.get('items', [])
            self.total_records = res.get('total_records', 0)
            self.total_pages = res.get('total_pages', 1)
        except Exception as e:
            self.monsters = []
            self.total_records = 0
            self.total_pages = 1
            print(f"Error loading monsters: {e}")

        self._refresh_tree()
        self._update_page_ui()

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
