import tkinter as tk
from tkinter import ttk
from lib.ui_style_v2 import UIStyleV2 as UIStyle
from lib.ui.controllers.language_manager_controller import LanguageManagerController
from ui.components.base.responsive_grid_base import ResponsiveGridBase
from lib.ui.dialog_service import DialogService
import threading
from ui.helpers.tooltip import attach_i18n_tooltip


class LanguageManagerFrame(ResponsiveGridBase):
    MODULE_NAME = "language_manager_frame"
    SCREEN_NAME = "main"

    def __init__(self, parent, app, **kwargs):
        super().__init__(parent, app=app, bg=UIStyle.BG_BASE, **kwargs)
        self.app = app
        self._t = app._t if hasattr(app, '_t') else lambda x, **kw: x

        self.controller = LanguageManagerController()

        # Get the inner content frame from ResponsiveGridBase
        self.content_container = self.get_content_frame()

        # Define layout parts
        self._build_toolbar()
        self._build_bottom_section()
        self._build_tree_section()

        # Pack them following the "Top -> Bottom -> Fill Middle" approach
        self.toolbar.pack(side=tk.TOP, fill=tk.X, padx=10, pady=(10, 10))
        self.bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=(0, 10))
        self.tree_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        # Load initial data
        self.refresh_data()

    def _build_toolbar(self):
        # Toolbar
        self.toolbar = tk.Frame(self.content_container, bg=UIStyle.BG_BASE)

        # Namespace Filter
        ttk.Label(self.toolbar, text=self._t("lang_mgr_namespace", default="Namespace:")).pack(side=tk.LEFT, padx=(0, 5))
        self.cb_namespace_var = tk.StringVar()
        self.cb_namespace = ttk.Combobox(self.toolbar, textvariable=self.cb_namespace_var, state="readonly", width=15)
        self.cb_namespace.pack(side=tk.LEFT, padx=(0, 15))
        self.cb_namespace.bind("<<ComboboxSelected>>", lambda e: self.apply_filters())

        # Search
        ttk.Label(self.toolbar, text=self._t("lang_mgr_search", default="Search:")).pack(side=tk.LEFT, padx=(0, 5))
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(self.toolbar, textvariable=self.search_var, width=30)
        search_entry.pack(side=tk.LEFT, padx=(0, 15))
        search_entry.bind("<KeyRelease>", lambda e: self.apply_filters())

        # Action Buttons
        refresh_btn = ttk.Button(self.toolbar, text=self._t("lang_mgr_refresh", default="Refresh"), command=self.refresh_data)
        refresh_btn.pack(side=tk.RIGHT, padx=(5, 0))

        sync_btn = ttk.Button(self.toolbar, text=self._t("lang_mgr_sync", default="Sync to JSON"), command=self.sync_to_json)
        sync_btn.pack(side=tk.RIGHT, padx=(5, 0))

    def _build_tree_section(self):
        # Treeview
        self.tree_frame = tk.Frame(self.content_container, bg=UIStyle.BG_BASE)

        columns = ("namespace", "key", "en", "vi", "updated_at")
        self.tree = ttk.Treeview(self.tree_frame, columns=columns, show="headings", selectmode="browse")

        self.tree.heading("namespace", text=self._t("lang_mgr_col_ns", default="Namespace"), command=lambda: self._sort_tree("namespace", False))
        self.tree.heading("key", text=self._t("lang_mgr_col_key", default="Key"), command=lambda: self._sort_tree("key", False))
        self.tree.heading("en", text=self._t("lang_mgr_col_en", default="Text (EN)"))
        self.tree.heading("vi", text=self._t("lang_mgr_col_vi", default="Text (VI)"))
        self.tree.heading("updated_at", text=self._t("lang_mgr_col_updated", default="Updated At"), command=lambda: self._sort_tree("updated_at", False))

        self.tree.column("namespace", width=100, anchor=tk.W)
        self.tree.column("key", width=200, anchor=tk.W)
        self.tree.column("en", width=300, anchor=tk.W)
        self.tree.column("vi", width=300, anchor=tk.W)
        self.tree.column("updated_at", width=150, anchor=tk.W)

        scrollbar = ttk.Scrollbar(self.tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)

    def _build_bottom_section(self):
        self.bottom_frame = tk.LabelFrame(self.content_container, text=self._t("lang_mgr_edit_form", default="Add / Edit Translation"), bg=UIStyle.BG_ELEVATED, fg=UIStyle.TEXT_PRIMARY)

        self.bottom_frame.grid_rowconfigure(2, weight=1)
        self.bottom_frame.grid_columnconfigure(1, weight=1)
        self.bottom_frame.grid_columnconfigure(3, weight=1)

        # Row 0: Namespace & Key
        ns_label = ttk.Label(self.bottom_frame, text=self._t("lang_mgr_namespace", default="Namespace:"))
        ns_label.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        attach_i18n_tooltip(ns_label, key="tip_lang_mgr_namespace", ns="_global", lang_provider=lambda: getattr(self.app, "lang", "vi"))
        self.form_ns_var = tk.StringVar()
        self.form_ns_entry = ttk.Combobox(self.bottom_frame, textvariable=self.form_ns_var)
        self.form_ns_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        attach_i18n_tooltip(self.form_ns_entry, key="tip_lang_mgr_namespace", ns="_global", lang_provider=lambda: getattr(self.app, "lang", "vi"))

        ttk.Label(self.bottom_frame, text=self._t("lang_mgr_key", default="Key:")).grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        self.form_key_var = tk.StringVar()
        self.form_key_entry = ttk.Entry(self.bottom_frame, textvariable=self.form_key_var)
        self.form_key_entry.grid(row=0, column=3, sticky="ew", padx=5, pady=5)

        # Row 1: Text EN & VI Labels
        ttk.Label(self.bottom_frame, text=self._t("lang_mgr_text_en", default="Text (EN):")).grid(row=1, column=0, columnspan=2, sticky=tk.W, padx=5, pady=(5, 0))
        ttk.Label(self.bottom_frame, text=self._t("lang_mgr_text_vi", default="Text (VI):")).grid(row=1, column=2, columnspan=2, sticky=tk.W, padx=5, pady=(5, 0))

        # Row 2: Text Areas
        self.text_en = tk.Text(self.bottom_frame, height=5, bg=UIStyle.BG_BASE, fg=UIStyle.TEXT_PRIMARY, insertbackground=UIStyle.TEXT_PRIMARY)
        self.text_en.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)

        self.text_vi = tk.Text(self.bottom_frame, height=5, bg=UIStyle.BG_BASE, fg=UIStyle.TEXT_PRIMARY, insertbackground=UIStyle.TEXT_PRIMARY)
        self.text_vi.grid(row=2, column=2, columnspan=2, sticky="nsew", padx=5, pady=5)

        # Row 3: Action Buttons
        btn_frame = tk.Frame(self.bottom_frame, bg=UIStyle.BG_ELEVATED)
        btn_frame.grid(row=3, column=0, columnspan=4, sticky="e", padx=5, pady=10)

        ttk.Button(btn_frame, text=self._t("lang_mgr_add_new", default="Add New (Clear)"), command=self.clear_form).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text=self._t("lang_mgr_delete", default="Delete Key"), command=self.delete_key).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text=self._t("lang_mgr_save", default="Save"), command=self.save_translation).pack(side=tk.LEFT, padx=5)

        self.is_editing_existing = False
        self.form_key_entry.focus_set()

    def refresh_data(self):
        """Reload data from DB and update UI."""
        self.all_data = self.controller.get_all_grouped()

        # Update namespaces list for filters and form
        namespaces = self.controller.get_namespaces()
        cb_values = ["All"] + namespaces
        self.cb_namespace['values'] = cb_values
        if not self.cb_namespace_var.get() or self.cb_namespace_var.get() not in cb_values:
            self.cb_namespace.current(0)

        self.form_ns_entry['values'] = namespaces

        self.apply_filters()
        self.clear_form()

    def apply_filters(self):
        """Apply search and namespace filters to Treeview."""
        self.tree.delete(*self.tree.get_children())

        ns_filter = self.cb_namespace_var.get()
        search_term = self.search_var.get().lower()

        for row in self.all_data:
            if ns_filter != "All" and row["namespace"] != ns_filter:
                continue

            en_val = row["en"] or ""
            vi_val = row["vi"] or ""

            if search_term and (
                search_term not in row["key"].lower() and
                search_term not in en_val.lower() and
                search_term not in vi_val.lower()
            ):
                continue

            # Handle missing translations with placeholder
            display_en = en_val if row["en"] is not None else "<Chưa có bản dịch>"
            display_vi = vi_val if row["vi"] is not None else "<Chưa có bản dịch>"

            self.tree.insert("", tk.END, values=(
                row["namespace"],
                row["key"],
                display_en,
                display_vi,
                row["updated_at"]
            ))

    def _on_tree_select(self, event):
        selected = self.tree.selection()
        if not selected:
            return

        item = self.tree.item(selected[0])
        values = item['values']

        self.form_ns_var.set(values[0])
        self.form_key_var.set(values[1])

        self.text_en.delete("1.0", tk.END)
        en_val = values[2]
        if en_val != "<Chưa có bản dịch>":
            self.text_en.insert("1.0", en_val)

        self.text_vi.delete("1.0", tk.END)
        vi_val = values[3]
        if vi_val != "<Chưa có bản dịch>":
            self.text_vi.insert("1.0", vi_val)

        self.form_key_entry.configure(state="disabled")
        self.is_editing_existing = True

    def clear_form(self):
        self.form_ns_var.set("_global")
        self.form_key_var.set("")
        self.text_en.delete("1.0", tk.END)
        self.text_vi.delete("1.0", tk.END)
        self.form_key_entry.configure(state="normal")
        self.tree.selection_remove(self.tree.selection())
        self.is_editing_existing = False
        self.form_key_entry.focus_set()

        # Visual feedback for users to know they can start typing
        original_bg = self.form_key_entry.cget('background')
        self.form_key_entry.configure(background='#fff3cd') # Light yellow to highlight

        # Reset background after 1 second
        self.after(1000, lambda: self.form_key_entry.configure(background=original_bg))


    def save_translation(self):
        ns = self.form_ns_var.get().strip()
        key = self.form_key_var.get().strip()
        en_text = self.text_en.get("1.0", tk.END).strip()
        vi_text = self.text_vi.get("1.0", tk.END).strip()

        if not ns or not key:
            DialogService.show_error("Validation Error", "Namespace and Key are required.")
            return

        if not en_text and not vi_text:
            DialogService.show_error("Validation Error", "At least one language translation is required.")
            return

        if self.controller.save_translation(ns, key, en_text, vi_text):
            self.refresh_data()
            DialogService.show_info("Success", "Translation saved successfully!")

            # Select the newly saved/edited item
            for child in self.tree.get_children():
                if self.tree.item(child)["values"][0] == ns and self.tree.item(child)["values"][1] == key:
                    self.tree.selection_set(child)
                    self.tree.see(child)
                    break
        else:
            DialogService.show_error("Error", "Failed to save translation.")

    def delete_key(self):
        if not self.is_editing_existing:
            return

        ns = self.form_ns_var.get().strip()
        key = self.form_key_var.get().strip()

        if DialogService.ask_yes_no("Confirm Delete", f"Are you sure you want to delete the key '{ns}.{key}'?"):
            if self.controller.delete_key(ns, key):
                self.refresh_data()
                DialogService.show_info("Success", "Translation deleted successfully.")
            else:
                DialogService.show_error("Error", "Failed to delete translation.")

    def sync_to_json(self):
        def _sync_thread():
            if self.controller.sync_to_json():
                self.after(0, lambda: DialogService.show_info("Success", "Successfully exported translations to JSON."))
            else:
                self.after(0, lambda: DialogService.show_error("Error", "Failed to export translations."))

        threading.Thread(target=_sync_thread, daemon=True).start()

    def _sort_tree(self, col, reverse):
        """Sort treeview content when clicking on column headers"""
        l = [(self.tree.set(k, col), k) for k in self.tree.get_children('')]
        l.sort(reverse=reverse)

        # rearrange items in sorted positions
        for index, (val, k) in enumerate(l):
            self.tree.move(k, '', index)

        # reverse sort next time
        self.tree.heading(col, command=lambda _col=col: self._sort_tree(_col, not reverse))
