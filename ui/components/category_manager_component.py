import tkinter as tk
from tkinter import ttk, messagebox
from lib.ui_style_v2 import UIStyleV2 as UIStyle

class CategoryManagerComponent(tk.Frame):
    def __init__(self, parent, app, icon_service, tree_model, on_category_changed, *args, **kwargs):
        super().__init__(parent, bg=UIStyle.BG_BASE, *args, **kwargs)
        self.app = app
        self.icon_service = icon_service
        self.tree_model = tree_model
        self.on_category_changed = on_category_changed

        self.var_cat_id = None
        self.var_cat_name = None
        self.entry_cat_name = None
        self.btn_cat_save = None
        self.btn_cat_cancel = None
        self.btn_cat_delete = None
        self.btn_cat_add = None
        self.cat_tree = None
        self._cat_current_state = "view"

    def _prevent_scroll_propagation(self, event):
        """Prevent mouse wheel events from bubbling up to the main canvas."""
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

    def _setup_ui(self):
        # 1. Main PanedWindow (Split Tree vs Form 1:1)
        self.cat_main_frame = tk.Frame(self, bg=UIStyle.BG_BASE)
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
        self.cat_tree.bind('<MouseWheel>', self._prevent_scroll_propagation)
        self.cat_tree.bind('<Button-4>', self._prevent_scroll_propagation)
        self.cat_tree.bind('<Button-5>', self._prevent_scroll_propagation)
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


    def start(self):
        self._setup_ui()
        self._load_categories_tree()
        self._set_cat_form_state("view")

    def _load_categories_tree(self):
        for item in self.cat_tree.get_children():
            self.cat_tree.delete(item)

        categories = self.icon_service.get_all_categories()
        for cat in categories:
            self.cat_tree.insert("", "end", values=(cat["id"], cat["name"]))

        # Optional: could notify parent just in case, but usually handled by save/delete.
        # self.on_category_changed()

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

    def _on_cat_tree_interaction(self, event):
        if getattr(self, '_cat_current_state', 'view') in ("add", "edit"):
            from tkinter import messagebox
            msg = self.i18n_t("msg_unsaved_changes_lock", default="Vui lòng nhấn Lưu hoặc Hủy trước khi chọn dòng khác.")
            messagebox.showwarning(self.i18n_t("warning", default="Cảnh báo"), msg)
            return "break"

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

                if self.on_category_changed:
                    self.on_category_changed()
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

                if self.on_category_changed:
                    self.on_category_changed()
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

                    if self.on_category_changed:
                        self.on_category_changed()
                else:
                    messagebox.showerror("Error", "Failed to delete category.")
            except ValueError as e:
                if str(e) == "category_in_use_error":
                    messagebox.showerror("Error", "Cannot delete category because it is used by icons.")
                else:
                    messagebox.showerror("Error", f"An error occurred: {e}")
