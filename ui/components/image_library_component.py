import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
import os
from lib.ui_style_v2 import UIStyleV2 as UIStyle

class ImageLibraryComponent(tk.Frame):
    def __init__(self, parent, app, image_model, on_image_selected, get_used_filepaths, *args, **kwargs):
        super().__init__(parent, bg=UIStyle.BG_SURFACE, *args, **kwargs)
        self.app = app
        self.image_model = image_model
        self.on_image_selected = on_image_selected
        self.get_used_filepaths = get_used_filepaths

        # UI Variables
        self.img_search_var = tk.StringVar()
        self.var_hide_used = tk.BooleanVar(value=True)
        self._img_search_after_id = None
        self._current_selected_filepath = ""

        # Widgets
        self.img_search_entry = None
        self.chk_hide_used = None
        self.btn_import_img = None
        self.img_listbox = None
        self._listbox_items = []

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

    def set_current_filepath(self, filepath):
        self._current_selected_filepath = filepath
        if filepath:
            self._highlight_image_in_list(filepath)
        elif hasattr(self, 'img_listbox') and self.img_listbox:
            self.img_listbox.selection_clear(0, tk.END)

    def set_state(self, state):
        if hasattr(self, 'img_listbox'):
            if state in ("ADD", "EDIT"):
                self.img_listbox.config(state="normal")
                self.btn_import_img.config(state="normal")
            else:
                self.img_listbox.config(state="disabled")
                self.btn_import_img.config(state="disabled")

    def _setup_ui(self):
        self.grid_rowconfigure(0, weight=0) # Toolbar
        self.grid_rowconfigure(1, weight=1) # List
        self.grid_columnconfigure(0, weight=1)

        # Toolbar
        toolbar = tk.Frame(self, bg=UIStyle.BG_ELEVATED)
        toolbar.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        toolbar.grid_columnconfigure(0, weight=1)

        search_frame = tk.Frame(toolbar, bg=UIStyle.BG_ELEVATED)
        search_frame.pack(side="left", fill="x", expand=True)
        tk.Label(search_frame, text="🔍", bg=UIStyle.BG_ELEVATED, fg=UIStyle.TEXT_MUTED).pack(side="left", padx=(5,2))

        self.img_search_entry = ttk.Entry(search_frame, textvariable=self.img_search_var)
        self.img_search_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))

        self.chk_hide_used = tk.Checkbutton(
            toolbar, text=self.i18n_t("chk_hide_used", default="Ẩn ảnh đã dùng"),
            variable=self.var_hide_used, bg=UIStyle.BG_ELEVATED, fg=UIStyle.TEXT_PRIMARY,
            selectcolor=UIStyle.BG_BASE
        )
        self.chk_hide_used.pack(side="right", padx=(5, 10))

        self.btn_import_img = tk.Button(
            toolbar, text=self.i18n_t("btn_import_img", default="Import Image"),
            **(UIStyle.get_button_style("secondary") if hasattr(UIStyle, "get_button_style") else {})
        )
        self.btn_import_img.pack(side="right", padx=5)

        # Listbox container
        list_frame = tk.Frame(self, bg=UIStyle.BG_BASE)
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

        self.img_listbox.bind('<MouseWheel>', self._prevent_scroll_propagation)
        self.img_listbox.bind('<Button-4>', self._prevent_scroll_propagation)
        self.img_listbox.bind('<Button-5>', self._prevent_scroll_propagation)

        # Bind events
        self.img_search_var.trace_add("write", self._on_img_search_change)
        self.chk_hide_used.config(command=self._on_img_search_change)
        self.btn_import_img.config(command=self._on_import_image_clicked)
        self.img_listbox.bind("<<ListboxSelect>>", self._on_image_selected)

        # Start scanning image library
        self.image_model.scan_async(self._on_image_library_scanned)

    def _on_img_search_change(self, *args):
        if self._img_search_after_id:
            self.after_cancel(self._img_search_after_id)
        self._img_search_after_id = self.after(300, self._perform_img_search)

    def _perform_img_search(self):
        query = self.img_search_var.get()
        results = self.image_model.search(query)

        # Filter used images if checkbox is ticked
        used_files = self.get_used_filepaths()

        if self.var_hide_used.get():
            current_file = self._current_selected_filepath
            results = [f for f in results if f not in used_files or f == current_file]

        self._update_image_listbox(results, used_files)

    def _on_image_library_scanned(self, file_list, error_msg):
        def update_ui():
            try:
                if not self.winfo_exists():
                    return
            except Exception:
                return
            if error_msg:
                self.img_listbox.insert(tk.END, f"Error: {error_msg}")
                self.img_listbox.config(state="disabled")
            else:
                self._perform_img_search()

        try:
            self.after(0, update_ui)
        except RuntimeError:
            pass

    def _update_image_listbox(self, file_list, used_files=None):
        if used_files is None:
            used_files = self.get_used_filepaths()

        # Temporarily enable listbox if disabled to allow inserting items
        current_state = self.img_listbox.cget('state')
        if current_state == 'disabled':
            self.img_listbox.config(state='normal')

        self.img_listbox.delete(0, tk.END)
        self._listbox_items = []
        for f in file_list:
            display_text = f
            if f in used_files and used_files[f]:
                usages_str = ", ".join(sorted(list(used_files[f])))
                display_text = f"{f} [{usages_str}]"

            self.img_listbox.insert(tk.END, display_text)
            self._listbox_items.append(f)

        if self._current_selected_filepath:
            self._highlight_image_in_list(self._current_selected_filepath)

        if current_state == 'disabled':
            self.img_listbox.config(state='disabled')

    def _highlight_image_in_list(self, filename):
        if filename in self._listbox_items:
            idx = self._listbox_items.index(filename)
            self.img_listbox.selection_clear(0, tk.END)
            self.img_listbox.selection_set(idx)
            self.img_listbox.see(idx)

    def _on_image_selected(self, event):
        selection = self.img_listbox.curselection()
        if not selection:
            return

        idx = selection[0]
        if 0 <= idx < len(self._listbox_items):
            selected_file = self._listbox_items[idx]
            # Allow parent component to validate and decide if selection is accepted
            if self.on_image_selected:
                self.on_image_selected(selected_file)

    def _on_import_image_clicked(self):
        from tkinter import filedialog
        import logging
        logger = logging.getLogger(__name__)

        file_path = filedialog.askopenfilename(
            title=self.i18n_t("select_icon_file", default="Select Icon File"),
            filetypes=[("Image files", "*.png *.ico")]
        )

        if not file_path:
            return

        original_name = Path(file_path).name
        target_name = original_name
        overwrite = False

        if self.image_model.check_name_collision(original_name):
            msg = f"Ảnh '{original_name}' đã tồn tại.\n- Yes: Ghi đè (Replace)\n- No: Giữ cả hai (Đổi tên)\n- Cancel: Hủy bỏ"
            res = messagebox.askyesnocancel("Trùng tên file", msg)

            if res is None:
                return
            elif res is True:
                overwrite = True
                logger.info(f"Import: Người dùng chọn Ghi đè (Replace) file {target_name}")
            else:
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

        # Reload list and search
        self.img_search_var.set("")
        self._on_img_search_change()

        # Update parent component via callback
        if self.on_image_selected:
            self.on_image_selected(final_filename, is_new_import=True)

    def reload(self):
        """Method to trigger an explicit scan/reload from outside."""
        self.image_model.scan_async(self._on_image_library_scanned)
