import tkinter as tk
from tkinter import ttk
from tkinter import ttk

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

        self._setup_ui()
        self.load_tree_data()

    def i18n_t(self, key: str, **kwargs) -> str:
        """Helper to get translations dynamically based on current app language"""
        if hasattr(self.app, 'i18n_t'):
            return self.app.i18n_t(key, **kwargs)

        # Fallback to direct import if app doesn't have it
        from lib.i18n import t as fallback_t
        lang = getattr(self.app, 'lang', 'vi')
        return fallback_t(key, lang=lang, **kwargs)

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

        self.right_detail_frame.grid_rowconfigure(0, weight=1)  # Preview
        self.right_detail_frame.grid_rowconfigure(1, weight=1)  # Form
        self.right_detail_frame.grid_columnconfigure(0, weight=1)

        self._build_preview_zone()
        self._build_detail_form()

        # 3. Bottom Action Bar
        self.bottom_action_frame = tk.Frame(content_frame, bg=UIStyle.BG_SUBTLE, height=60)
        self.bottom_action_frame.grid(row=2, column=0, sticky="ew")
        self.bottom_action_frame.grid_propagate(False)

        # Build Action Buttons
        self._build_action_bar()

    def _build_preview_zone(self):
        self.preview_frame = tk.Frame(self.right_detail_frame, bg=UIStyle.BG_SURFACE)
        self.preview_frame.grid(row=0, column=0, sticky="nsew", pady=(0, UIStyle.SPACE_SM))
        self.preview_frame.grid_rowconfigure(0, weight=1)
        self.preview_frame.grid_columnconfigure(0, weight=1)

        self.lbl_preview = tk.Label(
            self.preview_frame,
            bg=UIStyle.BG_ELEVATED,
            text="No Icon Selected",
            font=UIStyle.get_font("body"),
            width=20,
            height=5,
            relief="groove"
        )
        self.lbl_preview.grid(row=0, column=0, padx=UIStyle.SPACE_MD, pady=UIStyle.SPACE_MD)

    def _build_detail_form(self):
        self.form_frame = tk.Frame(self.right_detail_frame, bg=UIStyle.BG_SURFACE)
        self.form_frame.grid(row=1, column=0, sticky="nsew")

        # Configure columns for form labels and entries
        self.form_frame.grid_columnconfigure(0, weight=0, minsize=100)
        self.form_frame.grid_columnconfigure(1, weight=1)

        # StringVars
        self.var_id = tk.StringVar()
        self.var_name = tk.StringVar()
        self.var_icon_key = tk.StringVar()
        self.var_category = tk.StringVar()
        self.var_fallback_emoji = tk.StringVar()
        self.var_tooltip_key = tk.StringVar()
        self.var_filepath = tk.StringVar()

        # 1. ID (Read-only)
        tk.Label(self.form_frame, text="ID:", bg=UIStyle.BG_SURFACE, fg=UIStyle.TEXT_PRIMARY).grid(row=0, column=0, sticky="e", padx=5, pady=2)
        self.entry_id = ttk.Entry(self.form_frame, textvariable=self.var_id, state="disabled")
        self.entry_id.grid(row=0, column=1, sticky="ew", padx=5, pady=2)

        # 2. Name
        tk.Label(self.form_frame, text="Name:", bg=UIStyle.BG_SURFACE, fg=UIStyle.TEXT_PRIMARY).grid(row=1, column=0, sticky="e", padx=5, pady=2)
        self.entry_name = ttk.Entry(self.form_frame, textvariable=self.var_name)
        self.entry_name.grid(row=1, column=1, sticky="ew", padx=5, pady=2)

        # 3. Icon Key
        tk.Label(self.form_frame, text="Icon Key:", bg=UIStyle.BG_SURFACE, fg=UIStyle.TEXT_PRIMARY).grid(row=2, column=0, sticky="e", padx=5, pady=2)
        self.entry_icon_key = ttk.Entry(self.form_frame, textvariable=self.var_icon_key)
        self.entry_icon_key.grid(row=2, column=1, sticky="ew", padx=5, pady=2)

        # 4. Category
        tk.Label(self.form_frame, text="Category:", bg=UIStyle.BG_SURFACE, fg=UIStyle.TEXT_PRIMARY).grid(row=3, column=0, sticky="e", padx=5, pady=2)
        self.combo_category = ttk.Combobox(self.form_frame, textvariable=self.var_category, state="readonly")
        self.combo_category.grid(row=3, column=1, sticky="ew", padx=5, pady=2)

        # 5. Fallback Emoji
        tk.Label(self.form_frame, text="Fallback Emoji:", bg=UIStyle.BG_SURFACE, fg=UIStyle.TEXT_PRIMARY).grid(row=4, column=0, sticky="e", padx=5, pady=2)
        self.entry_fallback = ttk.Entry(self.form_frame, textvariable=self.var_fallback_emoji)
        self.entry_fallback.grid(row=4, column=1, sticky="ew", padx=5, pady=2)

        # 6. Tooltip Key
        tk.Label(self.form_frame, text="Tooltip Key:", bg=UIStyle.BG_SURFACE, fg=UIStyle.TEXT_PRIMARY).grid(row=5, column=0, sticky="e", padx=5, pady=2)
        self.entry_tooltip = ttk.Entry(self.form_frame, textvariable=self.var_tooltip_key)
        self.entry_tooltip.grid(row=5, column=1, sticky="ew", padx=5, pady=2)

        # 7. Filepath (with Browse button)
        tk.Label(self.form_frame, text="Filepath:", bg=UIStyle.BG_SURFACE, fg=UIStyle.TEXT_PRIMARY).grid(row=6, column=0, sticky="e", padx=5, pady=2)

        filepath_frame = tk.Frame(self.form_frame, bg=UIStyle.BG_SURFACE)
        filepath_frame.grid(row=6, column=1, sticky="ew", padx=5, pady=2)
        filepath_frame.grid_columnconfigure(0, weight=1)

        self.entry_filepath = ttk.Entry(filepath_frame, textvariable=self.var_filepath, state="disabled")
        self.entry_filepath.grid(row=0, column=0, sticky="ew")

        self.btn_browse = tk.Button(filepath_frame, text="...", command=self._on_browse_clicked, **(UIStyle.get_button_style("secondary") if hasattr(UIStyle, "get_button_style") else {}))
        self.btn_browse.grid(row=0, column=1, padx=(5, 0))

    def _render_preview(self, icon_data):
        if not icon_data:
            self.lbl_preview.config(image='', text="No Icon Selected", font=UIStyle.get_font("body"))
            self.lbl_preview.image = None
            return

        icon_key = icon_data.get("icon_key", "")
        fallback_emoji = icon_data.get("fallback_emoji", "")

        # We need a large icon. Let's try 128x128
        giant_icon = self.icon_helper.get_icon(icon_key, fallback=fallback_emoji, size=128)

        if giant_icon and not isinstance(giant_icon, str):
            self.lbl_preview.config(image=giant_icon, text="")
            self.lbl_preview.image = giant_icon
        else:
            # Fallback to emoji text
            emoji_text = giant_icon if giant_icon else fallback_emoji
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
        from tkinter import filedialog
        from lib.managers.icon_file_manager import import_icon_file

        file_path = filedialog.askopenfilename(
            title=self.i18n_t("select_icon_file", default="Select Icon File"),
            filetypes=[("Image files", "*.png *.ico")]
        )

        if file_path:
            try:
                # Import icon into assets directory
                filename = import_icon_file(file_path)
                # Update filepath entry
                self.var_filepath.set(filename)

                # Update Preview
                temp_data = {
                    "icon_key": self.var_icon_key.get() or "preview_temp",
                    "filepath": filename,
                    "fallback_emoji": self.var_fallback_emoji.get(),
                    "tooltip_translation_key": self.var_tooltip_key.get()
                }

                # We need to temporarily add this to helper so it can find it without DB
                self.icon_helper._icon_cache = getattr(self.icon_helper, "_icon_cache", {})

                # Normally get_icon looks in DB or config.
                # Let's bypass and just use evaluate_icon_status or we can just load the image directly.
                from PIL import Image, ImageTk
                from lib.managers.icon_file_manager import get_icons_directory

                icons_dir = get_icons_directory()
                target_path = icons_dir / filename

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
                from tkinter import messagebox
                messagebox.showerror("Error", f"Could not import file:\n{str(e)}")

    def _build_action_bar(self):
        # We place Add, Edit, Delete on the left, and Refresh, Sync, Save, Cancel on the right.
        left_frame = tk.Frame(self.bottom_action_frame, bg=UIStyle.BG_SUBTLE)
        left_frame.pack(side="left", padx=UIStyle.SPACE_MD, pady=UIStyle.SPACE_SM)

        right_frame = tk.Frame(self.bottom_action_frame, bg=UIStyle.BG_SUBTLE)
        right_frame.pack(side="right", padx=UIStyle.SPACE_MD, pady=UIStyle.SPACE_SM)

        self.btn_add = tk.Button(left_frame, text=self.i18n_t("btn_add"), command=self._on_add, **UIStyle.get_button_style("primary"))
        self.btn_add.pack(side="left", padx=UIStyle.SPACE_XS)
        if hasattr(self.app, 'bind_translation'):
            self.app.bind_translation(self.btn_add, "btn_add")

        self.btn_edit = tk.Button(left_frame, text=self.i18n_t("btn_edit"), command=self._on_edit, **UIStyle.get_button_style("secondary"))
        self.btn_edit.pack(side="left", padx=UIStyle.SPACE_XS)
        if hasattr(self.app, 'bind_translation'):
            self.app.bind_translation(self.btn_edit, "btn_edit")

        self.btn_delete = tk.Button(left_frame, text=self.i18n_t("btn_delete"), command=self._on_delete, **UIStyle.get_button_style("danger" if hasattr(UIStyle, 'get_button_style') and 'danger' in [v for v in UIStyle.get_button_style.__code__.co_consts if isinstance(v, str)] else "secondary"))
        self.btn_delete.pack(side="left", padx=UIStyle.SPACE_XS)
        if hasattr(self.app, 'bind_translation'):
            self.app.bind_translation(self.btn_delete, "btn_delete")

        # Override danger if needed (Tkinter style compatibility)
        if not hasattr(UIStyle, 'get_button_style') or 'danger' not in [v for v in UIStyle.get_button_style.__code__.co_consts if isinstance(v, str)]:
            self.btn_delete.configure(bg=UIStyle.DANGER, fg="white")

        self.btn_refresh = tk.Button(right_frame, text=self.i18n_t("btn_refresh"), command=self._on_refresh, **UIStyle.get_button_style("secondary"))
        self.btn_refresh.pack(side="left", padx=UIStyle.SPACE_XS)
        if hasattr(self.app, 'bind_translation'):
            self.app.bind_translation(self.btn_refresh, "btn_refresh")

        self.btn_sync = tk.Button(right_frame, text=self.i18n_t("btn_sync", default="Đồng bộ"), command=self._on_sync, **UIStyle.get_button_style("secondary"))
        self.btn_sync.pack(side="left", padx=UIStyle.SPACE_XS)
        if hasattr(self.app, 'bind_translation'):
            self.app.bind_translation(self.btn_sync, "btn_sync", default="Đồng bộ")

        self.btn_save = tk.Button(right_frame, text=self.i18n_t("btn_save"), command=self._on_save, **UIStyle.get_button_style("primary"))
        self.btn_save.pack(side="left", padx=UIStyle.SPACE_XS)
        if hasattr(self.app, 'bind_translation'):
            self.app.bind_translation(self.btn_save, "btn_save")

        self.btn_cancel = tk.Button(right_frame, text=self.i18n_t("btn_cancel"), command=self._on_cancel, **UIStyle.get_button_style("secondary"))
        self.btn_cancel.pack(side="left", padx=UIStyle.SPACE_XS)
        if hasattr(self.app, 'bind_translation'):
            self.app.bind_translation(self.btn_cancel, "btn_cancel")

        self.set_form_state("VIEW")

    def set_form_state(self, state):
        self._current_state = state

        # Enable/Disable form entries
        entry_state = "normal" if state in ("ADD", "EDIT") else "disabled"
        cb_state = "readonly" if state in ("ADD", "EDIT") else "disabled"

        # Keep ID always readonly or disabled
        self.entry_id.config(state="disabled")

        self.entry_name.config(state=entry_state)
        self.entry_icon_key.config(state=entry_state)
        self.combo_category.config(state=cb_state)
        self.entry_fallback.config(state=entry_state)
        self.entry_tooltip.config(state=entry_state)
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

    def _on_add(self):
        # Clear form variables
        self.var_id.set("")
        self.var_name.set("")
        self.var_icon_key.set("")
        self.var_category.set("")
        self.var_fallback_emoji.set("")
        self.var_tooltip_key.set("")
        self.var_filepath.set("")

        self._render_preview({})
        self.set_form_state("ADD")

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
            success = self.icon_service.delete_icon(icon_key)
            if success:
                # Clear form
                self.var_id.set("")
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
            else:
                messagebox.showerror("Error", f"Failed to delete icon '{icon_key}'.")

    def _on_refresh(self):
        self.apply_filters()

    def _on_sync(self):
        # Stub for next prompts
        pass

    def _on_save(self):
        icon_key = self.var_icon_key.get().strip()
        if not icon_key:
            from tkinter import messagebox
            messagebox.showerror("Error", "Icon Key is required.")
            return

        icon_data = {
            "icon_key": icon_key,
            "name": self.var_name.get().strip(),
            "filepath": self.var_filepath.get().strip(),
            "fallback_emoji": self.var_fallback_emoji.get().strip(),
            "tooltip_translation_key": self.var_tooltip_key.get().strip(),
            "category": self.var_category.get().strip() or "General",
            "description": ""
        }

        success = self.icon_service.upsert_icon(icon_data)
        if success:
            self.load_tree_data()

            # Re-select the saved item
            for item in self.tree.get_children():
                if item.startswith('cat_'):
                    for child in self.tree.get_children(item):
                        if child == icon_key:
                            self.tree.selection_set(child)
                            self.tree.see(child)
                            break

            self.set_form_state("VIEW")
        else:
            from tkinter import messagebox
            messagebox.showerror("Error", "Failed to save icon data.")

    def _on_cancel(self):
        self._on_tree_select(None)
        self.set_form_state("VIEW")

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
            # Clear form
            self.var_id.set("")
            self.var_name.set("")
            self.var_icon_key.set("")
            self.var_category.set("")
            self.var_fallback_emoji.set("")
            self.var_tooltip_key.set("")
            self.var_filepath.set("")
            self._render_preview({})
            self.set_form_state("VIEW")
            return

        item_id = selection[0]
        # Ignore category clicks (folders)
        if item_id.startswith('cat_'):
            return

        # Handle icon selection
        icon_key = item_id
        icon_data = self.icon_service.get_icon_by_key(icon_key)

        if icon_data:
            self.var_id.set(str(icon_data.get("id", "")))
            self.var_name.set(icon_data.get("name", ""))
            self.var_icon_key.set(icon_data.get("icon_key", ""))
            self.var_category.set(icon_data.get("category", ""))
            self.var_fallback_emoji.set(icon_data.get("fallback_emoji", ""))
            self.var_tooltip_key.set(icon_data.get("tooltip_translation_key", ""))
            self.var_filepath.set(icon_data.get("filepath", ""))

            self._render_preview(icon_data)

        self.set_form_state("VIEW")

    def _on_search_key_release(self, event):
        # Cancel any previous timer
        if hasattr(self, '_search_after_id') and self._search_after_id:
            self.after_cancel(self._search_after_id)
        # Set new timer for debounce (500ms)
        self._search_after_id = self.after(500, self.apply_filters)

    def apply_filters(self):
        pass