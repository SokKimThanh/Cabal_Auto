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

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
import numpy as np
import cv2
from typing import Optional, Dict, List, Any, Callable

# Import các module cần thiết từ lib
try:
    from lib.ui_style import UIStyle as UI
except ImportError:
    # Fallback nếu không tìm thấy UIStyle
    class UI:
        FONT_TITLE = ('Segoe UI', 12, 'bold')
        FONT_SECTION = ('Segoe UI', 11, 'bold')
        FONT_LABEL = ('Segoe UI', 10)
        FONT_TEXT = ('Segoe UI', 10)
        FONT_BUTTON = ('Segoe UI', 10)
        FONT_SMALL = ('Segoe UI', 8)
        COLOR_PRIMARY = '#2196F3'
        COLOR_TEXT = '#212121'
        COLOR_ACCENT = '#4CAF50'
        COLOR_DANGER = '#F44336'
        BG_DEFAULT = '#FFFFFF'
        BG_PANEL = '#F5F5F5'

try:
    from lib.i18n import t as i18n_t, get_lang, register_bulk as i18n_register_bulk
except ImportError:
    def i18n_t(key: str, **kwargs) -> str:
        return kwargs.get('default', key)
    def get_lang() -> str:
        return 'vi'
    def i18n_register_bulk(namespace: str, translations: dict) -> None:
        pass

try:
    from lib.ui.tooltip import attach_i18n_tooltip
except ImportError:
    def attach_i18n_tooltip(widget, key: str, **kwargs) -> None:
        pass

try:
    from lib.ui.icon_helper import get_icon_helper
    icon_helper = get_icon_helper()
except ImportError:
    icon_helper = None

try:
    from lib.vision.vision_engine import get_vision_engine, Detection
except ImportError:
    # Fallback nếu vision_engine chưa có
    get_vision_engine = None
    Detection = None


# ==================== TRANSLATIONS ====================
# Đăng ký bản dịch cho module này
VISION_WIZARD_TRANSLATIONS = {
    'vi': {
        'vision_wizard_title': 'Trình Quản Lý Vision System',
        'vision_wizard_subtitle': 'Cấu hình nhận diện hình ảnh và tracking',
        
        # Chế độ tìm kiếm
        'search_mode_label': 'Chế độ tìm kiếm:',
        'search_mode_position': 'Tìm tại vị trí chỉ định',
        'search_mode_fullscreen': 'Tìm toàn màn hình',
        'search_mode_region': 'Tìm trong vùng (ROI)',
        
        # Threshold
        'threshold_label': 'Ngưỡng nhận diện (0.0 - 1.0):',
        'threshold_tooltip': 'Độ chính xác cần thiết để nhận diện template (0.7 = 70%)',
        
        # Template list
        'template_list_label': 'Danh sách Template:',
        'template_name_col': 'Tên',
        'template_path_col': 'Đường dẫn',
        'template_threshold_col': 'Ngưỡng',
        
        # Buttons
        'btn_add_template': 'Thêm Template',
        'btn_remove_template': 'Xóa',
        'btn_save_threshold': 'Lưu Ngưỡng',
        'btn_test_recognition': 'Test Nhận Diện',
        'btn_close': 'Đóng',
        
        # Preview
        'preview_label': 'Preview / Overlay:',
        'preview_placeholder': 'Vùng preview sẽ hiển thị ở đây',
        
        # Messages
        'msg_no_template_selected': 'Vui lòng chọn một template',
        'msg_invalid_threshold': 'Ngưỡng không hợp lệ (phải từ 0.0 đến 1.0)',
        'msg_threshold_saved': 'Đã lưu ngưỡng thành công',
        'msg_template_added': 'Đã thêm template thành công',
        'msg_template_removed': 'Đã xóa template thành công',
        
        # Tooltips
        'tooltip_add_template': 'Thêm file ảnh template mới vào danh sách',
        'tooltip_remove_template': 'Xóa template đang chọn khỏi danh sách',
        'tooltip_save_threshold': 'Lưu ngưỡng nhận diện cho template đang chọn',
        'tooltip_test_recognition': 'Chạy test nhận diện với cấu hình hiện tại',
    },
    'en': {
        'vision_wizard_title': 'Vision System Manager',
        'vision_wizard_subtitle': 'Configure image recognition and tracking',
        
        # Search mode
        'search_mode_label': 'Search Mode:',
        'search_mode_position': 'Search at specified position',
        'search_mode_fullscreen': 'Search full screen',
        'search_mode_region': 'Search in region (ROI)',
        
        # Threshold
        'threshold_label': 'Recognition Threshold (0.0 - 1.0):',
        'threshold_tooltip': 'Accuracy required to recognize template (0.7 = 70%)',
        
        # Template list
        'template_list_label': 'Template List:',
        'template_name_col': 'Name',
        'template_path_col': 'Path',
        'template_threshold_col': 'Threshold',
        
        # Buttons
        'btn_add_template': 'Add Template',
        'btn_remove_template': 'Remove',
        'btn_save_threshold': 'Save Threshold',
        'btn_test_recognition': 'Test Recognition',
        'btn_close': 'Close',
        
        # Preview
        'preview_label': 'Preview / Overlay:',
        'preview_placeholder': 'Preview area will be displayed here',
        
        # Messages
        'msg_no_template_selected': 'Please select a template',
        'msg_invalid_threshold': 'Invalid threshold (must be between 0.0 and 1.0)',
        'msg_threshold_saved': 'Threshold saved successfully',
        'msg_template_added': 'Template added successfully',
        'msg_template_removed': 'Template removed successfully',
        
        # Tooltips
        'tooltip_add_template': 'Add new template image to list',
        'tooltip_remove_template': 'Remove selected template from list',
        'tooltip_save_threshold': 'Save recognition threshold for selected template',
        'tooltip_test_recognition': 'Run recognition test with current configuration',
    }
}

# Đăng ký translations
i18n_register_bulk('vision_wizard', VISION_WIZARD_TRANSLATIONS)


# ==================== SINGLETON INSTANCE ====================
_vision_wizard_instance: Optional['VisionWizard'] = None


def get_vision_wizard_instance() -> Optional['VisionWizard']:
    """Lấy instance hiện tại của VisionWizard (nếu có)"""
    return _vision_wizard_instance


def create_or_show_vision_wizard(parent: tk.Widget, **kwargs) -> 'VisionWizard':
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
        on_close: Optional[Callable] = None
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
        
        print(f"[VisionWizard] Init: parent={type(parent).__name__}, config_path={config_path}")
        
        # Dữ liệu
        self.templates: List[Dict[str, Any]] = []
        self.current_template: Optional[Dict[str, Any]] = None
        self.search_mode: str = "position"  # position, fullscreen, region
        
        # Vision Engine
        self.vision_engine = None
        if get_vision_engine:
            try:
                self.vision_engine = get_vision_engine()
            except Exception as e:
                print(f"Error initializing vision engine: {e}")
        
        # UI Components (sẽ được khởi tạo trong setup_ui)
        self.search_mode_combo: Optional[ttk.Combobox] = None
        self.threshold_entry: Optional[tk.Entry] = None
        self.threshold_frame: Optional[ttk.Frame] = None
        self.template_tree: Optional[ttk.Treeview] = None
        self.preview_canvas: Optional[tk.Canvas] = None
        
        # Cấu hình cửa sổ
        self._setup_window()
        
        # Thiết lập giao diện
        self.setup_ui()
        
        # Kết nối sự kiện
        self.bind_events()
        
        # Tải dữ liệu
        self.load_templates()
        self.load_thresholds()
        
        # Center window
        self._center_window()
        
    def _setup_window(self) -> None:
        """Cấu hình cửa sổ chính"""
        self.title(i18n_t('vision_wizard_title', ns='vision_wizard', default='Vision System Manager'))
        self.geometry('900x700')
        self.minsize(800, 600)
        
        # Luôn hiển thị trên cùng
        self.attributes('-topmost', True)
        
        # Icon (nếu có)
        if icon_helper:
            try:
                icon_path = icon_helper.get_icon_path('vision')
                if icon_path and os.path.exists(icon_path):
                    self.iconbitmap(icon_path)
            except Exception:
                pass
        
        # Xử lý khi đóng cửa sổ
        self.protocol('WM_DELETE_WINDOW', self._on_window_close)
        
    def _center_window(self) -> None:
        """Căn giữa cửa sổ trên màn hình"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
        
    def setup_ui(self) -> None:
        """
        Thiết lập giao diện người dùng.
        
        Layout:
        - Header: Tiêu đề và subtitle
        - Top Panel: Chế độ tìm kiếm và threshold
        - Middle Panel: Danh sách template (Treeview)
        - Bottom Panel: Buttons (Thêm, Xóa, Lưu, Test)
        - Preview Panel: Canvas để preview ảnh/overlay
        """
        # ===== HEADER =====
        header_frame = tk.Frame(self, bg=UI.COLOR_PRIMARY, height=80)
        header_frame.pack(fill='x', padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(
            header_frame,
            text=i18n_t('vision_wizard_title', ns='vision_wizard', default='Vision System Manager'),
            font=UI.FONT_TITLE,
            bg=UI.COLOR_PRIMARY,
            fg='white'
        )
        title_label.pack(pady=(15, 5))
        
        subtitle_label = tk.Label(
            header_frame,
            text=i18n_t('vision_wizard_subtitle', ns='vision_wizard', default='Cấu hình nhận diện hình ảnh và tracking'),
            font=UI.FONT_LABEL,
            bg=UI.COLOR_PRIMARY,
            fg='white'
        )
        subtitle_label.pack(pady=(0, 10))
        
        # ===== MAIN CONTAINER =====
        main_container = tk.Frame(self, bg=UI.BG_DEFAULT)
        main_container.pack(fill='both', expand=True, padx=15, pady=15)
        
        # ===== TOP PANEL: Chế độ tìm kiếm và Threshold =====
        top_panel = ttk.LabelFrame(
            main_container,
            text=i18n_t('search_mode_label', ns='vision_wizard', default='Chế độ tìm kiếm'),
            padding=10
        )
        top_panel.pack(fill='x', pady=(0, 10))
        
        # Chế độ tìm kiếm
        search_mode_frame = tk.Frame(top_panel, bg=UI.BG_DEFAULT)
        search_mode_frame.pack(fill='x', pady=5)
        
        tk.Label(
            search_mode_frame,
            text=i18n_t('search_mode_label', ns='vision_wizard', default='Chế độ tìm kiếm:'),
            font=UI.FONT_LABEL,
            bg=UI.BG_DEFAULT
        ).pack(side='left', padx=(0, 10))
        
        self.search_mode_combo = ttk.Combobox(
            search_mode_frame,
            font=UI.FONT_TEXT,
            state='readonly',
            width=30
        )
        self.search_mode_combo['values'] = (
            i18n_t('search_mode_position', ns='vision_wizard', default='Tìm tại vị trí chỉ định'),
            i18n_t('search_mode_fullscreen', ns='vision_wizard', default='Tìm toàn màn hình'),
            i18n_t('search_mode_region', ns='vision_wizard', default='Tìm trong vùng (ROI)')
        )
        self.search_mode_combo.current(0)
        self.search_mode_combo.pack(side='left', fill='x', expand=True)
        
        # Threshold (có thể ẩn/hiện tùy theo chế độ)
        self.threshold_frame = tk.Frame(top_panel, bg=UI.BG_DEFAULT)
        self.threshold_frame.pack(fill='x', pady=5)
        
        tk.Label(
            self.threshold_frame,
            text=i18n_t('threshold_label', ns='vision_wizard', default='Ngưỡng nhận diện:'),
            font=UI.FONT_LABEL,
            bg=UI.BG_DEFAULT
        ).pack(side='left', padx=(0, 10))
        
        self.threshold_entry = tk.Entry(
            self.threshold_frame,
            font=UI.FONT_TEXT,
            width=10
        )
        self.threshold_entry.pack(side='left')
        self.threshold_entry.insert(0, '0.7')  # Giá trị mặc định
        
        attach_i18n_tooltip(
            self.threshold_entry,
            'threshold_tooltip',
            ns='vision_wizard',
            default='Độ chính xác cần thiết để nhận diện template (0.7 = 70%)'
        )
        
        # ===== MIDDLE PANEL: Danh sách Template =====
        template_panel = ttk.LabelFrame(
            main_container,
            text=i18n_t('template_list_label', ns='vision_wizard', default='Danh sách Template'),
            padding=10
        )
        template_panel.pack(fill='both', expand=True, pady=(0, 10))
        
        # Treeview với scrollbar
        tree_frame = tk.Frame(template_panel)
        tree_frame.pack(fill='both', expand=True)
        
        # Scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient='vertical')
        hsb = ttk.Scrollbar(tree_frame, orient='horizontal')
        
        # Treeview
        self.template_tree = ttk.Treeview(
            tree_frame,
            columns=('name', 'path', 'threshold'),
            show='headings',
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set,
            selectmode='browse'
        )
        
        # Configure scrollbars
        vsb.config(command=self.template_tree.yview)
        hsb.config(command=self.template_tree.xview)
        
        # Column headings
        self.template_tree.heading('name', text=i18n_t('template_name_col', ns='vision_wizard', default='Tên'))
        self.template_tree.heading('path', text=i18n_t('template_path_col', ns='vision_wizard', default='Đường dẫn'))
        self.template_tree.heading('threshold', text=i18n_t('template_threshold_col', ns='vision_wizard', default='Ngưỡng'))
        
        # Column widths
        self.template_tree.column('name', width=150, minwidth=100)
        self.template_tree.column('path', width=400, minwidth=200)
        self.template_tree.column('threshold', width=100, minwidth=80)
        
        # Pack components
        self.template_tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # ===== BOTTOM PANEL: Buttons =====
        button_panel = tk.Frame(main_container, bg=UI.BG_DEFAULT)
        button_panel.pack(fill='x', pady=(0, 10))
        
        # Left buttons (Thêm, Xóa)
        left_buttons = tk.Frame(button_panel, bg=UI.BG_DEFAULT)
        left_buttons.pack(side='left')
        
        btn_add = ttk.Button(
            left_buttons,
            text=i18n_t('btn_add_template', ns='vision_wizard', default='Thêm Template'),
            command=self.add_template
        )
        btn_add.pack(side='left', padx=5)
        attach_i18n_tooltip(btn_add, 'tooltip_add_template', ns='vision_wizard')
        
        btn_remove = ttk.Button(
            left_buttons,
            text=i18n_t('btn_remove_template', ns='vision_wizard', default='Xóa'),
            command=self.remove_template
        )
        btn_remove.pack(side='left', padx=5)
        attach_i18n_tooltip(btn_remove, 'tooltip_remove_template', ns='vision_wizard')
        
        # Right buttons (Lưu, Test, Đóng)
        right_buttons = tk.Frame(button_panel, bg=UI.BG_DEFAULT)
        right_buttons.pack(side='right')
        
        btn_save = ttk.Button(
            right_buttons,
            text=i18n_t('btn_save_threshold', ns='vision_wizard', default='Lưu Ngưỡng'),
            command=self.save_threshold
        )
        btn_save.pack(side='left', padx=5)
        attach_i18n_tooltip(btn_save, 'tooltip_save_threshold', ns='vision_wizard')
        
        btn_test = ttk.Button(
            right_buttons,
            text=i18n_t('btn_test_recognition', ns='vision_wizard', default='Test Nhận Diện'),
            command=self.test_recognition
        )
        btn_test.pack(side='left', padx=5)
        attach_i18n_tooltip(btn_test, 'tooltip_test_recognition', ns='vision_wizard')
        
        btn_close = ttk.Button(
            right_buttons,
            text=i18n_t('btn_close', ns='vision_wizard', default='Đóng'),
            command=self._on_window_close
        )
        btn_close.pack(side='left', padx=5)
        
        # ===== PREVIEW PANEL =====
        preview_panel = ttk.LabelFrame(
            main_container,
            text=i18n_t('preview_label', ns='vision_wizard', default='Preview / Overlay'),
            padding=10
        )
        preview_panel.pack(fill='both', expand=False, pady=(0, 0))
        
        # Canvas để hiển thị preview
        self.preview_canvas = tk.Canvas(
            preview_panel,
            width=860,
            height=150,
            bg='#f0f0f0',
            relief='sunken',
            bd=2
        )
        self.preview_canvas.pack(fill='both', expand=True)
        
        # Placeholder text
        self.preview_canvas.create_text(
            430, 75,
            text=i18n_t('preview_placeholder', ns='vision_wizard', default='Vùng preview sẽ hiển thị ở đây'),
            font=UI.FONT_LABEL,
            fill='gray'
        )
        
        # TODO: Bổ sung logic preview ảnh và overlay sau
        
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
            self.search_mode_combo.bind('<<ComboboxSelected>>', self._on_search_mode_changed)
        
        # Sự kiện khi chọn template trong tree
        if self.template_tree:
            self.template_tree.bind('<<TreeviewSelect>>', self._on_template_selected)
            # Double click để edit/view
            self.template_tree.bind('<Double-1>', self._on_template_double_click)
        
        # Validation cho threshold entry
        if self.threshold_entry:
            # Chỉ cho phép nhập số và dấu chấm
            vcmd = (self.register(self._validate_threshold), '%P')
            self.threshold_entry.config(validate='key', validatecommand=vcmd)
        
        # Keyboard shortcuts
        self.bind('<Escape>', lambda e: self._on_window_close())
        self.bind('<Control-s>', lambda e: self.save_threshold())
        self.bind('<Control-t>', lambda e: self.test_recognition())
        self.bind('<Delete>', lambda e: self.remove_template())
        
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
                with open(config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.templates = data if isinstance(data, list) else data.get('templates', [])
            except Exception as e:
                print(f"Error loading templates config: {e}")
                self.templates = []
        else:
            # Fallback: Sample data
            self.templates = [
                {
                    'id': 'monster_hp_bar',
                    'name': 'Monster_HP_Bar',
                    'path': 'assets/images/monsters/hp_bar.png',
                    'threshold': 0.8,
                    'scales': [0.8, 1.0, 1.2],
                    'enabled': True
                },
                {
                    'id': 'skill_icon_1',
                    'name': 'Skill_Icon_1',
                    'path': 'assets/images/skills/skill_1.png',
                    'threshold': 0.75,
                    'scales': [1.0],
                    'enabled': True
                },
            ]
        
        # Wire: Load vào vision engine
        if self.vision_engine:
            try:
                # Extract paths từ templates
                enabled_templates = [t for t in self.templates if t.get('enabled', True)]
                paths = [t['path'] for t in enabled_templates if os.path.exists(t.get('path', ''))]
                
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
    
    def save_region(self, region_name: str, x: int, y: int, width: int, height: int) -> None:
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
                with open(region_config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    regions = data.get('regions', {})
            
            # Add/update region
            regions[region_name] = {
                'x': x,
                'y': y,
                'width': width,
                'height': height
            }
            
            # Save back
            with open(region_config_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'default_region': regions.get('default', {'x': 0, 'y': 0, 'width': 1920, 'height': 1080}),
                    'regions': regions
                }, f, indent=2, ensure_ascii=False)
            
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
                with open(region_config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # Try regions dict first
                    regions = data.get('regions', {})
                    if region_name in regions:
                        r = regions[region_name]
                        return (r['x'], r['y'], r['width'], r['height'])
                    
                    # Fallback to default_region
                    if region_name == 'default' and 'default_region' in data:
                        r = data['default_region']
                        return (r['x'], r['y'], r['width'], r['height'])
            
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
                i18n_t('warning', default='Cảnh báo'),
                'Vision engine not initialized'
            )
            return
        
        # Start worker với frame callback
        try:
            self.vision_engine.start_worker(frame_callback=self._get_current_frame)
            
            # Start UI polling loop
            self._poll_interval_ms = 66  # ~15 FPS
            self._poll_queue()
            
            messagebox.showinfo(
                'Detection Started',
                'Detection loop started.\n\n'
                'Worker thread is running in background.\n'
                'UI updates at ~15 FPS via queue polling.'
            )
            
        except Exception as e:
            messagebox.showerror(
                i18n_t('error', default='Lỗi'),
                f'Failed to start detection: {e}'
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
        except:
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
            frame = result.get('frame')
            if frame is None:
                return
            
            # Convert BGR to RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Convert to PhotoImage (single conversion per frame)
            from PIL import Image, ImageTk
            pil_image = Image.fromarray(frame_rgb)
            photo = ImageTk.PhotoImage(pil_image)
            
            # Update preview_canvas
            if hasattr(self, 'preview_canvas') and self.preview_canvas:
                # Clear canvas
                self.preview_canvas.delete("all")
                
                # Draw image
                self.preview_canvas.create_image(0, 0, anchor='nw', image=photo)
                
                # Keep reference to prevent garbage collection
                self.preview_canvas.image = photo  # type: ignore
                
                # Update status
                result_type = result.get('type', 'unknown')
                data_count = len(result.get('data', []))
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
            ('Image files', '*.png *.jpg *.jpeg *.bmp'),
            ('PNG files', '*.png'),
            ('JPEG files', '*.jpg *.jpeg'),
            ('All files', '*.*')
        ]
        
        file_path = filedialog.askopenfilename(
            parent=self,
            title=i18n_t('btn_add_template', ns='vision_wizard', default='Thêm Template'),
            filetypes=filetypes
        )
        
        if not file_path:
            return  # User cancelled
        
        # Validate file exists
        if not os.path.exists(file_path):
            messagebox.showerror(
                i18n_t('error', default='Lỗi'),
                f'File không tồn tại: {file_path}'
            )
            return
        
        # Extract name from filename
        name = os.path.splitext(os.path.basename(file_path))[0]
        
        # Thêm vào danh sách
        new_template = {
            'id': name.lower().replace(' ', '_'),
            'name': name,
            'path': file_path,
            'threshold': 0.7,  # Default
            'scales': [1.0],
            'enabled': True
        }
        self.templates.append(new_template)
        
        # Refresh tree
        self._refresh_template_tree()
        
        # Save to config
        self._save_templates_config()
        
        # Reload engine templates
        if self.vision_engine:
            try:
                enabled_templates = [t for t in self.templates if t.get('enabled', True)]
                paths = [t['path'] for t in enabled_templates if os.path.exists(t.get('path', ''))]
                if paths:
                    self.vision_engine.load_templates(paths)
            except Exception as e:
                print(f"Error reloading engine templates: {e}")
        
        messagebox.showinfo(
            i18n_t('success', default='Thành công'),
            i18n_t('msg_template_added', ns='vision_wizard', default='Đã thêm template thành công')
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
                i18n_t('warning', default='Cảnh báo'),
                i18n_t('msg_no_template_selected', ns='vision_wizard', default='Vui lòng chọn một template')
            )
            return
        
        # Confirm
        result = messagebox.askyesno(
            i18n_t('confirm', default='Xác nhận'),
            'Bạn có chắc muốn xóa template này?'
        )
        
        if not result:
            return
        
        # Get selected item
        item_id = selection[0]
        values = self.template_tree.item(item_id, 'values')
        
        if values:
            name = values[0]
            # Tìm và xóa khỏi self.templates
            self.templates = [t for t in self.templates if t['name'] != name]
            
            # Refresh tree
            self._refresh_template_tree()
            
            # Save to config
            self._save_templates_config()
            
            # Reload engine templates
            if self.vision_engine:
                try:
                    enabled_templates = [t for t in self.templates if t.get('enabled', True)]
                    paths = [t['path'] for t in enabled_templates if os.path.exists(t.get('path', ''))]
                    if paths:
                        self.vision_engine.load_templates(paths)
                    else:
                        # Clear all templates if none enabled
                        self.vision_engine.templates.clear()
                except Exception as e:
                    print(f"Error reloading engine templates: {e}")
            
            messagebox.showinfo(
                i18n_t('success', default='Thành công'),
                i18n_t('msg_template_removed', ns='vision_wizard', default='Đã xóa template thành công')
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
                i18n_t('warning', default='Cảnh báo'),
                i18n_t('msg_no_template_selected', ns='vision_wizard', default='Vui lòng chọn một template')
            )
            return
        
        # Get threshold value
        try:
            threshold = float(self.threshold_entry.get())
            if not (0.0 <= threshold <= 1.0):
                raise ValueError()
        except ValueError:
            messagebox.showerror(
                i18n_t('error', default='Lỗi'),
                i18n_t('msg_invalid_threshold', ns='vision_wizard', default='Ngưỡng không hợp lệ')
            )
            return
        
        # Get selected template
        item_id = selection[0]
        values = self.template_tree.item(item_id, 'values')
        
        if values:
            name = values[0]
            # Update trong self.templates
            for template in self.templates:
                if template['name'] == name:
                    template['threshold'] = threshold
                    break
            
            # Refresh tree
            self._refresh_template_tree()
            
            # Save to config
            self._save_templates_config()
            
            messagebox.showinfo(
                i18n_t('success', default='Thành công'),
                i18n_t('msg_threshold_saved', ns='vision_wizard', default='Đã lưu ngưỡng thành công')
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
                'Vision Engine',
                'Vision engine not initialized.\n\n'
                'Please check that lib/vision/vision_engine.py is available.'
            )
            return
        
        # Kiểm tra có templates loaded không
        if not self.vision_engine.templates:
            messagebox.showwarning(
                'No Templates',
                'No templates loaded.\n\n'
                'Please add templates before testing recognition.'
            )
            return
        
        try:
            # Start detection loop để test (sử dụng worker thread)
            self.start_detection_loop()
            
        except Exception as e:
            messagebox.showerror(
                'Test Error',
                f'Error starting test recognition:\n\n{str(e)}'
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
                '',
                'end',
                values=(
                    template.get('name', ''),
                    template.get('path', ''),
                    template.get('threshold', 0.7)
                )
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
            with open(config_file, 'w', encoding='utf-8') as f:
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
        modes = ['position', 'fullscreen', 'region']
        self.search_mode = modes[selected] if selected < len(modes) else 'position'
        
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
        values = self.template_tree.item(item_id, 'values')
        
        if values:
            # Update threshold entry
            threshold = values[2]
            self.threshold_entry.delete(0, 'end')
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
        if value == '':
            return True
        
        # Chỉ cho phép số, dấu chấm, và tối đa 1 dấu chấm
        if value.count('.') > 1:
            return False
        
        try:
            float(value)
            return True
        except ValueError:
            return False
        
    def _on_window_close(self) -> None:
        """
        Xử lý khi đóng cửa sổ.
        
        TODO: Confirm nếu có thay đổi chưa lưu
        TODO: Cleanup resources
        """
        # TODO: Check unsaved changes
        
        # Call callback nếu có
        if self.on_close_callback:
            try:
                self.on_close_callback()
            except Exception as e:
                print(f'Error in on_close callback: {e}')
        
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
if __name__ == '__main__':
    """
    Test module độc lập.
    
    Run:
        python -m ui.setup_wizard_vision
    """
    root = tk.Tk()
    root.title('Test Vision Wizard')
    root.geometry('400x300')
    
    def test_open_wizard():
        """Test function để mở wizard"""
        wizard = create_or_show_vision_wizard(root)
        print(f'Wizard created: {wizard}')
    
    # Button để test
    btn = tk.Button(
        root,
        text='Open Vision Wizard\n(Ctrl+Shift+L)',
        font=('Segoe UI', 12),
        command=test_open_wizard,
        width=20,
        height=3
    )
    btn.pack(expand=True)
    
    # Bind hotkey
    root.bind('<Control-Shift-L>', lambda e: test_open_wizard())
    
    print('Test window started. Press Ctrl+Shift+L or click button to open Vision Wizard.')
    root.mainloop()
