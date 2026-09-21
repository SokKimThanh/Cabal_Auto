import tkinter as tk
from tkinter import ttk
import logging
from typing import Callable, Optional
from ui.helpers.icon_helper import get_icon_helper
from lib.ui_style_v2 import UIStyleV2 as UIStyle

logger = logging.getLogger(__name__)

class IconPickerWindow(tk.Toplevel):
    def __init__(self, parent, on_select: Callable[[str], None], app=None):
        super().__init__(parent)
        self.parent = parent
        self.on_select = on_select
        self.app = app
        self.icon_helper = get_icon_helper()

        self.title("Chọn Icon (Icon Picker)")
        self.geometry("600x500")
        self.minsize(400, 300)
        self.transient(parent)
        self.grab_set()

        # Debounce and Cache references
        self._search_after_id = None
        self._image_refs = []
        self._icon_cache = []  # All icons loaded from db or memory

        self.config(bg=UIStyle.BG_BASE if hasattr(UIStyle, "BG_BASE") else "#F3F4F6")

        self._setup_ui()
        self._load_icons_async()

    def _setup_ui(self):
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Top Bar (Search)
        top_frame = tk.Frame(self, bg=UIStyle.BG_SUBTLE if hasattr(UIStyle, "BG_SUBTLE") else "#FFFFFF")
        top_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        top_frame.grid_columnconfigure(1, weight=1)

        tk.Label(top_frame, text="Tìm kiếm:", bg=top_frame["bg"]).grid(row=0, column=0, padx=(0, 5))

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self._on_search_changed)
        search_entry = ttk.Entry(top_frame, textvariable=self.search_var)
        search_entry.grid(row=0, column=1, sticky="ew")

        # Canvas & Scrollbar for Grid
        grid_container = tk.Frame(self, bg=self["bg"])
        grid_container.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        grid_container.grid_rowconfigure(0, weight=1)
        grid_container.grid_columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(grid_container, bg=self["bg"], highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(grid_container, orient="vertical", command=self.canvas.yview)

        self.scrollable_frame = tk.Frame(self.canvas, bg=self["bg"])
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw", width=self.canvas.winfo_width())
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.scrollbar.grid(row=0, column=1, sticky="ns")

        # Bind resize to adjust wrap width
        self.canvas.bind("<Configure>", self._on_canvas_configure)

    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(1, width=event.width)
        # Optional: Re-layout grid based on width
        # self._render_grid()

    def _on_search_changed(self, *args):
        if self._search_after_id:
            self.after_cancel(self._search_after_id)
        self._search_after_id = self.after(300, self._render_grid)

    def _load_icons_async(self):
        # Load from IconService or IconHelper map
        # using IconHelper's map which is loaded from memory
        import threading

        def fetch_task():
            try:
                icons = []
                for icon_key, (icon_stem, emoji) in self.icon_helper.icon_map.items():
                    icons.append({
                        "key": icon_key,
                        "emoji": emoji
                    })

                # Sort alphabetically
                icons.sort(key=lambda x: x["key"])

                self.after(0, lambda: self._on_icons_loaded(icons))
            except Exception as e:
                logger.error(f"Error loading icons for picker: {e}")

        threading.Thread(target=fetch_task, daemon=True).start()

    def _on_icons_loaded(self, icons):
        self._icon_cache = icons
        self._render_grid()

    def _render_grid(self):
        # Clear existing
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        self._image_refs.clear()

        search_term = self.search_var.get().lower().strip()
        filtered = [ic for ic in self._icon_cache if search_term in ic["key"].lower()]

        if not filtered:
            lbl = tk.Label(self.scrollable_frame, text="Không tìm thấy biểu tượng nào.", bg=self.scrollable_frame["bg"])
            lbl.pack(pady=20)
            return

        # Grid layout
        # Estimate items per row based on current width. Minimum 4, padding etc.
        canvas_width = self.canvas.winfo_width()
        if canvas_width < 100:
            canvas_width = 580 # fallback default

        item_width = 80
        cols = max(1, canvas_width // item_width)

        for i, icon_data in enumerate(filtered):
            row = i // cols
            col = i % cols

            frame = tk.Frame(self.scrollable_frame, bg=self.scrollable_frame["bg"], width=item_width, height=item_width)
            frame.grid(row=row, column=col, padx=5, pady=5)
            frame.grid_propagate(False)

            # Fetch icon image (lazy load would be better, but doing it fast via icon_helper cache)
            icon_img = self.icon_helper.get_icon(icon_data["key"], fallback=icon_data["emoji"], size=32)

            btn = tk.Button(
                frame,
                image=icon_img if not isinstance(icon_img, str) else None,
                text=icon_img if isinstance(icon_img, str) else "",
                font=("Segoe UI Emoji", 24) if isinstance(icon_img, str) else None,
                command=lambda k=icon_data["key"]: self._on_icon_click(k),
                bg=UIStyle.BG_SURFACE if hasattr(UIStyle, "BG_SURFACE") else "#FFFFFF",
                relief="flat",
                cursor="hand2"
            )
            btn.pack(fill="both", expand=True)

            # Store ref to prevent GC
            if not isinstance(icon_img, str):
                self._image_refs.append(icon_img)

            lbl = tk.Label(frame, text=icon_data["key"], font=("Segoe UI", 8), bg=frame["bg"], fg="#555555", wraplength=item_width-4)
            lbl.pack(side="bottom")

    def _on_icon_click(self, icon_key: str):
        if self.on_select:
            self.on_select(icon_key)
        self.destroy()
