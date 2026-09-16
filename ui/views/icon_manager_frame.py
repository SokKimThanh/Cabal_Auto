import os
import tkinter as tk
import threading
from tkinter import ttk, messagebox

from ui.components.empty_state import EmptyState
from ui.components.base.responsive_grid_base import ResponsiveGridBase
from lib.ui_style_v2 import UIStyleV2 as UIStyle
from lib.db.services.icon_service import IconService
from ui.helpers.icon_helper import get_icon_helper
from database import get_db

from ui.helpers.tooltip import attach_i18n_tooltip


class IconManagerFrame(ResponsiveGridBase):
    def __init__(self, parent, app=None, *args, **kwargs):
        super().__init__(parent, app=app, bg=UIStyle.BG_BASE, *args, **kwargs)
        self.app = app
        self.db = get_db()
        self.icon_service = IconService(self.db.conn)
        self.icon_helper = get_icon_helper()

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

        self._setup_ui()
        self._check_and_auto_sync()
        self.load_tree_data()

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
        self.content_state_frame.grid_rowconfigure(0, weight=1) # Preview
        self.content_state_frame.grid_rowconfigure(1, weight=0) # Form ko co giãn quá mức
        self.content_state_frame.grid_columnconfigure(0, weight=1)

        # Bọc Form vào một container giới hạn max width
        self.detail_container = tk.Frame(self.content_state_frame, bg=UIStyle.BG_SURFACE)
        self.detail_container.grid(row=1, column=0, sticky="nw", padx=UIStyle.SPACE_MD, pady=UIStyle.SPACE_MD)

        self._build_preview_zone()
        self._build_detail_form()

        # Mặc định hiện empty state
        self.empty_state_frame.tkraise()

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

        # 6. Filepath (with Browse button)
        tk.Label(self.form_frame, text=self.i18n_t("lbl_filepath", default="Filepath:"), bg=UIStyle.BG_SURFACE, fg=UIStyle.TEXT_PRIMARY).grid(row=5, column=0, sticky="e", padx=5, pady=2)

        filepath_frame = tk.Frame(self.form_frame, bg=UIStyle.BG_SURFACE)
        filepath_frame.grid(row=5, column=1, sticky="ew", padx=5, pady=2)
        filepath_frame.grid_columnconfigure(0, weight=1)

        self.entry_filepath = ttk.Entry(filepath_frame, textvariable=self.var_filepath, state="disabled")
        self.entry_filepath.grid(row=0, column=0, sticky="ew")

        self.btn_browse = tk.Button(filepath_frame, text="...", command=self._on_browse_clicked, **(UIStyle.get_button_style("secondary") if hasattr(UIStyle, "get_button_style") else {}))
        self.btn_browse.grid(row=0, column=1, padx=(5, 0))


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

        # We need a large icon. Let's try 128x128
        giant_icon = self.icon_helper.get_icon(icon_key, fallback=fallback_emoji, size=128)

        if giant_icon and not isinstance(giant_icon, str):
            self.lbl_preview.config(image=giant_icon, text="")
            self.lbl_preview.image = giant_icon
        else:
            # Fallback to emoji text
            emoji_text = giant_icon if isinstance(giant_icon, str) and giant_icon != "❓" else fallback_emoji
            if not emoji_text:
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


                # Check if file is outside assets
                final_filename = selected_path.name

                resolved_selected = os.path.normcase(os.path.abspath(str(selected_path.resolve())))
                resolved_icons_dir = os.path.normcase(os.path.abspath(str(icons_dir.resolve())))

                if not resolved_selected.startswith(resolved_icons_dir):
                    target_filename = selected_path.name
                    target_path = icons_dir / target_filename
                    overwrite = False

                    if target_path.exists():
                        # Ask user if they want to replace the existing file
                        msg_overwrite = self.i18n_t(
                            "msg_file_exists_overwrite",
                            default=f"File ảnh '{target_filename}' đã tồn tại trong hệ thống.\nBạn có muốn thay thế file cũ bằng file mới này không?"
                        )
                        should_overwrite = messagebox.askyesno(
                            self.i18n_t("warning", default="Cảnh báo ghi đè"),
                            msg_overwrite
                        )
                        if should_overwrite:
                            overwrite = True
                        else:
                            # User chose not to overwrite. Abort import to keep the existing file as is.
                            return
                    else:
                        # File doesn't exist, ask normal copy warning
                        msg = self.i18n_t(
                            "msg_file_outside_assets",
                            default="File ảnh đang nằm ngoài thư mục hệ thống (assets). Nếu bạn xóa hoặc di chuyển file này, icon sẽ bị lỗi. Bạn có muốn tự động copy file này vào thư mục assets cho an toàn không?"
                        )
                        should_copy = messagebox.askyesno(
                            self.i18n_t("warning", default="Cảnh báo"),
                            msg
                        )
                        if not should_copy:
                            final_filename = file_path # Keep original absolute path
                            overwrite = None # Signal that we don't import

                    if overwrite is not None:
                        final_filename = import_icon_file(file_path, overwrite=overwrite)
                else:
                    final_filename = selected_path.name

                # Check for duplication (only if we have an icon_key selected)
                current_icon_key = self.var_icon_key.get().strip()
                if current_icon_key: # Form must be in ADD/EDIT mode and have key
                    # Need to check filename against DB
                    existing_usages = self.icon_service.get_icons_by_filepath(final_filename)
                    # Filter out the current icon we are editing
                    other_usages = [u for u in existing_usages if u.get("icon_key") != current_icon_key]

                    if other_usages:
                        usage_keys = ", ".join([u.get("icon_key", "") for u in other_usages])
                        msg_dup = self.i18n_t(
                            "msg_icon_duplicated",
                            default=f"File ảnh '{final_filename}' đã được sử dụng cho Icon Key(s): {usage_keys}.\nBạn có chắc chắn muốn dùng chung file ảnh này không?",
                            filename=final_filename,
                            usage_keys=usage_keys
                        )
                        should_reuse = messagebox.askyesno(
                            self.i18n_t("warning", default="Cảnh báo trùng lặp"),
                            msg_dup
                        )
                        if not should_reuse:
                            return # User aborted

                # Update filepath entry
                self.var_filepath.set(final_filename)

                # Update Preview
                self.icon_helper._icon_cache = getattr(self.icon_helper, "_icon_cache", {})
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
        self.btn_browse.config(state="normal" if state in ("ADD", "EDIT") else "disabled")

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

    def _on_delete(self):
        icon_key = self.var_icon_key.get()
        if not icon_key:
            return

        from tkinter import messagebox
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

                self.after(0, lambda: self._on_sync_complete(count, show_message))
            except Exception as e:
                self.after(0, lambda: self._on_sync_error(str(e), show_message))

        threading.Thread(target=run_sync, daemon=True).start()

    def _on_sync_complete(self, count, show_message):
        import tkinter.messagebox as messagebox
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

    def _on_save(self):
        icon_key = self.var_icon_key.get().strip()
        if not icon_key:
            from tkinter import messagebox
            messagebox.showerror("Error", "Icon Key is required.")
            return

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

        success = self.icon_service.upsert_icon(icon_data)
        if success:
            self.load_tree_data()

            # Mở lại thư mục vừa thêm vào
            cat_node_id = f"cat_{cat_name}"
            if self.tree.exists(cat_node_id):
                self.tree.item(cat_node_id, open=True)

            # Re-select the saved item
            for item in self.tree.get_children():
                if item.startswith('cat_'):
                    for child in self.tree.get_children(item):
                        if child == icon_key:
                            self.tree.selection_set(child)
                            self.tree.see(child)
                            break

            self.set_form_state("VIEW")
            self.tree.focus_set()
        else:
            from tkinter import messagebox
            messagebox.showerror("Error", "Failed to save icon data.")

    def _on_cancel(self):
        # Dọn dẹp dòng dummy nếu đang ở trạng thái ADD
        if self._current_state == "ADD":
            selection = self.tree.selection()
            if selection:
                item_id = selection[0]
                if item_id.startswith("new_icon_"):
                    self.tree.delete(item_id)

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
        all_icons = self.icon_service.get_all_icons()
        if not all_icons:
            self._on_sync(show_message=False)


    def apply_filters(self):
        self.load_tree_data()

    def load_tree_data(self):
        # Clear current tree
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Get filter values
        search_term = (self.search_var.get() or '').strip().lower()
        selected_category_name = self.category_var.get()
        selected_category_id = ""
        if selected_category_name and selected_category_name != "All":
            if hasattr(self, 'categories_map'):
                selected_category_id = self.categories_map.get(selected_category_name, "")

        selected_status_raw = self.status_var.get()
        # Parse status filter
        status_filter = ""
        if "Xanh" in selected_status_raw:
            status_filter = "GREEN"
        elif "Vàng" in selected_status_raw:
            status_filter = "YELLOW"
        elif "Đỏ" in selected_status_raw:
            status_filter = "RED"

        # Fetch all icons (using search and category from DB)
        all_icons = self.icon_service.get_all_icons(search_term=search_term, category=selected_category_id)

        # Dropdown population is now handled by _load_categories_tree

        # Group by category and filter by status
        grouped_data = {}
        for icon in all_icons:
            # Check status logic
            status = self.icon_helper.evaluate_icon_status(icon)

            # Apply status filter in Python
            if status_filter and status != status_filter:
                continue

            cat = icon.get("category_name", "General")
            if cat not in grouped_data:
                grouped_data[cat] = []
            grouped_data[cat].append((icon, status))

        # Render Treeview
        for cat_name, items in sorted(grouped_data.items()):
            # Insert Category Node
            cat_id = f"cat_{cat_name}"
            self.tree.insert('', 'end', iid=cat_id, text=f"📁 {cat_name}", open=True)

            for icon, status in sorted(items, key=lambda x: x[0].get("name", "").lower()):
                icon_key = icon.get("icon_key", "")
                icon_name = icon.get("name", "")

                # Format status column with emoji
                status_color = "⚪"  # Default
                if status == "GREEN":
                    status_color = "🟢"
                elif status == "YELLOW":
                    status_color = "🟡"
                elif status == "RED":
                    status_color = "🔴"

                self.tree.insert(
                    cat_id,
                    'end',
                    iid=icon_key,
                    text=icon_name,
                    values=(icon_key, status_color)
                )

        # Recheck scrollbar
        self._check_scrollbar()

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

    def _on_tree_select(self, event):
        if hasattr(self, '_select_after_id') and self._select_after_id:
            self.after_cancel(self._select_after_id)
        self._select_after_id = self.after(50, self._process_tree_selection)

    def _process_tree_selection(self):
        selection = self.tree.selection()
        if not selection:
            return

        item_id = selection[0]
        if item_id.startswith('cat_'):
            return

        # It's an icon node
        if item_id.startswith("new_icon_"):
            return

        icon_data = self.icon_service.get_icon_by_key(item_id)
        if icon_data:
            self.var_name.set(icon_data.get('name', ''))
            self.var_icon_key.set(icon_data.get('icon_key', ''))

            # Map category_id back to name
            cat_name = icon_data.get("category_name", "General")
            self.var_category.set(cat_name)

            self.var_fallback_emoji.set(icon_data.get('fallback_emoji', ''))
            self.var_tooltip_key.set(icon_data.get('tooltip_translation_key', ''))
            self.var_filepath.set(icon_data.get('filepath', ''))

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
                    self.var_cat_id.set("")
                    self.var_cat_name.set("")
                    self._load_categories_tree()
                    self._set_cat_form_state("view")
                else:
                    messagebox.showerror("Error", "Failed to delete category.")
            except ValueError as e:
                if str(e) == "category_in_use_error":
                    messagebox.showerror("Error", "Cannot delete category because it is used by icons.")
                else:
                    messagebox.showerror("Error", f"An error occurred: {e}")
