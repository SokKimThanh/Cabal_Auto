import tkinter as tk
from tkinter import ttk, messagebox
from lib.ui_style_v2 import UIStyleV2 as UIStyle
from ui.helpers.tooltip import attach_i18n_tooltip

class IconTreeComponent(tk.Frame):
    def __init__(self, parent, app, tree_model, categories_map, on_node_selected_callback, on_interaction_callback, *args, **kwargs):
        super().__init__(parent, bg=UIStyle.BG_BASE, *args, **kwargs)
        self.app = app
        self.tree_model = tree_model
        self.categories_map = categories_map
        self.on_node_selected = on_node_selected_callback
        self.on_interaction = on_interaction_callback

        self.search_var = tk.StringVar()
        self.status_var = tk.StringVar(value="All")
        self.category_var = tk.StringVar(value="All")

        self._is_refreshing_tree = False
        self._suppress_tree_events = False
        self._render_queue = []
        self._render_after_id = None
        self._search_after_id = None
        self._debounce_after_id = None
        self._select_after_id = None

        self._setup_ui()

    def i18n_t(self, key: str, **kwargs) -> str:
        if hasattr(self.app, '_t'):
            return self.app._t(key, **kwargs)
        from lib.i18n import t as fallback_t
        lang = getattr(self.app, 'lang', 'vi')
        t_kwargs = {"lang": lang}
        if "default" in kwargs:
            t_kwargs["default"] = kwargs.pop("default")
        if "ns" in kwargs:
            t_kwargs["ns"] = kwargs.pop("ns")
        translated = fallback_t(key, **t_kwargs)
        if kwargs:
            try:
                translated = translated.format(**kwargs)
            except Exception:
                pass
        return translated

    def _prevent_scroll_propagation(self, event):
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
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # 1. Top Filter Bar
        self.top_filter_frame = tk.Frame(self, bg=UIStyle.BG_SUBTLE, height=60)
        self.top_filter_frame.grid(row=0, column=0, sticky="ew")
        self.top_filter_frame.grid_columnconfigure(0, weight=1)
        self.top_filter_frame.grid_columnconfigure(1, weight=0)
        self.top_filter_frame.grid_columnconfigure(2, weight=0)

        # 1.1 Search Box
        search_frame = tk.Frame(self.top_filter_frame, bg=UIStyle.BG_SUBTLE)
        search_frame.grid(row=0, column=0, sticky="ew", padx=(10, 5), pady=15)
        tk.Label(search_frame, text=self.i18n_t("lbl_search", default="Search:"), bg=UIStyle.BG_SUBTLE, fg=UIStyle.TEXT_PRIMARY).pack(side="left")
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(5, 0))
        self.search_var.trace_add("write", self.trigger_filter)
        self.search_entry.bind("<KeyRelease>", self._on_search_key_release)

        # 1.2 Status Filter
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

        # 2. Main Content
        self.left_master_frame = tk.Frame(self, bg=UIStyle.BG_ELEVATED)
        self.left_master_frame.grid(row=1, column=0, sticky="nsew")
        self.left_master_frame.grid_rowconfigure(0, weight=0)
        self.left_master_frame.grid_rowconfigure(1, weight=1)
        self.left_master_frame.grid_columnconfigure(0, weight=1)
        self.left_master_frame.grid_columnconfigure(1, weight=0)

        # Toolbar
        self.tree_toolbar = tk.Frame(self.left_master_frame, bg=UIStyle.BG_ELEVATED)
        self.tree_toolbar.grid(row=0, column=0, columnspan=2, sticky="ew", padx=2, pady=2)

        btn_style = UIStyle.get_button_style("secondary") if hasattr(UIStyle, "get_button_style") else {}
        self.btn_collapse_all = tk.Button(
            self.tree_toolbar,
            text=self.i18n_t("btn_collapse_all", default="Thu gọn tất cả"),
            command=self._on_collapse_all,
            **btn_style
        )
        self.btn_collapse_all.pack(side="right", padx=5)

        self.btn_expand_all = tk.Button(
            self.tree_toolbar,
            text=self.i18n_t("btn_expand_all", default="Mở rộng tất cả"),
            command=self._on_expand_all,
            **btn_style
        )
        self.btn_expand_all.pack(side="right", padx=5)

        # Treeview
        style = ttk.Style()
        style.configure("IconManager.Treeview", rowheight=28)

        columns = ("col_key", "col_status")
        self.tree = ttk.Treeview(
            self.left_master_frame,
            columns=columns,
            show="tree headings",
            selectmode="browse",
            style="IconManager.Treeview"
        )
        self.tree.heading("#0", text=self.i18n_t("col_name_category", default="Tên / Danh mục"), anchor="w")
        self.tree.heading("col_key", text="Icon Key", anchor="w")
        self.tree.heading("col_status", text=self.i18n_t("col_status", default="Trạng Thái"), anchor="center")
        self.tree.column("#0", width=150, minwidth=100, stretch=tk.YES)
        self.tree.column("col_key", width=180, minwidth=100, stretch=tk.YES)
        self.tree.column("col_status", width=95, minwidth=95, stretch=tk.NO, anchor="center")

        self.tree_scroll_y = ttk.Scrollbar(self.left_master_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.tree_scroll_y.set)

        self.tree.bind('<MouseWheel>', self._prevent_scroll_propagation)
        self.tree.bind('<Button-4>', self._prevent_scroll_propagation)
        self.tree.bind('<Button-5>', self._prevent_scroll_propagation)

        self.tree.grid(row=1, column=0, sticky="nsew")
        self.tree_scroll_y.grid(row=1, column=1, sticky="ns")

        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)
        self.tree.bind("<<TreeviewOpen>>", self._on_tree_open)

        self.tree.bind("<Button-1>", self._on_tree_interaction)
        self.tree.bind("<Up>", self._on_tree_interaction)
        self.tree.bind("<Down>", self._on_tree_interaction)

    def set_categories(self, categories, categories_map):
        self.categories_map = categories_map
        cat_names = ["All"]
        if categories:
            cat_names.extend([cat['name'] for cat in categories if cat.get('name')])
        if self.category_combo:
            self.category_combo.configure(values=cat_names)

    def trigger_filter(self, *args):
        if self._search_after_id:
            self.after_cancel(self._search_after_id)
        self._search_after_id = self.after(300, self.apply_filters)

    def apply_filters(self):
        self.load_tree_data()

    def _on_search_key_release(self, event):
        if event.keysym in ('Return', 'KP_Enter'):
            self.apply_filters()

    def _on_collapse_all(self):
        for item in self.tree.get_children(''):
            self.tree.item(item, open=False)

    def _on_expand_all(self):
        for item in self.tree.get_children(''):
            self.tree.item(item, open=True)
            for child in self.tree.get_children(item):
                self.tree.item(child, open=True)

    def _on_tree_interaction(self, event):
        if self.on_interaction:
            return self.on_interaction(event)

    def _on_tree_select(self, event):
        if self._select_after_id:
            self.after_cancel(self._select_after_id)
        self._select_after_id = self.after(50, self._process_tree_selection)

    def _process_tree_selection(self):
        if self._is_refreshing_tree or self._suppress_tree_events:
            return

        selection = self.tree.selection()
        if not selection:
            return

        item_id = selection[0]
        if item_id.startswith('cat_') or item_id.startswith('usage_') or item_id.startswith("new_icon_"):
            return

        values = self.tree.item(item_id, 'values')
        icon_key = values[0] if values else item_id

        if self.on_node_selected:
            self.on_node_selected(icon_key)

    def _safe_after(self, delay, callback):
        def wrapper():
            if self.winfo_exists():
                callback()
        return self.after(delay, wrapper)

    def _on_tree_open(self, event):
        item_id = self.tree.focus()
        if not item_id or not item_id.startswith("icon_"):
            return

        icon_key = item_id.replace("icon_", "")
        children = self.tree.get_children(item_id)

        if children and not children[0].startswith("loading_") and not children[0].startswith("dummy_"):
            return

        for child in children:
            if child.startswith("loading_") or child.startswith("dummy_"):
                self.tree.delete(child)

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

        for child in self.tree.get_children(node_id):
            if child.startswith("loading_"):
                self.tree.delete(child)

        current_text = self.tree.item(node_id, "text")
        if " (Usages: " not in current_text:
             self.tree.item(node_id, text=f"{current_text} (Usages: {len(usages)})")
        else:
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

    def request_load_tree_data(self):
        if self._debounce_after_id:
            self.after_cancel(self._debounce_after_id)
        self._debounce_after_id = self.after(300, self.load_tree_data)

    def load_tree_data(self):
        if not hasattr(self, 'tree_model') or not getattr(self.tree_model, 'loaded', False):
            return

        self._is_refreshing_tree = True

        expanded_nodes = []
        for item in self.tree.get_children(''):
            if self.tree.item(item, "open"):
                expanded_nodes.append(item)
            for child in self.tree.get_children(item):
                if self.tree.item(child, "open"):
                    expanded_nodes.append(child)

        selected_nodes = self.tree.selection()

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

        if hasattr(self.tree_model, 'set_filters'):
             self.tree_model.set_filters(search=search_term, category_id=selected_category_id, status=status_filter)

        filtered_data = {}
        if hasattr(self.tree_model, 'get_filtered_tree_data'):
             filtered_data = self.tree_model.get_filtered_tree_data()

        self._render_queue = []
        for cat_id, icons in filtered_data.items():
            cat = self.tree_model.get_category(cat_id) if hasattr(self.tree_model, 'get_category') else None
            cat_name = cat.get('name', 'Unknown') if cat else 'General'
            node_iid = f"cat_{cat_id}"

            self._render_queue.append(
                ('category', '', node_iid, f"📁 {cat_name}", ("category",), True)
            )

            icons.sort(key=lambda x: x.get('name', '').lower())

            for idx, icon in enumerate(icons):
                icon_key = icon.get('icon_key')
                icon_name = icon.get('name', '')
                status = self.tree_model.status_cache.get(icon_key, '⚪') if hasattr(self.tree_model, 'status_cache') else '⚪'
                usage_count = self.tree_model.dependency_cache.get(icon_key, 0) if hasattr(self.tree_model, 'dependency_cache') else 0

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

            existing_cats = {item for item in self.tree.get_children('') if item.startswith("cat_")}
            for cat_id in existing_cats:
                 if cat_id in self._desired_icons:
                      existing_icons = {item for item in self.tree.get_children(cat_id) if item.startswith("icon_")}
                      for old_icon in existing_icons - self._desired_icons[cat_id]:
                           self.tree.delete(old_icon)

            for old_cat in existing_cats - self._desired_cats:
                self.tree.delete(old_cat)

            self._is_refreshing_tree = False

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
                     continue

                 if not self.tree.exists(icon_iid):
                     self.tree.insert(node_iid, idx, iid=icon_iid, text=text, values=values)
                     if usage_count > 0:
                         self.tree.insert(icon_iid, 'end', iid=f"dummy_{values[0]}", text="dummy")
                 else:
                     self.tree.item(icon_iid, text=text, values=values)
                     current_idx = self.tree.index(icon_iid)
                     if current_idx != idx:
                         self.tree.move(icon_iid, node_iid, idx)

                     if usage_count > 0 and not self.tree.get_children(icon_iid):
                         self.tree.insert(icon_iid, 'end', iid=f"dummy_{values[0]}", text="dummy")

        self._render_after_id = self.after(5, lambda: self._process_incremental_queue(expanded_nodes, selected_nodes))

    def _check_scrollbar(self, event=None):
        if not hasattr(self, 'tree') or not hasattr(self, 'tree_scroll_y'):
            return
        try:
            yview = self.tree.yview()
            if yview[0] == 0.0 and yview[1] == 1.0:
                self.tree_scroll_y.grid_remove()
            else:
                self.tree_scroll_y.grid()
        except Exception:
            pass
