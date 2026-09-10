import tkinter as tk
from tkinter import ttk
from lib.ui_style_v2 import UIStyleV2 as UI


class ActivityLogsFrame(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=UI.BG_BASE)
        self.app = app

        # Variables
        self.auto_scroll_var = tk.BooleanVar(value=True)
        self.filter_var = tk.StringVar(value="All")
        self.search_var = tk.StringVar()

        # Main Header
        self.header_frame = tk.Frame(self, bg=UI.BG_ELEVATED, height=36)
        self.header_frame.pack(fill="x", side="top")
        self.header_frame.pack_propagate(False)

        self.title_label = tk.Label(
            self.header_frame,
            bg=UI.BG_ELEVATED,
            fg=UI.TEXT_PRIMARY,
            font=UI.FONT_TITLE,
        )
        if hasattr(self.app, "bind_text"):
            self.app.bind_text(self.title_label, "logs_title")
        else:
            self.title_label.config(text=self.app._t("logs_title"))
        self.title_label.pack(side="left", padx=12)

        self.clear_btn = tk.Button(
            self.header_frame,
            bg=UI.BG_ELEVATED,
            fg=UI.TEXT_PRIMARY,
            font=UI.FONT_BODY,
            relief="flat",
            activebackground=UI.BG_SURFACE,
            activeforeground=UI.TEXT_PRIMARY,
            cursor="hand2",
            command=self.clear,
        )
        if hasattr(self.app, "bind_text"):
            self.app.bind_text(self.clear_btn, "logs_clear")
        else:
            self.clear_btn.config(text=self.app._t("logs_clear"))
        self.clear_btn.pack(side="right", padx=12)

        # Toolbar Frame
        self.toolbar_frame = tk.Frame(self, bg=UI.BG_BASE)
        self.toolbar_frame.pack(fill="x", side="top", pady=4, padx=12)

        # Auto-scroll
        self.autoscroll_cb = tk.Checkbutton(
            self.toolbar_frame,
            text=self.app._t("logs_autoscroll"),
            variable=self.auto_scroll_var,
            bg=UI.BG_BASE,
            fg=UI.TEXT_PRIMARY,
            activebackground=UI.BG_BASE,
            activeforeground=UI.TEXT_PRIMARY,
            selectcolor=UI.BG_SURFACE,
            font=UI.FONT_BODY,
        )
        if hasattr(self.app, "bind_text"):
            self.app.bind_text(self.autoscroll_cb, "logs_autoscroll")
        self.autoscroll_cb.pack(side="left", padx=(0, 10))

        # Log Level Filter
        filter_label = tk.Label(
            self.toolbar_frame,
            text=self.app._t("logs_level"),
            bg=UI.BG_BASE,
            fg=UI.TEXT_SECONDARY,
            font=UI.FONT_BODY,
        )
        if hasattr(self.app, "bind_text"):
            self.app.bind_text(filter_label, "logs_level")
        filter_label.pack(side="left")

        self.filter_cb = ttk.Combobox(
            self.toolbar_frame,
            textvariable=self.filter_var,
            values=["All", "INFO", "WARNING", "ERROR"],
            state="readonly",
            width=10,
        )
        self.filter_cb.pack(side="left", padx=(5, 15))

        # Search
        self.search_entry = ttk.Entry(self.toolbar_frame, textvariable=self.search_var, width=20)
        self.search_entry.pack(side="left", padx=(0, 5))
        self.search_entry.bind("<Return>", lambda e: self.do_search())

        self.search_btn = tk.Button(
            self.toolbar_frame,
            text=self.app._t("logs_search"),
            bg=UI.BG_SURFACE,
            fg=UI.TEXT_PRIMARY,
            relief="flat",
            command=self.do_search,
        )
        if hasattr(self.app, "bind_text"):
            self.app.bind_text(self.search_btn, "logs_search")
        self.search_btn.pack(side="left")

        # Utility Buttons (Folder & Copy) will be on the right
        self.copy_btn = tk.Button(
            self.toolbar_frame,
            text=self.app._t("logs_copy"),
            bg=UI.BG_SURFACE,
            fg=UI.TEXT_PRIMARY,
            relief="flat",
            command=self.copy_logs,
        )
        if hasattr(self.app, "bind_text"):
            self.app.bind_text(self.copy_btn, "logs_copy")
        self.copy_btn.pack(side="right", padx=(5, 0))

        self.folder_btn = tk.Button(
            self.toolbar_frame,
            text=self.app._t("logs_folder"),
            bg=UI.BG_SURFACE,
            fg=UI.TEXT_PRIMARY,
            relief="flat",
            command=self.open_log_folder,
        )
        if hasattr(self.app, "bind_text"):
            self.app.bind_text(self.folder_btn, "logs_folder")
        self.folder_btn.pack(side="right")

        # Content container
        self.content_frame = tk.Frame(self, bg=UI.BG_SURFACE)
        self.content_frame.pack(fill="both", expand=True, padx=0, pady=0)

        # Text widget
        self.text_widget = tk.Text(
            self.content_frame,
            bg=UI.BG_SURFACE,
            fg=UI.TEXT_PRIMARY,
            font=UI.FONT_BODY,
            wrap="word",
            state="disabled",
            relief="flat",
            padx=12,
            pady=12,
        )
        self.text_widget.pack(fill="both", expand=True, side="left")

        # Scrollbar
        self.scrollbar = ttk.Scrollbar(
            self.content_frame, command=self.text_widget.yview
        )
        self.scrollbar.pack(side="right", fill="y")
        self.text_widget.config(yscrollcommand=self.scrollbar.set)

    def append_message(self, message: str, levelname: str = "INFO"):
        """Appends a message to the text widget and auto-scrolls to the bottom."""
        # Level filtering
        current_filter = self.filter_var.get()
        if current_filter != "All":
            # If warning filter is active, only show warning and error.
            # If error is active, only show error.
            if current_filter == "INFO" and levelname not in ["INFO", "WARNING", "ERROR", "CRITICAL"]:
                return
            if current_filter == "WARNING" and levelname not in ["WARNING", "ERROR", "CRITICAL"]:
                return
            if current_filter == "ERROR" and levelname not in ["ERROR", "CRITICAL"]:
                return

        self.text_widget.config(state="normal")
        self.text_widget.insert(tk.END, message + "\n")
        self.text_widget.config(state="disabled")

        if self.auto_scroll_var.get():
            self.text_widget.see(tk.END)
        # In actual usage, trim_to_limit will be called in batch from the main app.
        # Calling it here on every line is bad for performance if multiple lines are appended rapidly.

    def trim_to_limit(self, limit: int = 1000):
        """Trims the text widget to keep only the latest `limit` lines."""
        lines = int(self.text_widget.index("end-1c").split(".")[0])
        if lines > limit:
            self.text_widget.config(state="normal")
            self.text_widget.delete("1.0", f"{lines - limit + 1}.0")
            self.text_widget.config(state="disabled")

    def clear(self):
        """Clears all text from the text widget."""
        self.text_widget.config(state="normal")
        self.text_widget.delete("1.0", tk.END)
        self.text_widget.config(state="disabled")

    def do_search(self):
        """Searches for text and highlights occurrences."""
        self.text_widget.tag_remove("search", "1.0", tk.END)
        search_text = self.search_var.get()
        if not search_text:
            return

        idx = "1.0"
        self.text_widget.tag_configure("search", background=UI.ACCENT_PRIMARY, foreground=UI.TEXT_INVERSE)
        while True:
            idx = self.text_widget.search(search_text, idx, nocase=1, stopindex=tk.END)
            if not idx:
                break
            lastidx = f"{idx}+{len(search_text)}c"
            self.text_widget.tag_add("search", idx, lastidx)
            idx = lastidx

        # Ensure first match is visible if we found any
        first_match = self.text_widget.tag_ranges("search")
        if first_match:
            self.text_widget.see(first_match[0])

    def copy_logs(self):
        """Copies the text widget's content to the clipboard."""
        self.clipboard_clear()
        self.clipboard_append(self.text_widget.get("1.0", tk.END))

    def open_log_folder(self):
        """Opens the directory where logs are saved using the OS file explorer."""
        import os
        import platform
        import subprocess
        from pathlib import Path

        log_dir = Path("logs").absolute()
        log_dir.mkdir(parents=True, exist_ok=True)

        try:
            if platform.system() == "Windows":
                os.startfile(str(log_dir))
            elif platform.system() == "Darwin":
                subprocess.Popen(["open", str(log_dir)])
            else:
                subprocess.Popen(["xdg-open", str(log_dir)])
        except Exception as e:
            print(f"Failed to open log folder: {e}")
