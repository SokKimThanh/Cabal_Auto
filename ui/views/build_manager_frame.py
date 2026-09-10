import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from typing import Dict, Any, List, Optional
import math

from ui.components.base.responsive_grid_base import ResponsiveGridBase
from lib.ui_style_v2 import UIStyleV2 as UIStyle

class BuildEditDialog(tk.Toplevel):
    def __init__(self, parent, app, title: str, build_data: Optional[Dict[str, Any]], classes: List[Dict[str, Any]], on_save):
        super().__init__(parent)
        self.app = app
        self.title(title)
        self.build_data = build_data or {}
        self.classes = classes
        self.on_save = on_save

        self.transient(parent)
        self.grab_set()

        self.config(bg=UIStyle.BG_BASE)
        self.geometry("450x350")
        self.resizable(False, False)

        self._setup_ui()
        self._center_window()
        self._populate_data()
        self.focus_set()

    def _center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    def _setup_ui(self):
        main_frame = tk.Frame(self, bg=UIStyle.BG_BASE)
        main_frame.pack(fill="both", expand=True, padx=UIStyle.SPACE_MD, pady=UIStyle.SPACE_MD)

        # Class Combobox
        tk.Label(main_frame, text="Class (*):", bg=UIStyle.BG_BASE, fg=UIStyle.TEXT_PRIMARY).grid(row=0, column=0, sticky="e", pady=5, padx=5)
        self.class_var = tk.StringVar()
        self.class_cb = ttk.Combobox(main_frame, textvariable=self.class_var, state="readonly", width=30)

        self.class_options = [f"{c.get('id', c.get('class_id', ''))} - {c.get('name', 'Unknown')}" for c in self.classes]
        if not self.class_options:
            self.class_options = ["0 - None"]

        self.class_cb['values'] = self.class_options
        self.class_cb.grid(row=0, column=1, sticky="w", pady=5, padx=5)

        # Author
        tk.Label(main_frame, text="Author:", bg=UIStyle.BG_BASE, fg=UIStyle.TEXT_PRIMARY).grid(row=1, column=0, sticky="e", pady=5, padx=5)
        self.author_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.author_var, width=33).grid(row=1, column=1, sticky="w", pady=5, padx=5)

        # Description
        tk.Label(main_frame, text="Description:", bg=UIStyle.BG_BASE, fg=UIStyle.TEXT_PRIMARY).grid(row=2, column=0, sticky="ne", pady=5, padx=5)
        self.desc_text = tk.Text(main_frame, width=33, height=4, bg=UIStyle.BG_SURFACE, fg=UIStyle.TEXT_PRIMARY, insertbackground=UIStyle.TEXT_PRIMARY)
        self.desc_text.grid(row=2, column=1, sticky="w", pady=5, padx=5)

        # Upvote Count (readonly but we can set initial)
        tk.Label(main_frame, text="Upvotes:", bg=UIStyle.BG_BASE, fg=UIStyle.TEXT_PRIMARY).grid(row=3, column=0, sticky="e", pady=5, padx=5)
        self.upvote_var = tk.IntVar(value=0)
        upvote_spin = ttk.Spinbox(main_frame, from_=0, to=999999, increment=1, textvariable=self.upvote_var, width=10)
        upvote_spin.grid(row=3, column=1, sticky="w", pady=5, padx=5)

        btn_frame = tk.Frame(main_frame, bg=UIStyle.BG_BASE)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=20)

        tk.Button(btn_frame, text="Save", command=self._on_save_click, **UIStyle.get_button_style("primary")).pack(side="left", padx=10)
        tk.Button(btn_frame, text="Cancel", command=self.destroy, **UIStyle.get_button_style("secondary")).pack(side="left", padx=10)

    def _populate_data(self):
        if not self.build_data:
            if self.class_options:
                self.class_cb.set(self.class_options[0])
            return

        cid = self.build_data.get("class_id")
        if cid is not None:
            for opt in self.class_options:
                if opt.startswith(f"{cid} -"):
                    self.class_cb.set(opt)
                    break
        else:
            if self.class_options:
                self.class_cb.set(self.class_options[0])

        self.author_var.set(self.build_data.get("author", ""))
        self.desc_text.insert("1.0", self.build_data.get("description", ""))
        self.upvote_var.set(self.build_data.get("upvote_count", 0))

    def _on_save_click(self):
        class_str = self.class_var.get()
        class_id = None
        try:
            class_id = int(class_str.split(" - ")[0])
        except (ValueError, IndexError):
            messagebox.showerror("Lỗi", "Vui lòng chọn Class hợp lệ.", parent=self)
            return

        if class_id == 0:
            messagebox.showerror("Lỗi", "Khóa ngoại class_id không được để trống/None.", parent=self)
            return

        data = {
            "class_id": class_id,
            "author": self.author_var.get().strip(),
            "description": self.desc_text.get("1.0", tk.END).strip(),
            "upvote_count": self.upvote_var.get(),
        }

        if "build_id" in self.build_data:
            data["build_id"] = self.build_data["build_id"]

        self.on_save(data)
        self.destroy()


class BuildManagerFrame(ResponsiveGridBase):
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
        content.columnconfigure(0, weight=1)
        content.rowconfigure(1, weight=1)

        # Top Bar
        top_bar = tk.Frame(content, bg=UIStyle.BG_BASE)
        top_bar.grid(row=0, column=0, sticky="ew", padx=UIStyle.SPACE_MD, pady=UIStyle.SPACE_MD)

        # Add Button
        add_btn = tk.Button(
            top_bar,
            text=self.app._t("btn_add_build", default="➕ Thêm Build"),
            command=self._add_build,
            **UIStyle.get_button_style("primary")
        )
        add_btn.pack(side="left", padx=(0, UIStyle.SPACE_MD))

        # Class Filter
        tk.Label(top_bar, text="Filter Class:", bg=UIStyle.BG_BASE, fg=UIStyle.TEXT_PRIMARY).pack(side="left", padx=(UIStyle.SPACE_MD, UIStyle.SPACE_XS))
        self.filter_class_var = tk.StringVar()
        self.filter_class_cb = ttk.Combobox(top_bar, textvariable=self.filter_class_var, state="readonly", width=25)
        self.filter_class_cb.pack(side="left", padx=UIStyle.SPACE_XS)
        self.filter_class_cb.bind("<<ComboboxSelected>>", self._on_filter_changed)

        # Search Bar
        tk.Label(top_bar, text="Search:", bg=UIStyle.BG_BASE, fg=UIStyle.TEXT_PRIMARY).pack(side="left", padx=(UIStyle.SPACE_MD, UIStyle.SPACE_XS))
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(top_bar, textvariable=self.search_var, width=30)
        search_entry.pack(side="left")
        search_entry.bind("<KeyRelease>", self._on_search_delayed)
        self._search_timer = None

        # Table
        table_frame = tk.Frame(content, bg=UIStyle.BG_BASE)
        table_frame.grid(row=1, column=0, sticky="nsew", padx=UIStyle.SPACE_MD)

        columns = ("ID", "Class Name", "Author", "Description", "Upvotes")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", style="Custom.Treeview")

        self.tree.heading("ID", text="Build ID")
        self.tree.heading("Class Name", text="Class Name")
        self.tree.heading("Author", text="Author")
        self.tree.heading("Description", text="Description")
        self.tree.heading("Upvotes", text="Upvotes")

        self.tree.column("ID", width=60, anchor="center")
        self.tree.column("Class Name", width=150, anchor="w")
        self.tree.column("Author", width=120, anchor="w")
        self.tree.column("Description", width=300, anchor="w")
        self.tree.column("Upvotes", width=80, anchor="center")

        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)

        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        self.tree.bind("<Double-1>", lambda e: self._edit_build())

        # Action Bar (Bottom)
        bottom_bar = tk.Frame(content, bg=UIStyle.BG_BASE)
        bottom_bar.grid(row=2, column=0, sticky="ew", padx=UIStyle.SPACE_MD, pady=UIStyle.SPACE_MD)

        action_frame = tk.Frame(bottom_bar, bg=UIStyle.BG_BASE)
        action_frame.pack(side="left")

        edit_btn = tk.Button(action_frame, text=self.app._t("btn_edit", default=" Sửa"), command=self._edit_build, **UIStyle.get_button_style("secondary"))
        edit_btn.pack(side="left", padx=(0, UIStyle.SPACE_XS))

        del_btn = tk.Button(action_frame, text=self.app._t("btn_delete", default=" Xóa"), command=self._delete_build, **UIStyle.get_button_style("danger"))
        del_btn.pack(side="left", padx=UIStyle.SPACE_XS)

        # Pagination
        page_frame = tk.Frame(bottom_bar, bg=UIStyle.BG_BASE)
        page_frame.pack(side="right")

        self.btn_prev_page = tk.Button(
            page_frame, text="<", command=self._prev_page, width=3,
            **UIStyle.get_button_style("secondary")
        )
        self.btn_prev_page.pack(side="left", padx=UIStyle.SPACE_XS)

        self.lbl_page_info = tk.Label(page_frame, text="1 / 1", bg=UIStyle.BG_BASE, fg=UIStyle.TEXT_PRIMARY)
        self.lbl_page_info.pack(side="left", padx=UIStyle.SPACE_SM)

        self.btn_next_page = tk.Button(
            page_frame, text=">", command=self._next_page, width=3,
            **UIStyle.get_button_style("secondary")
        )
        self.btn_next_page.pack(side="left", padx=UIStyle.SPACE_XS)

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
