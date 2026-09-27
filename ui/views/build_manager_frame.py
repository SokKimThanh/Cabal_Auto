import tkinter as tk
from ui.components import create_icon_button
from ui.dialogs.build_edit_dialog import BuildEditDialog
from lib.events.ui_element_registry import CommonUI
from tkinter import ttk, messagebox, simpledialog
from typing import Dict, Any, List, Optional
import math

from ui.components.base.responsive_grid_base import ResponsiveGridBase
from lib.ui_style_v2 import UIStyleV2 as UIStyle



class BuildManagerFrame(ResponsiveGridBase):
    MODULE_NAME = "build_manager"
    SCREEN_NAME = "main"

    def __init__(self, parent, app):
        super().__init__(parent, app=app, bg=UIStyle.BG_BASE)
        self.app = app

        self.builds = []
        self.filtered_builds = []
        self.classes_map = {}

        self.current_page = 1
        self.items_per_page = 20
        self.total_pages = 1
        self.total_items = 0

        self._build_ui()

    def _build_ui(self):
        content = self.get_content_frame()
        # Title Label
        title_lbl = tk.Label(
            content,
            font=(UIStyle.resolve_font_family("title"), 16, "bold"),
            bg=UIStyle.BG_BASE,
            fg=UIStyle.TEXT_PRIMARY
        )
        if hasattr(self.app, "bind_text"):
            self.app.bind_text(title_lbl, "build_manager_title")
        else:
            title_lbl.config(text=self.app._t("build_manager_title", default="Quản Lý Build"))
        title_lbl.pack(pady=UIStyle.SPACE_MD)

        self._create_search_bar(content)

        # -------------------------------------------------------------
        # Action Bar (Bottom) - Packed FIRST from Bottom
        # -------------------------------------------------------------
        bottom_bar = tk.Frame(content, bg=UIStyle.BG_SURFACE, height=50)
        bottom_bar.pack(side="bottom", fill="x", pady=UIStyle.SPACE_SM)

        add_btn = create_icon_button(
            parent=bottom_bar,
            icon_name="add",
            text=self.app._t("btn_add", default="Thêm"),
            command=self._add_build,
            button_type="green_light",
            element_id=CommonUI.BTN_ADD
        )
        add_btn.pack(side="left", padx=UIStyle.SPACE_MD, pady=UIStyle.SPACE_SM)

        edit_btn = create_icon_button(
            parent=bottom_bar,
            icon_name="edit",
            text=self.app._t("btn_edit", default="Sửa"),
            command=self._edit_build,
            button_type="blue",
            element_id=CommonUI.BTN_EDIT
        )
        edit_btn.pack(side="left", padx=UIStyle.SPACE_MD, pady=UIStyle.SPACE_SM)

        del_btn = create_icon_button(
            parent=bottom_bar,
            icon_name="delete",
            text=self.app._t("btn_delete", default="Xóa"),
            command=self._delete_build,
            button_type="red",
            element_id=CommonUI.BTN_DELETE
        )
        del_btn.pack(side="left", padx=UIStyle.SPACE_MD, pady=UIStyle.SPACE_SM)

        self.btn_apply_build = create_icon_button(
            parent=bottom_bar,
            icon_name="play",
            text=self.app._t("btn_apply_build", default="Apply Build"),
            command=self._apply_build,
            button_type="green",
            element_id="btn_apply_build"
        )
        self.btn_apply_build.pack(side="left", padx=UIStyle.SPACE_MD, pady=UIStyle.SPACE_SM)
        self.btn_apply_build.config(state="disabled")

        ref_btn = create_icon_button(
            parent=bottom_bar,
            icon_name="refresh",
            text=self.app._t("btn_refresh", default="Làm mới"),
            command=self._on_refresh,
            button_type="refresh",
            element_id=CommonUI.BTN_REFRESH
        )
        ref_btn.pack(side="right", padx=UIStyle.SPACE_MD, pady=UIStyle.SPACE_SM)

        # Pagination controls in bottom bar
        self.btn_next_page = create_icon_button(
            parent=bottom_bar,
            icon_name="right",
            text=self.app._t("btn_next", default="Sau"),
            command=self._next_page,
            button_type="refresh",
            element_id="build_mgr_btn_next_page"
        )
        self.btn_next_page.pack(side="right", padx=(0, UIStyle.SPACE_MD), pady=UIStyle.SPACE_SM)

        self.lbl_page_info = tk.Label(
            bottom_bar,
            text="1 / 1",
            bg=UIStyle.BG_SURFACE,
            fg=UIStyle.TEXT_PRIMARY
        )
        self.lbl_page_info.pack(side="right", padx=(0, 10))

        self.btn_prev_page = create_icon_button(
            parent=bottom_bar,
            icon_name="left",
            text=self.app._t("btn_prev", default="Trước"),
            command=self._prev_page,
            button_type="refresh",
            element_id="build_mgr_btn_prev_page"
        )
        self.btn_prev_page.pack(side="right", padx=(0, 10), pady=UIStyle.SPACE_SM)

        # -------------------------------------------------------------
        # Table - Packed LAST to expand in the middle
        # -------------------------------------------------------------
        table_frame = tk.Frame(content, bg=UIStyle.BG_BASE)
        table_frame.pack(side="top", fill="both", expand=True, padx=UIStyle.SPACE_MD, pady=UIStyle.SPACE_MD)

        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        self.tree_scroll_y = ttk.Scrollbar(table_frame, orient=tk.VERTICAL)
        self.tree_scroll_x = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL)

        columns = ("ID", "Class Name", "Author", "Description", "Upvotes")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", style="Custom.Treeview",
                                 yscrollcommand=self._autoscroll_y, xscrollcommand=self._autoscroll_x)

        self.tree_scroll_y.config(command=self.tree.yview)
        self.tree_scroll_x.config(command=self.tree.xview)

        self.tree.heading("ID", text="Build ID")
        self.tree.heading("Class Name", text="Class Name")
        self.tree.heading("Author", text="Author")
        self.tree.heading("Description", text="Description")
        self.tree.heading("Upvotes", text="Upvotes")

        self.tree.column("ID", width=60, anchor="center", minwidth=50)
        self.tree.column("Class Name", width=150, anchor="w", minwidth=100)
        self.tree.column("Author", width=120, anchor="w", minwidth=80)
        self.tree.column("Description", width=300, anchor="w", minwidth=150)
        self.tree.column("Upvotes", width=80, anchor="center", minwidth=50)

        self.tree.grid(row=0, column=0, sticky="nsew")

        self.tree.bind("<Double-1>", lambda e: self._edit_build())
        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)

        # -------------------------------------------------------------
        # Details/Preview Area
        # -------------------------------------------------------------
        self.details_frame = tk.Frame(table_frame, bg=UIStyle.BG_SURFACE, height=100)
        self.details_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(UIStyle.SPACE_MD, 0))
        self.details_frame.grid_propagate(False)

        # Labels for selected skills
        lbl_atk = tk.Label(self.details_frame, text=self.app._t("lbl_attack_skills", default="Attack Skills:"), bg=UIStyle.BG_SURFACE, fg=UIStyle.TEXT_PRIMARY, font=("", 10, "bold"))
        lbl_atk.grid(row=0, column=0, sticky="w", padx=UIStyle.SPACE_SM, pady=(UIStyle.SPACE_SM, 0))
        self.lbl_atk_val = tk.Label(self.details_frame, text="-", bg=UIStyle.BG_SURFACE, fg=UIStyle.TEXT_SECONDARY)
        self.lbl_atk_val.grid(row=0, column=1, sticky="w", padx=UIStyle.SPACE_SM, pady=(UIStyle.SPACE_SM, 0))

        lbl_buff = tk.Label(self.details_frame, text=self.app._t("lbl_buff_skills", default="Buff Skills:"), bg=UIStyle.BG_SURFACE, fg=UIStyle.TEXT_PRIMARY, font=("", 10, "bold"))
        lbl_buff.grid(row=1, column=0, sticky="w", padx=UIStyle.SPACE_SM, pady=UIStyle.SPACE_SM)
        self.lbl_buff_val = tk.Label(self.details_frame, text="-", bg=UIStyle.BG_SURFACE, fg=UIStyle.TEXT_SECONDARY)
        self.lbl_buff_val.grid(row=1, column=1, sticky="w", padx=UIStyle.SPACE_SM, pady=UIStyle.SPACE_SM)



    def _on_tree_select(self, event=None):
        selected = self.tree.selection()
        if not selected:
            self.lbl_atk_val.config(text="-")
            self.lbl_buff_val.config(text="-")
            if hasattr(self, 'btn_apply_build'):
                self.btn_apply_build.config(state="disabled")
            return

        build_id = selected[0]
        build_data = next((b for b in self.builds if str(b.get("build_id")) == build_id), None)
        if build_data:
            atk_ids = build_data.get("attack_skill_ids", [])
            buff_ids = build_data.get("buff_skill_ids", [])
            self.lbl_atk_val.config(text=str(atk_ids) if atk_ids else self.app._t("lbl_none", default="None"))
            self.lbl_buff_val.config(text=str(buff_ids) if buff_ids else self.app._t("lbl_none", default="None"))
            if hasattr(self, 'btn_apply_build'):
                self.btn_apply_build.config(state="normal")
        else:
            self.lbl_atk_val.config(text="-")
            self.lbl_buff_val.config(text="-")
            if hasattr(self, 'btn_apply_build'):
                self.btn_apply_build.config(state="disabled")

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

        lbl_search = tk.Label(search_frame, bg=UIStyle.BG_BASE, fg=UIStyle.TEXT_PRIMARY)
        if hasattr(self.app, "bind_text"):
            self.app.bind_text(lbl_search, "search_label")
        else:
            lbl_search.config(text=self.app._t("search_label", default="Tìm kiếm:"))
        lbl_search.grid(row=0, column=0, padx=(5, 5), pady=5, sticky="w")

        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        self.search_entry.grid(row=0, column=1, sticky="ew", padx=(0, 5), pady=5)
        self.search_entry.bind("<KeyRelease>", self._on_search_delayed)
        self.search_entry.bind("<Escape>", self._on_clear_search)
        self._search_timer = None

        self.filter_class_var = tk.StringVar()
        self.filter_class_cb = ttk.Combobox(search_frame, textvariable=self.filter_class_var, state="readonly", width=25)
        self.filter_class_cb.grid(row=0, column=2, sticky="ew", padx=(0, 5), pady=5)
        self.filter_class_cb.bind("<<ComboboxSelected>>", self._on_filter_changed)

        search_frame.columnconfigure(1, weight=1)

    def _on_clear_search(self, event=None) -> None:
        self.search_var.set("")
        self._apply_filters()

    def _on_refresh(self) -> None:
        self.search_var.set("")
        self.filter_class_var.set("All Classes")
        self.current_page = 1
        self._load_classes_and_builds()

    def on_view_shown(self):
        """Called when this view becomes active in the shell."""
        self._load_classes_and_builds()

    def _load_classes_and_builds(self):
        if not hasattr(self.app, 'db_class_service') or not hasattr(self.app, 'db_build_service'):
            return

        classes = self.app.db_class_service.get_all_classes()

        # Populate Classes map
        self.classes_map = {}
        for c in classes:
            cid = c.get("id") or c.get("class_id")
            if cid is not None:
                self.classes_map[cid] = c.get("name", f"Class {cid}")

        # Update Filter Options
        filter_opts = ["All Classes"]
        for c in classes:
            cid = c.get("id") or c.get("class_id")
            if cid is not None:
                filter_opts.append(f"{cid} - {c.get('name', 'Unknown')}")

        self.filter_class_cb['values'] = filter_opts
        if not self.filter_class_var.get() or self.filter_class_var.get() not in filter_opts:
            self.filter_class_cb.set("All Classes")

        self.builds = self.app.db_build_service.get_builds()
        self._apply_filters()

    def _on_search_delayed(self, event=None):
        if self._search_timer:
            self.after_cancel(self._search_timer)
        self._search_timer = self.after(500, self._apply_filters)

    def _on_filter_changed(self, event=None):
        self._apply_filters()

    def _apply_filters(self):
        keyword = self.search_var.get().lower().strip()
        class_filter_val = self.filter_class_var.get()

        filter_class_id = None
        if class_filter_val and class_filter_val != "All Classes":
            try:
                filter_class_id = int(class_filter_val.split(" - ")[0])
            except (ValueError, IndexError):
                pass

        self.filtered_builds = []
        for b in self.builds:
            # Check class filter
            b_cid = b.get("class_id")
            if filter_class_id is not None and b_cid != filter_class_id:
                continue

            # Check keyword
            if keyword:
                class_name = self.classes_map.get(b_cid, "").lower()
                author = b.get("author", "").lower()
                desc = b.get("description", "").lower()
                if keyword not in class_name and keyword not in author and keyword not in desc:
                    continue

            self.filtered_builds.append(b)

        self.total_items = len(self.filtered_builds)
        self.total_pages = max(1, math.ceil(self.total_items / self.items_per_page))

        if self.current_page > self.total_pages:
            self.current_page = 1

        self._refresh_tree()
        self._update_page_ui()

    def _refresh_tree(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        start_idx = (self.current_page - 1) * self.items_per_page
        end_idx = start_idx + self.items_per_page

        page_data = self.filtered_builds[start_idx:end_idx]

        for b in page_data:
            cid = b.get("class_id")
            cname = self.classes_map.get(cid, f"Class {cid}" if cid else "Unknown")

            values = (
                b.get("build_id", ""),
                cname,
                b.get("author", ""),
                b.get("description", ""),
                b.get("upvote_count", 0)
            )
            self.tree.insert("", "end", iid=str(b.get("build_id", "")), values=values)

    def _update_page_ui(self):
        if self.total_items == 0:
            self.lbl_page_info.config(text="0 / 0")
            self.btn_prev_page.config(state="disabled")
            self.btn_next_page.config(state="disabled")
            return

        self.lbl_page_info.config(text=f"{self.current_page} / {self.total_pages}")

        if self.current_page <= 1:
            self.btn_prev_page.config(state="disabled")
        else:
            self.btn_prev_page.config(state="normal")

        if self.current_page >= self.total_pages:
            self.btn_next_page.config(state="disabled")
        else:
            self.btn_next_page.config(state="normal")

    def _prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self._refresh_tree()
            self._update_page_ui()

    def _next_page(self):
        if self.current_page < self.total_pages:
            self.current_page += 1
            self._refresh_tree()
            self._update_page_ui()

    def _apply_build(self):
        selected = self.tree.selection()
        if not selected:
            return
        build_id = selected[0]
        print(f"Apply build clicked for build_id: {build_id}")
        # Event or business logic will be handled in future batches

    def _add_build(self):
        if not hasattr(self.app, 'db_class_service'):
            return
        classes = self.app.db_class_service.get_all_classes()
        BuildEditDialog(self, self.app, self.app._t("title_add_build", default="Thêm Build"), None, classes, self._on_save_build)

    def _edit_build(self):
        selected = self.tree.selection()
        if not selected:
            return

        build_id = selected[0]
        build_data = next((b for b in self.builds if str(b.get("build_id")) == build_id), None)

        if build_data:
            classes = self.app.db_class_service.get_all_classes()
            BuildEditDialog(self, self.app, self.app._t("title_edit_build", default="Sửa Build"), build_data, classes, self._on_save_build)

    def _delete_build(self):
        selected = self.tree.selection()
        if not selected:
            return

        build_id = selected[0]

        if messagebox.askyesno(
            self.app._t("confirm_title", default="Xác nhận"),
            self.app._t("confirm_delete_build", default="Bạn có chắc muốn xóa build này?"),
            parent=self
        ):
            if hasattr(self.app, 'db_build_service'):
                success = self.app.db_build_service.delete_build(int(build_id))
                if success:
                    self._load_classes_and_builds()
                else:
                    messagebox.showerror(self.app._t("err_title", default="Lỗi"), self.app._t("err_delete_build", default="Không thể xóa build."), parent=self)

    def _on_save_build(self, data: Dict[str, Any]):
        if not hasattr(self.app, 'db_build_service'):
            return

        success = False
        if "build_id" in data:
            success = self.app.db_build_service.update_build(data["build_id"], data)
        else:
            res = self.app.db_build_service.create_build(data)
            success = res is not None

        if success:
            self._load_classes_and_builds()
        else:
            messagebox.showerror(self.app._t("err_title", default="Lỗi"), self.app._t("err_save_build", default="Lỗi khi lưu build."), parent=self)
