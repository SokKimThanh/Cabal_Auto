import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Any, List

from ui.components.base.responsive_grid_base import ResponsiveGridBase
from lib.ui_style_v2 import UIStyleV2 as UIStyle
from database import get_db, get_all_monsters_api
from dialogs.monster_edit import MonsterEditDialog

class MonsterManagerFrame(ResponsiveGridBase):

    def __init__(self, parent, app=None, *args, **kwargs):
        super().__init__(parent, app=app, bg=UIStyle.BG_BASE, *args, **kwargs)
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
        self.monster_type_filter = self.app._t("all_monsters", default="All Monsters") if self.app else "All Monsters"
        self.dungeon_filter = self.app._t("all_locations", default="All Habitats") if self.app else "All Locations"

        self._setup_ui()
        self._load_reference_data()
        self._load_monsters()

    def _setup_ui(self):
        content_frame = self.get_content_frame()
        # Title Label
        title_lbl = tk.Label(
            content_frame,
            font=(UIStyle.resolve_font_family("title"), 16, "bold"),
            bg=UIStyle.BG_BASE,
            fg=UIStyle.TEXT_PRIMARY
        )
        if hasattr(self.app, "bind_text"):
            self.app.bind_text(title_lbl, "monster_manager_title")
        else:
            title_lbl.config(text=self.app._t("monster_manager_title", default="Quản lý Quái vật"))
        title_lbl.pack(pady=UIStyle.SPACE_MD)

        self._create_search_bar(content_frame)

        # Treeview Area
        table_frame = tk.Frame(content_frame, bg=UIStyle.BG_BASE)
        table_frame.pack(fill="both", expand=True, padx=UIStyle.SPACE_MD, pady=UIStyle.SPACE_MD)

        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        self.tree_scroll_y = ttk.Scrollbar(table_frame, orient=tk.VERTICAL)
        self.tree_scroll_x = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL)

        self.columns = ("ID", "Name", "Level", "HP", "Defense", "Type", "Dungeon")
        self.tree = ttk.Treeview(
            table_frame,
            columns=self.columns,
            show="headings",
            selectmode="browse",

            yscrollcommand=self._autoscroll_y,
            xscrollcommand=self._autoscroll_x
        )

        self.tree_scroll_y.config(command=self.tree.yview)
        self.tree_scroll_x.config(command=self.tree.xview)

        for col in self.columns:
            self.tree.heading(col, text=self.app._t(f"col_{col.lower()}", default=col), command=lambda c=col: self._sort_treeview(c, False))
            self.tree.column(col, width=100, minwidth=80)

        self.tree.grid(row=0, column=0, sticky="nsew")

        self.tree.bind("<Double-1>", lambda e: self._edit_monster())

        # Pagination bar removed

        # Bottom Bar for Actions
        bottom_bar = tk.Frame(content_frame, bg=UIStyle.BG_SURFACE, )
        bottom_bar.pack(side="bottom", fill="x", pady=UIStyle.SPACE_SM)

        add_btn = tk.Button(
            bottom_bar,
            text=self.app._t("btn_add", default="Thêm"),
            command=self._add_monster,
            **UIStyle.get_button_style("primary")
        )
        add_btn.pack(side="left", padx=UIStyle.SPACE_MD, pady=UIStyle.SPACE_SM)

        edit_btn = tk.Button(
            bottom_bar,
            text=self.app._t("btn_edit", default="Sửa"),
            command=self._edit_monster,
            **UIStyle.get_button_style("primary")
        )
        edit_btn.pack(side="left", padx=UIStyle.SPACE_MD, pady=UIStyle.SPACE_SM)

        del_btn = tk.Button(
            bottom_bar,
            text=self.app._t("btn_delete", default="Xóa"),
            command=self._delete_monster,
            **{**UIStyle.get_button_style("primary"), "bg": UIStyle.DANGER, "activebackground": "#ef4444", "fg": "#ffffff", "activeforeground": "#ffffff"}
        )
        del_btn.pack(side="left", padx=UIStyle.SPACE_MD, pady=UIStyle.SPACE_SM)

        ref_btn = tk.Button(
            bottom_bar,
            text=self.app._t("btn_refresh", default="Làm mới"),
            command=self._on_refresh,
            **UIStyle.get_button_style("secondary")
        )
        ref_btn.pack(side="right", padx=UIStyle.SPACE_MD, pady=UIStyle.SPACE_SM)

        # Pagination controls in bottom bar
        self.btn_next_page = tk.Button(
            bottom_bar,
            text=self.app._t("btn_next", default="Sau"),
            command=self._on_next_page,
            bg=UIStyle.BG_BASE,
            fg=UIStyle.TEXT_PRIMARY,
            relief="flat"
        )
        self.btn_next_page.pack(side="right", padx=(0, UIStyle.SPACE_MD), pady=UIStyle.SPACE_SM)

        self.stats_label = tk.Label(
            bottom_bar,
            text="1 / 1",
            bg=UIStyle.BG_SURFACE,
            fg=UIStyle.TEXT_PRIMARY
        )
        self.stats_label.pack(side="right", padx=(0, 10))

        self.btn_prev_page = tk.Button(
            bottom_bar,
            text=self.app._t("btn_prev", default="Trước"),
            command=self._on_prev_page,
            bg=UIStyle.BG_BASE,
            fg=UIStyle.TEXT_PRIMARY,
            relief="flat"
        )
        self.btn_prev_page.pack(side="right", padx=(0, 10), pady=UIStyle.SPACE_SM)

        # -------------------------------------------------------------
        # Monster Type Management Panel
        # -------------------------------------------------------------
        type_panel_container = tk.Frame(content_frame, bg=UIStyle.BG_BASE)
        type_panel_container.pack(fill="x", padx=UIStyle.SPACE_MD, pady=UIStyle.SPACE_MD)

        # Title for Type Panel
        self.type_panel_expanded = False

        self.type_title_lbl = tk.Label(
            type_panel_container,
            text=self.app._t("panel_types_title_collapsed", default="▶ Quản lý Loại Quái vật") if self.app else "▶ Quản lý Loại Quái vật",
            font=(UIStyle.resolve_font_family("title"), 12, "bold"),
            bg=UIStyle.BG_BASE,
            fg=UIStyle.TEXT_PRIMARY,
            cursor="hand2"
        )
        self.type_title_lbl.pack(anchor="w", pady=(0, UIStyle.SPACE_SM))
        self.type_title_lbl.bind("<Button-1>", self._toggle_type_panel)

        # Main frame for the Type Management UI (split into left list, right form)
        self.type_content_frame = tk.Frame(type_panel_container, bg=UIStyle.BG_BASE)
        # Initially hidden
        # self.type_content_frame.pack(fill="x", expand=True)

        # Left: Treeview for Types
        type_list_frame = tk.Frame(self.type_content_frame, bg=UIStyle.BG_BASE)
        type_list_frame.pack(side="left", fill="y", expand=True)

        self.type_tree_scroll_y = ttk.Scrollbar(type_list_frame, orient=tk.VERTICAL)
        self.type_tree = ttk.Treeview(
            type_list_frame,
            columns=("ID", "Label"),
            show="headings",
            selectmode="browse",

            yscrollcommand=self.type_tree_scroll_y.set
        )
        self.type_tree_scroll_y.config(command=self.type_tree.yview)

        self.type_tree.heading("ID", text="ID")
        self.type_tree.column("ID", width=100, anchor="center")
        self.type_tree.heading("Label", text=self.app._t("col_label", default="Tên Loại") if self.app else "Tên Loại")
        self.type_tree.column("Label", width=250, anchor="w")

        self.type_tree.pack(side="left", fill="both", expand=True)
        self.type_tree_scroll_y.pack(side="left", fill="y")
        self.type_tree.bind("<<TreeviewSelect>>", self._on_type_selected)

        # Right: Form to Add/Edit Type
        type_form_frame = tk.Frame(self.type_content_frame, bg=UIStyle.BG_BASE)
        type_form_frame.pack(side="right", fill="both", expand=True, padx=(UIStyle.SPACE_MD, 0))

        form_title = tk.Label(
            type_form_frame,
            text=self.app._t("lbl_type_details", default="Chi tiết Loại Quái vật") if self.app else "Chi tiết Loại Quái vật",
            font=(UIStyle.resolve_font_family("title"), 10, "bold"),
            bg=UIStyle.BG_BASE,
            fg=UIStyle.TEXT_PRIMARY
        )
        form_title.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))

        tk.Label(type_form_frame, text="ID:", bg=UIStyle.BG_BASE, fg=UIStyle.TEXT_PRIMARY).grid(row=1, column=0, sticky="e", pady=2, padx=5)
        self.type_id_entry = ttk.Entry(type_form_frame, width=25)
        self.type_id_entry.grid(row=1, column=1, sticky="w", pady=2)

        tk.Label(type_form_frame, text=self.app._t("col_label", default="Tên Loại:") if self.app else "Tên Loại:", bg=UIStyle.BG_BASE, fg=UIStyle.TEXT_PRIMARY).grid(row=2, column=0, sticky="e", pady=2, padx=5)
        self.type_label_entry = ttk.Entry(type_form_frame, width=25)
        self.type_label_entry.grid(row=2, column=1, sticky="w", pady=2)

        type_btn_frame = tk.Frame(type_form_frame, bg=UIStyle.BG_BASE)
        type_btn_frame.grid(row=3, column=0, columnspan=2, sticky="w", pady=10)

        self.btn_save_type = tk.Button(
            type_btn_frame,
            text=self.app._t("btn_save", default="Save") if self.app else "Save",
            command=self._on_save_type,
            **UIStyle.get_button_style("primary")
        )
        self.btn_save_type.pack(side="left", padx=(5, 5))

        self.btn_cancel_type = tk.Button(
            type_btn_frame,
            text=self.app._t("btn_cancel", default="Cancel") if self.app else "Cancel",
            command=self._on_cancel_type,
            **UIStyle.get_button_style("secondary")
        )
        self.btn_cancel_type.pack(side="left", padx=5)

        self.btn_delete_type = tk.Button(
            type_btn_frame,
            text=self.app._t("btn_delete", default="Delete") if self.app else "Delete",
            command=self._on_delete_type,
            **{**UIStyle.get_button_style("primary"), "bg": UIStyle.DANGER, "activebackground": "#ef4444", "fg": "#ffffff", "activeforeground": "#ffffff"}
        )
        self.btn_delete_type.pack(side="left", padx=5)


    def _toggle_type_panel(self, event=None):
        if self.type_panel_expanded:
            self.type_content_frame.pack_forget()
            self.type_title_lbl.config(text=self.app._t("panel_types_title_collapsed", default="▶ Quản lý Loại Quái vật") if self.app else "▶ Quản lý Loại Quái vật")
            self.type_panel_expanded = False
        else:
            self.type_content_frame.pack(fill="x", expand=False)
            self.type_title_lbl.config(text=self.app._t("panel_types_title_expanded", default="▼ Quản lý Loại Quái vật") if self.app else "▼ Quản lý Loại Quái vật")
            self.type_panel_expanded = True

    def _autoscroll_y(self, first, last):
        self.tree_scroll_y.set(first, last)
        if float(first) <= 0.0 and float(last) >= 1.0:
            self.tree_scroll_y.grid_remove()
        else:
            self.tree_scroll_y.grid(row=0, column=1, sticky="ns")

    def _autoscroll_x(self, first, last):
        self.tree_scroll_x.set(first, last)
        if float(first) <= 0.0 and float(last) >= 1.0:
            self.tree_scroll_x.grid_remove()
        else:
            self.tree_scroll_x.grid(row=1, column=0, sticky="ew")

    def _create_search_bar(self, parent) -> None:
        search_frame = tk.Frame(parent, bg=UIStyle.BG_BASE)
        search_frame.pack(fill="x", padx=UIStyle.SPACE_MD, pady=(UIStyle.SPACE_SM, 0))

        # Keyword Search
        lbl_search = tk.Label(search_frame, bg=UIStyle.BG_BASE, fg=UIStyle.TEXT_PRIMARY)
        if hasattr(self.app, "bind_text"):
            self.app.bind_text(lbl_search, "search_label")
        else:
            lbl_search.config(text=self.app._t("search_label", default="Tìm kiếm:"))
        lbl_search.grid(row=0, column=0, padx=(5, 5), pady=5, sticky="w")

        self.search_entry = ttk.Entry(search_frame)
        self.search_entry.grid(row=0, column=1, sticky="ew", padx=(0, 5), pady=5)
        self.search_entry.bind("<KeyRelease>", self._on_search_changed)
        self.search_entry.bind("<Escape>", self._on_clear_search)

        # Monster Type
        self.monster_type_var = tk.StringVar(value=self.monster_type_filter)
        self.monster_type_box = ttk.Combobox(search_frame, textvariable=self.monster_type_var, state="readonly", width=15)
        self.monster_type_box.grid(row=0, column=2, sticky="ew", padx=(0, 5), pady=5)
        self.monster_type_box.bind("<<ComboboxSelected>>", self._on_filter_changed)

        # Location / Dungeon
        self.location_var = tk.StringVar(value=self.dungeon_filter)
        self.location_box = ttk.Combobox(search_frame, textvariable=self.location_var, state="readonly", width=15)
        self.location_box.grid(row=0, column=3, sticky="ew", padx=(0, 5), pady=5)
        self.location_box.bind("<<ComboboxSelected>>", self._on_filter_changed)

        # Page size
        self.page_size_var = tk.StringVar(value="25")
        self.page_size_box = ttk.Combobox(search_frame, textvariable=self.page_size_var, state="readonly", width=5, values=["25", "50", "100", "200"])
        self.page_size_box.grid(row=0, column=4, sticky="ew", padx=(0, 5), pady=5)
        self.page_size_box.bind("<<ComboboxSelected>>", self._on_filter_changed)

        search_frame.columnconfigure(1, weight=1)

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
        self.monster_type_var.set(self.app._t("all_monsters", default="All Monsters") if self.app else "All Monsters")
        self.location_var.set(self.app._t("all_locations", default="All Habitats") if self.app else "All Locations")
        self.page_size_var.set("25")
        self.monster_type_filter = self.app._t("all_monsters", default="All Monsters") if self.app else "All Monsters"
        self.dungeon_filter = self.app._t("all_locations", default="All Habitats") if self.app else "All Locations"
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

    def _update_page_ui(self) -> None:
        stats_text = f"{self.current_page} / {max(1, self.total_pages)}"
        self.stats_label.config(text=stats_text)

        if self.current_page <= 1:
            self.btn_prev_page.config(state="disabled")
        else:
            self.btn_prev_page.config(state="normal")

        if self.current_page >= self.total_pages:
            self.btn_next_page.config(state="disabled")
        else:
            self.btn_next_page.config(state="normal")

    def _load_reference_data(self):
        try:
            type_list = self.db.get_monster_type_list() if hasattr(self.db, "get_monster_type_list") else []
            self.type_map = {str(t['value']): t['label'] for t in type_list}
            type_values = [self.app._t("all_monsters", default="All Monsters") if self.app else "All Monsters"] + [t['label'] for t in type_list]
            if hasattr(self, "monster_type_box"):
                self.monster_type_box.config(values=type_values)

            dungeon_list = self.db.get_dungeon_list() if hasattr(self.db, "get_dungeon_list") else []
            self.dungeon_map = {str(d['id']): d['name'] for d in dungeon_list}
            dungeon_values = [self.app._t("all_locations", default="All Habitats") if self.app else "All Locations"] + [d['name'] for d in dungeon_list]
            if hasattr(self, "location_box"):
                self.location_box.config(values=dungeon_values)

            self._load_type_tree()

        except Exception as e:
            print(f"Error loading reference data: {e}")

    def _load_type_tree(self):
        for item in self.type_tree.get_children():
            self.type_tree.delete(item)

        if not hasattr(self.db, "get_monster_type_list"):
            return

        type_list = self.db.get_monster_type_list()
        for t in type_list:
            self.type_tree.insert("", "end", iid=str(t['value']), values=(t['value'], t['label']))

    def _on_type_selected(self, event=None):
        selected = self.type_tree.selection()
        if not selected:
            return

        type_id = selected[0]
        item = self.type_tree.item(type_id)
        values = item.get("values", [])

        self._on_cancel_type() # clear form first

        if len(values) >= 2:
            self.type_id_entry.insert(0, str(values[0]))
            self.type_id_entry.config(state="readonly")
            self.type_label_entry.insert(0, str(values[1]))

    def _on_cancel_type(self, event=None):
        self.type_id_entry.config(state="normal")
        self.type_id_entry.delete(0, tk.END)
        self.type_label_entry.delete(0, tk.END)
        self.type_tree.selection_remove(self.type_tree.selection())

    def _on_save_type(self, event=None):
        t_id = self.type_id_entry.get().strip()
        t_label = self.type_label_entry.get().strip()

        if not t_id or not t_label:
            messagebox.showwarning(
                self.app._t("warn_title", default="Cảnh báo") if self.app else "Cảnh báo",
                self.app._t("warn_type_empty", default="Vui lòng nhập cả ID và Tên Loại") if self.app else "Vui lòng nhập cả ID và Tên Loại",
                parent=self
            )
            return

        if hasattr(self.db, "insert_or_update_monster_type"):
            success = self.db.insert_or_update_monster_type(t_id, t_label)
            if success:
                self._load_reference_data()
                self._on_cancel_type()
            else:
                messagebox.showerror(
                    self.app._t("err_title", default="Lỗi") if self.app else "Lỗi",
                    self.app._t("err_save_type", default="Không thể lưu Loại Quái vật.") if self.app else "Không thể lưu Loại Quái vật.",
                    parent=self
                )
        else:
            messagebox.showerror("Error", "Missing DB method 'insert_or_update_monster_type'", parent=self)

    def _on_delete_type(self, event=None):
        selected = self.type_tree.selection()
        if not selected:
            messagebox.showwarning(
                self.app._t("warn_title", default="Cảnh báo") if self.app else "Cảnh báo",
                self.app._t("warn_no_sel_type", default="Vui lòng chọn Loại Quái vật để xóa") if self.app else "Vui lòng chọn Loại Quái vật để xóa",
                parent=self
            )
            return

        type_id = selected[0]
        item = self.type_tree.item(type_id)
        values = item.get("values", [])
        type_name = values[1] if len(values) >= 2 else type_id

        confirm = messagebox.askyesno(
            self.app._t("confirm_del_title", default="Xác nhận xóa") if self.app else "Xác nhận xóa",
            (self.app._t("confirm_del_type_msg", default="Bạn có chắc muốn xóa Loại Quái vật '{}' không?") if self.app else "Bạn có chắc muốn xóa Loại Quái vật '{}' không?").format(type_name),
            parent=self
        )

        if confirm:
            if hasattr(self.db, "delete_monster_type"):
                success = self.db.delete_monster_type(type_id)
                if success:
                    self._load_reference_data()
                    self._on_cancel_type()
                else:
                    messagebox.showerror(
                        self.app._t("err_title", default="Lỗi") if self.app else "Lỗi",
                        self.app._t("err_del_type", default="Không thể xóa Loại Quái vật.") if self.app else "Không thể xóa Loại Quái vật.",
                        parent=self
                    )
            else:
                 messagebox.showerror("Error", "Missing DB method 'delete_monster_type'", parent=self)

    def _load_monsters(self):
        try:
            m_type = self.monster_type_filter if self.monster_type_filter != (self.app._t("all_monsters", default="All Monsters") if self.app else "All Monsters") else None
            d_id = self.dungeon_filter if self.dungeon_filter != (self.app._t("all_locations", default="All Habitats") if self.app else "All Locations") else None

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
