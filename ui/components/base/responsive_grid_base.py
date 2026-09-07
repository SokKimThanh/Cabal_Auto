import tkinter as tk
from tkinter import ttk
import logging
import sys

logger = logging.getLogger(__name__)

class ResponsiveGridBase(tk.Frame):
    """
    A responsive grid container with a scrollable canvas.
    Ensures zero-occlusion by providing vertical scrolling when space is limited.
    """

    # Valid kwargs for tk.Frame
    _VALID_KWARGS = {
        'bg', 'bd', 'bg', 'border', 'borderwidth', 'class', 'colormap',
        'container', 'cursor', 'height', 'highlightbackground',
        'highlightcolor', 'highlightthickness', 'padx', 'pady',
        'relief', 'takefocus', 'visual', 'width', 'background'
    }

    def __init__(self, parent, *args, **kwargs):
        # Filter kwargs to avoid _tkinter.TclError if subclasses pass unsupported kwargs
        frame_kwargs = {k: v for k, v in kwargs.items() if k in self._VALID_KWARGS}
        super().__init__(parent, *args, **frame_kwargs)

        self._parent = parent
        self._resize_timer = None
        self._scroll_debounce_timer = None
        self._is_mounted = False

        # Setup layout
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Canvas for scrolling
        canvas_bg = frame_kwargs.get('bg') or frame_kwargs.get('background') or self.cget('bg')
        self.canvas = tk.Canvas(self, bg=canvas_bg, highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="nsew")

        # Scrollbar
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Inner Content Frame
        self.content_frame = tk.Frame(self.canvas, bg=canvas_bg)
        self.content_window = self.canvas.create_window((0, 0), window=self.content_frame, anchor="nw")

        # Bindings
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.content_frame.bind("<Configure>", self._on_frame_configure)

        # Mouse scrolling bindings
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

        # Also bind to content frame to ensure scroll works when hovering over children
        self.content_frame.bind("<Enter>", self._on_enter)
        self.content_frame.bind("<Leave>", self._on_leave)

        self._on_mount()

    def _on_mount(self):
        """Lifecycle event when component is initialized."""
        logger.debug(f"[ResponsiveGridBase] Component mounted: {self.__class__.__name__}")
        self._is_mounted = True

    def _on_resize(self, width, height):
        """Lifecycle event when component changes size."""
        logger.debug(f"[ResponsiveGridBase] Size changed: {width}x{height} - {self.__class__.__name__}")

    def get_content_frame(self):
        """Returns the inner frame where child widgets should be placed."""
        return self.content_frame

    def _on_canvas_configure(self, event):
        """Update the inner frame's width to match the canvas."""
        if self.canvas.winfo_width() > 0:
            self.canvas.itemconfig(self.content_window, width=event.width)
            if self._resize_timer:
                self.after_cancel(self._resize_timer)
            self._resize_timer = self.after(100, lambda: self._on_resize(event.width, event.height))

    def _on_frame_configure(self, event=None):
        """Update the scrollregion when the inner frame changes size (debounced)."""
        if self._scroll_debounce_timer:
            try:
                self.after_cancel(self._scroll_debounce_timer)
            except Exception:
                pass
        self._scroll_debounce_timer = self.after(50, self._update_scrollregion)

    def _update_scrollregion(self):
        try:
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        except tk.TclError:
            pass # Widget might have been destroyed

    def _on_enter(self, event=None):
        """Bind mouse wheel scrolling cross-platform when mouse enters the widget."""
        if sys.platform == "win32" or sys.platform == "darwin":
            self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        else:
            self.canvas.bind_all("<Button-4>", self._on_mousewheel)
            self.canvas.bind_all("<Button-5>", self._on_mousewheel)

    def _on_leave(self, event=None):
        """Unbind mouse wheel scrolling when mouse leaves the actual component."""
        # Avoid unbinding if hovering over child widgets inside the grid
        if event is not None:
            widget_under_mouse = self.winfo_containing(event.x_root, event.y_root)
            # If the widget under the mouse is a descendant of self, don't unbind
            if widget_under_mouse and (widget_under_mouse == self or str(widget_under_mouse).startswith(str(self) + ".")):
                return

        if sys.platform == "win32" or sys.platform == "darwin":
            self.canvas.unbind_all("<MouseWheel>")
        else:
            self.canvas.unbind_all("<Button-4>")
            self.canvas.unbind_all("<Button-5>")

    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling safely."""
        try:
            if sys.platform == "win32":
                self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            elif sys.platform == "darwin":
                # macOS usually sends delta as actual units to scroll
                self.canvas.yview_scroll(int(-1 * event.delta), "units")
            elif event.num == 4:
                self.canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                self.canvas.yview_scroll(1, "units")
        except Exception:
            pass # Ignore errors if widget is destroyed during event processing
