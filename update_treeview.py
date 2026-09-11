import re

with open('ui/views/icon_manager_frame.py', 'r') as f:
    content = f.read()

setup_ui_search = """        # Left Master List Frame
        self.left_master_frame = tk.Frame(self.main_content_frame, bg=UIStyle.BG_ELEVATED)
        self.left_master_frame.grid(row=0, column=0, sticky="nsew", padx=(0, UIStyle.SPACE_SM))
        tk.Label(self.left_master_frame, text="Master List Area", bg=UIStyle.BG_ELEVATED, fg=UIStyle.TEXT_PRIMARY).pack(expand=True)"""

setup_ui_replace = """        # Left Master List Frame
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
        self.tree.bind("<Configure>", self._check_scrollbar)"""

content = content.replace(setup_ui_search, setup_ui_replace)

methods_str = """
    def _check_scrollbar(self, event=None):
        \"\"\"Auto-hide scrollbar when not needed\"\"\"
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
"""

content = content + methods_str

with open('ui/views/icon_manager_frame.py', 'w') as f:
    f.write(content)
