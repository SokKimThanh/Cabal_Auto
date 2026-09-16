import math
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from typing import Dict, Any

from ui.components.base.responsive_grid_base import ResponsiveGridBase
from lib.ui_style_v2 import UIStyleV2 as UIStyle

class SkillManagerFrame(ResponsiveGridBase):
    def __init__(self, parent, app=None, *args, **kwargs):
        super().__init__(parent, app=app, bg=UIStyle.BG_BASE, *args, **kwargs)
        self.app = app
        self.skills = []
        self.skill_types = []

        # Pagination state
        self.current_page = 1
        self.items_per_page = 25
        self.total_pages = 1
        self.total_items = 0

        # Filter state variables
        self.search_var = tk.StringVar()
        self.class_filter_var = tk.StringVar(value="All")
        self.type_filter_var = tk.StringVar(value="All")
        self.classes_map = {}
        self.types_map = {}

        # Skill Type Editor State
        self.editing_type_id = None
        self.type_name_var = tk.StringVar()

        self._setup_ui()
        self._load_classes()
        self._load_types()
        self._load_skills()

    def _setup_ui(self):
        content_frame = self.get_content_frame()

        # Title Label
        title_lbl = tk.Label(
            content_frame,
            text=self.app._t("skill_manager_title", default="Quản lý Kỹ năng"),
            font=(UIStyle.resolve_font_family("title") if hasattr(UIStyle, "resolve_font_family") else "IBM Plex Sans", 16, "bold"),
            bg=UIStyle.BG_BASE,
            fg=UIStyle.TEXT_PRIMARY
        )
        title_lbl.pack(pady=UIStyle.SPACE_MD if hasattr(UIStyle, "SPACE_MD") else 8, anchor="w", padx=UIStyle.SPACE_MD if hasattr(UIStyle, "SPACE_MD") else 8)

        # Main Container
        self.main_container = tk.Frame(content_frame, bg=UIStyle.BG_BASE)
        self.main_container.pack(fill="both", expand=True)

        self._create_collapsible_panel(
            self.main_container,
            "skills",
            self.app._t("panel_skills_title", default="Danh sách Kỹ năng"),
            self._build_skills_panel
        )

        self._create_collapsible_panel(
            self.main_container,
            "skill_types",
            self.app._t("panel_types_title", default="Quản lý Loại Kỹ năng"),
            self._build_types_panel
        )

    def _create_collapsible_panel(self, parent_frame, panel_id, title_text, build_func):
        container = tk.Frame(parent_frame, bg=UIStyle.BG_BASE)
        container.pack(fill="x", pady=(0, UIStyle.SPACE_MD if hasattr(UIStyle, "SPACE_MD") else 8), padx=UIStyle.SPACE_MD if hasattr(UIStyle, "SPACE_MD") else 8)

        # Top bar with title and toggle button
        top_bar = tk.Frame(container, bg=UIStyle.BG_SURFACE)
        top_bar.pack(fill="x")

        # Content frame (visible by default)
        content_frame = tk.Frame(container, bg=UIStyle.BG_BASE)

        is_open = True

        def toggle():
            nonlocal is_open
            if is_open:
                content_frame.pack_forget()
                title_btn.config(text=f"▶ {title_text}")
                is_open = False
            else:
                content_frame.pack(fill="both", expand=True, pady=UIStyle.SPACE_SM if hasattr(UIStyle, "SPACE_SM") else 4)
                title_btn.config(text=f"▼ {title_text}")
                is_open = True

        # Let the entire top bar act as a button
        font_header = getattr(UIStyle, "FONT_HEADER", ("IBM Plex Sans", 12, "bold"))
        title_btn = tk.Button(
            top_bar,
            text=f"▼ {title_text}",
            anchor="w",
            padx=UIStyle.SPACE_MD if hasattr(UIStyle, "SPACE_MD") else 8,
            pady=UIStyle.SPACE_SM if hasattr(UIStyle, "SPACE_SM") else 4,
            command=toggle,
            **{**UIStyle.get_button_style('secondary'), 'font': font_header}
        )
        title_btn.pack(fill="x")

        # Build content inside
        build_func(content_frame)
        content_frame.pack(fill="both", expand=True, pady=UIStyle.SPACE_SM if hasattr(UIStyle, "SPACE_SM") else 4)

    def _build_skills_panel(self, container):
        # Filters Area
        filter_frame = tk.Frame(container, bg=UIStyle.BG_BASE)
        filter_frame.pack(fill="x", pady=(0, UIStyle.SPACE_MD if hasattr(UIStyle, "SPACE_MD") else 8))

        # Search
        search_lbl = tk.Label(filter_frame, text=self.app._t("lbl_search", default="Tìm kiếm:"), bg=UIStyle.BG_BASE, fg=UIStyle.TEXT_PRIMARY)
        search_lbl.pack(side="left", padx=(0, 5))
        self.search_entry = ttk.Entry(filter_frame, textvariable=self.search_var, width=20)
        self.search_entry.pack(side="left", padx=(0, 15))
        self.search_entry.bind("<KeyRelease>", self._on_search_changed)
        self.search_entry.bind("<Escape>", self._on_clear_search)

        # Class Filter
        class_lbl = tk.Label(filter_frame, text=self.app._t("lbl_class", default="Class:"), bg=UIStyle.BG_BASE, fg=UIStyle.TEXT_PRIMARY)
        class_lbl.pack(side="left", padx=(0, 5))
        self.class_combo = ttk.Combobox(filter_frame, textvariable=self.class_filter_var, state="readonly", width=15)
        self.class_combo.pack(side="left", padx=(0, 15))
        self.class_combo.bind("<<ComboboxSelected>>", lambda e: self._on_filter_changed())

        # Type Filter
        type_lbl = tk.Label(filter_frame, text=self.app._t("lbl_type", default="Loại:"), bg=UIStyle.BG_BASE, fg=UIStyle.TEXT_PRIMARY)
        type_lbl.pack(side="left", padx=(0, 5))
        self.type_combo = ttk.Combobox(filter_frame, textvariable=self.type_filter_var, state="readonly", width=15)
        self.type_combo.pack(side="left", padx=(0, 15))
        self.type_combo.bind("<<ComboboxSelected>>", lambda e: self._on_filter_changed())

        # Page size
        page_size_lbl = tk.Label(filter_frame, text=self.app._t("lbl_page_size", default="Page size:"), bg=UIStyle.BG_BASE, fg=UIStyle.TEXT_PRIMARY)
        page_size_lbl.pack(side="left", padx=(0, 5))
        self.page_size_var = tk.StringVar(value="25")
        self.page_size_box = ttk.Combobox(filter_frame, textvariable=self.page_size_var, state="readonly", width=5, values=["25", "50", "100", "200"])
        self.page_size_box.pack(side="left", padx=(0, 5))
        self.page_size_box.bind("<<ComboboxSelected>>", lambda e: self._on_filter_changed())

        # Treeview Area
        table_frame = tk.Frame(container, bg=UIStyle.BG_BASE)
        table_frame.pack(fill="both", expand=True)

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
            height=12,
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
        bottom_bar = tk.Frame(container, bg=UIStyle.BG_SURFACE, height=50)
        bottom_bar.pack(side="bottom", fill="x", pady=UIStyle.SPACE_SM if hasattr(UIStyle, "SPACE_SM") else 4)

        add_btn = tk.Button(
            bottom_bar,
            text=self.app._t("btn_add", default="Thêm"),
            command=self._add_skill,
            **UIStyle.get_button_style("primary")
        )
        add_btn.pack(side="left", padx=UIStyle.SPACE_MD if hasattr(UIStyle, "SPACE_MD") else 8, pady=UIStyle.SPACE_SM if hasattr(UIStyle, "SPACE_SM") else 4)

        edit_btn = tk.Button(
            bottom_bar,
            text=self.app._t("btn_edit", default="Sửa"),
            command=self._edit_skill,
            **UIStyle.get_button_style("primary")
        )
        edit_btn.pack(side="left", padx=UIStyle.SPACE_MD if hasattr(UIStyle, "SPACE_MD") else 8, pady=UIStyle.SPACE_SM if hasattr(UIStyle, "SPACE_SM") else 4)

        del_btn = tk.Button(
            bottom_bar,
            text=self.app._t("btn_delete", default="Xóa"),
            command=self._delete_skill,
            **{**UIStyle.get_button_style("primary"), "bg": UIStyle.DANGER, "activebackground": "#ef4444", "fg": "#ffffff", "activeforeground": "#ffffff"}
        )
        del_btn.pack(side="left", padx=UIStyle.SPACE_MD if hasattr(UIStyle, "SPACE_MD") else 8, pady=UIStyle.SPACE_SM if hasattr(UIStyle, "SPACE_SM") else 4)

        ref_btn = tk.Button(
            bottom_bar,
            text=self.app._t("btn_refresh", default="Refresh"),
            command=self._load_skills,
            **UIStyle.get_button_style("secondary")
        )
        ref_btn.pack(side="right", padx=UIStyle.SPACE_MD if hasattr(UIStyle, "SPACE_MD") else 8, pady=UIStyle.SPACE_SM if hasattr(UIStyle, "SPACE_SM") else 4)

        # Pagination controls
        self.next_btn = tk.Button(
            bottom_bar,
            text="Next",
            command=self._next_page,
            bg=UIStyle.BG_BASE,
            fg=UIStyle.TEXT_PRIMARY,
            relief="flat"
        )
        self.next_btn.pack(side="right", padx=(0, 10), pady=UIStyle.SPACE_SM if hasattr(UIStyle, "SPACE_SM") else 4)

        self.page_lbl = tk.Label(bottom_bar, text="1 / 1", bg=UIStyle.BG_SURFACE, fg=UIStyle.TEXT_SECONDARY)
        self.page_lbl.pack(side="right", padx=(0, 10), pady=UIStyle.SPACE_SM if hasattr(UIStyle, "SPACE_SM") else 4)

        self.prev_btn = tk.Button(
            bottom_bar,
            text="Prev",
            command=self._prev_page,
            bg=UIStyle.BG_BASE,
            fg=UIStyle.TEXT_PRIMARY,
            relief="flat"
        )
        self.prev_btn.pack(side="right", padx=(0, 10), pady=UIStyle.SPACE_SM if hasattr(UIStyle, "SPACE_SM") else 4)

    def _build_types_panel(self, container):
        # 50/50 Layout
        pane = ttk.PanedWindow(container, orient=tk.HORIZONTAL)
        pane.pack(fill="both", expand=True)

        # Left side: Treeview
        left_frame = tk.Frame(pane, bg=UIStyle.BG_BASE)
        pane.add(left_frame, weight=1)

        # Right side: Form
        right_frame = tk.Frame(pane, bg=UIStyle.BG_BASE, padx=UIStyle.SPACE_LG if hasattr(UIStyle, "SPACE_LG") else 16)
        pane.add(right_frame, weight=1)

        # Build Left Side
        self.type_tree_scroll_y = ttk.Scrollbar(left_frame, orient=tk.VERTICAL)
        self.type_tree_scroll_y.pack(side="right", fill="y")

        self.type_tree = ttk.Treeview(
            left_frame,
            columns=("ID", "Name"),
            show="headings",
            selectmode="browse",
            height=6,
            yscrollcommand=self.type_tree_scroll_y.set
        )
        self.type_tree_scroll_y.config(command=self.type_tree.yview)

        self.type_tree.heading("ID", text="ID")
        self.type_tree.column("ID", width=50, anchor="center")
        self.type_tree.heading("Name", text=self.app._t("col_skill_type_name", default="Tên Loại"))
        self.type_tree.column("Name", width=200, anchor="w")
        self.type_tree.pack(fill="both", expand=True)
        self.type_tree.bind("<<TreeviewSelect>>", self._on_type_selected)

        # Build Right Side
        lbl = tk.Label(right_frame, text=self.app._t("lbl_type_details", default="Chi tiết Loại Kỹ năng"), bg=UIStyle.BG_BASE, fg=UIStyle.TEXT_PRIMARY, font=("IBM Plex Sans", 10, "bold"))
        lbl.pack(anchor="w", pady=(0, 10))

        form_frame = tk.Frame(right_frame, bg=UIStyle.BG_BASE)
        form_frame.pack(fill="x")

        tk.Label(form_frame, text=self.app._t("lbl_type_name", default="Tên Loại:"), bg=UIStyle.BG_BASE, fg=UIStyle.TEXT_PRIMARY).grid(row=0, column=0, sticky="w", pady=5)
        self.type_entry = ttk.Entry(form_frame, textvariable=self.type_name_var, width=30)
        self.type_entry.grid(row=0, column=1, sticky="w", pady=5, padx=5)

        action_frame = tk.Frame(right_frame, bg=UIStyle.BG_BASE)
        action_frame.pack(fill="x", pady=15)

        tk.Button(action_frame, text=self.app._t("btn_save", default="Lưu"), command=self._save_type, **UIStyle.get_button_style("primary")).pack(side="left", padx=(0, 10))
        tk.Button(action_frame, text=self.app._t("btn_cancel", default="Hủy"), command=self._clear_type_form, **UIStyle.get_button_style("secondary")).pack(side="left", padx=(0, 10))
        self.del_type_btn = tk.Button(action_frame, text=self.app._t("btn_delete", default="Xóa"), command=self._delete_type, **{**UIStyle.get_button_style("primary"), "bg": UIStyle.DANGER, "activebackground": "#ef4444", "fg": "#ffffff", "activeforeground": "#ffffff"})
        self.del_type_btn.pack(side="left")

    def _load_classes(self):
        try:
            if hasattr(self.app, "db_class_service"):
                svc = self.app.db_class_service
                classes = svc.get_all_classes()
                self.classes_map = {str(c.get("id") or c.get("class_id", "")): c.get("name") for c in classes}
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

    def _load_types(self):
        try:
            self.type_tree.delete(*self.type_tree.get_children())
            if hasattr(self.app, "db_skill_type_service"):
                svc = self.app.db_skill_type_service
                types = svc.get_all_skill_types()
                self.skill_types = types
                self.types_map = {str(t.get("skill_type_id")): t.get("name") for t in types}

                # Update Combo
                values = ["All"] + [f"{t.get('skill_type_id')} - {t.get('name')}" for t in types]

                # Check if type_combo has been initialized before configuring values
                if hasattr(self, 'type_combo'):
                    self.type_combo.config(values=values)
                    if values and self.type_filter_var.get() not in values:
                        self.type_combo.current(0)

                # Update Tree
                for t in types:
                    self.type_tree.insert("", "end", iid=str(t.get("skill_type_id")), values=(t.get("skill_type_id"), t.get("name")))
            else:
                if hasattr(self, 'type_combo'):
                    self.type_combo.config(values=["All"])
                    self.type_combo.current(0)
        except Exception as e:
            print(f"Error loading types: {e}")
            if hasattr(self, 'type_combo'):
                self.type_combo.config(values=["All"])
                self.type_combo.current(0)

    def _on_type_selected(self, event):
        selected = self.type_tree.selection()
        if not selected:
            return
        item_id = selected[0]
        self.editing_type_id = int(item_id)

        # Find type name
        for t in self.skill_types:
            if str(t.get("skill_type_id")) == item_id:
                self.type_name_var.set(t.get("name", ""))
                break

    def _clear_type_form(self):
        self.editing_type_id = None
        self.type_name_var.set("")
        self.type_tree.selection_remove(self.type_tree.selection())

    def _save_type(self):
        name = self.type_name_var.get().strip()
        if not name:
            messagebox.showwarning("Warning", "Tên loại không được để trống!")
            return

        if hasattr(self.app, "db_skill_type_service"):
            svc = self.app.db_skill_type_service
            if self.editing_type_id:
                # Update
                if svc.update_skill_type(self.editing_type_id, name):
                    self._load_types()
                    self._clear_type_form()
                    self._load_skills() # Update display text
                else:
                    messagebox.showerror("Error", "Lỗi khi cập nhật!")
            else:
                # Create
                new_id = svc.create_skill_type(name)
                if new_id:
                    self._load_types()
                    self._clear_type_form()
                else:
                    messagebox.showerror("Error", "Lỗi khi thêm mới!")

    def _delete_type(self):
        if not self.editing_type_id:
            messagebox.showwarning("Warning", "Chọn một loại để xóa!")
            return

        if messagebox.askyesno("Confirm", "Bạn có chắc muốn xóa loại kỹ năng này?"):
            if hasattr(self.app, "db_skill_type_service"):
                svc = self.app.db_skill_type_service
                if svc.delete_skill_type(self.editing_type_id):
                    self._load_types()
                    self._clear_type_form()
                    self._load_skills()
                else:
                    messagebox.showerror("Error", "Lỗi khi xóa! Có thể loại này đang được sử dụng.")


    def _on_search_changed(self, event=None):
        if hasattr(self, "_search_timer"):
            self.after_cancel(self._search_timer)
        self._search_timer = self.after(500, self._apply_search)

    def _apply_search(self):
        self.current_page = 1
        self._load_skills()

    def _on_clear_search(self, event=None):
        self.search_var.set("")
        self._apply_search()

    def _on_filter_changed(self):
        self.current_page = 1
        self._load_skills()

    def _next_page(self):
        if self.current_page < self.total_pages:
            self.current_page += 1
            self._load_skills()

    def _prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
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
                skill_type = None
                if type_val and type_val != "All":
                    try:
                        skill_type = int(type_val.split(" - ")[0])
                    except:
                        pass

                class_val = self.class_filter_var.get()
                class_id = None
                if class_val and class_val != "All":
                    try:
                        class_id = int(class_val.split(" - ")[0])
                    except:
                        pass

                try:
                    self.items_per_page = int(self.page_size_var.get())
                except:
                    self.items_per_page = 25

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

        # Update treeview
        for item in self.tree.get_children():
            self.tree.delete(item)

        for s in self.skills:
            if isinstance(s, dict):
                values = (
                    s.get("skill_id", ""),
                    s.get("name", "Unknown"),
                    s.get("type", str(s.get("skill_type_id", ""))),
                    s.get("class_id", ""),
                    s.get("alias", "")
                )
                self.tree.insert("", "end", iid=str(s.get("skill_id", str(id(s)))), values=values)

    def _add_skill(self):
        from ui.dialogs.skill_edit_dialog import SkillEditDialog

        def on_save(data):
            if hasattr(self.app, "db_skill_service"):
                svc = self.app.db_skill_service
                success_id = svc.create_skill(data)
                if success_id:
                    if hasattr(self.app, "notification_widget") and self.app.notification_widget:
                        self.app.notification_widget.show(
                            self.app._t("msg_add_skill_success", default="Thêm kỹ năng thành công."),
                            type="success"
                        )
                    self._load_skills()
                else:
                    if hasattr(self.app, "notification_widget") and self.app.notification_widget:
                        self.app.notification_widget.show(
                            self.app._t("err_add_skill", default="Không thể thêm kỹ năng."),
                            type="error"
                        )

        dialog = SkillEditDialog(
            parent=self.winfo_toplevel(),
            app=self.app,
            title=self.app._t("title_add_skill", default="Thêm Kỹ năng"),
            skill_data=None,
            on_save=on_save
        )

    def _edit_skill(self):
        from ui.dialogs.skill_edit_dialog import SkillEditDialog

        selected = self.tree.selection()
        if not selected:
            if hasattr(self.app, "notification_widget") and self.app.notification_widget:
                self.app.notification_widget.show(
                    self.app._t("warn_no_sel_skill", default="Vui lòng chọn kỹ năng để sửa"),
                    type="warning"
                )
            return

        s_id = selected[0]
        target_skill = None
        for s in self.skills:
            if str(s.get("skill_id", "")) == s_id:
                target_skill = s
                break

        if target_skill:
            def on_save(data):
                if hasattr(self.app, "db_skill_service"):
                    svc = self.app.db_skill_service
                    skill_id = data.get("skill_id")
                    if skill_id is None:
                        return

                    success = svc.update_skill(skill_id, data)
                    if success:
                        if hasattr(self.app, "notification_widget") and self.app.notification_widget:
                            self.app.notification_widget.show(
                                self.app._t("msg_edit_skill_success", default="Cập nhật kỹ năng thành công."),
                                type="success"
                            )
                        self._load_skills()
                    else:
                        if hasattr(self.app, "notification_widget") and self.app.notification_widget:
                            self.app.notification_widget.show(
                                self.app._t("err_edit_skill", default="Không thể cập nhật kỹ năng."),
                                type="error"
                            )

            dialog = SkillEditDialog(
                parent=self.winfo_toplevel(),
                app=self.app,
                title=self.app._t("title_edit_skill", default="Sửa Kỹ năng"),
                skill_data=target_skill,
                on_save=on_save
            )

    def _delete_skill(self):
        selected = self.tree.selection()
        if not selected:
            if hasattr(self.app, "notification_widget") and self.app.notification_widget:
                self.app.notification_widget.show(
                    self.app._t("warn_no_sel_skill", default="Vui lòng chọn kỹ năng để xóa"),
                    type="warning"
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
                self.app._t("title_confirm_del", default="Xác nhận xóa"),
                self.app._t("msg_confirm_del_skill", default="Bạn có chắc chắn muốn xóa kỹ năng '{0}'?").format(name),
                parent=self.winfo_toplevel()
            )
            if confirm:
                if hasattr(self.app, "db_skill_service"):
                    svc = self.app.db_skill_service
                    skill_id = target_skill.get("skill_id")
                    if skill_id is not None:
                        success = svc.delete_skill(skill_id)
                        if success:
                            if hasattr(self.app, "notification_widget") and self.app.notification_widget:
                                self.app.notification_widget.show(
                                    self.app._t("msg_del_skill_success", default="Xóa kỹ năng thành công."),
                                    type="success"
                                )
                            self._load_skills()
                        else:
                            if hasattr(self.app, "notification_widget") and self.app.notification_widget:
                                self.app.notification_widget.show(
                                    self.app._t("err_del_skill", default="Không thể xóa kỹ năng."),
                                    type="error"
                                )

    def on_view_shown(self):
        self._load_skills()

    def on_view_hidden(self):
        pass
