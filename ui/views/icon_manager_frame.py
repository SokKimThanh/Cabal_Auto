import os
from pathlib import Path
import tkinter as tk
import sqlite3
from tkinter import ttk, messagebox

from ui.components.empty_state import EmptyState
from ui.components.category_manager_component import CategoryManagerComponent
from ui.components.base.responsive_grid_base import ResponsiveGridBase
from lib.ui_style_v2 import UIStyleV2 as UIStyle
from lib.db.services.icon_service import IconService
from ui.helpers.icon_helper import get_icon_helper
from ui.models.icon_tree_model import IconTreeModel
from ui.models.image_library_model import ImageLibraryModel
from ui.components.image_library_component import ImageLibraryComponent
from ui.components.icon_preview_component import IconPreviewComponent
from ui.components.icon_form_component import IconFormComponent
from database import get_db

from ui.helpers.tooltip import attach_i18n_tooltip
from ui.controllers.icon_manager_controller import IconManagerController


class IconManagerFrame(ResponsiveGridBase):
    MODULE_NAME = "icon_manager_frame"
    SCREEN_NAME = "main"

    def __init__(self, parent, app=None, *args, **kwargs):
        super().__init__(parent, app=app, bg=UIStyle.BG_BASE, *args, **kwargs)
        self.app = app
        self.db = get_db()
        self.icon_service = IconService(self.db.conn)
        self.icon_helper = get_icon_helper()
        self.tree_model = IconTreeModel()
        self.image_model = ImageLibraryModel()

        self.controller = IconManagerController(
            app=self.app,
            icon_service=self.icon_service,
            tree_model=self.tree_model,
            image_model=self.image_model,
            icon_helper=self.icon_helper,
            categories_map={}
        )

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
        self._current_available_element_selection = None
        self._debounce_after_id = None
        self._render_queue = []
        self._render_after_id = None

        self.image_library = None

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



    def _prevent_scroll_propagation(self, event):
        """Prevent mouse wheel events from bubbling up to the main canvas."""
        # The event.widget provides the widget that triggered the scroll.
        # We process the scroll manually for this widget to keep it scrolling,
        # and then return "break" to stop propagation.
        widget = event.widget
        try:
            import sys
            if sys.platform == "win32":
                widget.yview_scroll(int(-1 * (event.delta / 120)), "units")
            elif sys.platform == "darwin":
                widget.yview_scroll(int(-1 * event.delta), "units")
            else:
                if event.num == 4:
                    widget.yview_scroll(-1, "units")
                elif event.num == 5:
                    widget.yview_scroll(1, "units")
        except Exception:
            pass
        return "break"

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
        content_frame.grid_rowconfigure(0, weight=1)
        content_frame.grid_columnconfigure(0, weight=1)

        self.main_content_frame = tk.Frame(content_frame, bg=UIStyle.BG_BASE)
        self.main_content_frame.grid(row=0, column=0, sticky="nsew", pady=UIStyle.SPACE_MD)
        self.main_content_frame.grid_rowconfigure(0, weight=1)
        self.main_content_frame.grid_columnconfigure(0, weight=1)

        style = ttk.Style()
        style.configure("IconManager.TPanedwindow", background=UIStyle.BG_BASE)

        self.paned_window = ttk.PanedWindow(self.main_content_frame, orient=tk.HORIZONTAL, style="IconManager.TPanedwindow")
        self.paned_window.grid(row=0, column=0, sticky="nsew")

        from ui.components.icon_tree_component import IconTreeComponent
        self.tree_component = IconTreeComponent(
            self.paned_window,
            app=self.app,
            tree_model=self.tree_model,
            categories_map=self.categories_map if hasattr(self, "categories_map") else {},
            on_node_selected_callback=self._process_tree_selection_callback,
            on_interaction_callback=self._on_tree_interaction
        )
        self.paned_window.add(self.tree_component, weight=0)

        # Right Detail Frame
        self.right_detail_frame = tk.Frame(self.paned_window, bg=UIStyle.BG_SURFACE)
        self.paned_window.add(self.right_detail_frame, weight=1)

        # Bind Configure to set 35:65 ratio on first render
        self._sash_configured = False
        def on_configure(event):
            if not self._sash_configured and event.width > 10:
                self._sash_configured = True
                sash_pos = int(event.width * 0.35)
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
            submessage=self.i18n_t("msg_no_icon_sub", default="Vui lòng chọn một icon từ danh sách để xem chi tiết"),
            wraplength=450
        )
        self.empty_preview.grid(row=0, column=0, sticky="nsew")

        # Trạng thái 2: Content (đã chọn icon, có form & preview)
        self.content_state_frame = tk.Frame(self.right_detail_frame, bg=UIStyle.BG_SURFACE)
        self.content_state_frame.grid(row=0, column=0, sticky="nsew")
        self.content_state_frame.grid_rowconfigure(0, weight=1)
        self.content_state_frame.grid_columnconfigure(0, weight=1)

        # Initialize the Notebook
        self.notebook = ttk.Notebook(self.content_state_frame)
        self.notebook.grid(row=0, column=0, sticky="nsew", padx=UIStyle.SPACE_MD, pady=UIStyle.SPACE_MD)

        # Tab 1: Gắn Icon (Usages) - Mặc định
        self.tab_usages = tk.Frame(self.notebook, bg=UIStyle.BG_SURFACE)
        self.notebook.add(self.tab_usages, text=self.i18n_t("tab_icon_usages", default="Gắn Icon"))

        # Build Usages Panel directly in the usages tab
        self._build_usages_panel(self.tab_usages)

        # Tab 2: Thông tin Icon (Details)
        self.tab_details = tk.Frame(self.notebook, bg=UIStyle.BG_SURFACE)
        self.notebook.add(self.tab_details, text=self.i18n_t("tab_icon_details", default="Thông tin Icon"))

        # Setup Tab 2 layout
        self.tab_details.grid_rowconfigure(0, weight=0)  # Form
        self.tab_details.grid_rowconfigure(1, weight=0)  # Top Detail
        self.tab_details.grid_rowconfigure(2, weight=1)  # Preview + Image Library
        self.tab_details.grid_columnconfigure(0, weight=1)

        self.detail_container = tk.Frame(self.tab_details, bg=UIStyle.BG_SURFACE)
        self.detail_container.grid(row=0, column=0, sticky="nsew", pady=(0, UIStyle.SPACE_MD))

        self.top_detail_container = tk.Frame(self.tab_details, bg=UIStyle.BG_SURFACE)
        self.top_detail_container.grid(row=1, column=0, sticky="nsew")

        self.bottom_detail_container = tk.Frame(self.tab_details, bg=UIStyle.BG_SURFACE)
        self.bottom_detail_container.grid(row=2, column=0, sticky="nsew")

        # Split bottom container into Preview (left) and Library (right)
        self.bottom_detail_container.grid_rowconfigure(0, weight=1)
        self.bottom_detail_container.grid_columnconfigure(0, weight=3) # Preview takes less space
        self.bottom_detail_container.grid_columnconfigure(1, weight=7) # Library takes more space

        self.preview_container = tk.Frame(self.bottom_detail_container, bg=UIStyle.BG_SURFACE)
        self.preview_container.grid(row=0, column=0, sticky="nsew", padx=(0, UIStyle.SPACE_MD))

        self.preview_component = IconPreviewComponent(self.preview_container, app=self.app, icon_helper=self.icon_helper)
        self.preview_component.pack(fill="both", expand=True)

        self.img_lib_container = tk.Frame(self.bottom_detail_container, bg=UIStyle.BG_SURFACE)
        self.img_lib_container.grid(row=0, column=1, sticky="nsew")

        self.image_library = ImageLibraryComponent(
            self.img_lib_container,
            app=self.app,
            image_model=self.image_model,
            on_image_selected=self._handle_image_selected,
            get_used_filepaths=self._get_used_filepaths
        )
        self.image_library.pack(fill="both", expand=True)

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
        self.category_manager = CategoryManagerComponent(
            parent_frame,
            app=self.app,
            icon_service=self.icon_service,
            tree_model=self.tree_model,
            on_category_changed=self._on_category_changed
        )
        self.category_manager.pack(fill="both", expand=True)
        self.category_manager.start()

    def _on_category_changed(self):
        self._populate_category_combo()
        self.tree_component.request_load_tree_data()

    def _on_form_name_changed(self, new_name):
        # Callback for when name changes to update dummy icon in tree and sync state if needed
        pass

    def _build_detail_form(self):
        self.icon_form = IconFormComponent(self.detail_container, app=self.app, on_name_changed_callback=self._on_form_name_changed)
        self.icon_form.pack(fill="x", expand=False)

    def _build_usages_panel(self, parent_frame):
        # Contextual label for mapping
        self.var_current_mapping_icon = tk.StringVar(value="Đang chọn Icon: (Chưa chọn)")
        lbl_context = tk.Label(
            parent_frame,
            textvariable=self.var_current_mapping_icon,
            bg=UIStyle.BG_SURFACE,
            fg=UIStyle.COLOR_PRIMARY if hasattr(UIStyle, "COLOR_PRIMARY") else "#0078D7",
            font=("Segoe UI", 11, "bold")
        )
        lbl_context.pack(fill="x", padx=10, pady=(10, 0))

        # Additional Contextual Label for Element ID
        self.var_current_mapping_element = tk.StringVar(value="UI Element ID đang chọn: (Chưa chọn)")
        lbl_context_element = tk.Label(
            parent_frame,
            textvariable=self.var_current_mapping_element,
            bg=UIStyle.BG_SURFACE,
            fg=UIStyle.TEXT_SECONDARY,
            font=("Segoe UI", 12, "bold")
        )
        lbl_context_element.pack(fill="x", padx=10, pady=(0, 10))

        usage_container = tk.Frame(parent_frame, bg=UIStyle.BG_SURFACE)
        usage_container.pack(fill="both", expand=True, padx=5, pady=10)

        # 50/50 horizontal split layout
        usage_container.grid_columnconfigure(0, weight=1, uniform="group1") # Left: Available Elements
        usage_container.grid_columnconfigure(1, weight=1, uniform="group1") # Right: Usages
        usage_container.grid_rowconfigure(0, weight=1)

        # Used for storing selection safely
        self.var_usage_mod = tk.StringVar(value="")
        self.var_usage_comp = tk.StringVar(value="")
        self.var_usage_element = tk.StringVar(value="")

        # =========================================================================
        # LEFT: Add Form (Available Elements)
        # =========================================================================
        add_frame = tk.Frame(usage_container, bg=UIStyle.BG_SURFACE)
        add_frame.grid(row=0, column=0, sticky="nsew", padx=(5, 5), pady=5)
        add_frame.grid_rowconfigure(1, weight=1) # Treeview row
        add_frame.grid_columnconfigure(0, weight=1)

        header_frame = tk.Frame(add_frame, bg=UIStyle.BG_SURFACE)
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        header_frame.grid_columnconfigure(1, weight=1)

        tk.Label(
            header_frame,
            text=self.i18n_t("lbl_available_elements", default="Chọn thành phần cần gắn (Available Elements):"),
            bg=UIStyle.BG_SURFACE,
            fg=UIStyle.TEXT_PRIMARY,
            font=("Segoe UI", 10, "bold")
        ).grid(row=0, column=0, sticky="w")

        # Search box for Available Elements
        self.var_element_search = tk.StringVar()
        self.entry_element_search = ttk.Entry(header_frame, textvariable=self.var_element_search, width=30)
        self.entry_element_search.grid(row=0, column=1, sticky="e", padx=(10, 0))
        self.entry_element_search.insert(0, "Search Element ID...")

        def on_search_focus_in(event):
            if self.entry_element_search.get() == "Search Element ID...":
                self.entry_element_search.delete(0, tk.END)

        def on_search_focus_out(event):
            if not self.entry_element_search.get():
                self.entry_element_search.insert(0, "Search Element ID...")

        self.entry_element_search.bind("<FocusIn>", on_search_focus_in)
        self.entry_element_search.bind("<FocusOut>", on_search_focus_out)
        self.var_element_search.trace_add("write", self._on_element_search_changed)

        # In-memory cache for available elements tree
        self._available_elements_cache = {}
        self._element_search_debounce_after_id = None
        self._last_search_term = None

        # Treeview for available elements
        self.available_elements_tree = ttk.Treeview(
            add_frame,
            columns=("id", "module", "component", "element", "mapped"),
            show="tree headings",
            selectmode="browse",
            height=4
        )
        self.available_elements_tree.heading("#0", text="Mục lục (Module/Screen)", anchor="w")
        self.available_elements_tree.heading("id", text="")
        self.available_elements_tree.heading("module", text="Module")
        self.available_elements_tree.heading("component", text="Type")
        self.available_elements_tree.heading("element", text="Element ID")
        self.available_elements_tree.heading("mapped", text="Mapped Icon")

        self.available_elements_tree.column("#0", width=150, stretch=tk.NO)
        self.available_elements_tree.column("id", width=0, stretch=tk.NO)
        self.available_elements_tree.column("module", width=80, stretch=tk.NO)
        self.available_elements_tree.column("component", width=80, stretch=tk.NO)
        self.available_elements_tree.column("element", width=120, stretch=tk.YES)
        self.available_elements_tree.column("mapped", width=100, stretch=tk.NO)

        self.available_elements_tree.grid(row=1, column=0, sticky="nsew")

        av_scroll = ttk.Scrollbar(add_frame, orient="vertical", command=self.available_elements_tree.yview)
        av_scroll.grid(row=1, column=1, sticky="ns")
        self.available_elements_tree.configure(yscrollcommand=av_scroll.set)

        self.available_elements_tree.bind('<MouseWheel>', self._prevent_scroll_propagation)
        self.available_elements_tree.bind('<Button-4>', self._prevent_scroll_propagation)
        self.available_elements_tree.bind('<Button-5>', self._prevent_scroll_propagation)
        self.available_elements_tree.bind('<<TreeviewSelect>>', self._on_available_element_select)

        # Left Action Button (Map)
        left_btn_frame = tk.Frame(add_frame, bg=UIStyle.BG_SURFACE)
        left_btn_frame.grid(row=2, column=0, sticky="w", pady=(5, 0))
        self.btn_add_usage = tk.Button(
            left_btn_frame,
            text="Gắn (Map)",
            command=self._on_add_usage,
            **(UIStyle.get_button_style("primary") if hasattr(UIStyle, "get_button_style") else {})
        )
        self.btn_add_usage.pack(side="left")

        # =========================================================================
        # RIGHT: Treeview for Usages
        # =========================================================================
        right_frame = tk.Frame(usage_container, bg=UIStyle.BG_SURFACE)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 5), pady=5)
        right_frame.grid_rowconfigure(1, weight=1) # Treeview row
        right_frame.grid_columnconfigure(0, weight=1)

        right_header_frame = tk.Frame(right_frame, bg=UIStyle.BG_SURFACE)
        right_header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 5))

        tk.Label(
            right_header_frame,
            text=self.i18n_t("lbl_mapped_usages", default="Các nơi đã gắn (Mapped Usages):"),
            bg=UIStyle.BG_SURFACE,
            fg=UIStyle.TEXT_PRIMARY,
            font=("Segoe UI", 10, "bold")
        ).pack(side="left")

        self.usage_tree = ttk.Treeview(
            right_frame,
            columns=("id", "module", "component", "element"),
            show="headings",
            selectmode="browse",
            height=4
        )
        self.usage_tree.heading("id", text="ID")
        self.usage_tree.heading("module", text="Module")
        self.usage_tree.heading("component", text="Component")
        self.usage_tree.heading("element", text="Element ID")

        self.usage_tree.column("id", width=30, stretch=tk.NO, anchor="center")
        self.usage_tree.column("module", width=80, stretch=tk.YES)
        self.usage_tree.column("component", width=80, stretch=tk.YES)
        self.usage_tree.column("element", width=120, stretch=tk.YES)

        self.usage_tree.grid(row=1, column=0, sticky="nsew")

        usage_scroll = ttk.Scrollbar(right_frame, orient="vertical", command=self.usage_tree.yview)
        usage_scroll.grid(row=1, column=1, sticky="ns")
        self.usage_tree.configure(yscrollcommand=usage_scroll.set)

        self.usage_tree.bind('<MouseWheel>', self._prevent_scroll_propagation)
        self.usage_tree.bind('<Button-4>', self._prevent_scroll_propagation)
        self.usage_tree.bind('<Button-5>', self._prevent_scroll_propagation)

        # Right Action Button (Unmap)
        right_btn_frame = tk.Frame(right_frame, bg=UIStyle.BG_SURFACE)
        right_btn_frame.grid(row=2, column=0, sticky="w", pady=(5, 0))
        self.btn_del_usage = tk.Button(
            right_btn_frame,
            text="Gỡ (Unmap)",
            command=self._on_del_usage,
            **(UIStyle.get_button_style("danger") if hasattr(UIStyle, "get_button_style") else {})
        )
        self.btn_del_usage.pack(side="left")

    def _on_element_search_changed(self, *args):
        if self._element_search_debounce_after_id:
            self.after_cancel(self._element_search_debounce_after_id)

        # Increase debounce time slightly to ensure user has stopped typing
        self._element_search_debounce_after_id = self.after(400, self._apply_element_filter)

    def _apply_element_filter(self, force=False):
        if not hasattr(self, 'available_elements_tree') or not self._available_elements_cache:
            return

        search_term = self.var_element_search.get().lower().strip()
        if search_term == "search element id...":
            search_term = ""

        if not force and hasattr(self, '_last_search_term') and self._last_search_term == search_term:
            return

        self._last_search_term = search_term

        # Save selection
        selected_item_values = None
        selection = self.available_elements_tree.selection()
        if selection:
            item = self.available_elements_tree.item(selection[0])
            selected_item_values = item.get("values")

        # Prevent GUI lag/flicker by detaching nodes instead of raw deletion
        children = self.available_elements_tree.get_children()
        if children:
            self.available_elements_tree.detach(*children)
            self.available_elements_tree.delete(*children)

        # Build list of insert operations first to minimize GUI overhead
        nodes_to_insert = []
        is_open = True if search_term else False

        for mod, screens in sorted(self._available_elements_cache.items()):
            mod_matches = search_term in mod.lower()
            mod_has_children = False
            mod_children_ops = []

            for screen, elements in sorted(screens.items()):
                screen_matches = search_term in screen.lower()
                filtered_elements = []

                for el in elements:
                    if search_term in el['id'].lower() or mod_matches or screen_matches:
                        filtered_elements.append(el)

                if filtered_elements:
                    mod_has_children = True
                    screen_children_ops = []
                    for el in sorted(filtered_elements, key=lambda x: x["id"]):
                        screen_children_ops.append(
                            (f"  {el['id']}", (el['id'], el['mod'], el['comp'], el['id'], el.get('mapped', '')), False)
                        )
                    mod_children_ops.append((f"📄 {screen}", None, is_open, screen_children_ops))

            if mod_has_children:
                nodes_to_insert.append((f"📁 {mod}", None, is_open, mod_children_ops))

        # Perform batched insertion
        item_to_select = None
        for mod_text, mod_vals, mod_open, screen_ops in nodes_to_insert:
            mod_node = self.available_elements_tree.insert("", "end", text=mod_text, open=mod_open)
            for screen_text, screen_vals, screen_open, el_ops in screen_ops:
                screen_node = self.available_elements_tree.insert(mod_node, "end", text=screen_text, open=screen_open)
                for el_text, el_vals, el_open in el_ops:
                    node_id = self.available_elements_tree.insert(screen_node, "end", text=el_text, values=el_vals)
                    if selected_item_values and el_vals and list(el_vals) == list(selected_item_values):
                        item_to_select = node_id

        if item_to_select:
            self._current_available_element_selection = item_to_select
            self.available_elements_tree.selection_set(item_to_select)
            self.available_elements_tree.see(item_to_select)


    def _load_all_usage_ids(self):
        import threading
        def fetch_data():
            try:
                # 1. Query db_usages
                # Use a new connection for thread safety
                import sqlite3
                from database import get_db
                conn = sqlite3.connect(str(get_db().DB_PATH))
                cursor = conn.cursor()
                cursor.execute("SELECT module_name, ui_component_type, ui_element_id, icon_key FROM icon_usages WHERE ui_element_id IS NOT NULL AND ui_element_id != ''")
                db_rows = cursor.fetchall()
                conn.close()

                # Build mapping dictionary from DB rows
                db_mapping = {}
                for r in db_rows:
                    m_name = r[0] or ""
                    c_type = r[1] or ""
                    el_id = r[2] or ""
                    icon_key = r[3] or ""
                    if el_id:
                        key = f"{m_name}:{c_type}:{el_id}"
                        db_mapping[key] = icon_key
                        # Also keep element ID only as fallback lookup
                        db_mapping[el_id] = icon_key

                # 2. Get descriptors from Registry + CommonUI enum
                registry_items = []
                try:
                    from lib.events.ui_element_registry import UIElementRegistry, UIElementDescriptor, CommonUI
                    registry_items = UIElementRegistry().get_all()

                    # Pre-populate with CommonUI items
                    for ui_enum in CommonUI:
                        val = ui_enum.value
                        if not any(d.element_id == val for d in registry_items):
                            registry_items.append(UIElementDescriptor(element_id=val, module="Common", screen="Global", element_type="button"))
                except ImportError:
                    pass

                # 3. Merge data
                tree_data = {}
                seen_elements = set()

                for desc in registry_items:
                    mod = desc.module or "Unknown"
                    screen = desc.screen or "Unknown"
                    if mod not in tree_data:
                        tree_data[mod] = {}
                    if screen not in tree_data[mod]:
                        tree_data[mod][screen] = []

                    mapped_val = db_mapping.get(f"{mod}:{desc.element_type}:{desc.element_id}", db_mapping.get(desc.element_id, ""))
                    el_dict = {"id": desc.element_id, "comp": desc.element_type, "mod": mod, "mapped": mapped_val}
                    tree_data[mod][screen].append(el_dict)
                    # Use composite key to prevent semantic duplicates across modules
                    seen_elements.add((mod, screen, desc.element_id))

                # Merge DB rows
                for r in db_rows:
                    mod = r[0] or "Unknown"
                    comp = r[1] or "widget"
                    el_id = r[2]
                    mapped_val = r[3] or ""
                    screen = "Database"

                    # Skip if already exists in registry (using a rough check if the ID is already mapped)
                    # Note: We check if ANY screen in this module has this ID from the registry to avoid
                    # duplicating an ID that is just missing its "Database" screen qualifier.
                    is_duplicate = any(
                        (mod, s, el_id) in seen_elements for s in tree_data.get(mod, {})
                    )

                    if is_duplicate:
                        continue

                    if mod not in tree_data:
                        tree_data[mod] = {}
                    if screen not in tree_data[mod]:
                        tree_data[mod][screen] = []

                    tree_data[mod][screen].append({"id": el_id, "comp": comp, "mod": mod, "mapped": mapped_val})
                    seen_elements.add((mod, screen, el_id))

                # Update UI thread
                if self.winfo_exists():
                    self.after(0, lambda: self._update_usage_ids_ui(tree_data))

            except Exception as e:
                import logging
                logging.getLogger(__name__).warning(f"Failed to load usage IDs for tree: {e}")

        # Run fetch in background to prevent freezing
        threading.Thread(target=fetch_data, daemon=True).start()

    def _update_usage_ids_ui(self, tree_data):
        if not self.winfo_exists() or not hasattr(self, 'available_elements_tree'):
            return

        self._available_elements_cache = tree_data
        self._apply_element_filter(force=True)

    def _on_available_element_select(self, event=None):
        selection = self.available_elements_tree.selection()
        # Prevent infinite loop by checking if selection actually changed
        if not selection:
            self._current_available_element_selection = None
            return

        if self._current_available_element_selection == selection[0]:
            return

        self._current_available_element_selection = selection[0]
        if not selection:
            return

        item = self.available_elements_tree.item(selection[0])
        values = item.get("values")

        # It's a leaf node if it has values
        if values and len(values) >= 4:  # ID, Module, Type, Element ID, Mapped Icon
            self.var_usage_element.set(values[3])  # element_id
            self.var_usage_mod.set(values[1])      # mod
            self.var_usage_comp.set(values[2])     # comp

            if hasattr(self, 'var_current_mapping_element'):
                self.var_current_mapping_element.set(f"UI Element ID đang chọn: {values[3]}")

            mapped_icon = values[4] if len(values) > 4 and values[4] else ""
            if mapped_icon:
                # Highlight and load this icon
                if hasattr(self, 'tree_component'):
                    self.tree_component.search_var.set(mapped_icon)
                    self.apply_filters()
                    self._process_tree_selection_callback(mapped_icon)
            else:
                # Show message but do not clear left tree selection or form data
                if hasattr(self, 'var_current_mapping_icon'):
                    self.var_current_mapping_icon.set(f"⚠️ [Chưa gán Icon] Đang chọn Element: {values[3]}")
                # Disable Edit button to prevent editing wrong icon
                if hasattr(self, 'btn_edit'):
                    self.btn_edit.config(state="disabled")
        else:
            self.var_usage_element.set("")
            self.var_usage_mod.set("")
            self.var_usage_comp.set("")

            if hasattr(self, 'var_current_mapping_element'):
                self.var_current_mapping_element.set("UI Element ID đang chọn: (Chưa chọn)")

    def _sync_available_elements_selection(self, icon_key):
        if not hasattr(self, 'available_elements_tree') or not icon_key:
            return

        target_node = None
        # Use iterative BFS to prevent recursion depth issues and improve performance
        nodes_to_check = list(self.available_elements_tree.get_children(""))

        while nodes_to_check:
            current_node = nodes_to_check.pop(0)
            item = self.available_elements_tree.item(current_node)
            values = item.get("values")

            # Check if it's a leaf node with mapped icon (idx 4)
            if values and len(values) >= 5:
                mapped_icon = values[4]
                # Compare string representation to be safe, sometimes it comes back from Tkinter tuple differently
                if str(mapped_icon) == str(icon_key):
                    target_node = current_node
                    break

            # Add children to the queue
            children = self.available_elements_tree.get_children(current_node)
            if children:
                nodes_to_check.extend(children)

        if target_node:
            # We must NOT set self._current_available_element_selection to target_node before selection_set.
            # If we do, the `_on_available_element_select` event handler will return early and fail to update the labels.
            # By setting it to None or bypassing the check, we force the UI labels to synchronize correctly.
            self._current_available_element_selection = None
            self.available_elements_tree.selection_set(target_node)
            self.available_elements_tree.see(target_node)
        else:
            self._current_available_element_selection = None
            if self.available_elements_tree.selection():
                self.available_elements_tree.selection_remove(*self.available_elements_tree.selection())
            # Clear label variables if there is no mapping
            if hasattr(self, 'var_usage_element'):
                self.var_usage_element.set("")
            if hasattr(self, 'var_usage_mod'):
                self.var_usage_mod.set("")
            if hasattr(self, 'var_usage_comp'):
                self.var_usage_comp.set("")
            if hasattr(self, 'var_current_mapping_element'):
                self.var_current_mapping_element.set("UI Element ID đang chọn: (Chưa chọn)")

    def _load_usages_for_selected(self, icon_key):
        self.usage_tree.delete(*self.usage_tree.get_children())
        if not icon_key:
            return

        usages = self.icon_service.get_usages(icon_key)
        for u in usages:
            self.usage_tree.insert("", "end", values=(u.get("id"), u.get("module_name"), u.get("ui_component_type"), u.get("ui_element_id")))

    def _on_add_usage(self):
        icon_key = self.icon_form.get_form_data()['icon_key'].strip()
        if self._current_state == "ADD":
            messagebox.showwarning("Warning", "Vui lòng Lưu icon trước khi gắn usages.")
            return

        mod = self.var_usage_mod.get().strip()
        comp = self.var_usage_comp.get().strip()

        # Get raw string from entry and extract just the element_id
        selected_elem = self.var_usage_element.get().strip()
        elem = selected_elem.split("/")[-1] if selected_elem else ""

        if not elem:
            messagebox.showwarning("Warning", "Element ID cannot be empty. Vui lòng chọn một Nơi dùng.")
            return

        result = self.controller.add_usage(icon_key, mod, comp, elem)

        if result.success:
            self.var_usage_element.set("")
            self._load_usages_for_selected(icon_key)

            # Refresh available elements just in case it's a new db entry
            self._load_all_usage_ids()

            # Update main tree usages count
            if hasattr(self, 'tree_component'):
                self.after(100, self.tree_component.request_load_tree_data)

            from tkinter import messagebox
            messagebox.showinfo("Thành công", f"Đã gán Element ID '{elem}' cho icon '{icon_key}'.")
        else:
            messagebox.showerror("Lỗi", result.message)

    def _on_del_usage(self):
        selection = self.usage_tree.selection()
        if not selection:
            messagebox.showinfo("Info", "Vui lòng chọn 1 usage trong danh sách để gỡ.")
            return

        item = self.usage_tree.item(selection[0])
        usage_id = item["values"][0]
        elem_id = item["values"][3]

        if messagebox.askyesno("Xác nhận", f"Bạn có chắc muốn gỡ Element '{elem_id}' khỏi icon này?"):
            icon_key = self.icon_form.get_form_data()['icon_key'].strip()
            result = self.controller.delete_usage(icon_key, usage_id)
            if result.success:
                self._load_usages_for_selected(icon_key)

                # Update main tree usages count
                if hasattr(self, 'tree_component'):
                    self.after(100, self.tree_component.request_load_tree_data)
            else:
                messagebox.showerror("Error", result.message)

    def _get_used_filepaths(self):
        try:
            cursor = self.icon_service.conn.cursor()
            cursor.execute("""
                SELECT i.filepath, u.ui_component_type
                FROM icons i
                LEFT JOIN icon_usages u ON i.icon_key = u.icon_key
                WHERE i.filepath IS NOT NULL AND i.filepath != ''
            """)
            used_files = {}
            for filepath, comp_type in cursor.fetchall():
                if filepath not in used_files:
                    used_files[filepath] = set()
                if comp_type:
                    used_files[filepath].add(comp_type)
            return used_files
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"Failed to get used images: {e}")
            return {}

    def _check_image_sharing_restriction(self, selected_filepath: str, current_icon_key: str) -> bool:
        """
        Check if sharing the image is allowed based on sidebar_button constraints.
        Returns True if allowed, False if blocked.
        """
        if not selected_filepath or not current_icon_key:
            return True

        # Get usages of the current icon key
        current_usages = self.icon_service.get_usages(current_icon_key)
        is_current_sidebar = any(u.get('ui_component_type') == 'sidebar_button' for u in current_usages)

        # Get usages of the selected filepath by other icons
        existing_icons = self.icon_service.get_icons_by_filepath(selected_filepath)
        other_icons = [i for i in existing_icons if i.get("icon_key") != current_icon_key]

        is_other_sidebar = False
        for icon in other_icons:
            usages = self.icon_service.get_usages(icon.get('icon_key'))
            if any(u.get('ui_component_type') == 'sidebar_button' for u in usages):
                is_other_sidebar = True
                break

        if other_icons and (is_current_sidebar or is_other_sidebar):
            msg = self.i18n_t(
                "msg_sidebar_icon_sharing_blocked",
                default="Không thể dùng chung ảnh này vì một trong số các Icon đang sử dụng nó thuộc nhóm Sidebar (sidebar_button). Icon của Sidebar phải là duy nhất."
            )
            messagebox.showerror(self.i18n_t("error", default="Lỗi"), msg)
            return False

        return True

    def _handle_image_selected(self, selected_file, is_new_import=False):
        if self._current_state not in ("ADD", "EDIT"):
            return  # Only allow selection in edit mode

        if is_new_import:
            self._just_imported_file = selected_file

        current_icon_key = self.icon_form.get_form_data()['icon_key'].strip()

        if not self._check_image_sharing_restriction(selected_file, current_icon_key):
            # Revert selection in the library component
            if hasattr(self, 'image_library') and self.image_library:
                self.image_library.set_current_filepath(self.icon_form.get_form_data()['filepath'])
            return

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
                # Revert selection in the library component
                if hasattr(self, 'image_library') and self.image_library:
                    self.image_library.set_current_filepath(self.icon_form.get_form_data()['filepath'])
                return

        self.icon_form.var_filepath.set(selected_file)
        if hasattr(self, 'image_library') and self.image_library:
            self.image_library.set_current_filepath(selected_file)

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
            "fallback_emoji": self.icon_form.get_form_data()['fallback_emoji'],
            "filepath": selected_file,
            "tooltip_translation_key": self.icon_form.get_form_data()['tooltip_key']
        }
        self.content_state_frame.tkraise()
        self.preview_component.render(dummy_data)

    def _on_browse_clicked(self):
        from tkinter import filedialog, messagebox
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
                current_filename = self.icon_form.get_form_data()['filepath'].strip()

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
                            return  # Huỷ thao tác
                        overwrite = True
                    else:
                        # Trường hợp 1.1: File chưa tồn tại trong assets
                        msg = self.i18n_t(
                            "msg_file_outside_assets",
                            default="Ảnh đang nằm ngoài thư mục assets. Bạn có muốn copy ảnh vào assets không?"
                        )
                        if not messagebox.askyesno(self.i18n_t("warning", default="Cảnh báo"), msg):
                            return  # Huỷ thao tác

                    # Tiến hành copy/replace vào assets
                    final_filename = import_icon_file(file_path, overwrite=overwrite)
                else:
                    # Luồng 2: Ảnh trong assets
                    # Trường hợp 2.1: Chọn lại đúng file đang sử dụng
                    if final_filename == current_filename:
                        return  # Không làm gì cả
                    # Trường hợp 2.2: Chọn file khác, không cần hỏi copy

                # 3. Kiểm tra sử dụng chung ảnh (Duplication Check)
                current_icon_key = self.icon_form.get_form_data()['icon_key'].strip()

                if not self._check_image_sharing_restriction(final_filename, current_icon_key):
                    return # Huỷ thao tác

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
                        return  # Huỷ thao tác

                # Update filepath entry
                self.icon_form.var_filepath.set(final_filename)

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

        if hasattr(self, 'icon_form'):
            if state == "VIEW":
                self.icon_form.enter_view_mode()
            elif state == "ADD":
                self.icon_form.enter_add_mode()
            elif state == "EDIT":
                self.icon_form.enter_edit_mode()

        # Handle usages panel state
        if hasattr(self, 'usage_tree'):
            btn_state = "normal" if state == "EDIT" else "disabled"
            # Cannot map to new unsaved icon
            self.btn_add_usage.config(state=btn_state)
            self.btn_del_usage.config(state=btn_state)

        # Handle Image Library state
        if hasattr(self, 'image_library') and self.image_library:
            self.image_library.set_state(state)

        # Handle buttons
        if state == "VIEW":
            self.btn_add.config(state="normal")

            # Edit/Delete depends on selection
            has_selection = False
            if hasattr(self, 'tree_component') and self.tree_component.tree.selection():
                item_id = self.tree_component.tree.selection()[0]
                if item_id.startswith("icon_"):
                    has_selection = True

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

    def _on_add(self):
        import time

        # Xác định category hiện tại đang chọn
        selected_cat = "General"
        if hasattr(self, 'tree_component'):
            selection = self.tree_component.tree.selection()
            if selection:
                item_id = selection[0]
                if item_id.startswith("cat_"):
                    selected_cat = item_id.replace("cat_", "", 1)
                else:
                    parent_id = self.tree_component.tree.parent(item_id)
                    if parent_id and parent_id.startswith("cat_"):
                        selected_cat = parent_id.replace("cat_", "", 1)

        # When creating a new icon node, we need to map the name to ID for the tree
        # but display the name in the combobox.

        # If selected_cat is an ID, find its name for the combobox
        selected_cat_name = selected_cat
        if hasattr(self, 'categories_id_map') and str(selected_cat).isdigit():
            selected_cat_name = self.categories_id_map.get(int(selected_cat), selected_cat)

        # Set variables using the string name
        self.icon_form.set_form_data({
            "icon_key": "",
            "name": "New Icon",
            "category": selected_cat_name,
            "fallback_emoji": "❓",
            "tooltip_key": "",
            "filepath": ""
        })

        # Create dummy node in Treeview for visual feedback
        dummy_id = f"new_icon_{int(time.time())}"
        cat_node = f"cat_{selected_cat}"

        if hasattr(self, 'tree_component'):
            # Đảm bảo category node tồn tại và mở ra
            if not self.tree_component.tree.exists(cat_node):
                self.tree_component.tree.insert("", "end", iid=cat_node, text=selected_cat, open=True)
            else:
                self.tree_component.tree.item(cat_node, open=True)

            # Insert temp dummy icon item
            self.tree_component.tree.insert(cat_node, "end", iid=dummy_id, text="  [New] New Icon", values=(selected_cat, "🟡"))

            # Select and focus on the dummy item
            self.tree_component.tree.selection_set(dummy_id)
            self.tree_component.tree.see(dummy_id)

        self.set_form_state("ADD")
        self.icon_form.entry_name.focus_set()

        self.content_state_frame.tkraise()
        self.preview_component.render({
            "icon_key": dummy_id,
            "fallback_emoji": "❓"
        })
        self.set_form_state("ADD")

        # Focus vào entry name
        self.icon_form.entry_name.focus_set()

    def _on_edit(self):
        self.set_form_state("EDIT")
        # Automatically switch to the details tab when editing
        if hasattr(self, 'notebook') and hasattr(self, 'tab_details'):
            self.notebook.select(self.tab_details)
        # Start typing/editing will set it dirty, but explicitly marking it is safer if they just click browse
        self._is_dirty = True

    def _on_delete(self):
        icon_key = self.icon_form.get_form_data()['icon_key']
        if not icon_key:
            return

        from tkinter import messagebox

        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete the icon '{icon_key}'?",
            icon='warning'
        )

        if confirm:
            result = self.controller.delete_icon(icon_key)
            if result.success:
                # Clear form
                self.icon_form.set_form_data({})
                self.content_state_frame.tkraise()
                self.preview_component.render({})

                # Reload tree
                self.tree_component.request_load_tree_data()
                self.set_form_state("VIEW")
                if hasattr(self, 'tree_component'):
                    self.tree_component.tree.focus_set()
            else:
                if result.data == "in_use":
                    messagebox.showwarning(self.i18n_t("warning", default="Cảnh báo"), result.message)
                else:
                    messagebox.showerror("Error", result.message)

    def apply_filters(self):
        if hasattr(self, 'tree_component') and hasattr(self.tree_component, 'apply_filters'):
            self.tree_component.apply_filters()

    def _on_refresh(self):
        # 1. Clear search and selection in left tree
        if hasattr(self, 'tree_component'):
            self.tree_component.search_var.set("")
            if self.tree_component.tree.selection():
                self.tree_component.tree.selection_remove(*self.tree_component.tree.selection())
            self.tree_component.tree.focus('')
            self.tree_component.apply_filters()

        # 2. Clear search and selection in available elements tree
        if hasattr(self, 'var_element_search'):
            self.var_element_search.set("")
            self._apply_element_filter(force=True)
        if hasattr(self, 'available_elements_tree'):
            self._current_available_element_selection = None
            if self.available_elements_tree.selection():
                self.available_elements_tree.selection_remove(*self.available_elements_tree.selection())
            self.available_elements_tree.focus('')

        # 3. Reset state variables
        self._last_selected_item_id = None
        if hasattr(self, 'var_current_mapping_icon'):
            self.var_current_mapping_icon.set("Đang chọn Icon: (Chưa chọn)")
        if hasattr(self, 'var_usage_element'):
            self.var_usage_element.set("")
        if hasattr(self, 'var_usage_mod'):
            self.var_usage_mod.set("")
        if hasattr(self, 'var_usage_comp'):
            self.var_usage_comp.set("")

        # 4. Clear form and usage tree, ensure detail form is visible
        if hasattr(self, 'icon_form'):
            self.icon_form.set_form_data({})
        if hasattr(self, 'usage_tree'):
            self.usage_tree.delete(*self.usage_tree.get_children())
        if hasattr(self, 'preview_component'):
            self.preview_component.render({})
        if hasattr(self, 'image_library') and self.image_library:
            self.image_library.set_current_filepath("")
            self.image_library.clear_selection()

        self.set_form_state("VIEW")

        # In VIEW state, the Edit/Delete buttons are updated based on tree selection.
        # Since we just cleared the tree selection, explicitly update button states to disabled.
        if hasattr(self, 'btn_edit'):
            self.btn_edit.config(state="disabled")
        if hasattr(self, 'btn_delete'):
            self.btn_delete.config(state="disabled")

    def _on_sync(self, show_message=True):
        if self.btn_sync['state'] == 'disabled':
            return

        self.btn_sync.config(state='disabled', text=self.i18n_t("btn_syncing", default="Đang đồng bộ..."))

        def on_complete(count):
            if not self.winfo_exists():
                return
            try:
                self.after(0, lambda: self._on_sync_complete(count, show_message))
            except RuntimeError:
                pass

        def on_error(err_msg):
            if not self.winfo_exists():
                return
            try:
                self.after(0, lambda: self._on_sync_error(err_msg, show_message))
            except RuntimeError:
                pass

        self.controller.sync_system_icons_async(on_complete, on_error)

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
            self.tree_model.load_base_data_async(lambda: self._safe_after(0, self.tree_component.request_load_tree_data))
        else:
            self.tree_component.request_load_tree_data()

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
        form_data = self.icon_form.get_form_data()
        icon_key = form_data.get('icon_key', '').strip()

        # Save previous filepath to check for rollback if db insert fails
        icon_data_old = self.tree_model.get_icon(icon_key)
        old_filepath = icon_data_old.get('filepath') if icon_data_old else None

        just_imported_file = getattr(self, '_just_imported_file', None)

        # Cập nhật categories_map mới nhất cho controller trước khi save
        if hasattr(self, 'categories_map'):
            self.controller.update_categories_map(self.categories_map)

        result = self.controller.save_icon(form_data, old_filepath, just_imported_file)

        from tkinter import messagebox
        if not result.success:
            messagebox.showerror("Lỗi", result.message)
            if hasattr(self, 'image_library') and self.image_library:
                self.image_library.reload()  # refresh list if there was a rollback
            return

        # Nếu đang ở trạng thái ADD, xóa dòng dummy khỏi tree trước khi reload
        if self._current_state == "ADD":
            if hasattr(self, 'tree_component'):
                selection = self.tree_component.tree.selection()
                if selection:
                    item_id = selection[0]
                    if item_id.startswith("new_icon_"):
                        self.tree_component.tree.delete(item_id)

        # Xoá flag dirty
        self._is_dirty = False

        # Reload dữ liệu
        self.tree_component.request_load_tree_data()

        # Update local form tooltips
        t_key = form_data.get('tooltip_key', '').strip()
        if t_key and hasattr(self, 'icon_form'):
            self.icon_form.add_tooltip_key_if_missing(t_key)

        # Mở lại thư mục vừa thêm vào
        cat_node_id = f"cat_{result.category_id}"
        if hasattr(self, 'tree_component'):
            if self.tree_component.tree.exists(cat_node_id):
                self.tree_component.tree.item(cat_node_id, open=True)

            # Re-select the saved item để refresh Preview từ dữ liệu thực tế
            node_id = f"icon_{icon_key}"
            if self.tree_component.tree.exists(node_id):
                 self.tree_component.tree.selection_set(node_id)
                 self.tree_component.tree.see(node_id)

        self.set_form_state("VIEW")
        if hasattr(self, 'tree_component'):
            self.tree_component.tree.focus_set()

        # 4. Thông báo thành công
        messagebox.showinfo("Thành công", f"Đã lưu thành công icon {icon_key}.")

    def _on_cancel(self):
        # Dọn dẹp dòng dummy nếu đang ở trạng thái ADD
        if self._current_state == "ADD":
            if hasattr(self, 'tree_component'):
                selection = self.tree_component.tree.selection()
                if selection:
                    item_id = selection[0]
                    if item_id.startswith("new_icon_"):
                        self.tree_component.tree.delete(item_id)

        self._is_dirty = False
        if hasattr(self, 'tree_component'):
            self.tree_component._process_tree_selection()
        self.set_form_state("VIEW")
        if hasattr(self, 'tree_component'):
            self.tree_component.tree.focus_set()

    def _check_and_auto_sync(self):
        # Auto-sync icons if the database is empty
        conn = sqlite3.connect(str(self.db.DB_PATH))
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM icons")
        count = cursor.fetchone()[0]
        conn.close()
        if count == 0:
            self._on_sync(show_message=False)


    def _initial_load(self):
        self._load_all_usage_ids()
        if hasattr(self, "tree_component") and hasattr(self.tree_component, "tree"):
            self.tree_component.tree.delete(*self.tree_component.tree.get_children())
            self.tree_component.tree.insert("", "end", iid="loading", text="Loading data...")
        self.tree_model.load_base_data_async(self._on_data_loaded)

    def _on_data_loaded(self):
        try:
            if not self.winfo_exists():
                return
            # Update combo boxes based on categories
            self.after(0, self._populate_category_combo)
            self.after(0, self.tree_component.request_load_tree_data)
        except RuntimeError:
            pass  # main thread not in main loop during early exit

    def _populate_category_combo(self):
        if not hasattr(self, "tree_model"):
            return
        categories = list(self.tree_model.category_cache.values())
        categories.sort(key=lambda x: x.get("name", "").lower())

        self.categories_map = {c["name"]: c["id"] for c in categories}
        cat_names = ["All"] + [c["name"] for c in categories]

        if hasattr(self, "tree_component"):
            self.tree_component.set_categories(categories, self.categories_map)

        if hasattr(self, "combo_category") and self.combo_category:
            self.combo_category.config(values=[c["name"] for c in categories])

        if hasattr(self, 'icon_form'):
            c_names = [c['name'] for c in categories]
            self.icon_form.update_category_values(c_names)

    def _on_tree_interaction(self, event):
        if self._current_state in ("ADD", "EDIT"):
            from tkinter import messagebox
            msg = self.i18n_t("msg_unsaved_changes_lock", default="Vui lòng nhấn Lưu hoặc Hủy trước khi chọn dòng khác.")
            messagebox.showwarning(self.i18n_t("warning", default="Cảnh báo"), msg)
            return "break"

    def _process_tree_selection_callback(self, icon_key):
        if self._is_refreshing_tree or self._suppress_tree_events:
            return

        if not icon_key:
            return

        self._last_selected_item_id = f"icon_{icon_key}"

        if hasattr(self, 'var_current_mapping_icon'):
            self.var_current_mapping_icon.set(f"Đang chọn Icon: {icon_key}")

        # Ensure Edit button is re-enabled when an icon is selected
        if hasattr(self, 'btn_edit'):
            self.btn_edit.config(state="normal")

        icon_data = self.tree_model.get_icon(icon_key)
        if icon_data:
            # Map category_id back to name
            cat_id = icon_data.get("category_id")
            cat_data = self.tree_model.get_category(cat_id) if cat_id else None
            cat_name = cat_data.get("name", "General") if cat_data else "General"
            filepath = icon_data.get('filepath') or ''

            self.icon_form.set_form_data({
                "name": icon_data.get('name') or '',
                "icon_key": icon_data.get('icon_key') or '',
                "category": cat_name,
                "fallback_emoji": icon_data.get('fallback_emoji') or '',
                "tooltip_key": icon_data.get('tooltip_translation_key') or '',
                "filepath": filepath
            })

            if hasattr(self, 'image_library') and self.image_library:
                self.image_library.set_current_filepath(filepath)

            self.content_state_frame.tkraise()
            self.preview_component.render(icon_data)
            if hasattr(self, 'usage_tree'):
                self._load_usages_for_selected(icon_key)
            self._sync_available_elements_selection(icon_key)
        else:
            self.empty_state_frame.tkraise()

        self.set_form_state("VIEW")

