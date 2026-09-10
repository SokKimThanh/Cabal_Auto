import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from typing import Dict, Any, List, Optional
import math

from ui.components.base.responsive_grid_base import ResponsiveGridBase
from lib.ui_style_v2 import UIStyleV2 as UIStyle

class ClassEditDialog(tk.Toplevel):
    def __init__(self, parent, app, title: str, class_data: Optional[Dict[str, Any]], on_save):
        super().__init__(parent)
        self.app = app
        self.title(title)
        self.class_data = class_data or {}
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

        row = 0
        # ID Field (Read-only, only show if editing)
        if self.class_data.get("id"):
            tk.Label(main_frame, text=self.app._t("col_id", default="ID"), bg=UIStyle.BG_BASE, fg=UIStyle.TEXT_MUTED).grid(row=row, column=0, sticky="w", pady=(0, UIStyle.SPACE_SM))
            self.id_var = tk.StringVar()
            entry_id = ttk.Entry(main_frame, textvariable=self.id_var, state="readonly")
            entry_id.grid(row=row, column=1, sticky="ew", pady=(0, UIStyle.SPACE_SM))
            row += 1

        # Name Field
        tk.Label(main_frame, text=self.app._t("col_name", default="Name") + " *", bg=UIStyle.BG_BASE, fg=UIStyle.TEXT_PRIMARY).grid(row=row, column=0, sticky="w", pady=(0, UIStyle.SPACE_SM))
        self.name_var = tk.StringVar()
        self.entry_name = ttk.Entry(main_frame, textvariable=self.name_var)
        self.entry_name.grid(row=row, column=1, sticky="ew", pady=(0, UIStyle.SPACE_SM))
        row += 1

        # Description Field
        tk.Label(main_frame, text=self.app._t("col_description", default="Description"), bg=UIStyle.BG_BASE, fg=UIStyle.TEXT_PRIMARY).grid(row=row, column=0, sticky="w", pady=(0, UIStyle.SPACE_SM))
        self.desc_var = tk.StringVar()
        self.entry_desc = ttk.Entry(main_frame, textvariable=self.desc_var)
        self.entry_desc.grid(row=row, column=1, sticky="ew", pady=(0, UIStyle.SPACE_SM))
        row += 1

        # Base Stats Label
        tk.Label(main_frame, text="Base Stats", font=("Arial", 10, "bold"), bg=UIStyle.BG_BASE, fg=UIStyle.TEXT_PRIMARY).grid(row=row, column=0, columnspan=2, sticky="w", pady=(UIStyle.SPACE_SM, UIStyle.SPACE_XS))
        row += 1

        # STR Field
        tk.Label(main_frame, text="STR", bg=UIStyle.BG_BASE, fg=UIStyle.TEXT_PRIMARY).grid(row=row, column=0, sticky="w", pady=(0, UIStyle.SPACE_SM))
        self.str_var = tk.StringVar(value="0")
        self.entry_str = ttk.Spinbox(main_frame, textvariable=self.str_var, from_=0, to=9999, width=10)
        self.entry_str.grid(row=row, column=1, sticky="w", pady=(0, UIStyle.SPACE_SM))
        row += 1

        # INT Field
        tk.Label(main_frame, text="INT", bg=UIStyle.BG_BASE, fg=UIStyle.TEXT_PRIMARY).grid(row=row, column=0, sticky="w", pady=(0, UIStyle.SPACE_SM))
        self.int_var = tk.StringVar(value="0")
        self.entry_int = ttk.Spinbox(main_frame, textvariable=self.int_var, from_=0, to=9999, width=10)
        self.entry_int.grid(row=row, column=1, sticky="w", pady=(0, UIStyle.SPACE_SM))
        row += 1

        # DEX Field
        tk.Label(main_frame, text="DEX", bg=UIStyle.BG_BASE, fg=UIStyle.TEXT_PRIMARY).grid(row=row, column=0, sticky="w", pady=(0, UIStyle.SPACE_SM))
        self.dex_var = tk.StringVar(value="0")
        self.entry_dex = ttk.Spinbox(main_frame, textvariable=self.dex_var, from_=0, to=9999, width=10)
        self.entry_dex.grid(row=row, column=1, sticky="w", pady=(0, UIStyle.SPACE_SM))
        row += 1

        main_frame.columnconfigure(1, weight=1)

        # Buttons
        btn_frame = tk.Frame(self, bg=UIStyle.BG_SURFACE)
        btn_frame.pack(fill="x", side="bottom", pady=0)

        inner_btn = tk.Frame(btn_frame, bg=UIStyle.BG_SURFACE)
        inner_btn.pack(pady=UIStyle.SPACE_MD)

        save_btn = tk.Button(inner_btn, text=self.app._t("btn_save", default="Save"), command=self._on_save_clicked, **UIStyle.get_button_style("primary"))
        save_btn.pack(side="left", padx=UIStyle.SPACE_SM)

        cancel_btn = tk.Button(inner_btn, text=self.app._t("btn_cancel", default="Cancel"), command=self.destroy, **UIStyle.get_button_style("secondary"))
        cancel_btn.pack(side="left", padx=UIStyle.SPACE_SM)

        self.bind("<Return>", lambda e: self._on_save_clicked())
        self.bind("<Escape>", lambda e: self.destroy())

    def _populate_data(self):
        if not self.class_data:
            return

        if self.class_data.get("id") and hasattr(self, "id_var"):
            self.id_var.set(str(self.class_data.get("id")))

        self.name_var.set(self.class_data.get("name", ""))
        self.desc_var.set(self.class_data.get("description", ""))
        self.str_var.set(str(self.class_data.get("str_base", 0)))
        self.int_var.set(str(self.class_data.get("int_base", 0)))
        self.dex_var.set(str(self.class_data.get("dex_base", 0)))

    def _on_save_clicked(self):
        name = self.name_var.get().strip()
        if not name:
            messagebox.showerror(self.app._t("err_title", default="Error"), self.app._t("err_name_required", default="Name is required."), parent=self)
            self.entry_name.focus_set()
            return

        try:
            str_base = int(self.str_var.get() or 0)
            int_base = int(self.int_var.get() or 0)
            dex_base = int(self.dex_var.get() or 0)
        except ValueError:
            messagebox.showerror(self.app._t("err_title", default="Error"), self.app._t("err_stats_numeric", default="Base stats must be numeric."), parent=self)
            return

        data = {
            "name": name,
            "description": self.desc_var.get().strip(),
            "str_base": str_base,
            "int_base": int_base,
            "dex_base": dex_base
        }

        if self.class_data.get("id"):
            data["id"] = self.class_data["id"]

        self.on_save(data)
        self.destroy()

class ClassManagerFrame(ResponsiveGridBase):
    def __init__(self, parent, app=None, *args, **kwargs):
        super().__init__(parent, app=app, bg=UIStyle.BG_BASE, *args, **kwargs)
        self.app = app
        self.classes = []
        self.filtered_classes = []

        # Pagination state
        self.current_page = 1
        self.items_per_page = 25
        self.total_pages = 1
        self.total_items = 0

        # Filter state variables
        self.search_var = tk.StringVar()

        self._setup_ui()
        self._load_classes()

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
            self.app.bind_text(title_lbl, "class_manager_title")
        else:
            title_lbl.config(text=self.app._t("class_manager_title", default="Quản Lý Hệ Phái"))
        title_lbl.pack(pady=UIStyle.SPACE_MD)

        self._create_search_bar(content_frame)

        # Treeview Area
        table_frame = tk.Frame(content_frame, bg=UIStyle.BG_BASE)
        table_frame.pack(fill="both", expand=True, padx=UIStyle.SPACE_MD, pady=UIStyle.SPACE_MD)

        # Cấu hình grid cho table_frame để thanh cuộn tự động ẩn/hiện mượt mà
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        self.tree_scroll_y = ttk.Scrollbar(table_frame, orient=tk.VERTICAL)
        self.tree_scroll_x = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL)

        self.columns = ("ID", "Name", "Description", "STR", "INT", "DEX")
        self.tree = ttk.Treeview(
            table_frame,
            columns=self.columns,
            show="headings",
            selectmode="browse",
            height=20,
            yscrollcommand=self._autoscroll_y,
            xscrollcommand=self._autoscroll_x
        )

        self.tree_scroll_y.config(command=self.tree.yview)
        self.tree_scroll_x.config(command=self.tree.xview)

        for col in self.columns:
            self.tree.heading(col, text=self.app._t(f"col_{col.lower()}", default=col))
            width = 50 if col in ("ID", "STR", "INT", "DEX") else 150
            if col == "Description":
                width = 250
            self.tree.column(col, width=width, minwidth=50)

        # Đặt treeview và scrollbars bằng grid
        self.tree.grid(row=0, column=0, sticky="nsew")

        self.tree.bind("<Double-1>", lambda e: self._edit_class())

        # Bottom Bar for Actions
        bottom_bar = tk.Frame(content_frame, bg=UIStyle.BG_SURFACE, height=50)
        bottom_bar.pack(side="bottom", fill="x", pady=UIStyle.SPACE_SM)

        add_btn = tk.Button(
            bottom_bar,
            text=self.app._t("btn_add_class", default=" Thêm"),
            command=self._add_class,
            **UIStyle.get_button_style("primary")
        )
        add_btn.pack(side="left", padx=UIStyle.SPACE_MD, pady=UIStyle.SPACE_SM)

        edit_btn = tk.Button(
            bottom_bar,
            text=self.app._t("btn_edit_class", default=" Sửa"),
            command=self._edit_class,
            **UIStyle.get_button_style("primary")
        )
        edit_btn.pack(side="left", padx=UIStyle.SPACE_MD, pady=UIStyle.SPACE_SM)

        del_btn = tk.Button(
            bottom_bar,
            text=self.app._t("btn_del_class", default=" Xóa"),
            command=self._delete_class,
            **{**UIStyle.get_button_style("primary"), "bg": UIStyle.DANGER, "activebackground": "#ef4444", "fg": "#ffffff", "activeforeground": "#ffffff"}
        )
        del_btn.pack(side="left", padx=UIStyle.SPACE_MD, pady=UIStyle.SPACE_SM)

        ref_btn = tk.Button(
            bottom_bar,
            text=self.app._t("btn_refresh", default=" Làm mới"),
            command=self._on_refresh,
            **UIStyle.get_button_style("secondary")
        )
        ref_btn.pack(side="right", padx=UIStyle.SPACE_MD, pady=UIStyle.SPACE_SM)

        # Pagination controls in bottom bar
        self.btn_next_page = tk.Button(
            bottom_bar,
            text=self.app._t("btn_next", default="Sau >"),
            command=self._next_page,
            bg=UIStyle.BG_BASE,
            fg=UIStyle.TEXT_PRIMARY,
            relief="flat"
        )
        self.btn_next_page.pack(side="right", padx=(0, UIStyle.SPACE_MD), pady=UIStyle.SPACE_SM)

        self.lbl_page_info = tk.Label(
            bottom_bar,
            text="1 / 1",
            bg=UIStyle.BG_SURFACE,
            fg=UIStyle.TEXT_PRIMARY
        )
        self.lbl_page_info.pack(side="right", padx=(0, 10))

        self.btn_prev_page = tk.Button(
            bottom_bar,
            text=self.app._t("btn_prev", default="< Trước"),
            command=self._prev_page,
            bg=UIStyle.BG_BASE,
            fg=UIStyle.TEXT_PRIMARY,
            relief="flat"
        )
        self.btn_prev_page.pack(side="right", padx=(0, 10), pady=UIStyle.SPACE_SM)

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

        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        self.search_entry.grid(row=0, column=1, sticky="ew", padx=(0, 5), pady=5)
        search_frame.columnconfigure(1, weight=1)
        self.search_entry.bind("<KeyRelease>", self._on_search_changed)
        self.search_entry.bind("<Escape>", self._on_clear_search)

    def _on_clear_search(self, event=None) -> None:
        self.search_var.set("")
        self._apply_filters()

    def _on_refresh(self) -> None:
        self.search_var.set("")
        self.current_page = 1
        self._load_classes()


    def _load_classes(self):
        if not hasattr(self.app, 'db_class_service'):
            return

        self.classes = self.app.db_class_service.get_all_classes()
        self._apply_filters()

    def _on_search_changed(self, event=None):
        if hasattr(self, "_search_timer"):
            self.after_cancel(self._search_timer)
        self._search_timer = self.after(500, self._apply_filters)

    def _apply_filters(self):
        keyword = self.search_var.get().lower().strip()

        if keyword:
            self.filtered_classes = [
                c for c in self.classes
                if keyword in c.get("name", "").lower() or keyword in c.get("description", "").lower()
            ]
        else:
            self.filtered_classes = self.classes.copy()

        self.total_items = len(self.filtered_classes)
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

        page_data = self.filtered_classes[start_idx:end_idx]

        for c in page_data:
            values = (
                c.get("id", ""),
                c.get("name", ""),
                c.get("description", ""),
                c.get("str_base", 0),
                c.get("int_base", 0),
                c.get("dex_base", 0)
            )
            item_id = str(c.get("id", ""))
            if not self.tree.exists(item_id):
                self.tree.insert("", "end", iid=item_id, values=values)

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

    def _add_class(self):
        ClassEditDialog(self, self.app, self.app._t("title_add_class", default="Thêm Hệ Phái"), None, self._on_save_class)

    def _edit_class(self):
        selected = self.tree.selection()
        if not selected:
            return

        class_id = selected[0]
        # Find in our local loaded list
        class_data = next((c for c in self.classes if str(c.get("id")) == class_id), None)

        if class_data:
            ClassEditDialog(self, self.app, self.app._t("title_edit_class", default="Sửa Hệ Phái"), class_data, self._on_save_class)

    def _delete_class(self):
        selected = self.tree.selection()
        if not selected:
            return

        class_id = selected[0]

        if messagebox.askyesno(
            self.app._t("confirm_title", default="Xác nhận"),
            self.app._t("confirm_delete_class", default="Bạn có chắc muốn xóa hệ phái này?"),
            parent=self
        ):
            if hasattr(self.app, 'db_class_service'):
                success = self.app.db_class_service.delete_class(int(class_id))
                if success:
                    self._load_classes()
                else:
                    messagebox.showerror(self.app._t("err_title", default="Lỗi"), self.app._t("err_delete_class", default="Không thể xóa hệ phái."), parent=self)

    def _on_save_class(self, data: Dict[str, Any]):
        if not hasattr(self.app, 'db_class_service'):
            return

        success = False
        if "id" in data:
            success = self.app.db_class_service.update_class(data["id"], data)
        else:
            # We don't need the returned ID right now, just if it was not None
            res = self.app.db_class_service.create_class(data)
            success = res is not None

        if success:
            self._load_classes()
        else:
            messagebox.showerror(self.app._t("err_title", default="Lỗi"), self.app._t("err_save_class", default="Lỗi khi lưu hệ phái."), parent=self)
