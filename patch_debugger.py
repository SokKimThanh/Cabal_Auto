import re

with open("ui/components/vision_snapshot_debugger.py", "r") as f:
    content = f.read()

# Replace VisionSnapshotDebugger init and layout
search = """class VisionSnapshotDebugger:
    def __init__(self, app):
        self.app = app
        self.toplevel = None
        self.canvas = None
        self.current_image = None

        # Resolve vision engine either directly from the app (if injected/cached)
        # or via the singleton accessor
        if hasattr(self.app, "_vision_engine") and self.app._vision_engine is not None:
            self.vision_engine = self.app._vision_engine
        else:
            self.vision_engine = get_vision_engine()

    def _get_translation(self, key: str, default: str) -> str:
        _t = getattr(self.app, "_t", None)
        if _t:
            return _t(key)
        return default

    def open_debugger(self):
        if self.toplevel is not None and self.toplevel.winfo_exists():
            self.toplevel.lift()
            return

        self.toplevel = tk.Toplevel()
        self.toplevel.title(self._get_translation("vision_debugger.title", "Vision Debugger"))
        self.toplevel.geometry("1100x700") # Wider for dual panes
        self.toplevel.configure(bg=UI.BG_BASE)

        # Main PanedWindow layout
        self.paned_window = ttk.PanedWindow(self.toplevel, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True, padx=UI.SPACE_MD, pady=UI.SPACE_MD)

        # LEFT PANE: Canvas and Header
        self.left_frame_container = ResponsiveGridBase(self.paned_window, bg=UI.BG_BASE)
        self.left_frame = self.left_frame_container.get_content_frame()
        self.paned_window.add(self.left_frame_container, weight=3) # 75% width

        # Header controls
        header_frame = tk.Frame(self.left_frame, bg=UI.BG_BASE)
        header_frame.pack(side=tk.TOP, fill=tk.X, pady=(0, UI.SPACE_MD))

        # Debt: use create_icon_button instead of tk.Button
        refresh_btn = create_icon_button(
            header_frame,
            icon_name="refresh",
            text=self._get_translation("vision_debugger.refresh", "Refresh Snapshot"),
            command=self._refresh_snapshot,
            button_type="primary"
        )
        refresh_btn.pack(side=tk.LEFT)

        # Canvas for image
        self.canvas = tk.Canvas(self.left_frame, bg=UI.BG_SURFACE, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # RIGHT PANE: ROIs Panel
        self.right_frame = tk.Frame(self.paned_window, bg=UI.BG_SURFACE)
        self.paned_window.add(self.right_frame, weight=1) # 25% width

        # Header for Right Panel
        roi_header_label = tk.Label(
            self.right_frame,
            text=self._get_translation("vision_debugger.system_rois", "System ROIs"),
            font=UI.get_font(role="header"),
            bg=UI.BG_SURFACE,
            fg=UI.TEXT_PRIMARY
        )
        roi_header_label.pack(side=tk.TOP, fill=tk.X, padx=UI.SPACE_MD, pady=UI.SPACE_MD)

        # Scrollable area for ROI cards using ResponsiveGridBase
        self.roi_responsive_grid = ResponsiveGridBase(self.right_frame, bg=UI.BG_SURFACE)
        self.roi_responsive_grid.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.roi_scrollable_frame = self.roi_responsive_grid.get_content_frame()

        # Handle window close to clear image reference
        self.toplevel.protocol("WM_DELETE_WINDOW", self._on_close)

        # Initial load
        self._refresh_snapshot()"""

replace = """class VisionSnapshotDebugger(tk.Frame):
    def __init__(self, parent, app, **kwargs):
        super().__init__(parent, bg=UI.BG_BASE, **kwargs)
        self.app = app

        # Memory management for images to prevent leaks
        self._tab_images = {
            "roi": None,
            "processed": None,
            "output": None
        }
        self._raw_frames = {
            "roi": None,
            "processed": None,
            "output": None
        }
        self.expanded_toplevel = None
        self.expanded_image = None

        if hasattr(self.app, "_vision_engine") and self.app._vision_engine is not None:
            self.vision_engine = self.app._vision_engine
        else:
            self.vision_engine = get_vision_engine()

        self._build_ui()

    def _get_translation(self, key: str, default: str) -> str:
        _t = getattr(self.app, "_t", None)
        if _t:
            return _t(key)
        return default

    def _build_ui(self):
        # Notebook for 4 tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=UI.SPACE_MD, pady=UI.SPACE_MD)

        # Tab 1: Ảnh ROI gốc
        self.tab_roi = tk.Frame(self.notebook, bg=UI.BG_SURFACE)
        self.notebook.add(self.tab_roi, text=self._get_translation("vision_debugger.tab_roi", "1. Original ROI"))
        self.canvas_roi = tk.Canvas(self.tab_roi, bg=UI.BG_SURFACE, highlightthickness=0)
        self.canvas_roi.pack(fill=tk.BOTH, expand=True)
        self.canvas_roi.bind("<Button-1>", lambda e: self._expand_image("roi"))

        # Tab 2: Ảnh đã tiền xử lý
        self.tab_processed = tk.Frame(self.notebook, bg=UI.BG_SURFACE)
        self.notebook.add(self.tab_processed, text=self._get_translation("vision_debugger.tab_processed", "2. Preprocessed"))
        self.canvas_processed = tk.Canvas(self.tab_processed, bg=UI.BG_SURFACE, highlightthickness=0)
        self.canvas_processed.pack(fill=tk.BOTH, expand=True)
        self.canvas_processed.bind("<Button-1>", lambda e: self._expand_image("processed"))

        # Tab 3: Kết quả OCR/Vision
        self.tab_output = tk.Frame(self.notebook, bg=UI.BG_SURFACE)
        self.notebook.add(self.tab_output, text=self._get_translation("vision_debugger.tab_output", "3. Vision Output"))
        self.canvas_output = tk.Canvas(self.tab_output, bg=UI.BG_SURFACE, highlightthickness=0)
        self.canvas_output.pack(fill=tk.BOTH, expand=True)
        self.canvas_output.bind("<Button-1>", lambda e: self._expand_image("output"))

        # Tab 4: Trạng thái Pass/Fail
        self.tab_status = tk.Frame(self.notebook, bg=UI.BG_SURFACE)
        self.notebook.add(self.tab_status, text=self._get_translation("vision_debugger.tab_status", "4. Status"))

        self.status_label = tk.Label(
            self.tab_status,
            text=self._get_translation("vision_debugger.status_waiting", "Waiting for scan..."),
            font=UI.get_font(role="header", weight="bold"),
            bg=UI.BG_SURFACE,
            fg=UI.TEXT_MUTED
        )
        self.status_label.pack(pady=UI.SPACE_LG)

        self.reason_label = tk.Label(
            self.tab_status,
            text="",
            font=UI.get_font(role="body"),
            bg=UI.BG_SURFACE,
            fg=UI.TEXT_PRIMARY
        )
        self.reason_label.pack(pady=UI.SPACE_MD)"""

new_content = content.replace(search, replace)
with open("ui/components/vision_snapshot_debugger.py", "w") as f:
    f.write(new_content)
