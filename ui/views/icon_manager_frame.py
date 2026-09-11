import tkinter as tk
from tkinter import ttk

from ui.components.base.responsive_grid_base import ResponsiveGridBase
from lib.ui_style_v2 import UIStyleV2 as UIStyle
from lib.db.services.icon_service import IconService
from ui.helpers.icon_helper import get_icon_helper
from database import get_db


class IconManagerFrame(ResponsiveGridBase):
    def __init__(self, parent, app=None, *args, **kwargs):
        super().__init__(parent, app=app, bg=UIStyle.BG_BASE, *args, **kwargs)
        self.app = app
        self.db = get_db()
        self.icon_service = IconService(self.db.conn)
        self.icon_helper = get_icon_helper()

        self._setup_ui()
        self.load_tree_data()

    def _setup_ui(self):
        content_frame = self.get_content_frame()
        # Row 0: Top Filter Bar
        # Row 1: Vùng Content chính
        # Row 2: Bottom Bar
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

        tk.Label(search_frame, text="Search:", bg=UIStyle.BG_SUBTLE, fg=UIStyle.TEXT_PRIMARY).pack(side="left")
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(5, 0))
        self.search_entry.bind("<KeyRelease>", self._on_search_key_release)

        # 1.2 Status Filter
        self.status_var = tk.StringVar(value="All")
        status_frame = tk.Frame(self.top_filter_frame, bg=UIStyle.BG_SUBTLE)
        status_frame.grid(row=0, column=1, sticky="w", padx=5, pady=15)

        tk.Label(status_frame, text="Status:", bg=UIStyle.BG_SUBTLE, fg=UIStyle.TEXT_PRIMARY).pack(side="left")
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

        tk.Label(category_frame, text="Category:", bg=UIStyle.BG_SUBTLE, fg=UIStyle.TEXT_PRIMARY).pack(side="left")
        self.category_combo = ttk.Combobox(
            category_frame,
            textvariable=self.category_var,
            state="readonly",
            width=15
        )
        self.category_combo.pack(side="left", padx=(5, 0))
        self.category_combo.bind("<<ComboboxSelected>>", lambda e: self.apply_filters())

        # 2. Main Content (Left - Right split)
        self.main_content_frame = tk.Frame(content_frame, bg=UIStyle.BG_BASE)
        self.main_content_frame.grid(row=1, column=0, sticky="nsew", pady=UIStyle.SPACE_MD)

        # Configure columns for split
        self.main_content_frame.grid_rowconfigure(0, weight=1)
        self.main_content_frame.grid_columnconfigure(0, weight=0, minsize=250)  # Left Sidebar (Master List)
        self.main_content_frame.grid_columnconfigure(1, weight=1)              # Right Detail Zone

        # Left Master List Frame
        self.left_master_frame = tk.Frame(self.main_content_frame, bg=UIStyle.BG_ELEVATED)
        self.left_master_frame.grid(row=0, column=0, sticky="nsew", padx=(0, UIStyle.SPACE_SM))

        # Configure grid for treeview and scrollbar
        self.left_master_frame.grid_rowconfigure(0, weight=1)
        self.left_master_frame.grid_columnconfigure(0, weight=1)
        self.left_master_frame.grid_columnconfigure(1, weight=0)

        # Create Treeview
        columns = ("col_id", "col_key", "col_status")
        self.tree = ttk.Treeview(
            self.left_master_frame,
            columns=columns,
            show="tree headings",
            selectmode="browse"
        )

        # Define headings
        self.tree.heading("#0", text="Tên / Danh mục", anchor="w")
        self.tree.heading("col_id", text="ID", anchor="w")
        self.tree.heading("col_key", text="Icon Key", anchor="w")
        self.tree.heading("col_status", text="Trạng Thái", anchor="center")

        # Define columns
        self.tree.column("#0", width=150, minwidth=100, stretch=tk.YES)
        self.tree.column("col_id", width=50, minwidth=50, stretch=tk.NO)
        self.tree.column("col_key", width=150, minwidth=100, stretch=tk.YES)
        self.tree.column("col_status", width=80, minwidth=80, stretch=tk.NO, anchor="center")

        # Scrollbar
        self.tree_scroll_y = ttk.Scrollbar(self.left_master_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.tree_scroll_y.set)

        # Auto-hiding scrollbar implementation
        self.tree.grid(row=0, column=0, sticky="nsew")
        # Scrollbar will be managed dynamically but we set it up here
        self.tree_scroll_y.grid(row=0, column=1, sticky="ns")

        # Bind events
        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)
        # Bind configure to handle auto-hiding scrollbar
        self.tree.bind("<Configure>", self._check_scrollbar)

        # Right Detail Frame
        self.right_detail_frame = tk.Frame(self.main_content_frame, bg=UIStyle.BG_SURFACE)
        self.right_detail_frame.grid(row=0, column=1, sticky="nsew", padx=(UIStyle.SPACE_SM, 0))
        tk.Label(self.right_detail_frame, text="Detail & Form Area", bg=UIStyle.BG_SURFACE, fg=UIStyle.TEXT_PRIMARY).pack(expand=True)

        # 3. Bottom Action Bar
        self.bottom_action_frame = tk.Frame(content_frame, bg=UIStyle.BG_SUBTLE, height=60)
        self.bottom_action_frame.grid(row=2, column=0, sticky="ew")
        self.bottom_action_frame.grid_propagate(False)
        tk.Label(self.bottom_action_frame, text="Bottom Action Bar Area", bg=UIStyle.BG_SUBTLE, fg=UIStyle.TEXT_PRIMARY).pack(pady=20)

    def _on_search_key_release(self, event):
        # Cancel any previous timer
        if hasattr(self, '_search_after_id') and self._search_after_id:
            self.after_cancel(self._search_after_id)
        # Set new timer for debounce (500ms)
        self._search_after_id = self.after(500, self.apply_filters)

    def apply_filters(self):
        self.load_tree_data()

    def load_tree_data(self):
        # Clear current tree
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Get filter values
        search_term = self.search_var.get().strip().lower()
        selected_category = self.category_var.get()
        if selected_category == "All":
            selected_category = ""

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
        all_icons = self.icon_service.get_all_icons(search_term=search_term, category=selected_category)

        # Populate Category dropdown dynamically if it's the first time
        if not hasattr(self, '_categories_loaded') or not self._categories_loaded:
            # We fetch all without filters just to get unique categories
            all_raw = self.icon_service.get_all_icons()
            categories = set(icon.get("category", "General") for icon in all_raw if icon.get("category"))
            sorted_cats = ["All"] + sorted(list(categories))
            self.category_combo['values'] = sorted_cats
            self._categories_loaded = True

        # Group by category and filter by status
        grouped_data = {}
        for icon in all_icons:
            # Check status logic
            status = self.icon_helper.evaluate_icon_status(icon)

            # Apply status filter in Python
            if status_filter and status != status_filter:
                continue

            cat = icon.get("category", "General")
            if cat not in grouped_data:
                grouped_data[cat] = []
            grouped_data[cat].append((icon, status))

        # Render Treeview
        for cat_name, items in sorted(grouped_data.items()):
            # Insert Category Node
            cat_id = f"cat_{cat_name}"
            self.tree.insert('', 'end', iid=cat_id, text=f"📁 {cat_name}", open=True)

            for icon, status in sorted(items, key=lambda x: x[0].get("name", "").lower()):
                icon_id = icon.get("id")
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
                    values=(icon_id, icon_key, status_color)
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
        selection = self.tree.selection()
        if not selection:
            return

        item_id = selection[0]
        # Ignore category clicks (folders)
        if item_id.startswith('cat_'):
            return

        # Handle icon selection...
        pass
