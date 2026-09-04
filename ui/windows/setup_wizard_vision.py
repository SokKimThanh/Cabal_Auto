"""
Setup Wizard Vision - Module riêng cho Vision System
Sprint 22 - Vision Wizard

Module này chứa giao diện và logic của VisionWizard, tách biệt khỏi form chính.
Được gọi từ form chính khi người dùng nhấn phím tắt (ví dụ: Ctrl+Shift+L).

Chức năng chính:
- Giao diện luôn nổi trên cửa sổ game (topmost=True)
- Singleton pattern: chỉ mở một instance duy nhất
- Chọn chế độ tìm kiếm template
- Quản lý danh sách template và threshold
- Preview ảnh và overlay (sẽ bổ sung sau)
- Tích hợp OpenCV và tracking quái vật (sẽ bổ sung sau)
"""

import json
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import Any, Callable, Dict, List, Optional

import cv2
import numpy as np

# Import các module cần thiết từ lib
try:
    from lib.ui_style import UIStyle as UI
except ImportError:
    # Fallback nếu không tìm thấy UIStyle
    class UIStyle:
        FONT_TITLE = ("Segoe UI", 12, "bold")
        FONT_SECTION = ("Segoe UI", 11, "bold")
        FONT_LABEL = ("Segoe UI", 10)
        FONT_TEXT = ("Segoe UI", 10)
        FONT_BUTTON = ("Segoe UI", 10)
        FONT_SMALL = ("Segoe UI", 8)
        COLOR_PRIMARY = "#2196F3"
        COLOR_PRIMARY_TEXT = "#0D47A1"
        COLOR_TEXT = "#212121"
        COLOR_SUBTEXT = "#666666"
        COLOR_ACCENT = "#4CAF50"
        COLOR_DANGER = "#F44336"
        COLOR_WARNING = "#FF7043"
        BG_DEFAULT = "#FFFFFF"
        BG_PANEL = "#F5F5F5"

    UI = UIStyle  # Alias for consistency

try:
    from lib.i18n import get_lang
    from lib.i18n import t as i18n_t
except ImportError:

    def i18n_t(
        key: str,
        *,
        ns: Optional[str] = None,
        lang: Optional[str] = None,
        default: Optional[str] = None,
    ) -> str:
        return default if default else key

    def get_lang() -> str:
        return "vi"


try:
    from ui.helpers.tooltip import I18nToolTip, attach_i18n_tooltip  # type: ignore
except ImportError:

    class I18nToolTip:  # type: ignore
        """Fallback tooltip class"""

        pass

    def attach_i18n_tooltip(
        widget,
        key: str,
        ns: Optional[str],
        lang_provider: Callable[[], str],
        delay: int = 400,
    ) -> I18nToolTip:  # type: ignore
        """Fallback tooltip function when ui.helpers.tooltip not available"""
        return I18nToolTip()  # type: ignore


try:
    from ui.helpers.icon_helper import get_icon_helper

    icon_helper = get_icon_helper()
except ImportError:
    icon_helper = None

try:
    from lib.vision.vision_engine import Detection, get_vision_engine
except ImportError:
    # Fallback nếu vision_engine chưa có
    get_vision_engine = None
    Detection = None


# ==================== SINGLETON INSTANCE ====================
_vision_wizard_instance: Optional["VisionWizard"] = None


def get_vision_wizard_instance() -> Optional["VisionWizard"]:
    """Lấy instance hiện tại của VisionWizard (nếu có)"""
    return _vision_wizard_instance


def create_or_show_vision_wizard(parent: tk.Widget, **kwargs) -> "VisionWizard":
    """
    Tạo hoặc hiển thị VisionWizard (Singleton pattern).

    Args:
        parent: Widget cha (thường là root window)
        **kwargs: Các tham số bổ sung cho VisionWizard

    Returns:
        VisionWizard instance
    """
    global _vision_wizard_instance

    if _vision_wizard_instance is not None and _vision_wizard_instance.winfo_exists():
        # Instance đã tồn tại, chỉ cần lift lên
        _vision_wizard_instance.lift()
        _vision_wizard_instance.focus_force()
        return _vision_wizard_instance
    else:
        # Tạo instance mới
        _vision_wizard_instance = VisionWizard(parent, **kwargs)
        return _vision_wizard_instance


# ==================== MAIN CLASS ====================
class VisionWizard(tk.Toplevel):
    """
    Vision Wizard - Giao diện quản lý vision system.

    Features:
    - Singleton pattern: chỉ mở một instance duy nhất
    - Topmost: luôn hiển thị trên cửa sổ game
    - Quản lý template và threshold
    - Preview và overlay (TODO)
    - Tích hợp OpenCV (TODO)
    """

    def __init__(
        self,
        parent: tk.Widget,
        config_path: str = "lib/data/config.json",
        on_close: Optional[Callable] = None,
    ):
        """
        Khởi tạo VisionWizard.

        Args:
            parent: Widget cha
            config_path: Đường dẫn đến file config
            on_close: Callback khi đóng cửa sổ
        """
        super().__init__(parent)

        # Lưu tham chiếu đến instance hiện tại
        global _vision_wizard_instance
        _vision_wizard_instance = self

        self.parent = parent
        self.config_path = config_path
        self.on_close_callback = on_close

        print(
            f"[VisionWizard] Init: parent={type(parent).__name__}, config_path={config_path}"
        )

        # Dữ liệu
        self.templates: List[Dict[str, Any]] = []
        self.current_template: Optional[Dict[str, Any]] = None
        self.search_mode: str = "position"  # position, fullscreen, region

        # Local data storage for unsaved changes
        self.local_data: Dict[str, Any] = {}
        self.unsaved_tabs: set = set()  # Track tabs with unsaved changes
        self._syncing_hotkey = (
            False  # Flag to prevent infinite loop during combobox sync
        )

        # Vision Engine
        self.vision_engine = None
        if get_vision_engine:
            try:
                self.vision_engine = get_vision_engine()
            except Exception as e:
                print(f"Error initializing vision engine: {e}")

        # UI Components (sẽ được khởi tạo trong setup_ui)
        self.notebook: Optional[ttk.Notebook] = None  # Main tab container
        self.general_tab: Optional[tk.Frame] = None
        self.hotkeys_tab: Optional[tk.Frame] = None
        self.overlay_tab: Optional[tk.Frame] = None
        self.templates_tab: Optional[tk.Frame] = None

        # General tab widgets
        self.search_mode_combo: Optional[ttk.Combobox] = None
        self.threshold_entry: Optional[tk.Entry] = None
        self.threshold_frame: Optional[tk.Frame] = (
            None  # tk.Frame (not ttk) for bg support
        )

        # Hotkeys tab widgets
        self.overlay_hotkey_combo_hotkeys: Optional[ttk.Combobox] = (
            None  # In Hotkeys tab
        )

        # Overlay tab widgets
        self.overlay_enabled_var: Optional[tk.BooleanVar] = None
        self.overlay_confidence_scale: Optional[tk.Scale] = None
        self.overlay_confidence_label: Optional[tk.Label] = None
        self.overlay_detection_interval_spinbox: Optional[tk.Spinbox] = None
        self.overlay_stable_frames_spinbox: Optional[tk.Spinbox] = None
        self.overlay_lost_timeout_spinbox: Optional[tk.Spinbox] = None
        self.overlay_hotkey_combo_overlay: Optional[ttk.Combobox] = (
            None  # In Overlay tab
        )

        # Templates tab widgets
        self.template_tree: Optional[ttk.Treeview] = None
        self.preview_canvas: Optional[tk.Canvas] = None

        # Footer widgets
        self.save_all_button: Optional[tk.Button] = None
        self.status_label: Optional[tk.Label] = None

        # Cấu hình cửa sổ
        self._setup_window()

        # Thiết lập giao diện
        self.setup_ui()

        # Kết nối sự kiện
        self.bind_events()

        # Tải cấu hình từ hunt_config.json và populate widgets
        self._load_from_config()

        # Tải dữ liệu templates
        self.load_templates()
        self.load_thresholds()

        # Center window
        self._center_window()

    def _setup_window(self) -> None:
        """Cấu hình cửa sổ chính"""
        self.title(
            i18n_t(
                "vision_wizard_title",
                ns="vision_wizard",
                default="Vision System Manager",
            )
        )
        self.geometry("900x700")
        self.minsize(800, 600)

        # Luôn hiển thị trên cùng
        self.attributes("-topmost", True)

        # Icon (nếu có)
        if icon_helper:
            try:
                icon_path = icon_helper.get_icon_path("vision")
                if icon_path and os.path.exists(icon_path):
                    self.iconbitmap(icon_path)
            except Exception:
                pass

        # Xử lý khi đóng cửa sổ
        self.protocol("WM_DELETE_WINDOW", self._on_window_close)

    def _center_window(self) -> None:
        """Căn giữa cửa sổ trên màn hình"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def setup_ui(self) -> None:
        """
        Thiết lập giao diện người dùng với cấu trúc tab.

        Layout:
        - Header: Tiêu đề và subtitle
        - Notebook (Tabs):
          - General: Search mode, threshold
          - Hotkeys Settings: Overlay hotkey configuration
          - Overlay Settings: Confidence, interval, hotkey
          - Templates: Template list and preview
        - Footer: Save All button, status label
        """
        # ===== HEADER =====
        header_frame = tk.Frame(self, bg=UI.COLOR_PRIMARY, height=80)
        header_frame.pack(fill="x", padx=0, pady=0)
        header_frame.pack_propagate(False)

        title_label = tk.Label(
            header_frame,
            text=i18n_t(
                "vision_wizard_title",
                ns="vision_wizard",
                default="Vision System Manager",
            ),
            font=UI.FONT_TITLE,
            bg=UI.COLOR_PRIMARY,
            fg="white",
        )
        title_label.pack(pady=(15, 5))

        subtitle_label = tk.Label(
            header_frame,
            text=i18n_t(
                "vision_wizard_subtitle",
                ns="vision_wizard",
                default="Cấu hình nhận diện hình ảnh và tracking",
            ),
            font=UI.FONT_LABEL,
            bg=UI.COLOR_PRIMARY,
            fg="white",
        )
        subtitle_label.pack(pady=(0, 10))

        # ===== MAIN CONTAINER =====
        main_container = tk.Frame(self, bg=UI.BG_DEFAULT)
        main_container.pack(fill="both", expand=True, padx=15, pady=15)

        # ===== NOTEBOOK (TABS) =====
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill="both", expand=True, pady=(0, 10))

        # Create tabs
        self._create_general_tab()
        self._create_hotkeys_tab()
        self._create_overlay_tab()
        self._create_templates_tab()

        # ===== FOOTER =====
        self._create_footer(main_container)

    def _create_general_tab(self) -> None:
        """Tạo tab Tổng quan (General) với search mode và threshold."""
        if self.notebook is None:
            return

        self.general_tab = tk.Frame(self.notebook, bg=UI.BG_DEFAULT)
        self.notebook.add(
            self.general_tab,
            text=i18n_t("tab_general", ns="vision_wizard", default="Tổng quan"),
        )

        # Container với padding
        container = tk.Frame(self.general_tab, bg=UI.BG_DEFAULT)
        container.pack(fill="both", expand=True, padx=20, pady=20)

        # Search Mode Section
        search_section = ttk.LabelFrame(
            container,
            text=i18n_t(
                "search_mode_label", ns="vision_wizard", default="Chế độ tìm kiếm"
            ),
            padding=15,
        )
        search_section.pack(fill="x", pady=(0, 15))

        # Chế độ tìm kiếm
        search_mode_frame = tk.Frame(search_section, bg=UI.BG_DEFAULT)
        search_mode_frame.pack(fill="x", pady=5)

        tk.Label(
            search_mode_frame,
            text=i18n_t(
                "search_mode_label", ns="vision_wizard", default="Chế độ tìm kiếm:"
            ),
            font=UI.FONT_LABEL,
            bg=UI.BG_DEFAULT,
        ).pack(side="left", padx=(0, 10))

        self.search_mode_combo = ttk.Combobox(
            search_mode_frame, font=UI.FONT_TEXT, state="readonly", width=35
        )
        self.search_mode_combo["values"] = (
            i18n_t(
                "search_mode_position",
                ns="vision_wizard",
                default="Tìm tại vị trí chỉ định",
            ),
            i18n_t(
                "search_mode_fullscreen",
                ns="vision_wizard",
                default="Tìm toàn màn hình",
            ),
            i18n_t(
                "search_mode_region", ns="vision_wizard", default="Tìm trong vùng (ROI)"
            ),
        )
        self.search_mode_combo.current(0)
        self.search_mode_combo.pack(side="left", fill="x", expand=True)

        # Threshold Section
        threshold_section = ttk.LabelFrame(
            container,
            text=i18n_t(
                "threshold_label", ns="vision_wizard", default="Ngưỡng nhận diện"
            ),
            padding=15,
        )
        threshold_section.pack(fill="x", pady=(0, 15))

        self.threshold_frame = tk.Frame(threshold_section, bg=UI.BG_DEFAULT)
        self.threshold_frame.pack(fill="x", pady=5)

        tk.Label(
            self.threshold_frame,
            text=i18n_t(
                "threshold_label", ns="vision_wizard", default="Ngưỡng nhận diện:"
            ),
            font=UI.FONT_LABEL,
            bg=UI.BG_DEFAULT,
        ).pack(side="left", padx=(0, 10))

        self.threshold_entry = tk.Entry(
            self.threshold_frame, font=UI.FONT_TEXT, width=10
        )
        self.threshold_entry.pack(side="left")
        self.threshold_entry.insert(0, "0.7")  # Giá trị mặc định

        # Info label
        tk.Label(
            self.threshold_frame,
            text=i18n_t(
                "threshold_tooltip",
                ns="vision_wizard",
                default="Độ chính xác cần thiết (0.7 = 70%)",
            ),
            font=UI.FONT_SMALL,
            fg=UI.COLOR_SUBTEXT,
            bg=UI.BG_DEFAULT,
        ).pack(side="left", padx=(10, 0))

    def _create_hotkeys_tab(self) -> None:
        """Tạo tab Phím tắt (Hotkeys Settings) với overlay hotkey combobox."""
        if self.notebook is None:
            return

        self.hotkeys_tab = tk.Frame(self.notebook, bg=UI.BG_DEFAULT)
        self.notebook.add(
            self.hotkeys_tab,
            text=i18n_t("tab_hotkeys", ns="vision_wizard", default="Phím tắt"),
        )

        # Container với padding
        container = tk.Frame(self.hotkeys_tab, bg=UI.BG_DEFAULT)
        container.pack(fill="both", expand=True, padx=20, pady=20)

        # Title with Edit button
        title_frame = tk.Frame(container, bg=UI.BG_DEFAULT)
        title_frame.pack(fill="x", pady=(0, 15))

        tk.Label(
            title_frame,
            text=i18n_t(
                "hotkey_settings_title", ns="vision_wizard", default="Cấu hình phím tắt"
            ),
            font=UI.FONT_SECTION,
            fg=UI.COLOR_PRIMARY_TEXT,
            bg=UI.BG_DEFAULT,
        ).pack(side="left")

        # Edit button (will be added in Batch 3.2)
        # TODO: Add edit button here

        # Overlay Hotkey Section
        hotkey_section = ttk.LabelFrame(
            container,
            text=i18n_t(
                "overlay_hotkey_label", ns="vision_wizard", default="Phím tắt Overlay"
            ),
            padding=15,
        )
        hotkey_section.pack(fill="x", pady=(0, 15))

        hotkey_frame = tk.Frame(hotkey_section, bg=UI.BG_DEFAULT)
        hotkey_frame.pack(fill="x", pady=5)

        tk.Label(
            hotkey_frame,
            text=i18n_t(
                "overlay_hotkey_label", ns="vision_wizard", default="Phím tắt Overlay:"
            ),
            font=UI.FONT_LABEL,
            bg=UI.BG_DEFAULT,
        ).pack(side="left", padx=(0, 10))

        self.overlay_hotkey_combo_hotkeys = ttk.Combobox(
            hotkey_frame,
            font=UI.FONT_TEXT,
            state="disabled",  # Disabled until edit mode
            width=35,
        )
        self.overlay_hotkey_combo_hotkeys["values"] = self._get_hotkey_options()
        self.overlay_hotkey_combo_hotkeys.current(0)  # Default: Ctrl+Shift+O
        self.overlay_hotkey_combo_hotkeys.pack(side="left", fill="x", expand=True)

        # Tooltip
        attach_i18n_tooltip(
            self.overlay_hotkey_combo_hotkeys,
            "overlay_hotkey_tooltip",
            ns="vision_wizard",
            lang_provider=get_lang,
        )

        # Bind change event for synchronization (will be implemented in Batch 4.1)
        self.overlay_hotkey_combo_hotkeys.bind(
            "<<ComboboxSelected>>", self._on_hotkey_changed
        )

    def _create_overlay_tab(self) -> None:
        """Tạo tab Overlay Settings với các cài đặt overlay."""
        if self.notebook is None:
            return

        self.overlay_tab = tk.Frame(self.notebook, bg=UI.BG_DEFAULT)
        self.notebook.add(
            self.overlay_tab,
            text=i18n_t("tab_overlay", ns="vision_wizard", default="Overlay"),
        )

        # Container với padding
        container = tk.Frame(self.overlay_tab, bg=UI.BG_DEFAULT)
        container.pack(fill="both", expand=True, padx=20, pady=20)

        # Title with Edit button
        title_frame = tk.Frame(container, bg=UI.BG_DEFAULT)
        title_frame.pack(fill="x", pady=(0, 15))

        tk.Label(
            title_frame,
            text=i18n_t(
                "overlay_settings_title", ns="vision_wizard", default="Cấu hình Overlay"
            ),
            font=UI.FONT_SECTION,
            fg=UI.COLOR_PRIMARY_TEXT,
            bg=UI.BG_DEFAULT,
        ).pack(side="left")

        # Edit button (will be added in Batch 3.2)
        # TODO: Add edit button here

        # Overlay Enabled Section
        enabled_frame = tk.Frame(container, bg=UI.BG_DEFAULT)
        enabled_frame.pack(fill="x", pady=(0, 15))

        self.overlay_enabled_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            enabled_frame,
            text=i18n_t(
                "overlay_enabled_label", ns="vision_wizard", default="Bật overlay"
            ),
            variable=self.overlay_enabled_var,
            font=UI.FONT_LABEL,
            bg=UI.BG_DEFAULT,
            state="disabled",  # Disabled until edit mode
        ).pack(side="left")

        # Confidence Threshold Section with Slider
        confidence_section = ttk.LabelFrame(
            container,
            text=i18n_t(
                "overlay_confidence_label", ns="vision_wizard", default="Độ tin cậy"
            ),
            padding=15,
        )
        confidence_section.pack(fill="x", pady=(0, 15))

        confidence_frame = tk.Frame(confidence_section, bg=UI.BG_DEFAULT)
        confidence_frame.pack(fill="x", pady=5)

        tk.Label(
            confidence_frame,
            text=i18n_t(
                "overlay_confidence_label", ns="vision_wizard", default="Confidence:"
            ),
            font=UI.FONT_LABEL,
            bg=UI.BG_DEFAULT,
        ).pack(side="left", padx=(0, 10))

        self.overlay_confidence_scale = tk.Scale(
            confidence_frame,
            from_=0.0,
            to=1.0,
            resolution=0.1,
            orient="horizontal",
            length=300,
            font=UI.FONT_TEXT,
            bg=UI.BG_DEFAULT,
            state="disabled",  # Disabled until edit mode
        )
        self.overlay_confidence_scale.set(0.7)  # Default value
        self.overlay_confidence_scale.pack(
            side="left", fill="x", expand=True, padx=(0, 10)
        )

        self.overlay_confidence_label = tk.Label(
            confidence_frame, text="0.7", font=UI.FONT_LABEL, bg=UI.BG_DEFAULT, width=5
        )
        self.overlay_confidence_label.pack(side="left")

        # Update label when scale changes
        self.overlay_confidence_scale.config(command=self._update_confidence_label)

        # Detection Interval Section with Spinbox
        interval_section = ttk.LabelFrame(
            container,
            text=i18n_t(
                "overlay_detection_interval_label",
                ns="vision_wizard",
                default="Tần suất phát hiện",
            ),
            padding=15,
        )
        interval_section.pack(fill="x", pady=(0, 15))

        interval_frame = tk.Frame(interval_section, bg=UI.BG_DEFAULT)
        interval_frame.pack(fill="x", pady=5)

        tk.Label(
            interval_frame,
            text=i18n_t(
                "overlay_detection_interval_label",
                ns="vision_wizard",
                default="Interval (s):",
            ),
            font=UI.FONT_LABEL,
            bg=UI.BG_DEFAULT,
        ).pack(side="left", padx=(0, 10))

        # Spinbox with +/- buttons for integer values
        spinbox_frame = tk.Frame(interval_frame, bg=UI.BG_DEFAULT)
        spinbox_frame.pack(side="left")

        self.overlay_detection_interval_spinbox = tk.Spinbox(
            spinbox_frame,
            from_=0.1,
            to=10.0,
            increment=0.1,
            width=10,
            font=UI.FONT_TEXT,
            state="disabled",  # Disabled until edit mode
        )
        self.overlay_detection_interval_spinbox.delete(0, "end")
        self.overlay_detection_interval_spinbox.insert(0, "0.1")
        self.overlay_detection_interval_spinbox.pack(side="left")

        # Stable Frames Section
        frames_section = ttk.LabelFrame(
            container,
            text=i18n_t(
                "overlay_stable_frames_label",
                ns="vision_wizard",
                default="Số khung hình ổn định",
            ),
            padding=15,
        )
        frames_section.pack(fill="x", pady=(0, 15))

        frames_frame = tk.Frame(frames_section, bg=UI.BG_DEFAULT)
        frames_frame.pack(fill="x", pady=5)

        tk.Label(
            frames_frame,
            text=i18n_t(
                "overlay_stable_frames_label",
                ns="vision_wizard",
                default="Stable Frames:",
            ),
            font=UI.FONT_LABEL,
            bg=UI.BG_DEFAULT,
        ).pack(side="left", padx=(0, 10))

        # +/- buttons with spinbox for integer
        stable_frame_controls = tk.Frame(frames_frame, bg=UI.BG_DEFAULT)
        stable_frame_controls.pack(side="left")

        self.overlay_stable_frames_spinbox = tk.Spinbox(
            stable_frame_controls,
            from_=1,
            to=10,
            increment=1,
            width=10,
            font=UI.FONT_TEXT,
            state="disabled",  # Disabled until edit mode
        )
        self.overlay_stable_frames_spinbox.delete(0, "end")
        self.overlay_stable_frames_spinbox.insert(0, "3")
        self.overlay_stable_frames_spinbox.pack(side="left")

        # Lost Timeout Section
        timeout_section = ttk.LabelFrame(
            container,
            text=i18n_t(
                "overlay_lost_timeout_label",
                ns="vision_wizard",
                default="Timeout mất dấu",
            ),
            padding=15,
        )
        timeout_section.pack(fill="x", pady=(0, 15))

        timeout_frame = tk.Frame(timeout_section, bg=UI.BG_DEFAULT)
        timeout_frame.pack(fill="x", pady=5)

        tk.Label(
            timeout_frame,
            text=i18n_t(
                "overlay_lost_timeout_label", ns="vision_wizard", default="Timeout (s):"
            ),
            font=UI.FONT_LABEL,
            bg=UI.BG_DEFAULT,
        ).pack(side="left", padx=(0, 10))

        self.overlay_lost_timeout_spinbox = tk.Spinbox(
            timeout_frame,
            from_=0.5,
            to=30.0,
            increment=0.5,
            width=10,
            font=UI.FONT_TEXT,
            state="disabled",  # Disabled until edit mode
        )
        self.overlay_lost_timeout_spinbox.delete(0, "end")
        self.overlay_lost_timeout_spinbox.insert(0, "3.0")
        self.overlay_lost_timeout_spinbox.pack(side="left")

        # Overlay Hotkey Section (synced with Hotkeys tab)
        hotkey_section = ttk.LabelFrame(
            container,
            text=i18n_t(
                "overlay_hotkey_label", ns="vision_wizard", default="Phím tắt Overlay"
            ),
            padding=15,
        )
        hotkey_section.pack(fill="x", pady=(0, 15))

        hotkey_frame = tk.Frame(hotkey_section, bg=UI.BG_DEFAULT)
        hotkey_frame.pack(fill="x", pady=5)

        tk.Label(
            hotkey_frame,
            text=i18n_t(
                "overlay_hotkey_label", ns="vision_wizard", default="Phím tắt:"
            ),
            font=UI.FONT_LABEL,
            bg=UI.BG_DEFAULT,
        ).pack(side="left", padx=(0, 10))

        self.overlay_hotkey_combo_overlay = ttk.Combobox(
            hotkey_frame,
            font=UI.FONT_TEXT,
            state="disabled",  # Disabled until edit mode
            width=35,
        )
        self.overlay_hotkey_combo_overlay["values"] = self._get_hotkey_options()
        self.overlay_hotkey_combo_overlay.current(0)  # Default: Ctrl+Shift+O
        self.overlay_hotkey_combo_overlay.pack(side="left", fill="x", expand=True)

        # Bind change event for synchronization (will be implemented in Batch 4.1)
        self.overlay_hotkey_combo_overlay.bind(
            "<<ComboboxSelected>>", self._on_hotkey_changed
        )

    def _create_templates_tab(self) -> None:
        """Tạo tab Templates với danh sách template và preview."""
        if self.notebook is None:
            return

        self.templates_tab = tk.Frame(self.notebook, bg=UI.BG_DEFAULT)
        self.notebook.add(
            self.templates_tab,
            text=i18n_t("tab_templates", ns="vision_wizard", default="Templates"),
        )

        # Container với padding
        container = tk.Frame(self.templates_tab, bg=UI.BG_DEFAULT)
        container.pack(fill="both", expand=True, padx=20, pady=20)

        # ===== TEMPLATE LIST =====
        template_panel = ttk.LabelFrame(
            container,
            text=i18n_t(
                "template_list_label", ns="vision_wizard", default="Danh sách Template"
            ),
            padding=10,
        )
        template_panel.pack(fill="both", expand=True, pady=(0, 10))

        # Treeview với scrollbar
        tree_frame = tk.Frame(template_panel)
        tree_frame.pack(fill="both", expand=True)

        # Scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical")
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal")

        # Treeview
        self.template_tree = ttk.Treeview(
            tree_frame,
            columns=("name", "path", "threshold"),
            show="headings",
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set,
            selectmode="browse",
        )

        # Configure scrollbars
        vsb.config(command=self.template_tree.yview)
        hsb.config(command=self.template_tree.xview)

        # Column headings
        self.template_tree.heading(
            "name", text=i18n_t("template_name_col", ns="vision_wizard", default="Tên")
        )
        self.template_tree.heading(
            "path",
            text=i18n_t("template_path_col", ns="vision_wizard", default="Đường dẫn"),
        )
        self.template_tree.heading(
            "threshold",
            text=i18n_t("template_threshold_col", ns="vision_wizard", default="Ngưỡng"),
        )

        # Column widths
        self.template_tree.column("name", width=150, minwidth=100)
        self.template_tree.column("path", width=350, minwidth=200)
        self.template_tree.column("threshold", width=100, minwidth=80)

        # Pack components
        self.template_tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        # ===== BUTTONS =====
        button_panel = tk.Frame(container, bg=UI.BG_DEFAULT)
        button_panel.pack(fill="x", pady=(0, 10))

        # Left buttons (Thêm, Xóa)
        left_buttons = tk.Frame(button_panel, bg=UI.BG_DEFAULT)
        left_buttons.pack(side="left")

        btn_add = ttk.Button(
            left_buttons,
            text=i18n_t(
                "btn_add_template", ns="vision_wizard", default="Thêm Template"
            ),
            command=self.add_template,
        )
        btn_add.pack(side="left", padx=5)
        attach_i18n_tooltip(
            btn_add, "tooltip_add_template", ns="vision_wizard", lang_provider=get_lang
        )

        btn_remove = ttk.Button(
            left_buttons,
            text=i18n_t("btn_remove_template", ns="vision_wizard", default="Xóa"),
            command=self.remove_template,
        )
        btn_remove.pack(side="left", padx=5)
        attach_i18n_tooltip(
            btn_remove,
            "tooltip_remove_template",
            ns="vision_wizard",
            lang_provider=get_lang,
        )

        # Right buttons (Lưu, Test)
        right_buttons = tk.Frame(button_panel, bg=UI.BG_DEFAULT)
        right_buttons.pack(side="right")

        btn_save = ttk.Button(
            right_buttons,
            text=i18n_t("btn_save_threshold", ns="vision_wizard", default="Lưu Ngưỡng"),
            command=self.save_threshold,
        )
        btn_save.pack(side="left", padx=5)
        attach_i18n_tooltip(
            btn_save,
            "tooltip_save_threshold",
            ns="vision_wizard",
            lang_provider=get_lang,
        )

        btn_test = ttk.Button(
            right_buttons,
            text=i18n_t(
                "btn_test_recognition", ns="vision_wizard", default="Test Nhận Diện"
            ),
            command=self.test_recognition,
        )
        btn_test.pack(side="left", padx=5)
        attach_i18n_tooltip(
            btn_test,
            "tooltip_test_recognition",
            ns="vision_wizard",
            lang_provider=get_lang,
        )

        # ===== PREVIEW PANEL =====
        preview_panel = ttk.LabelFrame(
            container,
            text=i18n_t(
                "preview_label", ns="vision_wizard", default="Preview / Overlay"
            ),
            padding=10,
        )
        preview_panel.pack(fill="both", expand=False, pady=(0, 0))

        # Canvas để hiển thị preview
        self.preview_canvas = tk.Canvas(
            preview_panel, width=700, height=120, bg="#f0f0f0", relief="sunken", bd=2
        )
        self.preview_canvas.pack(fill="both", expand=True)

        # Placeholder text
        self.preview_canvas.create_text(
            350,
            60,
            text=i18n_t(
                "preview_placeholder",
                ns="vision_wizard",
                default="Vùng preview sẽ hiển thị ở đây",
            ),
            font=UI.FONT_LABEL,
            fill="gray",
        )

    def _create_footer(self, parent: tk.Widget) -> None:
        """Tạo footer với Save All button và status label."""
        footer_frame = tk.Frame(parent, bg=UI.BG_DEFAULT, height=50)
        footer_frame.pack(fill="x", pady=(10, 0))
        footer_frame.pack_propagate(False)

        # Status label (left side)
        status_frame = tk.Frame(footer_frame, bg=UI.BG_DEFAULT)
        status_frame.pack(side="left", fill="y")

        self.status_label = tk.Label(
            status_frame,
            text=i18n_t("status_saved", ns="vision_wizard", default="✓ Đã lưu"),
            font=UI.FONT_LABEL,
            fg=UI.COLOR_ACCENT,
            bg=UI.BG_DEFAULT,
        )
        self.status_label.pack(pady=10)

        # Buttons (right side)
        button_frame = tk.Frame(footer_frame, bg=UI.BG_DEFAULT)
        button_frame.pack(side="right", fill="y")

        # Close button
        from ui.helpers.button_styles import get_button_config

        btn_close = tk.Button(
            button_frame,
            text=i18n_t("btn_close", ns="vision_wizard", default="Đóng"),
            command=self._on_window_close,
            **get_button_config("blue"),
            width=10,
        )
        btn_close.pack(side="right", padx=5, pady=10)

        # Save All button (will be fully implemented in Batch 3.3)
        self.save_all_button = tk.Button(
            button_frame,
            text=i18n_t("btn_save_all", ns="vision_wizard", default="Lưu toàn bộ"),
            command=self._save_all_changes,
            **get_button_config("green"),
            width=12,
        )
        self.save_all_button.pack(side="right", padx=5, pady=10)
        attach_i18n_tooltip(
            self.save_all_button,
            "tooltip_save_all",
            ns="vision_wizard",
            lang_provider=get_lang,
        )

    def _get_hotkey_options(self) -> tuple:
        """Lấy danh sách các tùy chọn phím tắt cho overlay."""
        options = [
            i18n_t(
                "hotkey_option_default",
                ns="vision_wizard",
                default="Ctrl+Shift+O (Mặc định)",
            ),
        ]

        # Add F1-F12
        for i in range(1, 13):
            options.append(
                i18n_t(
                    "hotkey_option_f_key", ns="vision_wizard", default=f"F{i}"
                ).format(i)
            )

        # Add Ctrl+F1-F12
        for i in range(1, 13):
            options.append(
                i18n_t(
                    "hotkey_option_ctrl_f", ns="vision_wizard", default=f"Ctrl+F{i}"
                ).format(i)
            )

        # Add Alt+F1-F12
        for i in range(1, 13):
            options.append(
                i18n_t(
                    "hotkey_option_alt_f", ns="vision_wizard", default=f"Alt+F{i}"
                ).format(i)
            )

        # Add Ctrl+Shift+F1-F12
        for i in range(1, 13):
            options.append(
                i18n_t(
                    "hotkey_option_ctrl_shift_f",
                    ns="vision_wizard",
                    default=f"Ctrl+Shift+F{i}",
                ).format(i)
            )

        return tuple(options)

    def _on_hotkey_changed(self, event: Any) -> None:
        """Xử lý khi người dùng thay đổi hotkey (sẽ implement sync trong Batch 4.1)."""
        # TODO: Implement synchronization in Batch 4.1
        # Mark tab as having unsaved changes
        if self.notebook is not None:
            current_tab = self.notebook.select()
            self.unsaved_tabs.add(current_tab)
            self._update_save_status()

    def _update_save_status(self) -> None:
        """Cập nhật trạng thái Save All button và status label."""
        if len(self.unsaved_tabs) > 0:
            # Has unsaved changes - orange warning state
            from ui.helpers.button_styles import get_button_config

            config = get_button_config("orange")
            if self.save_all_button is not None:
                self.save_all_button.config(**config)
            if self.status_label is not None:
                self.status_label.config(
                    text=i18n_t(
                        "status_unsaved", ns="vision_wizard", default="⚠️ Chưa lưu"
                    ),
                    fg=UI.COLOR_WARNING,
                )
        else:
            # All saved - green success state
            from ui.helpers.button_styles import get_button_config

            config = get_button_config("green")
            if self.save_all_button is not None:
                self.save_all_button.config(**config)
            if self.status_label is not None:
                self.status_label.config(
                    text=i18n_t("status_saved", ns="vision_wizard", default="✓ Đã lưu"),
                    fg=UI.COLOR_ACCENT,
                )

    def _save_all_changes(self) -> None:
        """
        Lưu tất cả thay đổi vào file config.

        Workflow:
        1. Collect current widget values to local_data
        2. Validate data (hotkey conflicts, ranges, etc.)
        3. Write to hunt_config.json
        4. Clear unsaved tabs
        5. Update UI status
        """
        try:
            # Step 1: Collect current widget values
            self._collect_widget_values()

            # Step 2: Validate (will be fully implemented in Batch 4.2)
            # For now, just basic validation
            if not self._validate_basic():
                return

            # Step 3: Save to config file
            if self._save_to_config():
                # Step 4 & 5: Clear unsaved and update UI
                self.unsaved_tabs.clear()
                self._update_save_status()
                messagebox.showinfo(
                    i18n_t("info_settings_saved", ns="vision_wizard", default="Đã lưu"),
                    i18n_t(
                        "info_settings_saved",
                        ns="vision_wizard",
                        default="Đã lưu cài đặt thành công",
                    ),
                )
            else:
                messagebox.showerror(
                    "Error", "Không thể lưu cài đặt. Vui lòng kiểm tra file config."
                )
        except Exception as e:
            print(f"[VisionWizard] Error saving changes: {e}")
            messagebox.showerror("Error", f"Lỗi khi lưu cài đặt: {str(e)}")

    def _collect_widget_values(self) -> None:
        """
        Thu thập giá trị hiện tại từ tất cả widgets vào local_data.

        Collects from:
        - Overlay hotkey comboboxes (both tabs)
        - Overlay enabled checkbox
        - Confidence slider
        - Detection interval, stable frames, lost timeout spinboxes
        """
        try:
            # Get overlay hotkey from combobox
            if self.overlay_hotkey_combo_hotkeys is not None:
                selected_index = self.overlay_hotkey_combo_hotkeys.current()
                hotkey_value = self._get_hotkey_from_index(selected_index)
                self.local_data["overlay_hotkey"] = hotkey_value

            # Get overlay enabled
            if self.overlay_enabled_var is not None:
                self.local_data["overlay_enabled"] = self.overlay_enabled_var.get()

            # Get confidence threshold
            if self.overlay_confidence_scale is not None:
                self.local_data["confidence_threshold"] = (
                    self.overlay_confidence_scale.get()
                )

            # Get detection interval
            if self.overlay_detection_interval_spinbox is not None:
                try:
                    interval_str = self.overlay_detection_interval_spinbox.get()
                    self.local_data["detection_interval"] = float(interval_str)
                except ValueError:
                    self.local_data["detection_interval"] = 0.1  # Default

            # Get stable frames
            if self.overlay_stable_frames_spinbox is not None:
                try:
                    frames_str = self.overlay_stable_frames_spinbox.get()
                    self.local_data["stable_frames"] = int(frames_str)
                except ValueError:
                    self.local_data["stable_frames"] = 3  # Default

            # Get lost timeout
            if self.overlay_lost_timeout_spinbox is not None:
                try:
                    timeout_str = self.overlay_lost_timeout_spinbox.get()
                    self.local_data["lost_timeout"] = float(timeout_str)
                except ValueError:
                    self.local_data["lost_timeout"] = 3.0  # Default

            print(f"[VisionWizard] Collected widget values: {self.local_data}")

        except Exception as e:
            print(f"[VisionWizard] Error collecting widget values: {e}")
            raise

    def _get_hotkey_from_index(self, index: int) -> str:
        """
        Convert combobox index to hotkey string.

        Args:
            index: Combobox selected index (0-48)

        Returns:
            str: Hotkey string (e.g., 'ctrl+shift+o', 'f1', 'ctrl+f5')
        """
        if index == 0:
            return "ctrl+shift+o"  # Default
        elif 1 <= index <= 12:
            return f"f{index}"
        elif 13 <= index <= 24:
            return f"ctrl+f{index - 12}"
        elif 25 <= index <= 36:
            return f"alt+f{index - 24}"
        elif 37 <= index <= 48:
            return f"ctrl+shift+f{index - 36}"
        else:
            return "ctrl+shift+o"  # Fallback

    def _validate_basic(self) -> bool:
        """
        Basic validation của local_data.

        Validates:
        - Overlay hotkey not empty
        - Confidence in range [0.0, 1.0]
        - Detection interval > 0
        - Stable frames > 0
        - Lost timeout > 0

        Returns:
            bool: True if valid, False otherwise (shows error message)
        """
        try:
            # Validate hotkey
            hotkey = self.local_data.get("overlay_hotkey", "")
            if not hotkey:
                messagebox.showerror(
                    i18n_t("error_hotkey_empty", ns="vision_wizard", default="Lỗi"),
                    i18n_t(
                        "error_hotkey_empty",
                        ns="vision_wizard",
                        default="Phím tắt không được để trống",
                    ),
                )
                return False

            # Validate confidence range
            confidence = self.local_data.get("confidence_threshold", 0.7)
            if not (0.0 <= confidence <= 1.0):
                messagebox.showerror(
                    i18n_t("error_confidence_range", ns="vision_wizard", default="Lỗi"),
                    i18n_t(
                        "error_confidence_range",
                        ns="vision_wizard",
                        default="Độ tin cậy phải từ 0.0 đến 1.0",
                    ),
                )
                return False

            # Validate detection interval
            interval = self.local_data.get("detection_interval", 0.1)
            if interval <= 0:
                messagebox.showerror(
                    i18n_t("error_interval_range", ns="vision_wizard", default="Lỗi"),
                    i18n_t(
                        "error_interval_range",
                        ns="vision_wizard",
                        default="Tần suất phát hiện phải lớn hơn 0",
                    ),
                )
                return False

            # Validate stable frames
            frames = self.local_data.get("stable_frames", 3)
            if frames <= 0:
                messagebox.showerror(
                    "Validation Error", "Số khung hình ổn định phải lớn hơn 0"
                )
                return False

            # Validate lost timeout
            timeout = self.local_data.get("lost_timeout", 3.0)
            if timeout <= 0:
                messagebox.showerror(
                    "Validation Error", "Timeout mất dấu phải lớn hơn 0"
                )
                return False

            return True

        except Exception as e:
            print(f"[VisionWizard] Validation error: {e}")
            messagebox.showerror("Validation Error", f"Lỗi validation: {str(e)}")
            return False

    def _save_to_config(self) -> bool:
        """
        Ghi local_data vào hunt_config.json.

        Updates:
        - global_hotkeys.overlay_toggle_key
        - overlay.enabled
        - monster_tracking.confidence_threshold
        - monster_tracking.detection_interval
        - monster_tracking.stable_frames
        - monster_tracking.lost_timeout

        Returns:
            bool: True if save successful, False otherwise
        """
        config_path = "lib/data/hunt_config.json"

        try:
            # Read current config
            if os.path.exists(config_path):
                with open(config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
            else:
                config = {}

            # Update global_hotkeys section
            if "global_hotkeys" not in config:
                config["global_hotkeys"] = {}
            config["global_hotkeys"]["overlay_toggle_key"] = self.local_data.get(
                "overlay_hotkey", "ctrl+shift+o"
            )

            # Update overlay section
            if "overlay" not in config:
                config["overlay"] = {}
            config["overlay"]["enabled"] = self.local_data.get("overlay_enabled", False)

            # Update monster_tracking section
            if "monster_tracking" not in config:
                config["monster_tracking"] = {}

            config["monster_tracking"]["confidence_threshold"] = self.local_data.get(
                "confidence_threshold", 0.7
            )
            config["monster_tracking"]["detection_interval"] = self.local_data.get(
                "detection_interval", 0.1
            )
            config["monster_tracking"]["stable_frames"] = self.local_data.get(
                "stable_frames", 3
            )
            config["monster_tracking"]["lost_timeout"] = self.local_data.get(
                "lost_timeout", 3.0
            )

            # Write back to file with pretty formatting
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2, ensure_ascii=False)

            print(f"[VisionWizard] Config saved successfully to {config_path}")
            return True

        except Exception as e:
            print(f"[VisionWizard] Error saving config: {e}")
            return False

    def _load_from_config(self) -> None:
        """
        Load cấu hình từ hunt_config.json và populate widgets.

        Loads:
        - global_hotkeys.overlay_toggle_key (default: 'ctrl+shift+o')
        - monster_tracking.* settings (enabled, confidence, interval, etc.)
        - overlay.enabled

        Populates all tab widgets with loaded values.
        """
        config_path = "lib/data/hunt_config.json"

        # Default values
        defaults = {
            "overlay_hotkey": "ctrl+shift+o",
            "overlay_enabled": False,
            "confidence_threshold": 0.7,
            "detection_interval": 0.1,
            "stable_frames": 3,
            "lost_timeout": 3.0,
        }

        # Try to load from config file
        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)

                # Extract global_hotkeys.overlay_toggle_key
                global_hotkeys = config.get("global_hotkeys", {})
                overlay_hotkey = global_hotkeys.get(
                    "overlay_toggle_key", defaults["overlay_hotkey"]
                )

                # Extract overlay.enabled
                overlay = config.get("overlay", {})
                overlay_enabled = overlay.get("enabled", defaults["overlay_enabled"])

                # Extract monster_tracking settings
                monster_tracking = config.get("monster_tracking", {})
                confidence_threshold = monster_tracking.get(
                    "confidence_threshold", defaults["confidence_threshold"]
                )
                detection_interval = monster_tracking.get(
                    "detection_interval", defaults["detection_interval"]
                )
                stable_frames = monster_tracking.get(
                    "stable_frames", defaults["stable_frames"]
                )
                lost_timeout = monster_tracking.get(
                    "lost_timeout", defaults["lost_timeout"]
                )

                # Store in local_data
                self.local_data = {
                    "overlay_hotkey": overlay_hotkey,
                    "overlay_enabled": overlay_enabled,
                    "confidence_threshold": confidence_threshold,
                    "detection_interval": detection_interval,
                    "stable_frames": stable_frames,
                    "lost_timeout": lost_timeout,
                }

                print(f"[VisionWizard] Loaded config: {self.local_data}")

            except Exception as e:
                print(f"[VisionWizard] Error loading config: {e}")
                self.local_data = defaults.copy()
        else:
            print("[VisionWizard] Config not found, using defaults")
            self.local_data = defaults.copy()

        # Populate widgets with loaded values
        self._populate_widgets_from_local_data()

    def _populate_widgets_from_local_data(self) -> None:
        """Populate tất cả widgets với giá trị từ local_data."""
        try:
            # Populate overlay hotkey comboboxes
            overlay_hotkey = self.local_data.get("overlay_hotkey", "ctrl+shift+o")
            hotkey_index = self._find_hotkey_index(overlay_hotkey)

            if self.overlay_hotkey_combo_hotkeys is not None:
                self.overlay_hotkey_combo_hotkeys.current(hotkey_index)
            if self.overlay_hotkey_combo_overlay is not None:
                self.overlay_hotkey_combo_overlay.current(hotkey_index)

            # Populate overlay enabled checkbox
            if self.overlay_enabled_var is not None:
                self.overlay_enabled_var.set(
                    self.local_data.get("overlay_enabled", False)
                )

            # Populate confidence slider
            if self.overlay_confidence_scale is not None:
                confidence = self.local_data.get("confidence_threshold", 0.7)
                self.overlay_confidence_scale.set(confidence)
                if self.overlay_confidence_label is not None:
                    self.overlay_confidence_label.config(text=f"{confidence:.1f}")

            # Populate detection interval spinbox
            if self.overlay_detection_interval_spinbox is not None:
                interval = self.local_data.get("detection_interval", 0.1)
                self.overlay_detection_interval_spinbox.delete(0, "end")
                self.overlay_detection_interval_spinbox.insert(0, str(interval))

            # Populate stable frames spinbox
            if self.overlay_stable_frames_spinbox is not None:
                frames = self.local_data.get("stable_frames", 3)
                self.overlay_stable_frames_spinbox.delete(0, "end")
                self.overlay_stable_frames_spinbox.insert(0, str(frames))

            # Populate lost timeout spinbox
            if self.overlay_lost_timeout_spinbox is not None:
                timeout = self.local_data.get("lost_timeout", 3.0)
                self.overlay_lost_timeout_spinbox.delete(0, "end")
                self.overlay_lost_timeout_spinbox.insert(0, str(timeout))

            print("[VisionWizard] Widgets populated from local_data")

        except Exception as e:
            print(f"[VisionWizard] Error populating widgets: {e}")

    def _find_hotkey_index(self, hotkey_str: str) -> int:
        """
        Tìm index của hotkey trong combobox values.

        Args:
            hotkey_str: Hotkey string (e.g., 'ctrl+shift+o', 'f1', 'ctrl+f5')

        Returns:
            int: Index trong combobox, hoặc 0 (default) nếu không tìm thấy
        """
        # Normalize hotkey string
        hotkey_normalized = hotkey_str.lower().strip()

        # Map hotkey to display format
        hotkey_map = {
            "ctrl+shift+o": 0,  # Default
        }

        # F1-F12
        for i in range(1, 13):
            hotkey_map[f"f{i}"] = i

        # Ctrl+F1-F12
        for i in range(1, 13):
            hotkey_map[f"ctrl+f{i}"] = 12 + i

        # Alt+F1-F12
        for i in range(1, 13):
            hotkey_map[f"alt+f{i}"] = 24 + i

        # Ctrl+Shift+F1-F12
        for i in range(1, 13):
            hotkey_map[f"ctrl+shift+f{i}"] = 36 + i

        return hotkey_map.get(hotkey_normalized, 0)

    def _update_confidence_label(self, value: str) -> None:
        """
        Update confidence label khi slider thay đổi.

        Args:
            value: Giá trị từ Scale widget (string)
        """
        if self.overlay_confidence_label is not None:
            self.overlay_confidence_label.config(text=f"{float(value):.1f}")

    def bind_events(self) -> None:
        """
        Kết nối các sự kiện UI.

        Events:
        - Search mode combo: Khi thay đổi chế độ tìm kiếm
        - Template tree: Khi chọn template
        - Threshold entry: Validation
        """
        # Sự kiện khi thay đổi chế độ tìm kiếm
        if self.search_mode_combo:
            self.search_mode_combo.bind(
                "<<ComboboxSelected>>", self._on_search_mode_changed
            )

        # Sự kiện khi chọn template trong tree
        if self.template_tree:
            self.template_tree.bind("<<TreeviewSelect>>", self._on_template_selected)
            # Double click để edit/view
            self.template_tree.bind("<Double-1>", self._on_template_double_click)

        # Validation cho threshold entry
        if self.threshold_entry:
            # Chỉ cho phép nhập số và dấu chấm
            vcmd = (self.register(self._validate_threshold), "%P")
            self.threshold_entry.config(validate="key", validatecommand=vcmd)

        # Keyboard shortcuts
        self.bind("<Escape>", lambda e: self._on_window_close())
        self.bind("<Control-s>", lambda e: self.save_threshold())
        self.bind("<Control-t>", lambda e: self.test_recognition())
        self.bind("<Delete>", lambda e: self.remove_template())

    def load_templates(self) -> None:
        """
        Tải danh sách template từ config hoặc thư mục.

        Phase 2: Wire với vision_engine.py
        - Load từ lib/data/vision_templates.json
        - Gọi engine.load_templates() nếu có engine
        """
        # Load config JSON
        config_file = "lib/data/vision_templates.json"

        if os.path.exists(config_file):
            try:
                with open(config_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.templates = (
                        data if isinstance(data, list) else data.get("templates", [])
                    )
            except Exception as e:
                print(f"Error loading templates config: {e}")
                self.templates = []
        else:
            # Fallback: Sample data
            self.templates = [
                {
                    "id": "monster_hp_bar",
                    "name": "Monster_HP_Bar",
                    "path": "assets/images/monsters/hp_bar.png",
                    "threshold": 0.8,
                    "scales": [0.8, 1.0, 1.2],
                    "enabled": True,
                },
                {
                    "id": "skill_icon_1",
                    "name": "Skill_Icon_1",
                    "path": "assets/images/skills/skill_1.png",
                    "threshold": 0.75,
                    "scales": [1.0],
                    "enabled": True,
                },
            ]

        # Wire: Load vào vision engine
        if self.vision_engine:
            try:
                # Extract paths từ templates
                enabled_templates = [
                    t for t in self.templates if t.get("enabled", True)
                ]
                paths = [
                    t["path"]
                    for t in enabled_templates
                    if os.path.exists(t.get("path", ""))
                ]

                if paths:
                    loaded = self.vision_engine.load_templates(paths)
                    print(f"Vision engine loaded {loaded} templates")
            except Exception as e:
                print(f"Error loading templates into engine: {e}")

        self._refresh_template_tree()

    def load_thresholds(self) -> None:
        """
        Tải các ngưỡng nhận diện đã lưu.

        Phase 2: Thresholds đã embedded trong templates từ vision_templates.json
        Method này giữ lại cho backward compatibility.
        """
        # Thresholds already loaded via load_templates()
        pass

    def save_region(
        self, region_name: str, x: int, y: int, width: int, height: int
    ) -> None:
        """
        Lưu vùng ROI vào config.

        Args:
            region_name: Tên vùng (ví dụ: "monster_area", "skill_bar")
            x, y: Tọa độ góc trên bên trái
            width, height: Kích thước vùng
        """
        region_config_file = "lib/data/vision_region.json"

        try:
            # Load existing regions
            regions = {}
            if os.path.exists(region_config_file):
                with open(region_config_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    regions = data.get("regions", {})

            # Add/update region
            regions[region_name] = {"x": x, "y": y, "width": width, "height": height}

            # Save back
            with open(region_config_file, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "default_region": regions.get(
                            "default", {"x": 0, "y": 0, "width": 1920, "height": 1080}
                        ),
                        "regions": regions,
                    },
                    f,
                    indent=2,
                    ensure_ascii=False,
                )

            print(f"Region '{region_name}' saved: ({x}, {y}, {width}, {height})")

        except Exception as e:
            print(f"Error saving region: {e}")

    def load_region(self, region_name: str = "default") -> Optional[tuple]:
        """
        Load vùng ROI từ config.

        Args:
            region_name: Tên vùng cần load

        Returns:
            Tuple (x, y, width, height) hoặc None nếu không tìm thấy
        """
        region_config_file = "lib/data/vision_region.json"

        try:
            if os.path.exists(region_config_file):
                with open(region_config_file, "r", encoding="utf-8") as f:
                    data = json.load(f)

                    # Try regions dict first
                    regions = data.get("regions", {})
                    if region_name in regions:
                        r = regions[region_name]
                        return (r["x"], r["y"], r["width"], r["height"])

                    # Fallback to default_region
                    if region_name == "default" and "default_region" in data:
                        r = data["default_region"]
                        return (r["x"], r["y"], r["width"], r["height"])

            return None

        except Exception as e:
            print(f"Error loading region: {e}")
            return None

    def start_detection_loop(self) -> None:
        """
        Bắt đầu detection loop với worker thread.

        Flow:
        1. Start engine worker với frame callback
        2. Poll result_queue mỗi ~66ms (15 FPS max) bằng root.after()
        3. Render overlay lên preview_canvas

        Note:
            - Worker chạy trên background thread
            - UI chỉ blit bitmap từ queue
            - Không block main thread
        """
        if not self.vision_engine:
            messagebox.showwarning(
                i18n_t("warning", default="Cảnh báo"), "Vision engine not initialized"
            )
            return

        # Start worker với frame callback
        try:
            self.vision_engine.start_worker(frame_callback=self._get_current_frame)

            # Start UI polling loop
            self._poll_interval_ms = 66  # ~15 FPS
            self._poll_queue()

            messagebox.showinfo(
                "Detection Started",
                "Detection loop started.\n\n"
                "Worker thread is running in background.\n"
                "UI updates at ~15 FPS via queue polling.",
            )

        except Exception as e:
            messagebox.showerror(
                i18n_t("error", default="Lỗi"), f"Failed to start detection: {e}"
            )

    def stop_detection_loop(self) -> None:
        """
        Dừng detection loop và cleanup resources.
        """
        if self.vision_engine:
            self.vision_engine.stop_worker()
            print("Detection loop stopped")

    def _get_current_frame(self) -> Optional[np.ndarray]:
        """
        Frame callback cho worker thread.

        Returns:
            Current frame (np.ndarray) hoặc None

        Note:
            - TODO Phase 3: Replace với screen capture
            - Hiện tại trả về synthetic frame để test
        """
        # TODO Phase 3: Capture real game screen
        # For now, return synthetic test frame
        try:
            test_frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
            return test_frame
        except Exception as e:
            print(f"[VisionWizard] Error creating test frame: {e}")
            return None

    def _poll_queue(self) -> None:
        """
        Poll result_queue từ worker (non-blocking).

        Được gọi mỗi ~66ms bởi root.after() để không block UI.
        """
        if not self.vision_engine or not self.vision_engine.worker_running:
            return

        try:
            # Get result (non-blocking)
            result = self.vision_engine.get_result(timeout=0.0)

            if result:
                # Render overlay lên preview_canvas
                self._render_overlay(result)

        except Exception as e:
            print(f"Poll queue error: {e}")

        # Schedule next poll
        if self.vision_engine and self.vision_engine.worker_running:
            self.after(self._poll_interval_ms, self._poll_queue)

    def _render_overlay(self, result: Dict[str, Any]) -> None:
        """
        Render overlay từ worker result lên preview_canvas.

        Args:
            result: Dict with keys 'type', 'data', 'frame', 'timestamp'

        Note:
            - Frame đã được engine render overlay (boxes, labels)
            - UI chỉ convert sang PhotoImage và blit
        """
        try:
            frame = result.get("frame")
            if frame is None:
                return

            # Convert BGR to RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Convert to PhotoImage (single conversion per frame)
            from PIL import Image, ImageTk

            pil_image = Image.fromarray(frame_rgb)
            photo = ImageTk.PhotoImage(pil_image)

            # Update preview_canvas
            if hasattr(self, "preview_canvas") and self.preview_canvas:
                # Clear canvas
                self.preview_canvas.delete("all")

                # Draw image
                self.preview_canvas.create_image(0, 0, anchor="nw", image=photo)

                # Keep reference to prevent garbage collection
                self.preview_canvas.image = photo  # type: ignore

                # Update status
                result_type = result.get("type", "unknown")
                data_count = len(result.get("data", []))
                status_text = f"{result_type}: {data_count} objects"

                # TODO: Update status label if exists
                print(f"[Overlay] {status_text}")

        except Exception as e:
            print(f"Render overlay error: {e}")

    def destroy(self) -> None:
        """
        Override destroy để cleanup worker thread.
        """
        # Stop worker before closing
        self.stop_detection_loop()

        # Call parent destroy
        super().destroy()

    def add_template(self) -> None:
        """
        Thêm template mới vào danh sách.

        Phase 2: Wire với vision_engine
        - Lưu vào vision_templates.json
        - Reload engine templates
        """
        # Mở file dialog
        filetypes = [
            ("Image files", "*.png *.jpg *.jpeg *.bmp"),
            ("PNG files", "*.png"),
            ("JPEG files", "*.jpg *.jpeg"),
            ("All files", "*.*"),
        ]

        file_path = filedialog.askopenfilename(
            parent=self,
            title=i18n_t(
                "btn_add_template", ns="vision_wizard", default="Thêm Template"
            ),
            filetypes=filetypes,
        )

        if not file_path:
            return  # User cancelled

        # Validate file exists
        if not os.path.exists(file_path):
            messagebox.showerror(
                i18n_t("error", default="Lỗi"), f"File không tồn tại: {file_path}"
            )
            return

        # Extract name from filename
        name = os.path.splitext(os.path.basename(file_path))[0]

        # Thêm vào danh sách
        new_template = {
            "id": name.lower().replace(" ", "_"),
            "name": name,
            "path": file_path,
            "threshold": 0.7,  # Default
            "scales": [1.0],
            "enabled": True,
        }
        self.templates.append(new_template)

        # Refresh tree
        self._refresh_template_tree()

        # Save to config
        self._save_templates_config()

        # Reload engine templates
        if self.vision_engine:
            try:
                enabled_templates = [
                    t for t in self.templates if t.get("enabled", True)
                ]
                paths = [
                    t["path"]
                    for t in enabled_templates
                    if os.path.exists(t.get("path", ""))
                ]
                if paths:
                    self.vision_engine.load_templates(paths)
            except Exception as e:
                print(f"Error reloading engine templates: {e}")

        messagebox.showinfo(
            i18n_t("success", default="Thành công"),
            i18n_t(
                "msg_template_added",
                ns="vision_wizard",
                default="Đã thêm template thành công",
            ),
        )

    def remove_template(self) -> None:
        """
        Xóa template đang chọn khỏi danh sách.

        Phase 2: Persist to config and reload engine
        """
        if not self.template_tree:
            return

        selection = self.template_tree.selection()
        if not selection:
            messagebox.showwarning(
                i18n_t("warning", default="Cảnh báo"),
                i18n_t(
                    "msg_no_template_selected",
                    ns="vision_wizard",
                    default="Vui lòng chọn một template",
                ),
            )
            return

        # Confirm
        result = messagebox.askyesno(
            i18n_t("confirm", default="Xác nhận"), "Bạn có chắc muốn xóa template này?"
        )

        if not result:
            return

        # Get selected item
        item_id = selection[0]
        values = self.template_tree.item(item_id, "values")

        if values:
            name = values[0]
            # Tìm và xóa khỏi self.templates
            self.templates = [t for t in self.templates if t["name"] != name]

            # Refresh tree
            self._refresh_template_tree()

            # Save to config
            self._save_templates_config()

            # Reload engine templates
            if self.vision_engine:
                try:
                    enabled_templates = [
                        t for t in self.templates if t.get("enabled", True)
                    ]
                    paths = [
                        t["path"]
                        for t in enabled_templates
                        if os.path.exists(t.get("path", ""))
                    ]
                    if paths:
                        self.vision_engine.load_templates(paths)
                    else:
                        # Clear all templates if none enabled
                        self.vision_engine.templates.clear()
                except Exception as e:
                    print(f"Error reloading engine templates: {e}")

            messagebox.showinfo(
                i18n_t("success", default="Thành công"),
                i18n_t(
                    "msg_template_removed",
                    ns="vision_wizard",
                    default="Đã xóa template thành công",
                ),
            )

    def save_threshold(self) -> None:
        """
        Lưu ngưỡng nhận diện cho template đang chọn.

        Phase 2: Persist to vision_templates.json
        """
        if not self.template_tree or not self.threshold_entry:
            return

        selection = self.template_tree.selection()
        if not selection:
            messagebox.showwarning(
                i18n_t("warning", default="Cảnh báo"),
                i18n_t(
                    "msg_no_template_selected",
                    ns="vision_wizard",
                    default="Vui lòng chọn một template",
                ),
            )
            return

        # Get threshold value
        try:
            threshold = float(self.threshold_entry.get())
            if not (0.0 <= threshold <= 1.0):
                raise ValueError()
        except ValueError:
            messagebox.showerror(
                i18n_t("error", default="Lỗi"),
                i18n_t(
                    "msg_invalid_threshold",
                    ns="vision_wizard",
                    default="Ngưỡng không hợp lệ",
                ),
            )
            return

        # Get selected template
        item_id = selection[0]
        values = self.template_tree.item(item_id, "values")

        if values:
            name = values[0]
            # Update trong self.templates
            for template in self.templates:
                if template["name"] == name:
                    template["threshold"] = threshold
                    break

            # Refresh tree
            self._refresh_template_tree()

            # Save to config
            self._save_templates_config()

            messagebox.showinfo(
                i18n_t("success", default="Thành công"),
                i18n_t(
                    "msg_threshold_saved",
                    ns="vision_wizard",
                    default="Đã lưu ngưỡng thành công",
                ),
            )

    def test_recognition(self) -> None:
        """
        Chạy test nhận diện với worker thread (non-blocking).

        Phase 2: Wire với vision_engine.py
        - Start worker thread để test detection
        - Kết quả hiển thị qua queue polling
        - Không block UI thread
        """
        if not self.vision_engine:
            messagebox.showwarning(
                "Vision Engine",
                "Vision engine not initialized.\n\n"
                "Please check that lib/vision/vision_engine.py is available.",
            )
            return

        # Kiểm tra có templates loaded không
        if not self.vision_engine.templates:
            messagebox.showwarning(
                "No Templates",
                "No templates loaded.\n\n"
                "Please add templates before testing recognition.",
            )
            return

        try:
            # Start detection loop để test (sử dụng worker thread)
            self.start_detection_loop()

        except Exception as e:
            messagebox.showerror(
                "Test Error", f"Error starting test recognition:\n\n{str(e)}"
            )

    def _refresh_template_tree(self) -> None:
        """Làm mới danh sách template trong Treeview"""
        if not self.template_tree:
            return

        # Xóa tất cả items
        for item in self.template_tree.get_children():
            self.template_tree.delete(item)

        # Thêm lại từ self.templates
        for template in self.templates:
            self.template_tree.insert(
                "",
                "end",
                values=(
                    template.get("name", ""),
                    template.get("path", ""),
                    template.get("threshold", 0.7),
                ),
            )

    def _save_templates_config(self) -> None:
        """
        Lưu templates config vào file JSON.

        Phase 2: Persist templates to vision_templates.json
        """
        config_file = "lib/data/vision_templates.json"

        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(config_file), exist_ok=True)

            # Save templates
            with open(config_file, "w", encoding="utf-8") as f:
                json.dump(self.templates, f, indent=2, ensure_ascii=False)

            print(f"Templates config saved to {config_file}")

        except Exception as e:
            print(f"Error saving templates config: {e}")

    def _on_search_mode_changed(self, event=None) -> None:
        """
        Callback khi thay đổi chế độ tìm kiếm.

        TODO: Ẩn/hiện threshold entry tùy theo chế độ
        TODO: Update preview canvas
        """
        if not self.search_mode_combo:
            return

        selected = self.search_mode_combo.current()
        modes = ["position", "fullscreen", "region"]
        self.search_mode = modes[selected] if selected < len(modes) else "position"

        # TODO: Ẩn/hiện các control tùy theo chế độ
        # Ví dụ: Nếu chọn "region", hiện thêm control để chọn vùng ROI

    def _on_template_selected(self, event=None) -> None:
        """
        Callback khi chọn template trong tree.

        TODO: Update threshold entry với giá trị của template đang chọn
        TODO: Load và hiển thị preview ảnh template
        """
        if not self.template_tree or not self.threshold_entry:
            return

        selection = self.template_tree.selection()
        if not selection:
            return

        item_id = selection[0]
        values = self.template_tree.item(item_id, "values")

        if values:
            # Update threshold entry
            threshold = values[2]
            self.threshold_entry.delete(0, "end")
            self.threshold_entry.insert(0, str(threshold))

            # TODO: Load và hiển thị preview ảnh template trong canvas

    def _on_template_double_click(self, event=None) -> None:
        """
        Callback khi double-click vào template.

        TODO: Mở dialog để edit chi tiết template
        TODO: Hoặc mở file ảnh template bằng viewer mặc định
        """
        # Placeholder
        pass

    def _validate_threshold(self, value: str) -> bool:
        """
        Validate threshold entry (chỉ cho phép số và dấu chấm).

        Args:
            value: Giá trị đang nhập

        Returns:
            True nếu hợp lệ, False nếu không
        """
        if value == "":
            return True

        # Chỉ cho phép số, dấu chấm, và tối đa 1 dấu chấm
        if value.count(".") > 1:
            return False

        try:
            float(value)
            return True
        except ValueError:
            return False

    def _on_window_close(self) -> None:
        """
        Xử lý khi đóng cửa sổ.

        TODO: Cleanup resources
        """
        # Check unsaved changes
        if hasattr(self, "unsaved_tabs") and len(self.unsaved_tabs) > 0:
            result = messagebox.askyesno(
                i18n_t(
                    "confirm_unsaved_title",
                    ns="vision_wizard",
                    default="Có thay đổi chưa lưu",
                ),
                i18n_t(
                    "confirm_unsaved_message",
                    ns="vision_wizard",
                    default="Bạn có thay đổi chưa lưu.\nBạn có chắc chắn muốn thoát và mất các thay đổi?",
                ),
            )

            if not result:
                # User selected "No", abort closing
                return

        # Call callback nếu có
        if self.on_close_callback:
            try:
                self.on_close_callback()
            except Exception as e:
                print(f"Error in on_close callback: {e}")

        # Destroy window
        self.destroy()

        # Clear singleton reference
        global _vision_wizard_instance
        _vision_wizard_instance = None


# ==================== HELPER FUNCTIONS ====================
def open_vision_wizard_from_parent(parent: tk.Widget, **kwargs) -> None:
    """
    Hàm tiện ích để mở VisionWizard từ form chính.

    Usage từ form chính:
        from ui.setup_wizard_vision import open_vision_wizard_from_parent

        # Bind hotkey
        root.bind('<Control-Shift-L>', lambda e: open_vision_wizard_from_parent(root))

    Args:
        parent: Widget cha (thường là root window)
        **kwargs: Các tham số bổ sung
    """
    create_or_show_vision_wizard(parent, **kwargs)


# ==================== MAIN (FOR TESTING) ====================
if __name__ == "__main__":
    """
    Test module độc lập.

    Run:
        python -m ui.setup_wizard_vision
    """
    root = tk.Tk()
    root.title("Test Vision Wizard")
    root.geometry("400x300")

    def test_open_wizard():
        """Test function để mở wizard"""
        wizard = create_or_show_vision_wizard(root)
        print(f"Wizard created: {wizard}")

    # Button để test
    btn = tk.Button(
        root,
        text="Open Vision Wizard\n(Ctrl+Shift+L)",
        font=("Segoe UI", 12),
        command=test_open_wizard,
        width=20,
        height=3,
    )
    btn.pack(expand=True)

    # Bind hotkey
    root.bind("<Control-Shift-L>", lambda e: test_open_wizard())

    print(
        "Test window started. Press Ctrl+Shift+L or click button to open Vision Wizard."
    )
    root.mainloop()
