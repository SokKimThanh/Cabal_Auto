import os
import tkinter as tk
import threading
import sqlite3
from pathlib import Path
from tkinter import ttk, messagebox

from ui.components.empty_state import EmptyState
from ui.components.base.responsive_grid_base import ResponsiveGridBase
from lib.ui_style_v2 import UIStyleV2 as UIStyle
from lib.db.services.icon_service import IconService
from ui.helpers.icon_helper import get_icon_helper
from ui.models.icon_tree_model import IconTreeModel
from ui.models.image_library_model import ImageLibraryModel
from database import get_db

from ui.helpers.tooltip import attach_i18n_tooltip


class IconManagerFrame(ResponsiveGridBase):
    def __init__(self, parent, app=None, *args, **kwargs):
        super().__init__(parent, app=app, bg=UIStyle.BG_BASE, *args, **kwargs)
        self.app = app
        self.db = get_db()
        self.icon_service = IconService(self.db.conn)
        self.icon_helper = get_icon_helper()
        self.tree_model = IconTreeModel()

        self.preview_frame = None
        self.lbl_preview = None
        self.empty_preview = None
        self.form_frame = None
        self.var_id = None
        self.var_name = None
        self.var_icon_key = None
        self.var_category = None
        self.var_fallback_emoji = None
        self.var_tooltip_key = None
        self.var_filepath = None
        self.entry_id = None
        self.entry_name = None
        self.entry_icon_key = None
        self.combo_category = None
        self.entry_fallback = None
        self.entry_tooltip = None
        self.lbl_tooltip_warning = None
        self.entry_filepath = None
        self.btn_browse = None
        self._available_keys = []
        self.btn_add = None
        self.btn_edit = None
        self.btn_delete = None
        self.btn_refresh = None
        self.btn_sync = None
        self.btn_save = None
        self.btn_cancel = None
        self._current_state = None
        self._search_after_id = None
        self._categories_loaded = False
        self._is_dirty = False
        self._last_selected_item_id = None
        self._is_refreshing_tree = False
        self._suppress_tree_events = False
        self._debounce_after_id = None
        self._render_queue = []
        self._render_after_id = None

        self.image_model = ImageLibraryModel()
        self._img_search_after_id = None

        self._setup_ui()
        self._check_and_auto_sync()
        self._initial_load()

    def i18n_t(self, key: str, **kwargs) -> str:
        """Helper to get translations dynamically based on current app language"""
        if hasattr(self.app, '_t'):
            return self.app._t(key, **kwargs)

        # Fallback to direct import if app doesn't have it
        from lib.i18n import t as fallback_t
        lang = getattr(self.app, 'lang', 'vi')

        # Extract supported kwargs for fallback_t
        t_kwargs = {"lang": lang}
        if "default" in kwargs:
            t_kwargs["default"] = kwargs.pop("default")
        if "ns" in kwargs:
            t_kwargs["ns"] = kwargs.pop("ns")

        translated = fallback_t(key, **t_kwargs)

        # Apply formatting if there are extra kwargs
        if kwargs:
            try:
                translated = translated.format(**kwargs)
            except Exception:
                pass

        return translated


    def _setup_ui(self):
        content_frame = self.get_content_frame()

        # Title Label
        title_lbl = tk.Label(
            content_frame,
            text=self.i18n_t("icon_manager_title", default="Quản lý Icon"),
            font=(UIStyle.resolve_font_family("title") if hasattr(UIStyle, "resolve_font_family") else "IBM Plex Sans", 16, "bold"),
            bg=UIStyle.BG_BASE,
            fg=UIStyle.TEXT_PRIMARY
        )
        title_lbl.pack(pady=UIStyle.SPACE_MD if hasattr(UIStyle, "SPACE_MD") else 8, anchor="w", padx=UIStyle.SPACE_MD if hasattr(UIStyle, "SPACE_MD") else 8)

        # Main Container for panels
        self.main_container = tk.Frame(content_frame, bg=UIStyle.BG_BASE)
        self.main_container.pack(fill="both", expand=True)

        self._create_collapsible_panel(
            self.main_container,
            "icons",
            self.i18n_t("panel_icons_title", default="Danh sách Icon"),
            self._build_icons_panel
        )

        self._create_collapsible_panel(
            self.main_container,
            "categories",
            self.i18n_t("panel_categories_title", default="Quản lý Danh mục Icon"),
            self._build_categories_panel
        )

    def _create_collapsible_panel(self, parent_frame, panel_id, title_text, build_func):
        container = tk.Frame(parent_frame, bg=UIStyle.BG_BASE)
        container.pack(fill="both", expand=True, pady=(0, UIStyle.SPACE_MD if hasattr(UIStyle, "SPACE_MD") else 8), padx=UIStyle.SPACE_MD if hasattr(UIStyle, "SPACE_MD") else 8)

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

        font_header = getattr(UIStyle, "FONT_HEADER", ("IBM Plex Sans", 12, "bold"))
        title_btn = tk.Button(
            top_bar,
            text=f"▼ {title_text}",
            anchor="w",
            padx=UIStyle.SPACE_MD if hasattr(UIStyle, "SPACE_MD") else 8,
            pady=UIStyle.SPACE_SM if hasattr(UIStyle, "SPACE_SM") else 4,
            bg=UIStyle.BG_SURFACE,
            fg=UIStyle.TEXT_PRIMARY,
            activebackground=UIStyle.BG_SUBTLE,
            activeforeground=UIStyle.TEXT_PRIMARY,
            bd=0,
            font=font_header,
            command=toggle
        )
        title_btn.pack(fill="x")

        # Build content inside
        build_func(content_frame)

        # Show by default
        content_frame.pack(fill="both", expand=True, pady=UIStyle.SPACE_SM if hasattr(UIStyle, "SPACE_SM") else 4)

    def _build_icons_panel(self, parent_frame):
        content_frame = parent_frame
        content_frame.grid_rowconfigure(0, weight=0)
        content_frame.grid_rowconfigure(1, weight=1)
        content_frame.grid_rowconfigure(2, weight=0)
        content_frame.grid_columnconfigure(0, weight=1)

        # 1. Top Filter Bar
        self.top_filter_frame = tk.Frame(content_frame, bg=UIStyle.BG_SUBTLE, height=60)
        self.top_filter_frame.grid(row=0, column=0, sticky="ew")
        # Configure columns for Top Filter Bar
        self.top_filter_frame.grid_columnconfigure(0, weight=1)  # Search expand
        self.top_filter_frame.grid_columnconfigure(1, weight=0)  # Status filter
        self.top_filter_frame.grid_columnconfigure(2, weight=0)  # Category filter

        # 1.1 Search Box
        self.search_var = tk.StringVar()
        search_frame = tk.Frame(self.top_filter_frame, bg=UIStyle.BG_SUBTLE)
        search_frame.grid(row=0, column=0, sticky="ew", padx=(10, 5), pady=15)

        tk.Label(search_frame, text=self.i18n_t("lbl_search", default="Search:"), bg=UIStyle.BG_SUBTLE, fg=UIStyle.TEXT_PRIMARY).pack(side="left")
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(5, 0))
        self.search_var.trace_add("write", self.trigger_filter)
        self.search_entry.bind("<KeyRelease>", self._on_search_key_release)

        # 1.2 Status Filter
        self.status_var = tk.StringVar(value="All")
        status_frame = tk.Frame(self.top_filter_frame, bg=UIStyle.BG_SUBTLE)
        status_frame.grid(row=0, column=1, sticky="w", padx=5, pady=15)

        tk.Label(status_frame, text=self.i18n_t("lbl_status", default="Status:"), bg=UIStyle.BG_SUBTLE, fg=UIStyle.TEXT_PRIMARY).pack(side="left")
        self.status_combo = ttk.Combobox(
            status_frame,
            textvariable=self.status_var,
            values=["All", "🟢 Xanh (Tốt)", "🟡 Vàng (Fallback)", "🔴 Đỏ (Lỗi)"],
            state="readonly",
            width=15
        )
        self.status_combo.pack(side="left", padx=(5, 0))
        self.status_combo.bind("<<ComboboxSelected>>", lambda e: self.apply_filters())

        # 1.3 Category Filter
        self.category_var = tk.StringVar(value="All")
        category_frame = tk.Frame(self.top_filter_frame, bg=UIStyle.BG_SUBTLE)
        category_frame.grid(row=0, column=2, sticky="w", padx=(5, 10), pady=15)

        tk.Label(category_frame, text=self.i18n_t("lbl_category", default="Category:"), bg=UIStyle.BG_SUBTLE, fg=UIStyle.TEXT_PRIMARY).pack(side="left")
        self.category_combo = ttk.Combobox(
            category_frame,
            textvariable=self.category_var,
            state="readonly",
            width=15
        )
        self.category_combo.pack(side="left", padx=(5, 0))
        self.category_combo.bind("<<ComboboxSelected>>", lambda e: self.apply_filters())

        # 2. Main Content (Left - Right split) using PanedWindow
        self.main_content_frame = tk.Frame(content_frame, bg=UIStyle.BG_BASE)
        self.main_content_frame.grid(row=1, column=0, sticky="nsew", pady=UIStyle.SPACE_MD)
        self.main_content_frame.grid_rowconfigure(0, weight=1)
        self.main_content_frame.grid_columnconfigure(0, weight=1)

        # Style cho PanedWindow nếu cần
        style = ttk.Style()
        style.configure('IconManager.TPanedwindow', background=UIStyle.BG_BASE)

        self.paned_window = ttk.PanedWindow(self.main_content_frame, orient=tk.HORIZONTAL, style='IconManager.TPanedwindow')
        self.paned_window.grid(row=0, column=0, sticky="nsew")

        # Left Master List Frame
        self.left_master_frame = tk.Frame(self.paned_window, bg=UIStyle.BG_ELEVATED)
        self.paned_window.add(self.left_master_frame, weight=0) # Sẽ set width qua Configure

        # Configure grid for treeview and scrollbar
        self.left_master_frame.grid_rowconfigure(0, weight=1)
        self.left_master_frame.grid_columnconfigure(0, weight=1)
        self.left_master_frame.grid_columnconfigure(1, weight=0)

        # Toolbar cho TreeView (Left Master Frame)
        self.tree_toolbar = tk.Frame(self.left_master_frame, bg=UIStyle.BG_ELEVATED)
        self.tree_toolbar.grid(row=0, column=0, columnspan=2, sticky="ew", padx=2, pady=2)

        self.btn_collapse_all = tk.Button(
            self.tree_toolbar,
            text=self.i18n_t("btn_collapse_all", default="Thu gọn tất cả"),
            command=self._on_collapse_all,
            **(UIStyle.get_button_style("secondary") if hasattr(UIStyle, "get_button_style") else {})
        )
        self.btn_collapse_all.pack(side="right", padx=5)

        self.btn_expand_all = tk.Button(
            self.tree_toolbar,
            text=self.i18n_t("btn_expand_all", default="Mở rộng tất cả"),
            command=self._on_expand_all,
            **(UIStyle.get_button_style("secondary") if hasattr(UIStyle, "get_button_style") else {})
        )
        self.btn_expand_all.pack(side="right", padx=5)

        # Điều chỉnh lại row configuration cho left_master_frame
        self.left_master_frame.grid_rowconfigure(0, weight=0) # Toolbar
        self.left_master_frame.grid_rowconfigure(1, weight=1) # Treeview

        # Style Treeview để fix lỗi text clipping
        style = ttk.Style()
        style.configure("IconManager.Treeview", rowheight=28)

        # Create Treeview
        columns = ("col_key", "col_status")
        self.tree = ttk.Treeview(
            self.left_master_frame,
            columns=columns,
            show="tree headings",
            selectmode="browse",
            style="IconManager.Treeview"
        )

        # Define headings
        self.tree.heading("#0", text=self.i18n_t("col_name_category", default="Tên / Danh mục"), anchor="w")
        self.tree.heading("col_key", text="Icon Key", anchor="w")
        self.tree.heading("col_status", text=self.i18n_t("col_status", default="Trạng Thái"), anchor="center")

        # Define columns (tăng minwidth của col_status để tránh cắt chữ)
        self.tree.column("#0", width=150, minwidth=100, stretch=tk.YES)
        self.tree.column("col_key", width=180, minwidth=100, stretch=tk.YES)
        self.tree.column("col_status", width=95, minwidth=95, stretch=tk.NO, anchor="center")

        # Scrollbar
        self.tree_scroll_y = ttk.Scrollbar(self.left_master_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.tree_scroll_y.set)

        # Auto-hiding scrollbar implementation
        self.tree.grid(row=1, column=0, sticky="nsew")
        # Scrollbar will be managed dynamically but we set it up here
        self.tree_scroll_y.grid(row=1, column=1, sticky="ns")

        # Bind events
        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)
        self.tree.bind("<<TreeviewOpen>>", self._on_tree_open)
        self.tree.bind("<Button-1>", self._on_tree_interaction)
        self.tree.bind("<Up>", self._on_tree_interaction)
        self.tree.bind("<Down>", self._on_tree_interaction)
        # Bind configure to handle auto-hiding scrollbar
        self.tree.bind("<Configure>", self._check_scrollbar)

        # Right Detail Frame
        self.right_detail_frame = tk.Frame(self.paned_window, bg=UIStyle.BG_SURFACE)
        self.paned_window.add(self.right_detail_frame, weight=1)

        # Bind Configure to set 50:50 ratio on first render
        self._sash_configured = False
        def on_configure(event):
            if not self._sash_configured and event.width > 10:
                self._sash_configured = True
                sash_pos = int(event.width * 0.50)
                self.paned_window.sashpos(0, sash_pos)

        self.paned_window.bind('<Configure>', on_configure)

        self.right_detail_frame.grid_rowconfigure(0, weight=1)
        self.right_detail_frame.grid_columnconfigure(0, weight=1)

        # Trạng thái 1: Empty (chưa chọn icon)
        self.empty_state_frame = tk.Frame(self.right_detail_frame, bg=UIStyle.BG_SURFACE)
        self.empty_state_frame.grid(row=0, column=0, sticky="nsew")
        self.empty_state_frame.grid_rowconfigure(0, weight=1)
        self.empty_state_frame.grid_columnconfigure(0, weight=1)

        self.empty_preview = EmptyState(
            self.empty_state_frame,
            icon="🖼️",
            message=self.i18n_t("msg_no_icon_selected", default="Chưa tìm thấy icon nào trong thư mục hệ thống"),
            submessage=self.i18n_t("msg_no_icon_sub", default="Vui lòng chọn một icon từ danh sách để xem chi tiết")
        )
        self.empty_preview.grid(row=0, column=0, sticky="nsew")

        # Trạng thái 2: Content (đã chọn icon, có form & preview)
        self.content_state_frame = tk.Frame(self.right_detail_frame, bg=UIStyle.BG_SURFACE)
        self.content_state_frame.grid(row=0, column=0, sticky="nsew")
        self.content_state_frame.grid_rowconfigure(0, weight=0) # Preview - ko co gian max
        self.content_state_frame.grid_rowconfigure(1, weight=1) # Panel + Form sẽ co giãn
        self.content_state_frame.grid_columnconfigure(0, weight=1)

        self._build_preview_zone()

        # Bọc Library và Form vào một container chia 2 cột
        self.bottom_detail_container = tk.Frame(self.content_state_frame, bg=UIStyle.BG_SURFACE)
        self.bottom_detail_container.grid(row=1, column=0, sticky="nsew", padx=UIStyle.SPACE_MD, pady=UIStyle.SPACE_MD)
        self.bottom_detail_container.grid_rowconfigure(0, weight=1)
        self.bottom_detail_container.grid_columnconfigure(0, weight=1) # Image Library
        self.bottom_detail_container.grid_columnconfigure(1, weight=1) # Detail Form

        self.img_lib_container = tk.Frame(self.bottom_detail_container, bg=UIStyle.BG_SURFACE)
        self.img_lib_container.grid(row=0, column=0, sticky="nsew", padx=(0, UIStyle.SPACE_MD))

        self.detail_container = tk.Frame(self.bottom_detail_container, bg=UIStyle.BG_SURFACE)
        self.detail_container.grid(row=0, column=1, sticky="nw")

        self._build_image_library_panel(self.img_lib_container)
        self._build_detail_form()

        # Mặc định hiện empty state
        self.empty_state_frame.tkraise()

        # Bắt đầu scan library ngầm
        self.image_model.scan_async(self._on_image_library_scanned)

        # 3. Bottom Action Bar
        self.bottom_action_frame = tk.Frame(content_frame, bg=UIStyle.BG_SUBTLE, height=60)
        self.bottom_action_frame.grid(row=2, column=0, sticky="ew")
        self.bottom_action_frame.grid_propagate(False)

        # Build Action Buttons
        self._build_action_bar()



    def _build_categories_panel(self, parent_frame):
        # 1. Main PanedWindow (Split Tree vs Form 1:1)
        self.cat_main_frame = tk.Frame(parent_frame, bg=UIStyle.BG_BASE)
        self.cat_main_frame.pack(fill="both", expand=True, pady=UIStyle.SPACE_MD)
        self.cat_main_frame.grid_rowconfigure(0, weight=1)
        self.cat_main_frame.grid_columnconfigure(0, weight=1)

        style = ttk.Style()
        style.configure('IconManager.TPanedwindow', background=UIStyle.BG_BASE)

        self.cat_paned_window = ttk.PanedWindow(self.cat_main_frame, orient=tk.HORIZONTAL, style='IconManager.TPanedwindow')
        self.cat_paned_window.grid(row=0, column=0, sticky="nsew")

        # 2. Left Frame (Treeview)
        self.cat_left_frame = tk.Frame(self.cat_paned_window, bg=UIStyle.BG_ELEVATED)
        self.cat_paned_window.add(self.cat_left_frame, weight=1)

        self.cat_left_frame.grid_rowconfigure(0, weight=1)
        self.cat_left_frame.grid_columnconfigure(0, weight=1)
        self.cat_left_frame.grid_columnconfigure(1, weight=0)

        # Treeview for categories
        self.cat_tree = ttk.Treeview(
            self.cat_left_frame,
            columns=("ID", "Name"),
            show="headings",
            selectmode="browse"
        )
        self.cat_tree.heading("ID", text="ID")
        self.cat_tree.heading("Name", text=self.i18n_t("lbl_name", default="Name"))

        self.cat_tree.column("ID", width=50, anchor="center")
        self.cat_tree.column("Name", width=200, anchor="w")

        self.cat_tree.grid(row=0, column=0, sticky="nsew")

        cat_scrollbar = ttk.Scrollbar(self.cat_left_frame, orient="vertical", command=self.cat_tree.yview)
        self.cat_tree.configure(yscrollcommand=cat_scrollbar.set)
        cat_scrollbar.grid(row=0, column=1, sticky="ns")

        self.cat_tree.bind("<<TreeviewSelect>>", self._on_cat_tree_select)
        self.cat_tree.bind("<Button-1>", self._on_cat_tree_interaction)
        self.cat_tree.bind("<Up>", self._on_cat_tree_interaction)
        self.cat_tree.bind("<Down>", self._on_cat_tree_interaction)

        # 3. Right Frame (Form)
        self.cat_right_frame = tk.Frame(self.cat_paned_window, bg=UIStyle.BG_ELEVATED)
        self.cat_paned_window.add(self.cat_right_frame, weight=1)

        # Toolbar above form (Save, Cancel, Delete)
        self.cat_form_toolbar = tk.Frame(self.cat_right_frame, bg=UIStyle.BG_ELEVATED)
        self.cat_form_toolbar.pack(fill="x", padx=10, pady=(10, 5))

        lbl_cat_detail = tk.Label(self.cat_form_toolbar, text="Chi tiết Loại Icon", font=("IBM Plex Sans", 10, "bold"), bg=UIStyle.BG_ELEVATED, fg=UIStyle.TEXT_PRIMARY)
        lbl_cat_detail.pack(side="left")

        # Form content
        self.cat_form_content = tk.Frame(self.cat_right_frame, bg=UIStyle.BG_SURFACE)
        self.cat_form_content.pack(fill="both", expand=True, padx=10, pady=5)

        self.cat_form_content.grid_columnconfigure(0, weight=0, minsize=80)
        self.cat_form_content.grid_columnconfigure(1, weight=1)

        self.var_cat_id = tk.StringVar()
        self.var_cat_name = tk.StringVar()

        tk.Label(self.cat_form_content, text="Tên Loại:", bg=UIStyle.BG_SURFACE, fg=UIStyle.TEXT_PRIMARY).grid(row=0, column=0, sticky="e", padx=5, pady=10)
        self.entry_cat_name = ttk.Entry(self.cat_form_content, textvariable=self.var_cat_name)
        self.entry_cat_name.grid(row=0, column=1, sticky="ew", padx=5, pady=10)

        # Form Buttons
        self.cat_btn_frame = tk.Frame(self.cat_right_frame, bg=UIStyle.BG_ELEVATED)
        self.cat_btn_frame.pack(fill="x", padx=10, pady=10)

        self.btn_cat_save = tk.Button(self.cat_btn_frame, text="Save", command=self._on_cat_save, **(UIStyle.get_button_style("primary") if hasattr(UIStyle, "get_button_style") else {}))
        self.btn_cat_save.pack(side="left", padx=5)

        self.btn_cat_cancel = tk.Button(self.cat_btn_frame, text="Cancel", command=self._on_cat_cancel, **(UIStyle.get_button_style("secondary") if hasattr(UIStyle, "get_button_style") else {}))
        self.btn_cat_cancel.pack(side="left", padx=5)

        self.btn_cat_delete = tk.Button(self.cat_btn_frame, text="Delete", command=self._on_cat_delete, **(UIStyle.get_button_style("danger") if hasattr(UIStyle, "get_button_style") else {}))
        self.btn_cat_delete.pack(side="left", padx=5)

        # Add a new category button in Treeview toolbar
        self.cat_tree_toolbar = tk.Frame(self.cat_left_frame, bg=UIStyle.BG_ELEVATED)
        self.cat_tree_toolbar.grid(row=1, column=0, columnspan=2, sticky="ew", padx=2, pady=2)

        self.btn_cat_add = tk.Button(self.cat_tree_toolbar, text="Add", command=self._on_cat_add, **(UIStyle.get_button_style("primary") if hasattr(UIStyle, "get_button_style") else {}))
        self.btn_cat_add.pack(side="left", padx=5)

        # Initial data load
        self._load_categories_tree()
        self._set_cat_form_state("view")

    def _build_preview_zone(self):
        self.preview_frame = tk.Frame(self.content_state_frame, bg=UIStyle.BG_SURFACE)
        self.preview_frame.grid(row=0, column=0, sticky="nsew", pady=(0, UIStyle.SPACE_SM))
        self.preview_frame.grid_rowconfigure(0, weight=1)
        self.preview_frame.grid_columnconfigure(0, weight=1)
        self.preview_frame.grid_propagate(False) # Keep the height stable
        self.preview_frame.config(height=200)

        # Empty State
        self.empty_preview = EmptyState(
            self.preview_frame,
            icon="🖼️",
            message=self.i18n_t("msg_no_icon_selected", default="Chưa chọn icon nào hoặc dữ liệu trống"),
            submessage=self.i18n_t("msg_no_icon_sub", default="Vui lòng chọn icon từ danh sách hoặc nhấn Đồng bộ nếu danh sách trống")
        )
        self.empty_preview.grid(row=0, column=0, sticky="nsew")

        # Preview Label (Hidden by default)
        self.lbl_preview = tk.Label(
            self.preview_frame,
            bg=UIStyle.BG_ELEVATED,
            text="",
            font=UIStyle.get_font("body"),
            relief="groove"
        )

    def _build_detail_form(self):
        self.form_frame = tk.Frame(self.detail_container, bg=UIStyle.BG_SURFACE)
        self.form_frame.pack(fill="x", expand=False)

        # Configure columns for form labels and entries
        self.form_frame.grid_columnconfigure(0, weight=0, minsize=120)
        self.form_frame.grid_columnconfigure(1, weight=1, minsize=400)

        # StringVars
        self.var_name = tk.StringVar()
        self.var_icon_key = tk.StringVar()
        self.var_category = tk.StringVar()
        self.var_fallback_emoji = tk.StringVar()
        self.var_tooltip_key = tk.StringVar()
        self.var_filepath = tk.StringVar()

        # 1. Name
        tk.Label(self.form_frame, text=self.i18n_t("lbl_name", default="Name:"), bg=UIStyle.BG_SURFACE, fg=UIStyle.TEXT_PRIMARY).grid(row=0, column=0, sticky="e", padx=5, pady=2)
        self.entry_name = ttk.Entry(self.form_frame, textvariable=self.var_name)
        self.entry_name.grid(row=0, column=1, sticky="ew", padx=5, pady=2)

        # 2. Icon Key
        tk.Label(self.form_frame, text="Icon Key:", bg=UIStyle.BG_SURFACE, fg=UIStyle.TEXT_PRIMARY).grid(row=1, column=0, sticky="e", padx=5, pady=2)
        self.entry_icon_key = ttk.Entry(self.form_frame, textvariable=self.var_icon_key)
        self.entry_icon_key.grid(row=1, column=1, sticky="ew", padx=5, pady=2)

        # 3. Category
        tk.Label(self.form_frame, text=self.i18n_t("lbl_category", default="Category:"), bg=UIStyle.BG_SURFACE, fg=UIStyle.TEXT_PRIMARY).grid(row=2, column=0, sticky="e", padx=5, pady=2)
        self.combo_category = ttk.Combobox(self.form_frame, textvariable=self.var_category, state="readonly")
        self.combo_category.grid(row=2, column=1, sticky="ew", padx=5, pady=2)

        # 4. Fallback Emoji
        tk.Label(self.form_frame, text=self.i18n_t("lbl_fallback_emoji", default="Fallback Emoji:"), bg=UIStyle.BG_SURFACE, fg=UIStyle.TEXT_PRIMARY).grid(row=3, column=0, sticky="e", padx=5, pady=2)
        self.entry_fallback = ttk.Entry(self.form_frame, textvariable=self.var_fallback_emoji)
        self.entry_fallback.grid(row=3, column=1, sticky="ew", padx=5, pady=2)

        # 5. Tooltip Key
        tk.Label(self.form_frame, text=self.i18n_t("lbl_tooltip_key", default="Tooltip Key:"), bg=UIStyle.BG_SURFACE, fg=UIStyle.TEXT_PRIMARY).grid(row=4, column=0, sticky="e", padx=5, pady=2)

        tooltip_frame = tk.Frame(self.form_frame, bg=UIStyle.BG_SURFACE)
        tooltip_frame.grid(row=4, column=1, sticky="ew", padx=5, pady=2)
        tooltip_frame.grid_columnconfigure(0, weight=1)

        self.entry_tooltip = ttk.Combobox(tooltip_frame, textvariable=self.var_tooltip_key)
        self.entry_tooltip.grid(row=0, column=0, sticky="ew")

        self.lbl_tooltip_hint = tk.Label(tooltip_frame, text="Gợi ý: bắt đầu bằng icon_tooltip_...", bg=UIStyle.BG_SURFACE, fg=UIStyle.TEXT_MUTED, font=(UIStyle.FONT_FAMILY_UI, 9))
        self.lbl_tooltip_hint.grid(row=1, column=0, sticky="w", pady=(0, 2))

        self.lbl_tooltip_warning = tk.Label(tooltip_frame, text="", bg=UIStyle.BG_SURFACE, fg="#ff9800", font=(UIStyle.FONT_FAMILY_UI, 9, "bold"))
        self.lbl_tooltip_warning.grid(row=2, column=0, sticky="w")
        self.lbl_tooltip_priority_info = tk.Label(tooltip_frame, text="ⓘ Tooltip của Icon sẽ được ưu tiên hơn Tooltip của Button", bg=UIStyle.BG_SURFACE, fg=UIStyle.TEXT_MUTED, font=(UIStyle.FONT_FAMILY_UI, 8, "italic"))
        self.lbl_tooltip_priority_info.grid(row=3, column=0, sticky="w")


        # Validation bindings
        if hasattr(self.var_tooltip_key, 'trace_add'):
            self.var_tooltip_key.trace_add('write', self._validate_tooltip_key)
        self.entry_tooltip.bind('<KeyRelease>', self._autocomplete_tooltip)

        # Load keys
        self._load_i18n_keys()

        # 6. Filepath (Read-only now)
        tk.Label(self.form_frame, text=self.i18n_t("lbl_filepath", default="Filepath:"), bg=UIStyle.BG_SURFACE, fg=UIStyle.TEXT_PRIMARY).grid(row=5, column=0, sticky="e", padx=5, pady=2)

        filepath_frame = tk.Frame(self.form_frame, bg=UIStyle.BG_SURFACE)
        filepath_frame.grid(row=5, column=1, sticky="ew", padx=5, pady=2)
        filepath_frame.grid_columnconfigure(0, weight=1)

        self.entry_filepath = ttk.Entry(filepath_frame, textvariable=self.var_filepath, state="disabled")
        self.entry_filepath.grid(row=0, column=0, sticky="ew")


    def _build_image_library_panel(self, parent_frame):
        parent_frame.grid_rowconfigure(0, weight=0) # Toolbar
        parent_frame.grid_rowconfigure(1, weight=1) # List
        parent_frame.grid_columnconfigure(0, weight=1)

        # Toolbar
        toolbar = tk.Frame(parent_frame, bg=UIStyle.BG_ELEVATED)
        toolbar.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        toolbar.grid_columnconfigure(0, weight=1)

        search_frame = tk.Frame(toolbar, bg=UIStyle.BG_ELEVATED)
        search_frame.pack(side="left", fill="x", expand=True)
        tk.Label(search_frame, text="🔍", bg=UIStyle.BG_ELEVATED, fg=UIStyle.TEXT_MUTED).pack(side="left", padx=(5,2))

        self.img_search_var = tk.StringVar()
        self.img_search_entry = ttk.Entry(search_frame, textvariable=self.img_search_var)
        self.img_search_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.img_search_var.trace_add("write", self._on_img_search_change)

        self.btn_import_img = tk.Button(
            toolbar, text=self.i18n_t("btn_import_img", default="Import Image"),
            command=self._on_import_image_clicked,
            **(UIStyle.get_button_style("secondary") if hasattr(UIStyle, "get_button_style") else {})
        )
        self.btn_import_img.pack(side="right", padx=5)

        # Listbox container
        list_frame = tk.Frame(parent_frame, bg=UIStyle.BG_BASE)
        list_frame.grid(row=1, column=0, sticky="nsew")
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)

        self.img_listbox = tk.Listbox(
            list_frame,
            bg=UIStyle.BG_BASE, fg=UIStyle.TEXT_PRIMARY,
            selectbackground=getattr(UIStyle, "COLOR_PRIMARY", getattr(UIStyle, "THEME_STATE_SELECTED", "#2196F3")), selectforeground="white",
            borderwidth=1, relief="solid", highlightthickness=0
        )
        self.img_listbox.grid(row=0, column=0, sticky="nsew")

        img_scroll = ttk.Scrollbar(list_frame, orient="vertical", command=self.img_listbox.yview)
        img_scroll.grid(row=0, column=1, sticky="ns")
        self.img_listbox.configure(yscrollcommand=img_scroll.set)

        self.img_listbox.bind("<ButtonRelease-1>", self._on_image_selected)

    def _on_img_search_change(self, *args):
        if self._img_search_after_id:
            self.after_cancel(self._img_search_after_id)
        self._img_search_after_id = self.after(300, self._perform_img_search)

    def _perform_img_search(self):
        query = self.img_search_var.get()
        results = self.image_model.search(query)
        self._update_image_listbox(results)

    def _on_image_library_scanned(self, file_list, error_msg):
        def update_ui():
            try:
                if not self.winfo_exists():
                    return
            except Exception:
                return
            if error_msg:
                # Show error placeholder or toast
                self.img_listbox.insert(tk.END, f"Error: {error_msg}")
                self.img_listbox.config(state="disabled")
            else:
                self._update_image_listbox(file_list)

        try:
            self.after(0, update_ui)
        except RuntimeError:
            pass # main thread not in main loop during early exit

    def _update_image_listbox(self, file_list):
        self.img_listbox.delete(0, tk.END)
        for f in file_list:
            self.img_listbox.insert(tk.END, f)

        # Highlight current file if exists
        current_file = self.var_filepath.get()
        if current_file:
            self._highlight_image_in_list(current_file)

    def _highlight_image_in_list(self, filename):
        items = self.img_listbox.get(0, tk.END)
        if filename in items:
            idx = items.index(filename)
            self.img_listbox.selection_clear(0, tk.END)
            self.img_listbox.selection_set(idx)
            self.img_listbox.see(idx)

    def _on_image_selected(self, event):
        if self._current_state not in ("ADD", "EDIT"):
            return # Only allow selection in edit mode

        selection = self.img_listbox.curselection()
        if not selection:
            return

        selected_file = self.img_listbox.get(selection[0])
        current_icon_key = self.var_icon_key.get().strip()

        # Check duplication
        existing_usages = self.icon_service.get_icons_by_filepath(selected_file)
        other_usages = [u for u in existing_usages if u.get("icon_key") != current_icon_key]

        if other_usages:
            usage_keys = ", ".join([u.get("icon_key", "") for u in other_usages])
            msg_dup = self.i18n_t(
                "msg_icon_duplicated",
                default=f"Ảnh này hiện đang được sử dụng bởi các Icon Key khác: {usage_keys}.\nBạn có muốn tiếp tục sử dụng chung ảnh này không?"
            )
            if not messagebox.askyesno(self.i18n_t("warning", default="Cảnh báo trùng lặp"), msg_dup):
                # Revert selection
                self._highlight_image_in_list(self.var_filepath.get())
                return

        self.var_filepath.set(selected_file)
        self._is_dirty = True

        # Clear cache for the current icon to ensure fresh load
        if hasattr(self.icon_helper, 'clear_cache'):
            self.icon_helper.clear_cache(current_icon_key)
        elif hasattr(self.icon_helper, '_cache'):
            keys_to_remove = [k for k in self.icon_helper._cache.keys() if k.startswith(f"{current_icon_key}_")]
            for k in keys_to_remove:
                del self.icon_helper._cache[k]

        # Fake icon data and render
        dummy_data = {
            "icon_key": current_icon_key,
            "fallback_emoji": self.var_fallback_emoji.get(),
            "filepath": selected_file,
            "tooltip_translation_key": self.var_tooltip_key.get()
        }
        self._render_preview(dummy_data)

    def _on_import_image_clicked(self):
        from tkinter import filedialog
        import logging
        logger = logging.getLogger(__name__)

        if self._current_state not in ("ADD", "EDIT"):
            messagebox.showinfo("Info", "Vui lòng nhấn Add hoặc Edit trước khi Import ảnh mới.")
            return

        file_path = filedialog.askopenfilename(
            title=self.i18n_t("select_icon_file", default="Select Icon File"),
            filetypes=[("Image files", "*.png *.ico")]
        )

        if not file_path:
            return

        original_name = Path(file_path).name
        target_name = original_name
        overwrite = False

        # Check collision via Model
        if self.image_model.check_name_collision(original_name):
            # Cần tạo 1 custom dialog thay vì dùng messagebox để có 3 nút
            # Nhưng Tkinter mặc định không có 3-button dialog có sẵn tốt.
            # Ta dùng trick: askyesnocancel: Yes=Replace, No=Keep Both, Cancel=Cancel
            msg = f"Ảnh '{original_name}' đã tồn tại.\n- Yes: Ghi đè (Replace)\n- No: Giữ cả hai (Đổi tên)\n- Cancel: Hủy bỏ"
            res = messagebox.askyesnocancel("Trùng tên file", msg)

            if res is None: # Cancel
                return
            elif res is True: # Replace
                overwrite = True
                logger.info(f"Import: Người dùng chọn Ghi đè (Replace) file {target_name}")
            else: # Keep both
                target_name = self.image_model.generate_unique_filename(original_name)
                overwrite = False
                logger.info(f"Import: Người dùng chọn Giữ cả hai, đổi tên {original_name} thành {target_name}")
        else:
            target_name = self.image_model.sanitize_filename(original_name)

        success, final_filename, err_msg = self.image_model.import_image(file_path, target_name, overwrite)

        if not success:
            logger.error(f"Import thất bại: {err_msg}")
            messagebox.showerror("Import Error", err_msg)
            return

        logger.info(f"Import thành công: {final_filename}")
        self._just_imported_file = final_filename

        # Import thành công, reload lại list và chọn file mới
        self._on_img_search_change() # Clear search and reload
        self.img_search_var.set("") # Clear search box

        # Tự động gán cho icon đang chọn
        self.var_filepath.set(final_filename)
        self._is_dirty = True

        # Update preview
        current_icon_key = self.var_icon_key.get().strip()
        if hasattr(self.icon_helper, 'clear_cache'):
            self.icon_helper.clear_cache(current_icon_key)

        dummy_data = {
            "icon_key": current_icon_key,
            "fallback_emoji": self.var_fallback_emoji.get(),
            "filepath": final_filename,
            "tooltip_translation_key": self.var_tooltip_key.get()
        }
        self._render_preview(dummy_data)


    def _load_i18n_keys(self):
        self._available_keys = []
        try:
            # Fallback to direct import if app doesn't have it
            from lib.i18n import _REGISTRY
            keys_set = set()
            for _, langs in _REGISTRY.items():
                for _, mapping in langs.items():
                    keys_set.update(mapping.keys())
            self._available_keys = sorted(list(keys_set))
        except Exception:
            pass
        self.entry_tooltip['values'] = self._available_keys

    def _validate_tooltip_key(self, *args):
        key = self.var_tooltip_key.get().strip()
        if not key:
            self.lbl_tooltip_warning.config(text="")
            # Xoá tooltip của label preview
            if hasattr(self, 'lbl_preview'):
                if hasattr(self.lbl_preview, "_i18n_tooltip") and getattr(self.lbl_preview, "_i18n_tooltip"):
                    old_tip = getattr(self.lbl_preview, "_i18n_tooltip")
                    if hasattr(old_tip, "_hide"):
                        old_tip._hide()
                    self.lbl_preview.unbind("<Enter>")
                    self.lbl_preview.unbind("<Leave>")
                    self.lbl_preview.unbind("<ButtonPress>")
                setattr(self.lbl_preview, "_i18n_tooltip", None)
            return

        try:
            from lib.i18n import t
            # Tự đặt 1 chuỗi ngẫu nhiên không có khả năng bị trùng để test default
            test_missing = "___MISSING___"
            val = t(key, default=test_missing, ns=None, lang=None)
            if val == test_missing:
                self.lbl_tooltip_warning.config(text="⚠️ Tooltip chưa được khai báo trong thư viện ngôn ngữ!", fg="#ff9800")
            else:
                self.lbl_tooltip_warning.config(text="✓ Tooltip hợp lệ", fg="green")
        except Exception:
            pass

    def _autocomplete_tooltip(self, event):
        # Only process printable characters and backspace
        if event.keysym not in ['BackSpace', 'Delete', 'Return', 'Tab'] and not event.char:
            return

        typed = self.entry_tooltip.get()
        if typed == '':
            self.entry_tooltip['values'] = self._available_keys
        else:
            hits = [item for item in self._available_keys if typed.lower() in item.lower()]
            self.entry_tooltip['values'] = hits

    def _render_preview(self, icon_data):
        if not icon_data:
            self.empty_state_frame.tkraise()
            self.lbl_preview.grid_remove()
            self.lbl_preview.config(image='', text="")
            self.lbl_preview.image = None
            return

        self.content_state_frame.tkraise()
        self.lbl_preview.grid(row=0, column=0, padx=UIStyle.SPACE_MD, pady=UIStyle.SPACE_MD, sticky="nsew")

        icon_key = icon_data.get("icon_key", "")
        fallback_emoji = icon_data.get("fallback_emoji", "")
        filepath = icon_data.get("filepath", "")

        # Kiểm tra trạng thái tồn tại của file
        status = self.icon_helper.evaluate_icon_status({"filepath": filepath, "fallback_emoji": fallback_emoji})

        giant_icon = None
        # Chỉ load ảnh nếu status là GREEN (ảnh tồn tại)
        if status == "GREEN" and icon_key:
            # We need a large icon. Let's try 128x128
            giant_icon = self.icon_helper.get_icon(icon_key, fallback=fallback_emoji, size=128)

        if giant_icon and not isinstance(giant_icon, str):
            self.lbl_preview.config(image=giant_icon, text="")
            self.lbl_preview.image = giant_icon
        else:
            # Nếu file không tồn tại hoặc lỗi, fallback sang emoji
            emoji_text = fallback_emoji or "❓"
            self.lbl_preview.config(image='', text=emoji_text, font=(UIStyle.FONT_FAMILY_UI, 72))
            self.lbl_preview.image = None

        # Re-attach tooltip
        tooltip_key = icon_data.get("tooltip_translation_key", "")

        # Clear old tooltip by unbinding Enter/Leave if needed, or by redefining
        if hasattr(self.lbl_preview, "_i18n_tooltip") and getattr(self.lbl_preview, "_i18n_tooltip"):
            old_tip = getattr(self.lbl_preview, "_i18n_tooltip")
            if hasattr(old_tip, "_hide"):
                old_tip._hide()
            self.lbl_preview.unbind("<Enter>")
            self.lbl_preview.unbind("<Leave>")
            self.lbl_preview.unbind("<ButtonPress>")

        if tooltip_key:
            attach_i18n_tooltip(
                self.lbl_preview,
                key=tooltip_key,
                ns=None,  # Adjust if tooltip namespace is needed
                lang_provider=lambda: getattr(self.app, 'lang', 'vi') if self.app else 'vi'
            )
        else:
            setattr(self.lbl_preview, "_i18n_tooltip", None)

    def _on_browse_clicked(self):
        from tkinter import filedialog, messagebox
        from pathlib import Path
        from lib.managers.icon_file_manager import get_icons_directory, import_icon_file

        file_path = filedialog.askopenfilename(
            title=self.i18n_t("select_icon_file", default="Select Icon File"),
            filetypes=[("Image files", "*.png *.ico")]
        )

        if file_path:
            try:
                selected_path = Path(file_path)
                icons_dir = get_icons_directory()

                final_filename = selected_path.name
                current_filename = self.var_filepath.get().strip()

                resolved_selected = os.path.normcase(os.path.abspath(str(selected_path.resolve())))
                resolved_icons_dir = os.path.normcase(os.path.abspath(str(icons_dir.resolve())))

                # Luồng 1: Ảnh ngoài assets
                if not resolved_selected.startswith(resolved_icons_dir):
                    target_path = icons_dir / final_filename
                    overwrite = False

                    if target_path.exists():
                        # Trường hợp 1.2: File đã tồn tại trong assets
                        msg_overwrite = self.i18n_t(
                            "msg_file_exists_overwrite",
                            default=f"File ảnh '{final_filename}' đã tồn tại trong hệ thống.\nBạn có muốn thay thế file cũ bằng file mới này không?"
                        )
                        if not messagebox.askyesno(self.i18n_t("warning", default="Cảnh báo ghi đè"), msg_overwrite):
                            return # Huỷ thao tác
                        overwrite = True
                    else:
                        # Trường hợp 1.1: File chưa tồn tại trong assets
                        msg = self.i18n_t(
                            "msg_file_outside_assets",
                            default="Ảnh đang nằm ngoài thư mục assets. Bạn có muốn copy ảnh vào assets không?"
                        )
                        if not messagebox.askyesno(self.i18n_t("warning", default="Cảnh báo"), msg):
                            return # Huỷ thao tác

                    # Tiến hành copy/replace vào assets
                    final_filename = import_icon_file(file_path, overwrite=overwrite)
                else:
                    # Luồng 2: Ảnh trong assets
                    # Trường hợp 2.1: Chọn lại đúng file đang sử dụng
                    if final_filename == current_filename:
                        return # Không làm gì cả
                    # Trường hợp 2.2: Chọn file khác, không cần hỏi copy

                # 3. Kiểm tra sử dụng chung ảnh (Duplication Check)
                current_icon_key = self.var_icon_key.get().strip()
                existing_usages = self.icon_service.get_icons_by_filepath(final_filename)

                # Filter out the current icon we are editing
                other_usages = [u for u in existing_usages if u.get("icon_key") != current_icon_key]

                if other_usages:
                    usage_keys = ", ".join([u.get("icon_key", "") for u in other_usages])
                    msg_dup = self.i18n_t(
                        "msg_icon_duplicated",
                        default=f"Ảnh này hiện đang được sử dụng bởi các Icon Key khác: {usage_keys}.\nBạn có muốn tiếp tục sử dụng chung ảnh này không?"
                    )
                    if not messagebox.askyesno(self.i18n_t("warning", default="Cảnh báo trùng lặp"), msg_dup):
                        return # Huỷ thao tác

                # Update filepath entry
                self.var_filepath.set(final_filename)

                # Mark form as dirty
                self._is_dirty = True

                # Update Preview
                # Clear cache for the current icon to ensure fresh load
                if hasattr(self.icon_helper, 'clear_cache'):
                    self.icon_helper.clear_cache(current_icon_key)
                elif hasattr(self.icon_helper, '_cache'):
                    keys_to_remove = [k for k in self.icon_helper._cache.keys() if k.startswith(f"{current_icon_key}_")]
                    for k in keys_to_remove:
                        del self.icon_helper._cache[k]

                from PIL import Image, ImageTk

                # Determine correct target path for preview
                target_path = Path(final_filename)
                if not target_path.is_absolute():
                    target_path = icons_dir / final_filename

                if target_path.exists():
                    try:
                        img = Image.open(target_path)
                        img = img.resize((128, 128), Image.Resampling.LANCZOS)
                        photo_img = ImageTk.PhotoImage(img)
                        self.lbl_preview.config(image=photo_img, text="")
                        self.lbl_preview.image = photo_img
                    except Exception as e:
                        print(f"Error loading preview image: {e}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not process file:\n{str(e)}")

    def _build_action_bar(self):
        # We place Add, Edit, Delete on the left, and Refresh, Sync, Save, Cancel on the right.
        left_frame = tk.Frame(self.bottom_action_frame, bg=UIStyle.BG_SUBTLE)
        left_frame.pack(side="left", padx=UIStyle.SPACE_MD, pady=UIStyle.SPACE_SM)

        right_frame = tk.Frame(self.bottom_action_frame, bg=UIStyle.BG_SUBTLE)
        right_frame.pack(side="right", padx=UIStyle.SPACE_MD, pady=UIStyle.SPACE_SM)

        self.btn_add = tk.Button(left_frame, text=self.i18n_t("btn_add", default="Add"), command=self._on_add, **UIStyle.get_button_style("primary"))
        self.btn_add.pack(side="left", padx=UIStyle.SPACE_XS)
        if hasattr(self.app, 'bind_text'):
            self.app.bind_text(self.btn_add, "btn_add")

        self.btn_edit = tk.Button(left_frame, text=self.i18n_t("btn_edit", default="Edit"), command=self._on_edit, **UIStyle.get_button_style("secondary"))
        self.btn_edit.pack(side="left", padx=UIStyle.SPACE_XS)
        if hasattr(self.app, 'bind_text'):
            self.app.bind_text(self.btn_edit, "btn_edit")

        self.btn_delete = tk.Button(left_frame, text=self.i18n_t("btn_delete", default="Delete"), command=self._on_delete, **UIStyle.get_button_style("danger"))
        self.btn_delete.pack(side="left", padx=UIStyle.SPACE_XS)
        if hasattr(self.app, 'bind_text'):
            self.app.bind_text(self.btn_delete, "btn_delete")

        # Override danger if needed (Tkinter style compatibility)
        if not hasattr(UIStyle, 'get_button_style') or 'danger' not in [v for v in UIStyle.get_button_style.__code__.co_consts if isinstance(v, str)]:
            self.btn_delete.configure(bg=UIStyle.DANGER, fg="white")

        self.btn_refresh = tk.Button(right_frame, text=self.i18n_t("btn_refresh", default="Refresh"), command=self._on_refresh, **UIStyle.get_button_style("secondary"))
        self.btn_refresh.pack(side="left", padx=UIStyle.SPACE_XS)
        if hasattr(self.app, 'bind_text'):
            self.app.bind_text(self.btn_refresh, "btn_refresh")
        attach_i18n_tooltip(self.btn_refresh, "tooltip_icon_manager_refresh", ns=None, lang_provider=lambda: getattr(self.app, 'lang', 'vi') if self.app else 'vi')

        self.btn_sync = tk.Button(right_frame, text=self.i18n_t("btn_sync", default="Đồng bộ"), command=self._on_sync, **UIStyle.get_button_style("info"))
        self.btn_sync.pack(side="left", padx=UIStyle.SPACE_XS)
        if hasattr(self.app, 'bind_text'):
            self.app.bind_text(self.btn_sync, "btn_sync", default="Đồng bộ")
        attach_i18n_tooltip(self.btn_sync, "tooltip_icon_manager_sync", ns=None, lang_provider=lambda: getattr(self.app, 'lang', 'vi') if self.app else 'vi')

        self.btn_save = tk.Button(right_frame, text=self.i18n_t("btn_save"), command=self._on_save, **UIStyle.get_button_style("primary"))
        self.btn_save.pack(side="left", padx=UIStyle.SPACE_XS)
        if hasattr(self.app, 'bind_text'):
            self.app.bind_text(self.btn_save, "btn_save")

        self.btn_cancel = tk.Button(right_frame, text=self.i18n_t("btn_cancel"), command=self._on_cancel, **UIStyle.get_button_style("secondary"))
        self.btn_cancel.pack(side="left", padx=UIStyle.SPACE_XS)
        if hasattr(self.app, 'bind_text'):
            self.app.bind_text(self.btn_cancel, "btn_cancel")

        self.set_form_state("VIEW")

    def set_form_state(self, state):
        self._current_state = state

        # Enable/Disable form entries
        entry_state = "normal" if state in ("ADD", "EDIT") else "disabled"
        cb_state = "readonly" if state in ("ADD", "EDIT") else "disabled"

        self.entry_name.config(state=entry_state)
        self.entry_icon_key.config(state=entry_state)
        self.combo_category.config(state=cb_state)
        self.entry_fallback.config(state=entry_state)
        if hasattr(self, 'entry_tooltip'):
            self.entry_tooltip.config(state='normal' if state in ('ADD', 'EDIT') else 'disabled')
        # Filepath is visually selected via button
        self.entry_filepath.config(state="disabled")

        # Handle Image Library state
        if hasattr(self, 'img_listbox'):
            if state in ("ADD", "EDIT"):
                self.img_listbox.config(state="normal")
                self.btn_import_img.config(state="normal")
            else:
                self.img_listbox.config(state="disabled")
                self.btn_import_img.config(state="disabled")

        # Handle buttons
        if state == "VIEW":
            self.btn_add.config(state="normal")

            # Edit/Delete depends on selection
            has_selection = bool(self.tree.selection())
            self.btn_edit.config(state="normal" if has_selection else "disabled")
            self.btn_delete.config(state="normal" if has_selection else "disabled")

            self.btn_save.pack_forget()
            self.btn_cancel.pack_forget()

            self.btn_refresh.pack(side="left", padx=UIStyle.SPACE_XS)
            self.btn_sync.pack(side="left", padx=UIStyle.SPACE_XS)

        elif state in ("ADD", "EDIT"):
            self.btn_add.config(state="disabled")
            self.btn_edit.config(state="disabled")
            self.btn_delete.config(state="disabled")

            self.btn_refresh.pack_forget()
            self.btn_sync.pack_forget()

            self.btn_save.pack(side="left", padx=UIStyle.SPACE_XS)
            self.btn_cancel.pack(side="left", padx=UIStyle.SPACE_XS)

    def _on_collapse_all(self):
        for item in self.tree.get_children():
            if item.startswith("cat_"):
                self.tree.item(item, open=False)

    def _on_expand_all(self):
        for item in self.tree.get_children():
            if item.startswith("cat_"):
                self.tree.item(item, open=True)

    def _on_add(self):
        import time

        # Xác định category hiện tại đang chọn
        selected_cat = "General"
        selection = self.tree.selection()
        if selection:
            item_id = selection[0]
            if item_id.startswith("cat_"):
                selected_cat = item_id.replace("cat_", "", 1)
            else:
                parent_id = self.tree.parent(item_id)
                if parent_id and parent_id.startswith("cat_"):
                    selected_cat = parent_id.replace("cat_", "", 1)

        # Set variables
        self.var_icon_key.set("")
        self.var_name.set("New Icon")
        self.var_category.set(selected_cat)
        self.var_fallback_emoji.set("❓")
        self.var_tooltip_key.set("")
        self.var_filepath.set("")

        # Create dummy node in Treeview for visual feedback
        dummy_id = f"new_icon_{int(time.time())}"
        cat_node = f"cat_{selected_cat}"

        # Đảm bảo category node tồn tại và mở ra
        if not self.tree.exists(cat_node):
            self.tree.insert("", "end", iid=cat_node, text=selected_cat, open=True)
        else:
            self.tree.item(cat_node, open=True)

        # Insert temp dummy icon item
        self.tree.insert(cat_node, "end", iid=dummy_id, text="  [New] New Icon", values=(selected_cat, "🟡"))

        # Select and focus on the dummy item
        self.tree.selection_set(dummy_id)
        self.tree.see(dummy_id)

        self.set_form_state("ADD")
        self.entry_name.focus_set()

        self._render_preview({
            "icon_key": dummy_id,
            "fallback_emoji": "❓"
        })
        self.set_form_state("ADD")

        # Focus vào entry name
        self.entry_name.focus_set()

    def _on_edit(self):
        self.set_form_state("EDIT")
        # Start typing/editing will set it dirty, but explicitly marking it is safer if they just click browse
        self._is_dirty = True

    def _on_delete(self):
        icon_key = self.var_icon_key.get()
        if not icon_key:
            return

        from tkinter import messagebox

        # Check safe delete with tree_model first
        if hasattr(self, 'tree_model'):
            is_safe, usages = self.tree_model.check_safe_delete(icon_key)
            if not is_safe:
                msg = self.i18n_t("msg_icon_in_use", default=f"Icon '{icon_key}' đang được sử dụng ở {len(usages)} nơi. Vui lòng gỡ bỏ trước khi xóa.", count=len(usages), icon_key=icon_key)
                messagebox.showwarning(self.i18n_t("warning", default="Cảnh báo"), msg, parent=self.winfo_toplevel())
                return

        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete the icon '{icon_key}'?",
            icon='warning'
        )

        if confirm:
            try:
                success = self.icon_service.delete_icon(icon_key)
                if success:
                    # Clear form
                    self.var_name.set("")
                    self.var_icon_key.set("")
                    self.var_category.set("")
                    self.var_fallback_emoji.set("")
                    self.var_tooltip_key.set("")
                    self.var_filepath.set("")
                    self._render_preview({})

                    if hasattr(self, 'tree_model'):
                        self.tree_model.invalidate_icon(icon_key)

                    # Reload tree
                    self.load_tree_data()
                    self.set_form_state("VIEW")
                    self.tree.focus_set()
                else:
                    messagebox.showerror("Error", f"Failed to delete icon '{icon_key}'.")
            except ValueError as e:
                if str(e) == "icon_in_use_error":
                    usages = self.icon_service.get_usages(icon_key)
                    msg = self.i18n_t("msg_icon_in_use", default=f"Icon '{icon_key}' đang được sử dụng ở {len(usages)} nơi. Vui lòng gỡ bỏ trước khi xóa.", count=len(usages), icon_key=icon_key)
                    messagebox.showwarning(self.i18n_t("warning", default="Cảnh báo"), msg)
                else:
                    messagebox.showerror("Error", str(e))

    def _on_refresh(self):
        self.apply_filters()

    def _on_sync(self, show_message=True):
        if self.btn_sync['state'] == 'disabled':
            return

        self.btn_sync.config(state='disabled', text=self.i18n_t("btn_syncing", default="Đang đồng bộ..."))

        def run_sync():
            try:
                import sqlite3
                from lib.db.services.icon_service import IconService
                from database import MonsterDatabase

                thread_conn = sqlite3.connect(MonsterDatabase.DB_PATH)
                thread_icon_service = IconService(thread_conn)

                mappings = self.icon_helper.icon_map
                count = 0
                for icon_key, (icon_stem, emoji) in mappings.items():
                    icon_data = {
                        "icon_key": icon_key,
                        "name": icon_key.capitalize(),
                        "filepath": f"{icon_stem}.png",
                        "fallback_emoji": emoji,
                        "tooltip_translation_key": f"icon_tooltip_{icon_key}",
                        "category": "System",
                        "description": f"System icon for {icon_key}"
                    }

                    existing = thread_icon_service.get_icon_by_key(icon_key)
                    if not existing:
                        thread_icon_service.upsert_icon(icon_data)
                        count += 1

                try:
                    self.after(0, lambda: self._on_sync_complete(count, show_message))
                except RuntimeError:
                    pass
            except Exception as e:
                try:
                    self.after(0, lambda: self._on_sync_error(str(e), show_message))
                except RuntimeError:
                    pass

        threading.Thread(target=run_sync, daemon=True).start()

    def _safe_after(self, delay, callback):
        """Safely schedule a callback if the widget still exists"""
        if self.winfo_exists():
            try:
                self.after(delay, callback)
            except RuntimeError:
                pass

    def _on_sync_complete(self, count, show_message):
        import tkinter.messagebox as messagebox
        if hasattr(self, 'tree_model'):
            self.tree_model.load_base_data_async(lambda: self._safe_after(0, self.load_tree_data))
        else:
            self.load_tree_data()

        if show_message:
            if count > 0:
                msg = self.i18n_t("msg_sync_success", default=f"Đã đồng bộ {count} icons mới từ hệ thống vào cơ sở dữ liệu.", count=count)
                messagebox.showinfo(self.i18n_t("title_sync_success", default="Đồng bộ thành công"), msg)
            else:
                msg = self.i18n_t("msg_sync_success_none", default="Dữ liệu đã ở trạng thái mới nhất.")
                messagebox.showinfo(self.i18n_t("title_sync_success", default="Đồng bộ thành công"), msg)

        self._start_sync_cooldown(60)

    def _on_sync_error(self, err_msg, show_message):
        import tkinter.messagebox as messagebox
        self.btn_sync.config(state='normal', text=self.i18n_t("btn_sync", default="Đồng bộ"))
        if show_message:
            messagebox.showerror(self.i18n_t("title_sync_error", default="Lỗi đồng bộ"), f"Có lỗi xảy ra: {err_msg}")

    def _start_sync_cooldown(self, seconds_left):
        if not self.winfo_exists():
            return
        if seconds_left <= 0:
            self.btn_sync.config(state='normal', text=self.i18n_t("btn_sync", default="Đồng bộ"))
            return

        cooldown_text = self.i18n_t("btn_sync_cooldown", default=f"Đã đồng bộ ({seconds_left}s)", s=seconds_left).replace("{s}", str(seconds_left))
        if hasattr(self.app, 'i18n_t'):
            cooldown_text = self.app._t("btn_sync_cooldown", s=seconds_left)

        self.btn_sync.config(text=cooldown_text)
        self.after(1000, lambda: self._start_sync_cooldown(seconds_left - 1))

    def _validate_form_data(self):
        from tkinter import messagebox
        icon_key = self.var_icon_key.get().strip()
        if not icon_key:
            messagebox.showerror("Validation Error", "Icon Key is required.")
            return False

        # Add more validations if needed
        return True

    def _on_save(self):
        # 1. Validate dữ liệu
        if not self._validate_form_data():
            return

        icon_key = self.var_icon_key.get().strip()
        new_filepath = self.var_filepath.get().strip()

        # Save previous filepath to check for rollback if db insert fails
        icon_data_old = self.tree_model.get_icon(icon_key)
        old_filepath = icon_data_old.get('filepath') if icon_data_old else None

        cat_name = self.var_category.get().strip() or "General"
        cat_id = 1
        if hasattr(self, 'categories_map') and cat_name in self.categories_map:
            cat_id = self.categories_map[cat_name]

        icon_data = {
            "icon_key": icon_key,
            "name": self.var_name.get().strip(),
            "filepath": self.var_filepath.get().strip(),
            "fallback_emoji": self.var_fallback_emoji.get().strip(),
            "tooltip_translation_key": self.var_tooltip_key.get().strip(),
            "category_id": cat_id,
            "description": ""
        }

        # Nếu đang ở trạng thái ADD, xóa dòng dummy khỏi tree trước khi reload
        if self._current_state == "ADD":
            selection = self.tree.selection()
            if selection:
                item_id = selection[0]
                if item_id.startswith("new_icon_"):
                    self.tree.delete(item_id)

        # 2. Lưu Database
        success = self.icon_service.upsert_icon(icon_data)
        if success:
            # Xoá flag dirty
            self._is_dirty = False

            # Xoá cache trong IconHelper để bắt buộc load ảnh mới
            if hasattr(self.icon_helper, 'clear_cache'):
                self.icon_helper.clear_cache(icon_key)
            elif hasattr(self.icon_helper, '_cache'):
                keys_to_remove = [k for k in self.icon_helper._cache.keys() if k.startswith(f"{icon_key}_")]
                for k in keys_to_remove:
                    del self.icon_helper._cache[k]

            if hasattr(self, 'tree_model'):
                 icon_data["category_name"] = cat_name
                 # Re-evaluate status
                 existing_files = set()
                 if hasattr(self.icon_helper, 'icon_dirs'):
                     for d in self.icon_helper.icon_dirs:
                         if d.exists():
                             try:
                                 for file in d.iterdir():
                                     if file.is_file():
                                         existing_files.add(file.name)
                             except Exception:
                                 pass
                 status = self.icon_helper.evaluate_icon_status(icon_data, existing_files_cache=existing_files)
                 self.tree_model.update_icon_in_cache(icon_data, status)

            # 3. Reload dữ liệu
            self.load_tree_data()

            # Mở lại thư mục vừa thêm vào
            cat_node_id = f"cat_{cat_id}"
            if self.tree.exists(cat_node_id):
                self.tree.item(cat_node_id, open=True)

            # Re-select the saved item để refresh Preview từ dữ liệu thực tế
            node_id = f"icon_{icon_key}"
            if self.tree.exists(node_id):
                 self.tree.selection_set(node_id)
                 self.tree.see(node_id)

            self.set_form_state("VIEW")
            self.tree.focus_set()

            # 4. Thông báo thành công
            from tkinter import messagebox
            messagebox.showinfo("Thành công", f"Đã lưu thành công icon {icon_key}.")
        else:
            from tkinter import messagebox
            import logging
            logger = logging.getLogger(__name__)
            messagebox.showerror("Error", "Failed to save icon data.")
            logger.error(f"Lỗi database: Ghi icon {icon_key} thất bại.")
            # Rollback nếu đang có thao tác update DB thất bại
            # Theo requirements: "Nếu update DB lỗi -> Rollback, Không để DB và file hệ thống lệch nhau"
            if new_filepath and new_filepath != old_filepath:
                 # Check if the new file is already used by other icons
                 usages = self.icon_service.get_icons_by_filepath(new_filepath)
                 if not usages: # Only rollback/remove file if no other icons are using it
                      if getattr(self, '_just_imported_file', None) == new_filepath:
                          self.image_model.remove_file(new_filepath)
                          self._on_img_search_change() # refresh list

    def _on_cancel(self):
        # Dọn dẹp dòng dummy nếu đang ở trạng thái ADD
        if self._current_state == "ADD":
            selection = self.tree.selection()
            if selection:
                item_id = selection[0]
                if item_id.startswith("new_icon_"):
                    self.tree.delete(item_id)

        self._is_dirty = False
        self._process_tree_selection()
        self.set_form_state("VIEW")
        self.tree.focus_set()

    def _on_search_key_release(self, event):
        # Cancel any previous timer
        if hasattr(self, '_search_after_id') and self._search_after_id:
            self.after_cancel(self._search_after_id)
        # Set new timer for debounce (500ms)
        self._search_after_id = self.after(500, self.apply_filters)
    def _check_and_auto_sync(self):
        # Auto-sync icons if the database is empty
        conn = sqlite3.connect(str(self.db.DB_PATH))
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM icons")
        count = cursor.fetchone()[0]
        conn.close()
        if count == 0:
            self._on_sync(show_message=False)


    def apply_filters(self):
        self.load_tree_data()

    def _initial_load(self):
        # Indicate loading state
        self.tree.delete(*self.tree.get_children())
        self.tree.insert('', 'end', iid="loading", text="Loading data...")
        self.tree_model.load_base_data_async(self._on_data_loaded)

    def _on_data_loaded(self):
        try:
            if not self.winfo_exists():
                return
            # Update combo boxes based on categories
            self.after(0, self._populate_category_combo)
            self.after(0, self.load_tree_data)
        except RuntimeError:
            pass # main thread not in main loop during early exit

    def _populate_category_combo(self):
        if not hasattr(self, 'tree_model'): return
        categories = list(self.tree_model.category_cache.values())
        categories.sort(key=lambda x: x.get('name', '').lower())

        self.categories_map = {c['name']: c['id'] for c in categories}
        cat_names = ["All"] + [c['name'] for c in categories]

        # Only update Comboboxes
        if hasattr(self, 'category_var') and hasattr(self, 'combo_category_filter'):
            current_val = self.category_var.get()
            self.combo_category_filter.config(values=cat_names)
            if current_val not in cat_names:
                self.category_var.set("All")

        if hasattr(self, 'combo_category'):
            c_names = [c['name'] for c in categories]
            self.combo_category.config(values=c_names)

    def trigger_filter(self, *args):
        if self._debounce_after_id:
            self.after_cancel(self._debounce_after_id)
        self._debounce_after_id = self.after(300, self.load_tree_data)

    def load_tree_data(self):
        if not hasattr(self, 'tree_model') or not self.tree_model.loaded:
            return

        self._is_refreshing_tree = True

        # Save state
        expanded_nodes = []
        for item in self.tree.get_children(''):
            if self.tree.item(item, "open"):
                expanded_nodes.append(item)
            for child in self.tree.get_children(item):
                if self.tree.item(child, "open"):
                    expanded_nodes.append(child)

        selected_nodes = self.tree.selection()

        # Build filter kwargs
        search_term = (self.search_var.get() or '').strip()
        selected_category_name = self.category_var.get()
        selected_category_id = None
        if selected_category_name and selected_category_name != "All":
             selected_category_id = self.categories_map.get(selected_category_name)

        selected_status_raw = self.status_var.get()
        status_filter = None
        if "Xanh" in selected_status_raw: status_filter = "GREEN"
        elif "Vàng" in selected_status_raw: status_filter = "YELLOW"
        elif "Đỏ" in selected_status_raw: status_filter = "RED"

        self.tree_model.set_filters(search=search_term, category_id=selected_category_id, status=status_filter)
        filtered_data = self.tree_model.get_filtered_tree_data()

        # Batch Incremental Update logic to prevent UI flickering and freezing

        # Determine categories to insert
        self._render_queue = []
        for cat_id, icons in filtered_data.items():
            cat = self.tree_model.get_category(cat_id)
            cat_name = cat.get('name', 'Unknown') if cat else 'General'
            node_iid = f"cat_{cat_id}"

            self._render_queue.append(
                ('category', '', node_iid, f"📁 {cat_name}", ("category",), True)
            )

            icons.sort(key=lambda x: x.get('name', '').lower())

            for idx, icon in enumerate(icons):
                icon_key = icon.get('icon_key')
                icon_name = icon.get('name', '')
                status = self.tree_model.status_cache.get(icon_key, '⚪')
                usage_count = self.tree_model.dependency_cache.get(icon_key, 0)

                if usage_count > 0:
                    icon_name = f"{icon_name} (Usages: {usage_count})"

                status_color = "⚪"
                if status == "GREEN": status_color = "🟢"
                elif status == "YELLOW": status_color = "🟡"
                elif status == "RED": status_color = "🔴"

                icon_iid = f"icon_{icon_key}"

                self._render_queue.append(
                    ('icon', node_iid, idx, icon_iid, icon_name, (icon_key, status_color), usage_count)
                )

        self._desired_cats = {cmd[2] for cmd in self._render_queue if cmd[0] == 'category'}
        self._desired_icons = {cmd[2]: set() for cmd in self._render_queue if cmd[0] == 'category'}
        for cmd in self._render_queue:
             if cmd[0] == 'icon':
                  self._desired_icons[cmd[1]].add(cmd[3])

        self._process_incremental_queue(expanded_nodes, selected_nodes)

    def _process_incremental_queue(self, expanded_nodes, selected_nodes):
        if not self._render_queue:
            if self.tree.exists("loading"):
                 self.tree.delete("loading")
            # Finalize: Remove stale icons and categories
            existing_cats = {item for item in self.tree.get_children('') if item.startswith("cat_")}
            for cat_id in existing_cats:
                 if cat_id in self._desired_icons:
                      existing_icons = {item for item in self.tree.get_children(cat_id) if item.startswith("icon_")}
                      for old_icon in existing_icons - self._desired_icons[cat_id]:
                           self.tree.delete(old_icon)

            for old_cat in existing_cats - self._desired_cats:
                self.tree.delete(old_cat)

            self._is_refreshing_tree = False

            # Restore state
            for item in expanded_nodes:
                if self.tree.exists(item):
                    self.tree.item(item, open=True)

            if selected_nodes and self.tree.exists(selected_nodes[0]):
                self.tree.selection_set(selected_nodes[0])
                self.tree.see(selected_nodes[0])

            self._check_scrollbar()
            return

        batch = self._render_queue[:100]
        self._render_queue = self._render_queue[100:]

        for cmd in batch:
            if cmd[0] == 'category':
                 node_iid, text, values, open_state = cmd[2], cmd[3], cmd[4], cmd[5]
                 if not self.tree.exists(node_iid):
                     self.tree.insert('', 'end', iid=node_iid, text=text, values=values, open=open_state)
                 else:
                     self.tree.item(node_iid, text=text)

            elif cmd[0] == 'icon':
                 node_iid, idx, icon_iid, text, values, usage_count = cmd[1], cmd[2], cmd[3], cmd[4], cmd[5], cmd[6]
                 if not self.tree.exists(node_iid):
                     continue # Should not happen if sorted properly, but fail gracefully

                 if not self.tree.exists(icon_iid):
                     self.tree.insert(node_iid, idx, iid=icon_iid, text=text, values=values)
                     if usage_count > 0:
                         self.tree.insert(icon_iid, 'end', iid=f"dummy_{values[0]}", text="dummy")
                 else:
                     self.tree.item(icon_iid, text=text, values=values)
                     current_idx = self.tree.index(icon_iid)
                     if current_idx != idx:
                         self.tree.move(icon_iid, node_iid, idx)

                     # Ensure it has a dummy child if it has usages but no children yet
                     if usage_count > 0 and not self.tree.get_children(icon_iid):
                         self.tree.insert(icon_iid, 'end', iid=f"dummy_{values[0]}", text="dummy")

        self._render_after_id = self.after(5, lambda: self._process_incremental_queue(expanded_nodes, selected_nodes))



    def _check_scrollbar(self, event=None):
        """Auto-hide scrollbar when not needed"""
        if not hasattr(self, 'tree') or not hasattr(self, 'tree_scroll_y'):
            return

        # Get bounding box of the last item to determine if scrollbar is needed
        children = self.tree.get_children()
        if not children:
            self.tree_scroll_y.grid_remove()
            return

        try:
            # Check if all items fit in the view
            bbox = self.tree.bbox(children[-1])
            if bbox and self.tree.winfo_height() > (bbox[1] + bbox[3]):
                self.tree_scroll_y.grid_remove()
            else:
                self.tree_scroll_y.grid()
        except tk.TclError:
            pass

    def _on_tree_interaction(self, event):
        if self._current_state in ("ADD", "EDIT") and getattr(self, '_is_dirty', False):
            from tkinter import messagebox
            msg = self.i18n_t("msg_unsaved_changes_lock", default="Vui lòng nhấn Lưu hoặc Hủy trước khi chọn dòng khác.")
            messagebox.showwarning(self.i18n_t("warning", default="Cảnh báo"), msg)
            return "break"

    def _on_cat_tree_interaction(self, event):
        if getattr(self, '_cat_current_state', 'view') in ("add", "edit"):
            from tkinter import messagebox
            msg = self.i18n_t("msg_unsaved_changes_lock", default="Vui lòng nhấn Lưu hoặc Hủy trước khi chọn dòng khác.")
            messagebox.showwarning(self.i18n_t("warning", default="Cảnh báo"), msg)
            return "break"

    def _on_tree_select(self, event):
        if hasattr(self, '_select_after_id') and self._select_after_id:
            self.after_cancel(self._select_after_id)
        self._select_after_id = self.after(50, self._process_tree_selection)

    def _process_tree_selection(self):
        if self._is_refreshing_tree or self._suppress_tree_events:
            return

        selection = self.tree.selection()
        if not selection:
            return

        item_id = selection[0]
        self._last_selected_item_id = item_id

        if item_id.startswith('cat_'):
            return

        if item_id.startswith('usage_'):
            return

        # It's an icon node
        if item_id.startswith("new_icon_"):
            return

        # Get actual ID from values instead of string replace
        values = self.tree.item(item_id, 'values')
        icon_key = values[0] if values else item_id

        icon_data = self.tree_model.get_icon(icon_key)
        if icon_data:
            self.var_name.set(icon_data.get('name') or '')
            self.var_icon_key.set(icon_data.get('icon_key') or '')

            # Map category_id back to name
            cat_id = icon_data.get("category_id")
            cat_data = self.tree_model.get_category(cat_id) if cat_id else None
            cat_name = cat_data.get("name", "General") if cat_data else "General"
            self.var_category.set(cat_name)

            self.var_fallback_emoji.set(icon_data.get('fallback_emoji') or '')
            self.var_tooltip_key.set(icon_data.get('tooltip_translation_key') or '')

            # Sửa lỗi hiển thị None bằng cách ép chuỗi rỗng nếu giá trị là None
            filepath = icon_data.get('filepath') or ''
            self.var_filepath.set(filepath)

            if hasattr(self, 'img_listbox') and filepath:
                self._highlight_image_in_list(filepath)
            elif hasattr(self, 'img_listbox'):
                self.img_listbox.selection_clear(0, tk.END)

            self._render_preview(icon_data)

        self.set_form_state("VIEW")


    def _load_categories_tree(self):
        for item in self.cat_tree.get_children():
            self.cat_tree.delete(item)

        categories = self.icon_service.get_all_categories()
        for cat in categories:
            self.cat_tree.insert("", "end", values=(cat["id"], cat["name"]))

        # Also update the icon filter combobox
        cat_names = [c["name"] for c in categories]
        sorted_cats = ["All"] + sorted(cat_names)
        self.category_combo['values'] = sorted_cats
        self.combo_category['values'] = cat_names

        self.categories_map = {c["name"]: c["id"] for c in categories}
        self.categories_id_map = {c["id"]: c["name"] for c in categories}

    def _set_cat_form_state(self, state):
        self._cat_current_state = state
        if state == "view":
            self.entry_cat_name.config(state="disabled")
            self.btn_cat_save.config(state="disabled")
            self.btn_cat_cancel.config(state="disabled")
            self.btn_cat_delete.config(state="normal" if self.var_cat_id.get() else "disabled")
            self.btn_cat_add.config(state="normal")
        else: # edit/add
            self.entry_cat_name.config(state="normal")
            self.btn_cat_save.config(state="normal")
            self.btn_cat_cancel.config(state="normal")
            self.btn_cat_delete.config(state="disabled")
            self.btn_cat_add.config(state="disabled")

    def _on_cat_tree_select(self, event):
        selection = self.cat_tree.selection()
        if not selection:
            self._set_cat_form_state("view")
            return

        item = self.cat_tree.item(selection[0])
        values = item["values"]
        if values:
            self.var_cat_id.set(str(values[0]))
            self.var_cat_name.set(str(values[1]))

            # Remove any temp item if exists
            for child in self.cat_tree.get_children():
                if "new_item" in str(child):
                    if child != selection[0]:
                        self.cat_tree.delete(child)

            if "new_item" in str(selection[0]):
                self._set_cat_form_state("add")
            else:
                self._set_cat_form_state("view")
                # When selected, we can double click to edit, or just allow edit immediately. Let's make it editable on click.
                self._set_cat_form_state("edit")

    def _on_cat_add(self):
        self.var_cat_id.set("")
        self.var_cat_name.set("")
        # Remove existing new_item if it's there
        if self.cat_tree.exists("new_item"):
            self.cat_tree.delete("new_item")
        temp_id = self.cat_tree.insert("", "end", iid="new_item", values=("(New)", ""))
        self.cat_tree.selection_set(temp_id)
        self.cat_tree.see(temp_id)
        self.entry_cat_name.focus_set()
        self._set_cat_form_state("add")

    def _on_cat_save(self):
        cat_id = self.var_cat_id.get()
        name = self.var_cat_name.get().strip()

        if not name:
            messagebox.showwarning("Warning", "Name cannot be empty.")
            return

        if not cat_id or cat_id == "(New)":
            # Add
            new_id = self.icon_service.add_category(name)
            if new_id:
                if hasattr(self, 'tree_model'):
                    self.tree_model.category_cache[new_id] = {"id": new_id, "name": name}
                self._load_categories_tree()
                # Select the new one
                for child in self.cat_tree.get_children():
                    if str(self.cat_tree.item(child)["values"][0]) == str(new_id):
                        self.cat_tree.selection_set(child)
                        break
                self._set_cat_form_state("view")
                # trigger sync for icon manager if needed
                self.load_tree_data()
            else:
                messagebox.showerror("Error", "Could not add category (maybe duplicate name).")
        else:
            # Update
            success = self.icon_service.update_category(int(cat_id), name)
            if success:
                if hasattr(self, 'tree_model'):
                    if int(cat_id) in self.tree_model.category_cache:
                        self.tree_model.category_cache[int(cat_id)]["name"] = name
                self._load_categories_tree()
                for child in self.cat_tree.get_children():
                    if str(self.cat_tree.item(child)["values"][0]) == cat_id:
                        self.cat_tree.selection_set(child)
                        break
                self._set_cat_form_state("view")
                self.load_tree_data()
            else:
                messagebox.showerror("Error", "Could not update category.")

    def _on_cat_cancel(self):
        selection = self.cat_tree.selection()
        if selection and "new_item" in str(selection[0]):
            self.cat_tree.delete(selection[0])
            self.var_cat_id.set("")
            self.var_cat_name.set("")
        else:
            # Revert to selected values
            if selection:
                values = self.cat_tree.item(selection[0])["values"]
                self.var_cat_id.set(str(values[0]))
                self.var_cat_name.set(str(values[1]))

        self._set_cat_form_state("view")

    def _on_cat_delete(self):
        cat_id = self.var_cat_id.get()
        if not cat_id or cat_id == "(New)":
            return

        if messagebox.askyesno("Confirm", f"Delete category ID {cat_id}?"):
            try:
                success = self.icon_service.delete_category(int(cat_id))
                if success:
                    if hasattr(self, 'tree_model'):
                        self.tree_model.invalidate_category(int(cat_id))
                    self.var_cat_id.set("")
                    self.var_cat_name.set("")
                    self._load_categories_tree()
                    self._set_cat_form_state("view")
                    self.load_tree_data()
                else:
                    messagebox.showerror("Error", "Failed to delete category.")
            except ValueError as e:
                if str(e) == "category_in_use_error":
                    messagebox.showerror("Error", "Cannot delete category because it is used by icons.")
                else:
                    messagebox.showerror("Error", f"An error occurred: {e}")

    def _on_tree_open(self, event):
        """Lazy load usages when an icon node is opened"""
        item_id = self.tree.focus()
        if not item_id or not item_id.startswith("icon_"):
            return

        icon_key = item_id.replace("icon_", "")

        # Check if already loaded by looking for a usage node
        children = self.tree.get_children(item_id)
        # If the only child is dummy, we need to load. Otherwise, if it's already a usage node, return.
        if children and not children[0].startswith("loading_") and not children[0].startswith("dummy_"):
            return

        # Clean loading or dummy indicator if exists
        for child in children:
            if child.startswith("loading_") or child.startswith("dummy_"):
                self.tree.delete(child)

        # Insert loading node
        loading_id = f"loading_{icon_key}"
        self.tree.insert(item_id, "end", iid=loading_id, text="Loading usages...")

        try:
            self.tree_model.load_usages_for_icon_async(icon_key, lambda key, usages: self._safe_after(0, lambda: self._on_usages_loaded(key, usages)))
        except RuntimeError:
            pass

    def _on_usages_loaded(self, icon_key, usages):
        if not self.winfo_exists():
            return
        node_id = f"icon_{icon_key}"
        if not hasattr(self, 'tree') or not self.tree.exists(node_id):
            return

        # Remove loading node
        for child in self.tree.get_children(node_id):
            if child.startswith("loading_"):
                self.tree.delete(child)

        # Update text to show usage count
        current_text = self.tree.item(node_id, "text")
        if " (Usages: " not in current_text:
             self.tree.item(node_id, text=f"{current_text} (Usages: {len(usages)})")
        else:
             # Remove old count and append new
             base_text = current_text.split(" (Usages: ")[0]
             self.tree.item(node_id, text=f"{base_text} (Usages: {len(usages)})")

        if not usages:
             self.tree.insert(node_id, "end", text="No usages found", iid=f"no_usage_{icon_key}")
             return

        for usage in usages:
            usage_id = usage.get('usage_id')
            module_name = usage.get('module_name', 'Unknown')
            component_type = usage.get('ui_component_type', 'Unknown')
            usage_text = f"📍 {module_name} > {component_type}"
            self.tree.insert(node_id, "end", iid=f"usage_{usage_id}", text=usage_text, values=("usage", ""))
