import tkinter as tk
from lib.ui_style_v2 import UIStyleV2 as UI
from ui.components.base.responsive_grid_base import ResponsiveGridBase

class AppShell:
    def __init__(self, root, app):
        self.root = root
        self.app = app

        # UI Zones
        self.main_shell = None
        self.shell_zone_a = None
        self.shell_zone_b = None
        self.shell_zone_c1 = None
        self.status_bar_frame = None

    def update_title(self):
        """Updates the root window title based on current language translation."""
        if hasattr(self.app, "_t"):
            self.root.title(self.app._t("app_title"))
        else:
            self.root.title("AutoHunt")

    def build(self):
        # --- Window Configuration ---
        self.update_title()

        self.root.resizable(True, True)

        # Calculate scale factor for layout limits
        try:
            dpi_percent = self.root.tk.call("tk", "scaling") * 72
            scale_factor = dpi_percent / 100.0
        except Exception:
            scale_factor = 1.0

        self.root.minsize(int(1220 * scale_factor), int(656 * scale_factor))

        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()

        # Limit initial geometry to not cover taskbar/titlebar
        max_init_w = screen_w - 20
        max_init_h = screen_h - 80

        w = min(1920, max_init_w)
        h = min(1080, max_init_h)

        x = max((screen_w - w) // 2, 0)
        y = max((screen_h - h) // 2, 0)
        self.root.geometry(f"{w}x{h}+{x}+{y}")

        # --- Theme Initialization ---
        # Note: UIStyleV2 acts strictly as a namespace for global UI style constants
        # and does not contain an `.apply()` method. We apply the base window background here.
        self.root.configure(bg=UI.BG_BASE)

        # --- Grid Configuration ---
        # Clear (for language rebuild)
        for w_child in self.root.winfo_children():
            # Don't destroy menus or other non-frame items if not wanted, but standard App does this.
            # In standard App they use winfo_children and destroy.
            if not isinstance(w_child, tk.Menu) and not isinstance(w_child, tk.Toplevel):
                w_child.destroy()

        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Isolated main container
        self.main_shell = tk.Frame(self.root, bg=UI.BG_BASE)

        sidebar_width = int(64 * scale_factor)
        self.main_shell.columnconfigure(0, minsize=sidebar_width, weight=0)  # Vùng C1 - Sidebar
        self.main_shell.columnconfigure(1, minsize=int(960 * scale_factor), weight=1)  # Vùng B - Workspace

        self.main_shell.rowconfigure(0, minsize=int(96 * scale_factor), weight=0)  # Vùng A - Action Bar
        self.main_shell.rowconfigure(1, minsize=int(540 * scale_factor), weight=1)  # Vùng B - Workspace

        # Ensure main_shell fills root window
        self.main_shell.grid_rowconfigure(1, weight=1)
        self.main_shell.grid_columnconfigure(0, minsize=sidebar_width, weight=0)
        self.main_shell.grid_columnconfigure(1, weight=1)

        self.main_shell.rowconfigure(2, minsize=int(36 * scale_factor), weight=0)  # Vùng C2 - Logs, footer full-width

        # Vùng A: Quick Action Bar (Spans full width)
        self.shell_zone_a = tk.Frame(self.main_shell, bg=UI.BG_BASE, height=int(96 * scale_factor))
        self.shell_zone_a.grid(row=0, column=0, columnspan=2, sticky="nsew")
        self.shell_zone_a.grid_propagate(False)

        # Vùng C1: Secondary Configuration Sidebar (Spans rows 1 and 2)
        self.shell_zone_c1 = ResponsiveGridBase(self.main_shell, bg=UI.BG_ELEVATED, width=sidebar_width)
        self.shell_zone_c1.grid(row=1, column=0, rowspan=2, sticky="nsew")
        self.shell_zone_c1.get_content_frame().configure(padx=4, pady=12, bg=UI.BG_ELEVATED)
        self.shell_zone_c1.grid_propagate(False)

        # Vùng B: Main Workspace
        self.shell_zone_b = tk.Frame(self.main_shell, bg=UI.BG_BASE)
        self.shell_zone_b.grid(row=1, column=1, sticky="nsew")

        # DB Status Bar (bottom of window)
        self.status_bar_frame = tk.Frame(
            self.root,
            bg=UI.BG_SUBTLE,
            height=24,
            bd=0,
            highlightbackground=UI.BORDER_SUBTLE,
            highlightthickness=1,
        )
        self.status_bar_frame.grid(row=1, column=0, columnspan=7, sticky="ew")
        self.status_bar_frame.pack_propagate(False)

        self.main_shell.grid(row=0, column=0, columnspan=7, sticky="nsew", pady=(10, 0))
