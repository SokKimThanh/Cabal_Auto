import re

with open('ui/views/icon_manager_frame.py', 'r') as f:
    content = f.read()

import_str = """import tkinter as tk
from tkinter import ttk"""

content = content.replace("import tkinter as tk", import_str)

setup_ui_search = """        # 1. Top Filter Bar
        self.top_filter_frame = tk.Frame(content_frame, bg=UIStyle.BG_SUBTLE, height=60)
        self.top_filter_frame.grid(row=0, column=0, sticky="ew")
        self.top_filter_frame.grid_propagate(False)  # For visualizing

        tk.Label(self.top_filter_frame, text="Top Filter Bar Area", bg=UIStyle.BG_SUBTLE, fg=UIStyle.TEXT_PRIMARY).pack(pady=20)"""


setup_ui_replace = """        # 1. Top Filter Bar
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
        self.category_combo.bind("<<ComboboxSelected>>", lambda e: self.apply_filters())"""

content = content.replace(setup_ui_search, setup_ui_replace)

methods_str = """
    def _on_search_key_release(self, event):
        # Cancel any previous timer
        if hasattr(self, '_search_after_id') and self._search_after_id:
            self.after_cancel(self._search_after_id)
        # Set new timer for debounce (500ms)
        self._search_after_id = self.after(500, self.apply_filters)

    def apply_filters(self):
        pass"""

content = content + methods_str

with open('ui/views/icon_manager_frame.py', 'w') as f:
    f.write(content)
