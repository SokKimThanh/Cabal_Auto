import math
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from typing import Dict, Any

from ui.components.base.responsive_grid_base import ResponsiveGridBase
from lib.ui_style_v2 import UIStyleV2 as UIStyle

class SkillManagerFrame(ResponsiveGridBase):
    def __init__(self, parent, app=None, *args, **kwargs):
        super().__init__(parent, app=app, *args, **kwargs)
        self.app = app
        self.skills = []

        # Pagination state
        self.current_page = 1
        self.items_per_page = 20
        self.total_pages = 1
        self.total_items = 0

        # Filter state variables
        self.search_var = tk.StringVar()
        self.class_filter_var = tk.StringVar()
        self.type_filter_var = tk.StringVar()
        self.classes_map = {}

        self._setup_ui()
        self._load_skills()

    def _setup_ui(self):
        content_frame = self.get_content_frame()

        # Title Label
        title_lbl = tk.Label(
            content_frame,
            text=self.app._t("skill_manager_title", default="Quản lý Kỹ năng"),
            font=(UIStyle.resolve_font_family("title") if hasattr(UIStyle, "resolve_font_family") else "IBM Plex Sans", 16, "bold"),
            bg=UIStyle.THEME_BG_APP,
            fg=UIStyle.THEME_FG_TEXT if hasattr(UIStyle, "THEME_FG_TEXT") else UIStyle.TEXT_PRIMARY
        )
        title_lbl.pack(pady=UIStyle.SPACE_MD if hasattr(UIStyle, "SPACE_MD") else 8)

        # Filters Area
        filter_frame = tk.Frame(content_frame, bg=UIStyle.THEME_BG_APP)
        filter_frame.pack(fill="x", padx=UIStyle.SPACE_MD if hasattr(UIStyle, "SPACE_MD") else 8, pady=(0, UIStyle.SPACE_MD if hasattr(UIStyle, "SPACE_MD") else 8))

        # Search
        search_lbl = tk.Label(filter_frame, text=self.app._t("lbl_search", default="Tìm kiếm:"), bg=UIStyle.THEME_BG_APP, fg=UIStyle.THEME_FG_TEXT if hasattr(UIStyle, "THEME_FG_TEXT") else UIStyle.TEXT_PRIMARY)
        search_lbl.pack(side="left", padx=(0, 5))
        self.search_entry = ttk.Entry(filter_frame, textvariable=self.search_var, width=20)
        self.search_entry.pack(side="left", padx=(0, 15))
        self.search_entry.bind("<Return>", lambda e: self._on_filter_changed())

        # Class Filter
        class_lbl = tk.Label(filter_frame, text=self.app._t("lbl_class", default="Class:"), bg=UIStyle.THEME_BG_APP, fg=UIStyle.THEME_FG_TEXT if hasattr(UIStyle, "THEME_FG_TEXT") else UIStyle.TEXT_PRIMARY)
        class_lbl.pack(side="left", padx=(0, 5))
        self.class_combo = ttk.Combobox(filter_frame, textvariable=self.class_filter_var, state="readonly", width=15)
        self.class_combo.pack(side="left", padx=(0, 15))
        self.class_combo.bind("<<ComboboxSelected>>", lambda e: self._on_filter_changed())
        self._load_classes()

        # Type Filter
        type_lbl = tk.Label(filter_frame, text=self.app._t("lbl_type", default="Loại:"), bg=UIStyle.THEME_BG_APP, fg=UIStyle.THEME_FG_TEXT if hasattr(UIStyle, "THEME_FG_TEXT") else UIStyle.TEXT_PRIMARY)
        type_lbl.pack(side="left", padx=(0, 5))
        self.type_combo = ttk.Combobox(filter_frame, textvariable=self.type_filter_var, state="readonly", width=15,
                                       values=["All", "Attack", "Buff", "Dash", "Blink", "Passive", "GM"])
        self.type_combo.current(0)
        self.type_combo.pack(side="left", padx=(0, 15))
        self.type_combo.bind("<<ComboboxSelected>>", lambda e: self._on_filter_changed())

        # Filter Button
        filter_btn = tk.Button(
            filter_frame,
            text=self.app._t("btn_search", default="Lọc"),
            command=self._on_filter_changed,
            bg=UIStyle.ACCENT_BLUE if hasattr(UIStyle, "ACCENT_BLUE") else "#3b82f6",
            fg="white",
            relief="flat",
            padx=10
        )
        filter_btn.pack(side="left")

        # Treeview Area
        table_frame = tk.Frame(content_frame, bg=UIStyle.THEME_BG_APP)
        table_frame.pack(fill="both", expand=True, padx=UIStyle.SPACE_MD if hasattr(UIStyle, "SPACE_MD") else 8, pady=(0, UIStyle.SPACE_MD if hasattr(UIStyle, "SPACE_MD") else 8))

        self.tree_scroll_y = ttk.Scrollbar(table_frame, orient=tk.VERTICAL)
        self.tree_scroll_y.pack(side="right", fill="y")

        self.tree_scroll_x = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL)
        self.tree_scroll_x.pack(side="bottom", fill="x")

        self.columns = ("ID", "Name", "Type", "Class", "Alias")
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

        # 5 core columns for DB skills: ID, Name, Type, Class, Alias
        self.tree.heading("ID", text=self.app._t("col_skill_id", default="ID"))
        self.tree.column("ID", width=70, anchor="center")

        self.tree.heading("Name", text=self.app._t("col_skill_name", default="Name"))
        self.tree.column("Name", width=180, anchor="w")

        self.tree.heading("Type", text=self.app._t("col_skill_type", default="Type"))
        self.tree.column("Type", width=100, anchor="center")

        self.tree.heading("Class", text=self.app._t("col_skill_class", default="Class ID"))
        self.tree.column("Class", width=80, anchor="center")

        self.tree.heading("Alias", text=self.app._t("col_skill_alias", default="Alias"))
        self.tree.column("Alias", width=120, anchor="w")

        self.tree.pack(fill="both", expand=True)

        # Bottom Bar for Actions
        bottom_bar = tk.Frame(content_frame, bg=UIStyle.THEME_BG_PANEL, height=50)
        bottom_bar.pack(side="bottom", fill="x", pady=UIStyle.SPACE_SM if hasattr(UIStyle, "SPACE_SM") else 4)

        add_btn = tk.Button(
            bottom_bar,
            text=self.app._t("btn_add_skill", default=" Thêm"),
            command=self._add_skill,
            bg=UIStyle.ACCENT_GREEN,
            fg="white",
            relief="flat"
        )
        add_btn.pack(side="left", padx=UIStyle.SPACE_MD if hasattr(UIStyle, "SPACE_MD") else 8, pady=UIStyle.SPACE_SM if hasattr(UIStyle, "SPACE_SM") else 4)

        edit_btn = tk.Button(
            bottom_bar,
            text=self.app._t("btn_edit_skill", default=" Sửa"),
            command=self._edit_skill,
            bg=UIStyle.ACCENT_GREEN,
            fg="white",
            relief="flat"
        )
        edit_btn.pack(side="left", padx=UIStyle.SPACE_MD if hasattr(UIStyle, "SPACE_MD") else 8, pady=UIStyle.SPACE_SM if hasattr(UIStyle, "SPACE_SM") else 4)

        del_btn = tk.Button(
            bottom_bar,
            text=self.app._t("btn_del_skill", default=" Xóa"),
            command=self._delete_skill,
            bg=UIStyle.DANGER,
            fg="white",
            relief="flat"
        )
        del_btn.pack(side="left", padx=UIStyle.SPACE_MD if hasattr(UIStyle, "SPACE_MD") else 8, pady=UIStyle.SPACE_SM if hasattr(UIStyle, "SPACE_SM") else 4)

        ref_btn = tk.Button(
            bottom_bar,
            text=self.app._t("btn_refresh_skill", default=" Làm mới"),
            command=self._load_skills,
            bg=UIStyle.BG_ELEVATED,
            fg=UIStyle.TEXT_PRIMARY,
            relief="flat"
        )
        ref_btn.pack(side="right", padx=UIStyle.SPACE_MD if hasattr(UIStyle, "SPACE_MD") else 8, pady=UIStyle.SPACE_SM if hasattr(UIStyle, "SPACE_SM") else 4)

        # Pagination controls in bottom bar
        self.next_btn = tk.Button(
            bottom_bar,
            text=self.app._t("btn_next", default="Sau >"),
            command=self._next_page,
            bg=UIStyle.THEME_BG_APP,
            fg=UIStyle.TEXT_PRIMARY,
            relief="flat"
        )
        self.next_btn.pack(side="right", padx=(0, UIStyle.SPACE_MD if hasattr(UIStyle, "SPACE_MD") else 8), pady=UIStyle.SPACE_SM if hasattr(UIStyle, "SPACE_SM") else 4)

        self.page_lbl = tk.Label(
            bottom_bar,
            text="1 / 1",
            bg=UIStyle.THEME_BG_PANEL,
            fg=UIStyle.TEXT_PRIMARY
        )
        self.page_lbl.pack(side="right", padx=(0, 10))

        self.prev_btn = tk.Button(
            bottom_bar,
            text=self.app._t("btn_prev", default="< Trước"),
            command=self._prev_page,
            bg=UIStyle.THEME_BG_APP,
            fg=UIStyle.TEXT_PRIMARY,
            relief="flat"
        )
        self.prev_btn.pack(side="right", padx=(0, 10), pady=UIStyle.SPACE_SM if hasattr(UIStyle, "SPACE_SM") else 4)

    def _load_classes(self):
        try:
            if hasattr(self.app, "db_class_service"):
                svc = self.app.db_class_service
                classes = svc.get_all_classes()
                self.classes_map = {str(c.get("class_id")): c.get("name") for c in classes}
                values = ["All"] + [f"{c_id} - {name}" for c_id, name in self.classes_map.items()]
                self.class_combo['values'] = values
                if values:
                    self.class_combo.current(0)
            else:
                self.class_combo['values'] = ["All"]
                self.class_combo.current(0)
        except Exception as e:
            print(f"Error loading classes: {e}")
            self.class_combo['values'] = ["All"]
            self.class_combo.current(0)

    def _on_filter_changed(self):
        self.current_page = 1
        self._load_skills()

    def _prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self._load_skills()

    def _next_page(self):
        if self.current_page < self.total_pages:
            self.current_page += 1
            self._load_skills()

    def _update_pagination_ui(self):
        self.page_lbl.config(text=f"{self.current_page} / {max(1, self.total_pages)}")

        if self.current_page <= 1:
            self.prev_btn.config(state="disabled")
        else:
            self.prev_btn.config(state="normal")

        if self.current_page >= self.total_pages:
            self.next_btn.config(state="disabled")
        else:
            self.next_btn.config(state="normal")

    def _load_skills(self):
        try:
            if hasattr(self.app, "db_skill_service"):
                svc = self.app.db_skill_service

                # Parse filters
                search_text = self.search_var.get().strip() or None

                type_val = self.type_filter_var.get()
                skill_type = None if type_val == "All" or not type_val else type_val

                class_val = self.class_filter_var.get()
                class_id = None
                if class_val and class_val != "All":
                    try:
                        class_id = int(class_val.split(" - ")[0])
                    except:
                        pass

                offset = (self.current_page - 1) * self.items_per_page

                self.total_items = svc.get_total_skills_count(
                    class_id=class_id,
                    skill_type=skill_type,
                    search_text=search_text
                )

                self.total_pages = math.ceil(self.total_items / self.items_per_page) if self.total_items > 0 else 1
                if self.current_page > self.total_pages:
                    self.current_page = self.total_pages
                    offset = (self.current_page - 1) * self.items_per_page

                self.skills = svc.get_skills_by_filter(
                    class_id=class_id,
                    skill_type=skill_type,
                    search_text=search_text,
                    limit=self.items_per_page,
                    offset=offset
                )
            else:
                self.skills = []
                self.total_items = 0
                self.total_pages = 1

            if not isinstance(self.skills, list):
                self.skills = []
        except Exception as e:
            self.skills = []
            self.total_items = 0
            self.total_pages = 1
            print(f"Error loading skills: {e}")

        self._update_pagination_ui()
        self._refresh_tree()

    def _refresh_tree(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for s in self.skills:
            if isinstance(s, dict):
                values = (
                    s.get("skill_id", ""),
                    s.get("name", "Unknown"),
                    s.get("type", ""),
                    s.get("class_id", ""),
                    s.get("alias", "")
                )
                self.tree.insert("", "end", iid=str(s.get("skill_id", str(id(s)))), values=values)

    def _add_skill(self):
        from ui.dialogs.skill_edit_dialog import SkillEditDialog

        def _on_save(data: dict):
            if hasattr(self.app, "db_skill_service"):
                svc = self.app.db_skill_service
                success_id = svc.create_skill(data)
                if success_id:
                    messagebox.showinfo(
                        self.app._t("success_title", default="Thành công"),
                        self.app._t("msg_add_skill_success", default="Thêm kỹ năng thành công."),
                        parent=self
                    )
                    self._load_skills()
                else:
                    messagebox.showerror(
                        self.app._t("error_title", default="Lỗi"),
                        self.app._t("err_add_skill", default="Không thể thêm kỹ năng."),
                        parent=self
                    )

        SkillEditDialog(
            parent=self.winfo_toplevel(),
            app=self.app,
            title=self.app._t("title_add_skill", default="Thêm Kỹ năng"),
            skill_data=None,
            on_save=_on_save
        )

    def _edit_skill(self):
        from ui.dialogs.skill_edit_dialog import SkillEditDialog

        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning(
                self.app._t("warn_title", default="Cảnh báo"),
                self.app._t("warn_no_sel_skill", default="Vui lòng chọn kỹ năng để sửa"),
                parent=self
            )
            return

        s_id = selected[0]
        target_skill = None
        for s in self.skills:
            if str(s.get("skill_id", "")) == s_id:
                target_skill = s
                break

        if target_skill:
            def _on_save(data: dict):
                if hasattr(self.app, "db_skill_service"):
                    svc = self.app.db_skill_service
                    skill_id = data.get("skill_id")
                    if skill_id is None:
                        # Fallback for unexpected missing id
                        return

                    success = svc.update_skill(skill_id, data)
                    if success:
                        messagebox.showinfo(
                            self.app._t("success_title", default="Thành công"),
                            self.app._t("msg_edit_skill_success", default="Cập nhật kỹ năng thành công."),
                            parent=self
                        )
                        self._load_skills()
                    else:
                        messagebox.showerror(
                            self.app._t("error_title", default="Lỗi"),
                            self.app._t("err_edit_skill", default="Không thể cập nhật kỹ năng."),
                            parent=self
                        )

            SkillEditDialog(
                parent=self.winfo_toplevel(),
                app=self.app,
                title=self.app._t("title_edit_skill", default="Sửa Kỹ năng"),
                skill_data=target_skill,
                on_save=_on_save
            )

    def _delete_skill(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning(
                self.app._t("warn_title", default="Cảnh báo"),
                self.app._t("warn_no_sel_skill", default="Vui lòng chọn kỹ năng để xóa"),
                parent=self
            )
            return

        s_id = selected[0]
        target_skill = None
        for s in self.skills:
            if str(s.get("skill_id", "")) == s_id:
                target_skill = s
                break

        if target_skill:
            name = target_skill.get('name', 'Unknown')
            confirm = messagebox.askyesno(
                self.app._t("confirm_del_title", default="Xác nhận xóa"),
                self.app._t("confirm_del_msg", default=f"Bạn có chắc muốn xóa kỹ năng '{name}' không?"),
                parent=self
            )

            if confirm:
                if hasattr(self.app, "db_skill_service"):
                    svc = self.app.db_skill_service
                    skill_id = target_skill.get("skill_id")
                    if skill_id is not None:
                        success = svc.delete_skill(skill_id)
                        if success:
                            messagebox.showinfo(
                                self.app._t("success_title", default="Thành công"),
                                self.app._t("msg_del_skill_success", default="Xóa kỹ năng thành công."),
                                parent=self
                            )
                            self._load_skills()
                        else:
                            messagebox.showerror(
                                self.app._t("error_title", default="Lỗi"),
                                self.app._t("err_del_skill", default="Không thể xóa kỹ năng."),
                                parent=self
                            )

    def on_view_shown(self):
        self._load_skills()

    def on_view_hidden(self):
        pass
