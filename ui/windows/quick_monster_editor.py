"""
Quick Monster Editor - Modal dialog for quick monster editing.

Lightweight modal window that opens with Ctrl+Shift+M hotkey.
Dock layout: Top (title + actions), Center (form), Bottom (capture/test + progress).

Features:
- Topmost modal window
- Form fields: name, level, threshold
- Capture/Test buttons with progress spinner
- Queue-based worker integration
- No widget updates from threads
- All labels use lib.i18n
- All tooltips use lib.ui.tooltip

Author: SokKimThanh
Created: 2025-10-24
Status: Implementation
"""
from __future__ import annotations
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Optional, Dict, Any, Callable, List, Union
import queue
import threading
import json
import uuid
import re
import time
from pathlib import Path

# Import lib modules
try:
    from lib.i18n import t as i18n_t, get_lang, register_bulk as i18n_register_bulk
except ImportError:
    def i18n_t(key: str, *, ns: Optional[str] = None, lang: Optional[str] = None, default: Optional[str] = None) -> str:
        return default if default else key
    def get_lang() -> str:
        return 'vi'
    def i18n_register_bulk(namespace: str, translations: dict) -> None:
        pass

try:
    from ui.helpers.tooltip import attach_i18n_tooltip
except ImportError:
    def attach_i18n_tooltip(widget, key: str, ns: Optional[str], lang_provider: Callable, delay: int = 400) -> Any:
        pass

try:
    from ui.helpers.button_styles import get_button_config
except ImportError:
    def get_button_config(button_type: str) -> dict:
        return {'font': ('Arial', 10, 'bold')}

try:
    from ui.components import create_icon_button, create_icon_label
    from ui.components.game_window_mode_selector import create_game_window_mode_selector  # type: ignore[assignment]
    from ui.components.window_position_selector import create_app_window_selector, create_game_window_selector  # type: ignore[assignment]
    from ui.components.icon_button import set_button_enabled
    from ui.components.confirmation_widget import ConfirmationWidget
except ImportError:
    # Fallback if component not available
    def create_icon_button(parent, icon_name: str, command, text: str = '', button_type: str = 'green_light', **kwargs):
        """Fallback create_icon_button - filter invalid tk.Button parameters."""
        # Get base config
        config = get_button_config(button_type)
        
        # Remove parameters that tk.Button doesn't support
        invalid_params = [
            'icon_fallback', 'icon_size', 'variant', 
            'tooltip_key', 'tooltip_ns', 'auto_hover_disabled'
        ]
        
        # Filter kwargs
        filtered_kwargs = {k: v for k, v in kwargs.items() if k not in invalid_params}
        config.update(filtered_kwargs)
        
        # Use icon_fallback as text if provided
        icon_fallback = kwargs.get('icon_fallback', icon_name)
        display_text = text or icon_fallback
        
        return tk.Button(parent, text=display_text, command=command, **config)
    
    def create_game_window_mode_selector(parent, **kwargs):
        """Fallback if game_window_mode_selector not available."""
        return tk.Label(parent, text="[Game Mode Selector unavailable]")
    
    def create_app_window_selector(parent, **kwargs):
        """Fallback if app window selector not available."""
        return tk.Label(parent, text="[App Selector unavailable]")
    
    def create_game_window_selector(parent, **kwargs):
        """Fallback if game window selector not available."""
        return tk.Label(parent, text="[Game Selector unavailable]")
    
    def create_icon_label(parent, icon_name: str, text: str = '', icon_fallback: str = '❓', **kwargs):
        """Fallback create_icon_label."""
        # Filter out invalid Label parameters
        invalid_params = ['icon_size']
        filtered_kwargs = {k: v for k, v in kwargs.items() if k not in invalid_params}
        return tk.Label(parent, text=f"{icon_fallback} {text}", **filtered_kwargs)
    
    ConfirmationWidget = None  # type: ignore
    
    def set_button_enabled(button, enabled: bool, tooltip: Optional[str] = None) -> None:
        """Fallback for set_button_enabled."""
        button.config(state='normal' if enabled else 'disabled')
        if tooltip and enabled:
            button.config(text=f"💾")
        elif tooltip and not enabled:
            button.config(text=f"🚫")

# Capture helper imports
try:
    from lib.ui_style import UIStyle as UI
except ImportError:
    # Fallback UIStyle matching lib.ui.button_styles colors
    class UIStyle:
        # Fonts
        FONT_TITLE = ('Segoe UI', 12, 'bold')
        FONT_SECTION = ('Segoe UI', 11, 'bold')
        FONT_LABEL = ('Segoe UI', 10)
        FONT_TEXT = ('Segoe UI', 10)
        FONT_BUTTON = ('Arial', 10, 'bold')  # Match button_styles
        FONT_SMALL = ('Segoe UI', 8)
        
        # Colors matching button_styles.py
        COLOR_PRIMARY = '#2196F3'        # BTN_BLUE_BG
        COLOR_PRIMARY_TEXT = '#0D47A1'   # Darker blue for text
        COLOR_TEXT = '#333'              # TEXT_DARK
        COLOR_SUBTEXT = '#666'           # TEXT_GRAY
        COLOR_ACCENT = '#357A38'         # BTN_GREEN_LIGHT_BG
        COLOR_DANGER = '#C62828'         # BTN_RED_BG
        COLOR_WARNING = '#FF9800'        # BTN_ORANGE_BG
        
        # Backgrounds
        BG_DEFAULT = '#FFFFFF'
        BG_PANEL = '#F5F5F5'
    UI = UIStyle

try:
    from ui.helpers.icon_helper import IconHelper
    icon_helper = IconHelper()
except ImportError:
    class MockIconHelper:
        def get_icon(self, name: str, fallback: str = '', size: int = 16) -> str:
            return fallback
    icon_helper = MockIconHelper()

try:
    from ui.helpers.capture_helper import capture_region_and_save
    PIL_AVAILABLE = True
except ImportError:
    capture_region_and_save = None
    PIL_AVAILABLE = False

# PIL imports for image capture
try:
    from PIL import ImageGrab, Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    ImageGrab = None
    Image = None
    ImageTk = None
    PIL_AVAILABLE = False

# Template matcher for Test Recognition
try:
    from lib.vision.template_matcher import locate_template
except ImportError:
    locate_template = None

# Register translations
try:
    from lib.i18n.monster_editor_translations import MONSTER_EDITOR_TRANSLATIONS
    i18n_register_bulk('monster_editor', MONSTER_EDITOR_TRANSLATIONS)
except ImportError:
    pass


# Constants
DATA_PATH = Path("lib/data/monsters.json")


class QuickMonsterEditor(tk.Toplevel):
    """
    Quick monster editor modal dialog with dock layout.
    
    Layout:
    ┌─────────────────────────────────────┐
    │ Top: Title + Action Buttons         │
    ├─────────────────────────────────────┤
    │ Center: Form Fields (name/level/...) │
    ├─────────────────────────────────────┤
    │ Bottom: Capture/Test + Progress     │
    └─────────────────────────────────────┘
    
    Features:
    - Modal topmost window
    - Queue-based worker communication
    - Progress indication
    - Form validation
    """
    
    def __init__(
        self,
        parent: Any,  # Accept Tk or Widget
        monster_id: Optional[str] = None,
        on_save: Optional[Callable] = None
    ):
        """
        Initialize QuickMonsterEditor.
        
        Args:
            parent: Parent widget
            monster_id: Monster to edit (None for new monster)
            on_save: Callback when monster is saved
        """
        super().__init__(parent)
        
        self.parent = parent
        self.monster_id = monster_id
        self.on_save_callback = on_save
        
        # Data state
        self.monsters: List[Dict[str, Any]] = []
        self.current_monster_id: Optional[str] = monster_id
        self.is_dirty = False  # Global unsaved changes
        self.is_monster_dirty = False  # Current monster modified
        
        # Processing flags to prevent concurrent operations
        self._is_capturing = False
        self._is_browsing = False
        self._is_deleting = False
        self._is_testing = False
        self._last_warning_time = 0.0  # Track last warning to prevent spam
        
        # Hunt config path
        self.hunt_config_path = Path("lib/data/hunt_config.json")
        
        # UI settings path (for saving column visibility, window controls, etc.)
        self.ui_settings_path = Path("lib/data/monster_editor_ui_settings.json")
        
        # Game window mode (none, below, above)
        self.game_window_mode_var = tk.StringVar(value="none")
        self._load_hunt_config()
        self._load_ui_settings()  # Load UI settings
        
        # UI update debounce
        self._refresh_list_after_id: Optional[str] = None
        
        # Result queue for worker thread communication
        self.result_queue: queue.Queue = queue.Queue()
        self.is_working = False
        
        # Edit mode state
        self.is_editing: bool = False  # Lock/unlock fields
        
        # Window position selectors (created in _setup_ui)
        self.app_mode_selector: Any = None  # WindowPositionSelector
        self.game_mode_selector: Any = None  # WindowPositionSelector
        
        # Data
        self.monster_data: Dict[str, Any] = {
            'name': '',
            'level': 1,
            'threshold': 0.7,
            'templates': []
        }
        
        # Widgets (initialized in setup_ui)
        # Left panel
        self.monster_listbox: Optional[Union[tk.Listbox, ttk.Treeview]] = None
        self.add_monster_button: Optional[tk.Button] = None
        self.delete_monster_button: Optional[tk.Button] = None
        
        # Right panel - Notebook tabs
        self.notebook: Optional[ttk.Notebook] = None
        self.info_tab: Optional[tk.Frame] = None
        self.templates_tab: Optional[tk.Frame] = None
        
        # Edit mode widgets (Info tab)
        self.edit_toggle_button: Optional[tk.Button] = None
        self.editing_badge: Optional[tk.Label] = None
        
        # Edit mode widgets (Template tab)
        self.template_edit_toggle_button: Optional[tk.Button] = None
        self.template_editing_badge: Optional[tk.Label] = None
        
        # Info tab widgets
        self.name_entry: Optional[tk.Entry] = None
        self.level_spinbox: Optional[tk.Spinbox] = None
        self.priority_spinbox: Optional[tk.Spinbox] = None
        self.hp_entry: Optional[tk.Entry] = None
        self.damage_entry: Optional[tk.Entry] = None
        self.desc_text: Optional[tk.Text] = None
        
        # Templates tab widgets
        self.template_listbox: Optional[Union[tk.Listbox, ttk.Treeview]] = None
        self.template_scrollbar: Optional[tk.Scrollbar] = None
        self.template_preview_label: Optional[tk.Label] = None
        self.add_template_button: Optional[tk.Button] = None
        self.capture_button: Optional[tk.Button] = None
        self.browse_button: Optional[tk.Button] = None
        self.delete_template_button: Optional[tk.Button] = None
        self.test_template_button: Optional[tk.Button] = None
        
        # Top bar widgets
        self.save_button: Optional[tk.Button] = None
        self.cancel_button: Optional[tk.Button] = None
        self.status_badge: Optional[tk.Label] = None
        
        # Settings tab widgets
        self.settings_saved_badge: Optional[tk.Label] = None
        
        # Legacy widgets (from quick editor) - may be removed later
        self.progress_label: Optional[tk.Label] = None
        self.test_button: Optional[tk.Button] = None
        self.threshold_scale: Optional[tk.Scale] = None
        self.threshold_label: Optional[tk.Label] = None
        
        # Window configuration
        title = i18n_t('quick_editor_title', ns='monster_editor', default='Quick Monster Editor')
        self.title(title)
        self.geometry("750x450")  # Increased to accommodate left panel
        self.resizable(False, False)
        self.attributes('-topmost', True)
        
        # Center window on screen
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (750 // 2)  # Updated for new width
        y = (self.winfo_screenheight() // 2) - (450 // 2)  # Updated for new height
        self.geometry(f"+{x}+{y}")
        
        # Setup
        self._load_monsters()  # Load monsters list from JSON
        self._setup_ui()
        self._bind_events()
        self._start_queue_monitor()
        
        # Update UI to reflect initial dirty state
        self._update_dirty_state_ui()
        
        # Auto-select first monster and first template
        self.after(100, self._auto_select_first_items)
    
    def _load_monsters(self) -> None:
        """Load monsters from JSON file."""
        try:
            if DATA_PATH.exists():
                with open(DATA_PATH, 'r', encoding='utf-8') as f:
                    self.monsters = json.load(f)
                print(f"[MonsterEditor] Loaded {len(self.monsters)} monsters from {DATA_PATH}")
                # Ensure all monsters have ID
                for monster in self.monsters:
                    if 'id' not in monster:
                        monster['id'] = str(uuid.uuid4())
            else:
                self.monsters = []
                print(f"[MonsterEditor] No data file found at {DATA_PATH}, creating empty list")
                # Create empty file
                DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
                with open(DATA_PATH, 'w', encoding='utf-8') as f:
                    json.dump([], f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[MonsterEditor] Error loading monsters: {e}")
            self.monsters = []
    
    def _load_hunt_config(self) -> None:
        """Load hunt_config.json and set game_window_mode."""
        try:
            if self.hunt_config_path.exists():
                with open(self.hunt_config_path, 'r', encoding='utf-8') as f:
                    hunt_config = json.load(f)
                mode = hunt_config.get('game_window_mode', 'none')
                self.game_window_mode_var.set(mode)
                print(f"[MonsterEditor] Loaded game_window_mode: {mode}")
            else:
                print(f"[MonsterEditor] hunt_config.json not found, using default 'none'")
        except Exception as e:
            print(f"[MonsterEditor] Error loading hunt_config.json: {e}")
    
    def _load_ui_settings(self) -> None:
        """Load UI settings from JSON file."""
        try:
            if self.ui_settings_path.exists():
                with open(self.ui_settings_path, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                
                # Store settings to be applied after UI is created
                self._ui_settings = settings
                print(f"[MonsterEditor] Loaded UI settings: {settings}")
            else:
                # Default settings
                self._ui_settings = {
                    'col_image_visible': True,
                    'col_threshold_visible': True,
                    'col_path_visible': True,
                    'show_window_controls': True
                }
                print(f"[MonsterEditor] No UI settings file found, using defaults")
        except Exception as e:
            print(f"[MonsterEditor] Error loading UI settings: {e}")
            self._ui_settings = {
                'col_image_visible': True,
                'col_threshold_visible': True,
                'col_path_visible': True,
                'show_window_controls': True
            }
    
    def _save_ui_settings(self) -> None:
        """Save UI settings to JSON file."""
        try:
            settings = {
                'col_image_visible': self.col_image_visible.get(),
                'col_threshold_visible': self.col_threshold_visible.get(),
                'col_path_visible': self.col_path_visible.get(),
                'show_window_controls': self.show_window_controls_var.get()
            }
            
            # Ensure directory exists
            self.ui_settings_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.ui_settings_path, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
            
            print(f"[MonsterEditor] Saved UI settings: {settings}")
            
            # Show saved badge
            self._show_settings_saved_badge()
        except Exception as e:
            print(f"[MonsterEditor] Error saving UI settings: {e}")
    
    def _show_settings_saved_badge(self) -> None:
        """Show settings saved badge and auto-hide after 2 seconds."""
        if hasattr(self, 'settings_saved_badge') and self.settings_saved_badge:
            # Show badge
            self.settings_saved_badge.pack(side='right')
            
            # Hide after 2 seconds
            def hide_badge():
                if self.settings_saved_badge:
                    self.settings_saved_badge.pack_forget()
            
            self.after(2000, hide_badge)
    
    def set_dirty(self, value: bool = True) -> None:
        """Set dirty state and update UI."""
        self.is_dirty = value
        self._update_dirty_state_ui()

    def set_monster_dirty(self, value: bool = True) -> None:
        """Set monster dirty state and update UI."""
        self.is_monster_dirty = value
        self.set_dirty(value)
    
    def _update_dirty_state_ui(self) -> None:
        """Update status badge and Save button based on dirty state."""
        # Update status badge
        if self.status_badge:
            if self.is_dirty:
                # Orange badge for unsaved
                self.status_badge.config(
                    text=i18n_t('badge_unsaved', ns='monster_editor', default='Chưa lưu'),
                    bg='#FF8C00',  # Orange
                    fg='white'
                )
            else:
                # Green badge for saved
                self.status_badge.config(
                    text=i18n_t('badge_saved', ns='monster_editor', default='Đã lưu tất cả'),
                    bg='#28A745',  # Green
                    fg='white'
                )
        
        # Update Save button state
        if self.save_button:
            if self.is_dirty:
                # Enable save button
                self.save_button.config(state='normal')
            else:
                # Disable save button (auto hover shows prohibition icon)
                self.save_button.config(state='disabled')
    
    def _flash_save_success(self) -> None:
        """Flash status badge to indicate save success (subtle feedback)."""
        if not self.status_badge:
            return
        
        # Flash green "Saved!" message on badge
        original_bg = self.status_badge.cget('bg')
        original_text = self.status_badge.cget('text')
        
        self.status_badge.config(
            text="✓ Saved!" if get_lang() == 'en' else "✓ Đã lưu!",
            bg='#4CAF50',
            fg='white'
        )
        
        # Restore after 1.5 seconds
        def restore():
            if self.status_badge and self.status_badge.winfo_exists():
                self._update_dirty_state_ui()
        
        self.after(1500, restore)
    
    def _show_error(self, title: str, message: str) -> None:
        """
        Show error messagebox that appears on top.
        
        Args:
            title: Dialog title
            message: Error message
        """
        self.attributes('-topmost', False)  # Temporarily disable
        messagebox.showerror(title, message, parent=self)
        self.attributes('-topmost', True)  # Re-enable
    
    def _show_info(self, title: str, message: str) -> None:
        """
        Show info messagebox that appears on top.
        
        Args:
            title: Dialog title
            message: Info message
        """
        self.attributes('-topmost', False)
        messagebox.showinfo(title, message, parent=self)
        self.attributes('-topmost', True)
    
    def _show_warning(self, title: str, message: str) -> None:
        """
        Show warning messagebox that appears on top.
        
        Args:
            title: Dialog title
            message: Warning message
        """
        self.attributes('-topmost', False)
        messagebox.showwarning(title, message, parent=self)
        self.attributes('-topmost', True)
    
    def _ask_yes_no(self, title: str, message: str) -> bool:
        """
        Show yes/no question dialog that appears on top.
        
        Args:
            title: Dialog title
            message: Question message
            
        Returns:
            True if user clicked Yes, False otherwise
        """
        self.attributes('-topmost', False)
        result = messagebox.askyesno(title, message, parent=self)
        self.attributes('-topmost', True)
        return result

    def _save_monsters(self) -> bool:
        """Save monsters to JSON file."""
        try:
            DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
            with open(DATA_PATH, 'w', encoding='utf-8') as f:
                json.dump(self.monsters, f, indent=2, ensure_ascii=False)
            self.is_dirty = False
            self.is_monster_dirty = False
            self._update_dirty_state_ui()
            return True
        except Exception as e:
            print(f"[MonsterEditor] Error saving monsters: {e}")
            self._show_error('Error', f'Failed to save: {e}')
            return False
    
    def _setup_ui(self) -> None:
        """Create UI components with dock layout."""
        # Top: Title + Action Buttons
        self._create_top_panel()
        
        # Create main container for left + right panels with grid (3:9 ratio)
        main_container = tk.Frame(self, bg=UI.BG_DEFAULT)
        main_container.pack(side='top', fill='both', expand=True)
        
        # Configure grid weights for 3:9 ratio
        main_container.grid_rowconfigure(0, weight=1)
        main_container.grid_columnconfigure(0, weight=3)  # Left: Monster List (3 parts)
        main_container.grid_columnconfigure(1, weight=9)  # Right: Tabbed panel (9 parts)
        
        # Left: Monster List
        self._create_left_panel(main_container)
        
        # Right: Tabbed panel
        self._create_right_panel(main_container)
    
    def _create_top_panel(self) -> None:
        """Create top panel with title and action buttons."""
        top_frame = tk.Frame(self, bg=UI.BG_PANEL, height=60)
        top_frame.pack(side='top', fill='x', padx=0, pady=0)
        top_frame.pack_propagate(False)
        
        # Title
        title_text = i18n_t('quick_editor_title', ns='monster_editor', default='Quick Monster Editor')
        title_label = tk.Label(
            top_frame,
            text=title_text,
            font=UI.FONT_TITLE,
            fg=UI.COLOR_PRIMARY_TEXT,
            bg=UI.BG_PANEL
        )
        title_label.pack(side='left', padx=15, pady=15)
        
        # Action buttons (right side)
        button_frame = tk.Frame(top_frame, bg=UI.BG_PANEL)
        button_frame.pack(side='right', padx=15, pady=15)
        
        # Status badge (shows saved/unsaved state)
        self.status_badge = tk.Label(
            button_frame,
            text=i18n_t('badge_saved', ns='monster_editor', default='Đã lưu tất cả'),
            font=UI.FONT_SMALL,
            fg='white',
            bg='#28A745',  # Green for saved
            padx=8,
            pady=2,
            relief='flat'
        )
        self.status_badge.pack(side='left', padx=(0, 10))
        
        # Save button - icon only, with auto disabled hover
        self.save_button = create_icon_button(
            button_frame,
            icon_name='save',
            icon_fallback='💾',
            icon_size=16,
            command=self._on_save,
            button_type='green_light',
            variant='icon_only',  # Icon only, no text
            width=32,
            height=32,
            auto_hover_disabled=True,  # Show prohibition when disabled
            tooltip_key='tooltip_save',
            tooltip_ns='monster_editor'
        )
        self.save_button.pack(side='left', padx=5)
        
        # Initially disable save button (no changes)
        self.save_button.config(state='disabled')
        
        # Cancel button - icon only, no text
        self.cancel_button = create_icon_button(
            button_frame,
            icon_name='cancel',
            icon_fallback='✖',
            icon_size=16,
            command=self._on_cancel,
            button_type='refresh',  # Gray neutral style
            variant='icon_only',  # Icon only, no text
            width=32,
            height=32,
            tooltip_key='tooltip_cancel',
            tooltip_ns='monster_editor'
        )
        self.cancel_button.pack(side='left', padx=5)
    
    def _create_left_panel(self, parent: Any) -> None:
        """Create left panel with monster list and CRUD buttons."""
        left_frame = tk.Frame(parent, bg=UI.BG_PANEL)
        left_frame.grid(row=0, column=0, sticky='nsew', padx=0, pady=0)
        
        # Title with icon
        title_text = i18n_t('label_monster_list', ns='monster_editor', default='Monsters')
        title_label = create_icon_label(
            left_frame,
            icon_name='list',
            text=title_text,
            icon_fallback='🗂️',
            icon_size=16,
            font=UI.FONT_SECTION,
            fg=UI.COLOR_PRIMARY_TEXT,
            bg=UI.BG_PANEL
        )
        title_label.pack(side='top', padx=10, pady=(10, 5))
        
        # Monster listbox with scrollbar
        listbox_frame = tk.Frame(left_frame, bg=UI.BG_PANEL)
        listbox_frame.pack(side='top', fill='both', expand=True, padx=10, pady=5)
        
        # Use Treeview for 2 columns: icon + name
        scrollbar = tk.Scrollbar(listbox_frame, orient=tk.VERTICAL)
        scrollbar.pack(side='right', fill='y')
        
        # Create Treeview with 2 columns
        self.monster_listbox = ttk.Treeview(
            listbox_frame,
            columns=('icon', 'name'),
            show='tree headings',  # Show both tree and column headers
            selectmode='browse',
            yscrollcommand=scrollbar.set,
            height=15
        )
        
        # Configure columns
        self.monster_listbox.column('#0', width=0, stretch=False)  # Hide tree column
        self.monster_listbox.column('icon', width=40, minwidth=40, anchor='center')
        self.monster_listbox.column('name', width=180, minwidth=100, anchor='center')
        
        # Set headings
        self.monster_listbox.heading('icon', text='', anchor='center')
        self.monster_listbox.heading('name', text=i18n_t('header_name', ns='monster_editor', default='Name'), anchor='center')
        
        self.monster_listbox.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=self.monster_listbox.yview)
        
        # Bind selection event
        self.monster_listbox.bind('<<TreeviewSelect>>', self._on_monster_select)
        
        # Initial load
        self._refresh_monster_list()
    
    def _create_right_panel(self, parent: Any) -> None:
        """Create right panel with tabbed interface."""
        right_container = tk.Frame(parent, bg=UI.BG_DEFAULT)
        right_container.grid(row=0, column=1, sticky='nsew', padx=10, pady=10)
        
        # Create notebook (tabs)
        self.notebook = ttk.Notebook(right_container)
        self.notebook.pack(fill='both', expand=True, pady=(0, 10))
        
        # Bind tab change event to cancel confirmation
        self.notebook.bind('<<NotebookTabChanged>>', self._on_tab_changed)
        
        # ============================================
        # Confirmation Area (below tabs, always visible)
        # ============================================
        confirmation_frame = tk.Frame(right_container, bg='#FFF3CD', relief='solid', bd=1)
        confirmation_frame.pack(fill='x', pady=(0, 5))
        
        # Message label (left side)
        self.confirmation_message = tk.Label(
            confirmation_frame,
            text="",
            font=('Segoe UI', 10),
            fg='#856404',
            bg='#FFF3CD',
            anchor='w',
            padx=10,
            pady=8
        )
        self.confirmation_message.pack(side='left', fill='x', expand=True)
        
        # Buttons container (right side)
        buttons_container = tk.Frame(confirmation_frame, bg='#FFF3CD')
        buttons_container.pack(side='right', padx=10, pady=5)
        
        # Confirmation widget (Yes/No buttons)
        if ConfirmationWidget:
            self.confirmation_widget = ConfirmationWidget(
                parent=buttons_container,
                on_confirm=lambda: None,  # Will be set dynamically
                on_cancel=None,
                auto_hide_seconds=10,  # 10 seconds timeout
                bg='#FFF3CD'
            )
        else:
            self.confirmation_widget = None
        
        # Initially hide entire confirmation frame
        confirmation_frame.pack_forget()
        self.confirmation_frame = confirmation_frame
        
        # Create tabs
        self._create_info_tab()
        self._create_templates_tab()
        self._create_settings_tab()
    
    def _create_info_tab(self) -> None:
        """Create Monster Info tab."""
        if self.notebook is None:
            return
        
        # Create tab frame
        self.info_tab = tk.Frame(self.notebook, bg=UI.BG_DEFAULT)
        
        # Add to notebook
        tab_text = i18n_t('tab_info', ns='monster_editor', default='Monster Info')
        self.notebook.add(self.info_tab, text=tab_text)
        
        # Header with Edit button and badge (OUTSIDE scrollable area)
        header_frame = tk.Frame(self.info_tab, bg=UI.BG_DEFAULT)
        header_frame.pack(fill='x', padx=10, pady=(10, 5))
        
        # Left side: Editing badge
        left_buttons = tk.Frame(header_frame, bg=UI.BG_DEFAULT)
        left_buttons.pack(side='left')
        
        # Editing badge (orange background, white text)
        self.editing_badge = tk.Label(
            left_buttons,
            text=i18n_t('badge_editing', ns='monster_editor', default='Đang chỉnh sửa'),
            font=UI.FONT_SMALL,
            fg='white',
            bg='#FF8C00',  # Orange
            padx=8,
            pady=2,
            relief='flat'
        )
        # Initially hidden (not in edit mode)
        # self.editing_badge.pack(side='left')  # Don't pack yet
        
        # Right side: Edit/Add/Delete buttons (20x20, icon 16px)
        right_buttons = tk.Frame(header_frame, bg=UI.BG_DEFAULT)
        right_buttons.pack(side='right')
        
        # Edit button
        self.edit_toggle_button = create_icon_button(
            right_buttons,
            icon_name='edit',
            icon_fallback='✏️',
            icon_size=16,
            command=self._toggle_edit_mode,
            button_type='primary',
            variant='icon_only',  # Icon only
            width=20,
            height=20,
            tooltip_key='tooltip_edit_mode',
            tooltip_ns='monster_editor'
        )
        self.edit_toggle_button.pack(side='left', padx=(0, 2))
        
        # Add Monster button
        self.add_monster_button = create_icon_button(
            right_buttons,
            icon_name='add',
            icon_fallback='➕',
            icon_size=16,
            command=self._on_add_monster,
            button_type='green_light',
            variant='icon_only',
            width=20,
            height=20,
            auto_hover_disabled=True,
            tooltip_key='tooltip_add_monster',
            tooltip_ns='monster_editor'
        )
        self.add_monster_button.pack(side='left', padx=2)
        
        # Delete Monster button
        self.delete_monster_button = create_icon_button(
            right_buttons,
            icon_name='delete',
            icon_fallback='🗑️',
            icon_size=16,
            command=self._on_delete_monster,
            button_type='red',
            variant='icon_only',
            width=20,
            height=20,
            auto_hover_disabled=True,
            tooltip_key='tooltip_delete_monster',
            tooltip_ns='monster_editor'
        )
        self.delete_monster_button.pack(side='left', padx=2)
        
        # Initially enable Add button, Delete depends on selection
        if self.add_monster_button:
            self.add_monster_button.config(state='normal')
        if self.delete_monster_button:
            self.delete_monster_button.config(state='disabled')  # Will be enabled when monster selected
        
        # Create scrollable container (BELOW header)
        canvas = tk.Canvas(self.info_tab, bg=UI.BG_DEFAULT, highlightthickness=0)
        scrollbar = tk.Scrollbar(self.info_tab, orient='vertical', command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=UI.BG_DEFAULT)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side='left', fill='both', expand=True, padx=10, pady=(0, 10))
        scrollbar.pack(side='right', fill='y')
        
        # Form content
        form_frame = tk.Frame(scrollable_frame, bg=UI.BG_DEFAULT)
        form_frame.pack(fill='both', expand=True)
        
        # Monster Name
        name_label_text = i18n_t('monster_name_label', ns='monster_editor', default='Name')
        name_label = create_icon_label(
            form_frame,
            icon_name='monster',
            text=f"{name_label_text}:",
            icon_fallback='👹',
            icon_size=16,
            font=UI.FONT_LABEL,
            fg=UI.COLOR_TEXT,
            bg=UI.BG_DEFAULT
        )
        name_label.grid(row=0, column=0, sticky='w', pady=5)
        
        self.name_entry = tk.Entry(
            form_frame,
            font=UI.FONT_TEXT
        )
        self.name_entry.grid(row=0, column=1, sticky='ew', pady=5, padx=(10, 0))
        self.name_entry.bind('<KeyRelease>', self._on_info_change)
        
        # Level
        level_label_text = i18n_t('monster_level_label', ns='monster_editor', default='Level')
        level_label = create_icon_label(
            form_frame,
            icon_name='up',
            text=f"{level_label_text}:",
            icon_fallback='↑',
            icon_size=16,
            font=UI.FONT_LABEL,
            fg=UI.COLOR_TEXT,
            bg=UI.BG_DEFAULT
        )
        level_label.grid(row=1, column=0, sticky='w', pady=5)
        
        self.level_spinbox = tk.Spinbox(
            form_frame,
            from_=1,
            to=999,
            font=UI.FONT_TEXT
        )
        self.level_spinbox.grid(row=1, column=1, sticky='ew', pady=5, padx=(10, 0))
        self.level_spinbox.bind('<KeyRelease>', self._on_info_change)
        self.level_spinbox.bind('<<Increment>>', self._on_info_change)
        self.level_spinbox.bind('<<Decrement>>', self._on_info_change)
        
        # Priority
        priority_label_text = i18n_t('monster_priority_label', ns='monster_editor', default='Priority')
        priority_label = create_icon_label(
            form_frame,
            icon_name='priority',
            text=f"{priority_label_text}:",
            icon_fallback='🎯',
            icon_size=16,
            font=UI.FONT_LABEL,
            fg=UI.COLOR_TEXT,
            bg=UI.BG_DEFAULT
        )
        priority_label.grid(row=2, column=0, sticky='w', pady=5)
        
        self.priority_spinbox = tk.Spinbox(
            form_frame,
            from_=1,
            to=10,
            font=UI.FONT_TEXT
        )
        self.priority_spinbox.grid(row=2, column=1, sticky='ew', pady=5, padx=(10, 0))
        self.priority_spinbox.bind('<KeyRelease>', self._on_info_change)
        self.priority_spinbox.bind('<<Increment>>', self._on_info_change)
        self.priority_spinbox.bind('<<Decrement>>', self._on_info_change)
        
        # HP
        hp_label_text = i18n_t('monster_hp_label', ns='monster_editor', default='HP')
        hp_label = create_icon_label(
            form_frame,
            icon_name='hp',
            text=f"{hp_label_text}:",
            icon_fallback='❤️',
            icon_size=16,
            font=UI.FONT_LABEL,
            fg=UI.COLOR_TEXT,
            bg=UI.BG_DEFAULT
        )
        hp_label.grid(row=3, column=0, sticky='w', pady=5)
        
        self.hp_entry = tk.Entry(
            form_frame,
            font=UI.FONT_TEXT
        )
        self.hp_entry.grid(row=3, column=1, sticky='ew', pady=5, padx=(10, 0))
        self.hp_entry.bind('<KeyRelease>', self._on_info_change)
        
        # Damage per hit
        damage_label_text = i18n_t('monster_damage_label', ns='monster_editor', default='Damage')
        damage_label = create_icon_label(
            form_frame,
            icon_name='damage',
            text=f"{damage_label_text}:",
            icon_fallback='⚔️',
            icon_size=16,
            font=UI.FONT_LABEL,
            fg=UI.COLOR_TEXT,
            bg=UI.BG_DEFAULT
        )
        damage_label.grid(row=4, column=0, sticky='w', pady=5)
        
        self.damage_entry = tk.Entry(
            form_frame,
            font=UI.FONT_TEXT
        )
        self.damage_entry.grid(row=4, column=1, sticky='ew', pady=5, padx=(10, 0))
        self.damage_entry.bind('<KeyRelease>', self._on_info_change)
        
        # Description
        desc_label_text = i18n_t('monster_desc_label', ns='monster_editor', default='Description')
        desc_label = create_icon_label(
            form_frame,
            icon_name='info',
            text=f"{desc_label_text}:",
            icon_fallback='📋',
            icon_size=16,
            font=UI.FONT_LABEL,
            fg=UI.COLOR_TEXT,
            bg=UI.BG_DEFAULT
        )
        desc_label.grid(row=5, column=0, sticky='nw', pady=5)
        
        desc_frame = tk.Frame(form_frame, bg=UI.BG_DEFAULT)
        desc_frame.grid(row=5, column=1, sticky='ew', pady=5, padx=(10, 0))
        
        self.desc_text = tk.Text(
            desc_frame,
            font=UI.FONT_TEXT,
            height=5,
            wrap=tk.WORD
        )
        self.desc_text.pack(side='left', fill='both', expand=True)
        
        desc_scrollbar = tk.Scrollbar(desc_frame, orient='vertical', command=self.desc_text.yview)
        desc_scrollbar.pack(side='right', fill='y')
        self.desc_text.configure(yscrollcommand=desc_scrollbar.set)
        self.desc_text.bind('<KeyRelease>', self._on_info_change)
        
        # Configure grid weights
        form_frame.columnconfigure(1, weight=1)
    
    def _create_templates_tab(self) -> None:
        """
        Create Templates tab with DockLayer layout.
        
        Layout:
        ┌─────────────────────────────────────────────────────┐
        │ Top Layer: Button Row (Capture|Browse|Test|Add|Del|Edit) │
        ├────────────────────────┬────────────────────────────┤
        │ Left Column:           │ Right Column:              │
        │ - Template List (3col) │ - Preview Image            │
        │                        │ - Threshold Slider         │
        └────────────────────────┴────────────────────────────┘
        """
        if self.notebook is None:
            return
        
        # Create tab frame
        self.templates_tab = tk.Frame(self.notebook, bg=UI.BG_DEFAULT)
        
        # Add to notebook
        tab_text = i18n_t('tab_templates', ns='monster_editor', default='Templates')
        self.notebook.add(self.templates_tab, text=tab_text)
        
        # ========== Main Layout: 2 Columns (6:6 ratio) - Full Height ==========
        main_row = tk.Frame(self.templates_tab, bg=UI.BG_DEFAULT)
        main_row.pack(side='top', fill='both', expand=True, padx=10, pady=10)
        
        # Configure grid weights for 6:6 ratio
        main_row.grid_rowconfigure(0, weight=1)
        main_row.grid_columnconfigure(0, weight=6)  # Left column: 6 parts
        main_row.grid_columnconfigure(1, weight=6)  # Right column: 6 parts
        
        # === Left Column: Template List (6 parts) ===
        left_column = tk.Frame(main_row, bg=UI.BG_DEFAULT)
        left_column.grid(row=0, column=0, sticky='nsew', padx=(0, 5))
        
        # Top area: action buttons for template management
        top_list_area = tk.Frame(left_column, bg=UI.BG_DEFAULT)
        top_list_area.pack(side='top', fill='x', pady=(0, 4))
        
        # Action buttons frame (Add/Delete/Edit) - Left side
        action_buttons_frame = tk.Frame(top_list_area, bg=UI.BG_DEFAULT)
        action_buttons_frame.pack(side='left')
        
        # Badge for edit mode - Right side
        badge_frame = tk.Frame(top_list_area, bg=UI.BG_DEFAULT)
        badge_frame.pack(side='right')
        
        # Editing badge for template tab
        self.template_editing_badge = tk.Label(
            badge_frame,
            text=i18n_t('badge_editing', ns='monster_editor', default='Đang chỉnh sửa'),
            font=UI.FONT_SMALL,
            fg='white',
            bg='#FF8C00',  # Orange
            padx=6,
            pady=2,
            relief='flat'
        )
        # Initially hidden; will be shown when edit mode enabled
        self.template_editing_badge.pack(side='left')
        self.template_editing_badge.pack_forget()  # Hide initially
        # Add Template button (20x20, icon 16px)
        self.add_template_button = create_icon_button(
            action_buttons_frame,
            icon_name='add',
            icon_fallback='➕',
            icon_size=16,
            command=self._add_template,
            button_type='green_light',
            variant='icon_only',
            width=20,
            height=20,
            auto_hover_disabled=True,
            tooltip_key='tooltip_add_template',
            tooltip_ns='monster_editor'
        )
        self.add_template_button.pack(side='left', padx=(0, 2))

        # Delete Template button (20x20, icon 16px)
        self.delete_template_button = create_icon_button(
            action_buttons_frame,
            icon_name='delete',
            icon_fallback='🗑️',
            icon_size=16,
            command=self._delete_template,
            button_type='red',
            variant='icon_only',
            width=20,
            height=20,
            auto_hover_disabled=True,
            tooltip_key='tooltip_delete_template',
            tooltip_ns='monster_editor'
        )
        self.delete_template_button.pack(side='left', padx=2)

        # Edit Template button (20x20, icon 16px)
        self.template_edit_toggle_button = create_icon_button(
            action_buttons_frame,
            icon_name='edit',
            icon_fallback='✏️',
            icon_size=16,
            command=self._toggle_template_edit_mode,
            button_type='primary',
            variant='icon_only',
            width=20,
            height=20,
            tooltip_key='tooltip_edit_mode_template',
            tooltip_ns='monster_editor'
        )
        self.template_edit_toggle_button.pack(side='left', padx=2)
        
        # Start locked
        self.add_template_button.config(state='disabled')
        self.delete_template_button.config(state='disabled')
        
        # Treeview with 3 columns: Image | Threshold | Name
        list_frame = tk.Frame(left_column, bg=UI.BG_DEFAULT)
        list_frame.pack(side='top', fill='both', expand=True)
        
        self.template_scrollbar = tk.Scrollbar(list_frame, orient='vertical')
        self.template_listbox = ttk.Treeview(
            list_frame,
            columns=('image', 'threshold', 'name'),
            show='headings',
            selectmode='browse',
            yscrollcommand=self.template_scrollbar.set,
            height=15
        )
        
        # Configure columns with shorter widths
        # Column widths (image | threshold | path)
        self.template_listbox.column('image', width=40, minwidth=40, anchor='center', stretch=False)
        self.template_listbox.column('threshold', width=70, minwidth=60, anchor='center')
        self.template_listbox.column('name', width=150, minwidth=100, anchor='w')
        
        # Set headings
        self.template_listbox.heading('image', text=i18n_t('col_image', ns='monster_editor', default='Hình'), anchor='center')
        self.template_listbox.heading('threshold', text=i18n_t('col_threshold', ns='monster_editor', default='Ngưỡng'), anchor='center')
        # Rename 'name' column to 'Đường dẫn'
        self.template_listbox.heading('name', text=i18n_t('col_path', ns='monster_editor', default='Đường dẫn'), anchor='center')
        
        self.template_listbox.pack(side='left', fill='both', expand=True)
        self.template_scrollbar.config(command=self.template_listbox.yview)
        self.template_scrollbar.pack(side='right', fill='y')
        
        # Bind selection event
        self.template_listbox.bind('<<TreeviewSelect>>', self._on_template_select)
        
        # === Right Column: Preview + Buttons (6 parts) ===
        right_column = tk.Frame(main_row, bg=UI.BG_PANEL)
        right_column.grid(row=0, column=1, sticky='nsew', padx=(5, 0))
        
        # Preview header: title + action buttons on same row
        preview_header = tk.Frame(right_column, bg=UI.BG_PANEL)
        preview_header.pack(side='top', fill='x', padx=10, pady=(10, 5))
        
        # Preview title (left side)
        preview_title = tk.Label(
            preview_header,
            text=i18n_t('preview_label', ns='monster_editor', default='Xem trước'),
            font=UI.FONT_LABEL,
            fg=UI.COLOR_PRIMARY_TEXT,
            bg=UI.BG_PANEL
        )
        preview_title.pack(side='left')
        
        # Action buttons container (right side of header)
        header_buttons = tk.Frame(preview_header, bg=UI.BG_PANEL)
        header_buttons.pack(side='right')
        
        # Capture button (20x20, icon 16px)
        self.capture_preview_button = create_icon_button(
            header_buttons,
            icon_name='capture',
            icon_fallback='📸',
            icon_size=16,
            command=self._capture_template,
            button_type='blue',
            variant='icon_only',
            width=20,
            height=20,
            auto_hover_disabled=True,
            tooltip_key='tooltip_capture',
            tooltip_ns='monster_editor'
        )
        self.capture_preview_button.pack(side='left', padx=2)
        
        # Browse button (20x20, icon 16px)
        self.browse_preview_button = create_icon_button(
            header_buttons,
            icon_name='browse',
            icon_fallback='📂',
            icon_size=16,
            command=self._browse_template_image,
            button_type='refresh',
            variant='icon_only',
            width=20,
            height=20,
            auto_hover_disabled=True,
            tooltip_key='tooltip_browse',
            tooltip_ns='monster_editor'
        )
        self.browse_preview_button.pack(side='left', padx=2)
        
        # Test Recognition button (20x20, icon 16px)
        self.test_template_button = create_icon_button(
            header_buttons,
            icon_name='test',
            icon_fallback='🧪',
            icon_size=16,
            command=self._test_template_recognition,
            button_type='blue',
            variant='icon_only',
            width=20,
            height=20,
            auto_hover_disabled=True,
            tooltip_key='tooltip_test_template',
            tooltip_ns='monster_editor'
        )
        self.test_template_button.pack(side='left', padx=2)
        
        # Initially disable all action buttons
        self.capture_preview_button.config(state='disabled')
        self.browse_preview_button.config(state='disabled')
        self.test_template_button.config(state='disabled')
        
        # Preview image container (expand to fill)
        preview_container = tk.Frame(right_column, bg='white', relief='sunken', borderwidth=2)
        preview_container.pack(side='top', fill='both', expand=True, padx=10, pady=(0, 10))
        
        self.template_preview_label = tk.Label(
            preview_container,
            text='No template\nselected' if get_lang() == 'en' else 'Chưa chọn\ntemplate',
            font=UI.FONT_SMALL,
            fg=UI.COLOR_SUBTEXT,
            bg='white',
            justify='center'
        )
        self.template_preview_label.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Threshold slider section (BOTTOM)
        threshold_frame = tk.Frame(right_column, bg=UI.BG_PANEL)
        threshold_frame.pack(side='bottom', fill='x', padx=10, pady=(0, 10))

        threshold_label_text = i18n_t('monster_threshold_label', ns='monster_editor', default='Ngưỡng nhận diện')
        self.threshold_label = create_icon_label(
            threshold_frame,
            icon_name='settings',
            text=f"{threshold_label_text}:",
            icon_fallback='⚙️',
            icon_size=12,
            font=UI.FONT_SMALL,
            fg=UI.COLOR_TEXT,
            bg=UI.BG_PANEL
        )
        self.threshold_label.pack(side='left', padx=(0, 6))

        self.threshold_scale = tk.Scale(
            threshold_frame,
            from_=0.0,
            to=1.0,
            resolution=0.01,
            orient='horizontal',
            showvalue=True,
            length=200,
            font=UI.FONT_SMALL
        )
        self.threshold_scale.set(0.7)
        self.threshold_scale.pack(side='left', fill='x', expand=True)
    
    def _create_settings_tab(self) -> None:
        """Create Settings tab for display options and window controls."""
        if self.notebook is None:
            return
        
        # Create tab frame
        self.settings_tab = tk.Frame(self.notebook, bg=UI.BG_DEFAULT)
        
        # Add to notebook
        tab_text = i18n_t('tab_settings', ns='monster_editor', default='Cài đặt')
        self.notebook.add(self.settings_tab, text=tab_text)
        
        # Top bar with badge
        top_bar = tk.Frame(self.settings_tab, bg=UI.BG_DEFAULT)
        top_bar.pack(side='top', fill='x', padx=20, pady=(20, 10))
        
        # Settings saved badge (right side)
        self.settings_saved_badge = tk.Label(
            top_bar,
            text=i18n_t('badge_settings_saved', ns='monster_editor', default='✓ Đã lưu setting mới'),
            font=UI.FONT_SMALL,
            fg='white',
            bg='#2196F3',  # Blue for settings saved
            padx=8,
            pady=2,
            relief='flat'
        )
        self.settings_saved_badge.pack(side='right')
        self.settings_saved_badge.pack_forget()  # Initially hidden
        
        # Main container with padding
        main_container = tk.Frame(self.settings_tab, bg=UI.BG_DEFAULT)
        main_container.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        # ========== Column Visibility Options ==========
        col_visibility_frame = tk.LabelFrame(
            main_container,
            text='Hiển thị cột trong danh sách Template' if get_lang() == 'vi' else 'Template List Column Visibility',
            font=UI.FONT_LABEL,
            fg=UI.COLOR_PRIMARY_TEXT,
            bg=UI.BG_DEFAULT,
            padx=15,
            pady=10
        )
        col_visibility_frame.pack(fill='x', pady=(0, 20))
        
        # Initialize column visibility variables with saved settings
        self.col_image_visible = tk.BooleanVar(value=self._ui_settings.get('col_image_visible', True))
        self.col_threshold_visible = tk.BooleanVar(value=self._ui_settings.get('col_threshold_visible', True))
        self.col_path_visible = tk.BooleanVar(value=self._ui_settings.get('col_path_visible', True))
        
        # Checkboxes for column visibility
        tk.Checkbutton(
            col_visibility_frame,
            text='🖼️ Hình ảnh' if get_lang() == 'vi' else '🖼️ Image',
            variable=self.col_image_visible,
            command=self._on_column_visibility_change,
            bg=UI.BG_DEFAULT
        ).pack(anchor='w', pady=5)
        
        tk.Checkbutton(
            col_visibility_frame,
            text='% Ngưỡng nhận diện' if get_lang() == 'vi' else '% Threshold',
            variable=self.col_threshold_visible,
            command=self._on_column_visibility_change,
            bg=UI.BG_DEFAULT
        ).pack(anchor='w', pady=5)
        
        tk.Checkbutton(
            col_visibility_frame,
            text='📁 Đường dẫn' if get_lang() == 'vi' else '📁 Path',
            variable=self.col_path_visible,
            command=self._on_column_visibility_change,
            bg=UI.BG_DEFAULT
        ).pack(anchor='w', pady=5)
        
        # ========== Window Controls ==========
        window_controls_frame = tk.LabelFrame(
            main_container,
            text='Điều khiển cửa sổ' if get_lang() == 'vi' else 'Window Controls',
            font=UI.FONT_LABEL,
            fg=UI.COLOR_PRIMARY_TEXT,
            bg=UI.BG_DEFAULT,
            padx=15,
            pady=10
        )
        window_controls_frame.pack(fill='both', expand=True)
        
        # Window controls checkbox with saved setting
        self.show_window_controls_var = tk.BooleanVar(value=self._ui_settings.get('show_window_controls', True))
        
        def toggle_window_controls():
            """Toggle visibility of window position selectors."""
            show = self.show_window_controls_var.get()
            if show:
                windows_frame.pack(fill='x', pady=(10, 0))
                if hasattr(self, 'app_mode_selector') and hasattr(self.app_mode_selector, 'show'):
                    self.app_mode_selector.show()
                if hasattr(self, 'game_mode_selector') and hasattr(self.game_mode_selector, 'show'):
                    self.game_mode_selector.show()
            else:
                windows_frame.pack_forget()
                if hasattr(self, 'app_mode_selector') and hasattr(self.app_mode_selector, 'hide'):
                    self.app_mode_selector.hide()
                if hasattr(self, 'game_mode_selector') and hasattr(self.game_mode_selector, 'hide'):
                    self.game_mode_selector.hide()
            
            # Save settings when changed
            self._save_ui_settings()
        
        window_check = tk.Checkbutton(
            window_controls_frame,
            text="Hiển thị điều khiển vị trí cửa sổ" if get_lang() == 'vi' else "Show Window Position Controls",
            variable=self.show_window_controls_var,
            command=toggle_window_controls,
            bg=UI.BG_DEFAULT
        )
        window_check.pack(anchor='w', pady=5)
        
        # Tooltip for checkbox
        check_tooltip = (
            "Show Window Controls\n"
            "• App window positioning\n"
            "• Game window positioning"
            if get_lang() == "en" else
            "Hiện Điều Khiển Cửa Sổ\n"
            "• Vị trí cửa sổ ứng dụng\n"
            "• Vị trí cửa sổ game"
        )
        try:
            attach_i18n_tooltip(
                window_check,
                'tooltip_window_controls',
                ns='monster_editor',
                lang_provider=get_lang
            )
        except:
            # Fallback if tooltip fails
            pass
        
        # Window controls frame (App + Game)
        windows_frame = tk.Frame(window_controls_frame, bg=UI.BG_DEFAULT)
        windows_frame.pack(fill='x', pady=(10, 0))
        
        # App window mode selector (no label, tooltip explains)
        self.app_mode_selector = create_app_window_selector(
            parent=windows_frame,
            config_path=str(self.hunt_config_path),
            on_mode_change=self._on_app_mode_change
        )
        self.app_mode_selector.pack(side='left', padx=(0, 8))
        
        # Game window mode selector (no label, tooltip explains)
        self.game_mode_selector = create_game_window_selector(
            parent=windows_frame,
            config_path=str(self.hunt_config_path),
            on_mode_change=self._on_game_mode_change
        )
        self.game_mode_selector.pack(side='left')
        
        # Apply saved visibility state
        if not self.show_window_controls_var.get():
            windows_frame.pack_forget()
            if hasattr(self.app_mode_selector, 'hide'):
                self.app_mode_selector.hide()
            if hasattr(self.game_mode_selector, 'hide'):
                self.game_mode_selector.hide()
    
    def _create_center_panel(self, parent: Optional[Any] = None) -> None:
        """Create center panel with form fields."""
        if parent is None:
            parent = self
        center_frame = tk.Frame(parent, bg=UI.BG_DEFAULT)
        center_frame.pack(side='top', fill='both', expand=True, padx=20, pady=20)
        
        # Monster Name
        name_label_text = i18n_t('monster_name_label', ns='monster_editor', default='Monster name:')
        tk.Label(
            center_frame,
            text=name_label_text,
            font=UI.FONT_LABEL,
            bg=UI.BG_DEFAULT
        ).grid(row=0, column=0, sticky='w', pady=(0, 10))
        
        self.name_entry = tk.Entry(
            center_frame,
            font=UI.FONT_TEXT,
            width=30
        )
        self.name_entry.grid(row=0, column=1, sticky='ew', pady=(0, 10))
        self.name_entry.insert(0, self.monster_data['name'])
        
        # Monster Level
        level_label_text = i18n_t('monster_level_label', ns='monster_editor', default='Level:')
        tk.Label(
            center_frame,
            text=level_label_text,
            font=UI.FONT_LABEL,
            bg=UI.BG_DEFAULT
        ).grid(row=1, column=0, sticky='w', pady=(0, 10))
        
        self.level_spinbox = tk.Spinbox(
            center_frame,
            from_=1,
            to=200,
            font=UI.FONT_TEXT,
            width=28
        )
        self.level_spinbox.grid(row=1, column=1, sticky='ew', pady=(0, 10))
        self.level_spinbox.delete(0, 'end')
        self.level_spinbox.insert(0, str(self.monster_data['level']))
        
        # Recognition Threshold
        threshold_label_text = i18n_t('monster_threshold_label', ns='monster_editor', default='Recognition threshold:')
        tk.Label(
            center_frame,
            text=threshold_label_text,
            font=UI.FONT_LABEL,
            bg=UI.BG_DEFAULT
        ).grid(row=2, column=0, sticky='w', pady=(0, 10))
        
        threshold_frame = tk.Frame(center_frame, bg=UI.BG_DEFAULT)
        threshold_frame.grid(row=2, column=1, sticky='ew', pady=(0, 10))
        
        self.threshold_scale = tk.Scale(
            threshold_frame,
            from_=0.0,
            to=1.0,
            resolution=0.01,
            orient='horizontal',
            font=UI.FONT_TEXT,
            bg=UI.BG_DEFAULT,
            command=self._on_threshold_changed
        )
        self.threshold_scale.set(self.monster_data['threshold'])
        self.threshold_scale.pack(side='left', fill='x', expand=True, padx=(0, 10))
        
        self.threshold_label = tk.Label(
            threshold_frame,
            text=f"{self.monster_data['threshold']:.2f}",
            font=UI.FONT_LABEL,
            bg=UI.BG_DEFAULT,
            width=5
        )
        self.threshold_label.pack(side='left')
        
        # Configure grid weights
        center_frame.columnconfigure(1, weight=1)
    
    def _create_bottom_panel(self, parent: Optional[Any] = None) -> None:
        """Create bottom panel with capture/test buttons and progress."""
        if parent is None:
            parent = self
        bottom_frame = tk.Frame(parent, bg=UI.BG_PANEL, height=80)
        bottom_frame.pack(side='bottom', fill='x', padx=0, pady=0)
        bottom_frame.pack_propagate(False)
        
        # Button container
        button_container = tk.Frame(bottom_frame, bg=UI.BG_PANEL)
        button_container.pack(side='top', pady=(15, 5))
        
        # Capture button
        capture_text = i18n_t('btn_capture', ns='monster_editor', default='Capture Region')
        capture_config = get_button_config('blue')
        self.capture_button = tk.Button(
            button_container,
            text=capture_text,
            width=15,
            command=self._on_capture,
            **capture_config
        )
        self.capture_button.pack(side='left', padx=5)
        
        # Tooltip
        attach_i18n_tooltip(
            self.capture_button,
            'tooltip_capture',
            ns='monster_editor',
            lang_provider=get_lang
        )
        
        # Test button
        test_text = i18n_t('btn_test', ns='monster_editor', default='Test Recognition')
        test_config = get_button_config('blue')
        self.test_button = tk.Button(
            button_container,
            text=test_text,
            width=15,
            command=self._on_test,
            **test_config
        )
        self.test_button.pack(side='left', padx=5)
        
        # Tooltip
        attach_i18n_tooltip(
            self.test_button,
            'tooltip_test',
            ns='monster_editor',
            lang_provider=get_lang
        )
        
        # Progress label
        self.progress_label = tk.Label(
            bottom_frame,
            text='',
            font=UI.FONT_SMALL,
            fg=UI.COLOR_SUBTEXT,
            bg=UI.BG_PANEL
        )
        self.progress_label.pack(side='top', pady=(0, 10))
    
    def _bind_events(self) -> None:
        """Bind event handlers."""
        # Window close event
        self.protocol("WM_DELETE_WINDOW", self._on_cancel)
    
    def _start_queue_monitor(self) -> None:
        """Start monitoring result queue for worker responses."""
        self._check_queue()
    
    def _check_queue(self) -> None:
        """Check result queue for messages from worker thread."""
        try:
            while True:
                result = self.result_queue.get_nowait()
                self._handle_worker_result(result)
        except queue.Empty:
            pass
        finally:
            # Schedule next check
            if self.winfo_exists():
                self.after(100, self._check_queue)
    
    def _handle_worker_result(self, result: Dict[str, Any]) -> None:
        """
        Handle result from worker thread.
        
        Args:
            result: Result dictionary with 'type', 'data', 'error' keys
        """
        result_type = result.get('type', '')
        data = result.get('data', {})
        error = result.get('error')
        
        # Stop progress indication
        self._set_working(False)
        
        if error is not None:
            # Show error message
            error_msg = i18n_t('error_capture_failed', ns='monster_editor', default='Capture failed: {}')
            self._show_error('Error', error_msg.format(error))
            return
        
        if result_type == 'capture':
            # Handle capture result
            success_msg = i18n_t('msg_template_added', ns='monster_editor', default='Template added successfully')
            self._show_info('Success', success_msg)
            
        elif result_type == 'test':
            # Handle test result
            matches = data.get('matches', 0)
            confidence = data.get('confidence', 0.0)
            
            if matches > 0:
                success_msg = i18n_t('msg_test_success', ns='monster_editor', default='Found {} matches (confidence: {:.1%})')
                self._show_info('Test Result', success_msg.format(matches, confidence))
            else:
                fail_msg = i18n_t('msg_test_failed', ns='monster_editor', default='No matches found')
                self._show_info('Test Result', fail_msg)
    
    def _set_working(self, working: bool) -> None:
        """
        Set working state (show/hide progress, enable/disable buttons).
        
        Args:
            working: True if working, False otherwise
        """
        self.is_working = working
        
        if working:
            # Show progress
            progress_text = i18n_t('progress_loading', ns='monster_editor', default='Loading...')
            if self.progress_label is not None:
                self.progress_label.config(text=progress_text)
            
            # Disable buttons - icons auto-change to forbidden
            if self.capture_button is not None:
                set_button_enabled(
                    self.capture_button,
                    enabled=False,
                    tooltip='Busy...' if get_lang() == 'en' else 'Đang xử lý...'
                )
            if self.test_button is not None:
                set_button_enabled(
                    self.test_button,
                    enabled=False,
                    tooltip='Busy...' if get_lang() == 'en' else 'Đang xử lý...'
                )
            if self.save_button is not None:
                set_button_enabled(
                    self.save_button,
                    enabled=False,
                    tooltip='Busy...' if get_lang() == 'en' else 'Đang xử lý...'
                )
        else:
            # Hide progress
            if self.progress_label is not None:
                self.progress_label.config(text='')
            
            # Enable buttons - icons restore
            if self.capture_button is not None:
                set_button_enabled(
                    self.capture_button,
                    enabled=True,
                    tooltip='Capture template' if get_lang() == 'en' else 'Chụp template'
                )
            if self.test_button is not None:
                set_button_enabled(
                    self.test_button,
                    enabled=True,
                    tooltip='Test detection' if get_lang() == 'en' else 'Kiểm tra phát hiện'
                )
            if self.save_button is not None:
                # Save button state depends on dirty flag
                self._update_dirty_state_ui()
    
    def _on_threshold_changed(self, value: str) -> None:
        """Handle threshold scale change."""
        if self.threshold_label is not None:
            self.threshold_label.config(text=f"{float(value):.2f}")
    
    def _on_save(self) -> None:
        """
        Handle Save button click - save all monsters to JSON.
        
        Following PYTHON_CODING_GUIDELINES.md:
        - Rule 1: Type hints and validation
        - Rule 2: None checks before access
        - Rule 5: No duplication
        """
        # Rule 2: Check if there's anything to save
        if not self.monsters or not isinstance(self.monsters, list):
            error_msg = i18n_t('msg_no_data', ns='monster_editor', default='No data to save')
            self._show_warning('Warning', error_msg)
            return
        
        # Validate all monsters before saving
        for idx, monster in enumerate(self.monsters):
            # Rule 2: Check monster is dict
            if not isinstance(monster, dict):
                self._show_error('Error', f'Invalid monster data at index {idx}')
                return
            
            # Rule 1: Validate required fields
            name = monster.get('name', '').strip()
            if not name:
                self._show_error('Error', f'Monster at index {idx} has no name')
                return
        
        # Rule 5: Call save once, cache result
        success = self._save_monsters()
        
        if success:
            # Flash status label instead of popup (subtle feedback)
            self._flash_save_success()
            print(f"[MonsterEditor] Saved {len(self.monsters)} monsters successfully")
        else:
            # Error already shown by _save_monsters()
            pass
    
    def _on_cancel(self) -> None:
        """
        Handle cancel/close button click.
        
        Prompts user if there are unsaved changes.
        Following PYTHON_CODING_GUIDELINES.md:
        - Rule 2: Check is_dirty before prompting
        """
        # Cancel any pending confirmation first
        self._cancel_confirmation()
        
        # Rule 2: Check if there are unsaved changes
        if self.is_dirty:
            # Prompt user
            msg = i18n_t('msg_unsaved_changes', ns='monster_editor', 
                        default='You have unsaved changes. Discard them?')
            title = i18n_t('title_confirm', ns='monster_editor', default='Confirm')
            
            response = self._ask_yes_no(title, msg)
            
            if not response:
                # User chose "No" - don't close
                return
        
        # No unsaved changes or user confirmed - close window
        self.destroy()
    
    def _on_app_mode_change(self, mode: str) -> None:
        """
        Handle app window mode change from component callback.
        
        Args:
            mode: New mode string ('normal', 'topmost', 'minimized', 'maximized')
        
        Note: Component already saves to hunt_config.json.
        """
        print(f"[MonsterEditor] App window mode changed to: {mode}")
        
        # Apply to current window
        if mode == 'topmost':
            self.attributes('-topmost', True)
        elif mode == 'normal':
            self.attributes('-topmost', False)
        elif mode == 'minimized':
            self.iconify()
        elif mode == 'maximized':
            self.state('zoomed')  # Windows maximize
    
    def _on_game_mode_change(self, mode: str) -> None:
        """
        Handle game window mode change from component callback.
        
        Args:
            mode: New mode string ('none', 'below', 'above')
        
        Note: Component already saves to hunt_config.json, 
              this is just for additional app-level logic.
        """
        print(f"[MonsterEditor] Game window mode changed to: {mode}")
        
        # Update internal StringVar (for consistency)
        self.game_window_mode_var.set(mode)
        
        # TODO: Trigger game window launch if needed
        # if mode == 'above':
        #     self._launch_game_window(topmost=True)
        # elif mode == 'below':
        #     self._launch_game_window(topmost=False)
        # elif mode == 'none':
        #     self._close_game_window()
    
    def _on_capture(self) -> None:
        """Handle capture button click."""
        try:
            print("[QuickEditor] Capture button clicked")
            
            # Set working state
            self._set_working(True)
            
            # TODO: Start capture in worker thread
            # For now, simulate with mock result after 2 seconds
            def mock_capture():
                import time
                time.sleep(2)
                self.result_queue.put({
                    'type': 'capture',
                    'data': {'template_path': 'mock_template.png'},
                    'error': None
                })
            
            thread = threading.Thread(target=mock_capture, daemon=True)
            thread.start()
            
        except Exception as e:
            print(f"[QuickEditor] Error in capture: {e}")
            self._set_working(False)
            self._show_error('Error', f'Capture failed: {e}')
    
    def _on_test(self) -> None:
        """Handle test button click."""
        try:
            print("[QuickEditor] Test button clicked")
            
            # Set working state
            self._set_working(True)
            
            # TODO: Start test in worker thread
            # For now, simulate with mock result after 1.5 seconds
            def mock_test():
                import time
                time.sleep(1.5)
                self.result_queue.put({
                    'type': 'test',
                    'data': {'matches': 3, 'confidence': 0.85},
                    'error': None
                })
            
            thread = threading.Thread(target=mock_test, daemon=True)
            thread.start()
            
        except Exception as e:
            print(f"[QuickEditor] Error in test: {e}")
            self._set_working(False)
            self._show_error('Error', f'Test failed: {e}')
    
    def _validate(self) -> bool:
        """
        Validate form input.
        
        Returns:
            bool: True if valid, False otherwise
        """
        # Check name not empty
        if self.name_entry is not None:
            name = self.name_entry.get().strip()
            if not name:
                error_msg = i18n_t('error_name_empty', ns='monster_editor', default='Monster name cannot be empty')
                self._show_error('Validation Error', error_msg)
                return False
        
        # Check level is positive integer
        if self.level_spinbox is not None:
            try:
                level = int(self.level_spinbox.get())
                if level < 1:
                    raise ValueError()
            except ValueError:
                error_msg = i18n_t('error_level_invalid', ns='monster_editor', default='Level must be a positive integer')
                self._show_error('Validation Error', error_msg)
                return False
        
        return True
    
    def _refresh_monster_list(self) -> None:
        """Refresh the monster listbox with current monsters."""
        if self.monster_listbox is None:
            return
        
        # Handle Treeview vs Listbox
        if isinstance(self.monster_listbox, ttk.Treeview):
            # Clear Treeview
            for item in self.monster_listbox.get_children():
                self.monster_listbox.delete(item)
            
            # Load monsters if not already loaded
            if not self.monsters:
                self._load_monsters()
            
            # Populate Treeview with 2 columns: icon + name
            for idx, monster in enumerate(self.monsters):
                name = monster.get('name', 'Unnamed')
                level = monster.get('level', 1)
                icon = '👹'  # Monster emoji as icon
                display_name = f"{name} (Lv.{level})"
                
                # Insert with monster id as item id for easy lookup
                item_id = monster.get('id', str(idx))
                self.monster_listbox.insert('', 'end', iid=item_id, values=(icon, display_name))
            
            # Select current monster if editing
            if self.current_monster_id:
                try:
                    self.monster_listbox.selection_set(self.current_monster_id)
                    self.monster_listbox.see(self.current_monster_id)
                except:
                    pass  # Item not found
        else:
            # Legacy Listbox support
            self.monster_listbox.delete(0, tk.END)
            
            if not self.monsters:
                self._load_monsters()
            
            for idx, monster in enumerate(self.monsters):
                name = monster.get('name', 'Unnamed')
                level = monster.get('level', 1)
                display_name = f"👹 {name} (Lv.{level})"
                self.monster_listbox.insert(tk.END, display_name)
            
            # Select current monster if editing
            if self.current_monster_id:
                for idx, monster in enumerate(self.monsters):
                    if monster.get('id') == self.current_monster_id:
                        self.monster_listbox.selection_set(idx)
                        self.monster_listbox.see(idx)
                        break
    
    def _auto_select_first_items(self) -> None:
        """Auto-select first monster and first template when opening form."""
        # Select first monster
        if self.monster_listbox and self.monsters:
            if isinstance(self.monster_listbox, ttk.Treeview):
                # Get first item in Treeview
                children = self.monster_listbox.get_children()
                if children:
                    first_item_id = children[0]
                    self.monster_listbox.selection_set(first_item_id)
                    self.monster_listbox.see(first_item_id)
                    # Trigger selection event manually
                    self.current_monster_id = first_item_id
                    
                    # Find and populate first monster
                    for monster in self.monsters:
                        if monster.get('id') == first_item_id:
                            self._populate_info_form(monster)
                            print(f"[MonsterEditor] Auto-selected first monster: {monster.get('name')}")
                            
                            # Auto-select first template after a short delay
                            self.after(50, self._auto_select_first_template)
                            break
            else:
                # Legacy Listbox
                if len(self.monsters) > 0:
                    self.monster_listbox.selection_set(0)
                    self.monster_listbox.see(0)
                    monster = self.monsters[0]
                    self.current_monster_id = monster.get('id')
                    self._populate_info_form(monster)
                    print(f"[MonsterEditor] Auto-selected first monster: {monster.get('name')}")
                    
                    # Auto-select first template after a short delay
                    self.after(50, self._auto_select_first_template)
    
    def _auto_select_first_template(self) -> None:
        """Auto-select first template in template list."""
        if not self.template_listbox or not isinstance(self.template_listbox, ttk.Treeview):
            return
        
        # Get first template item
        children = self.template_listbox.get_children()
        if children:
            first_template_id = children[0]
            self.template_listbox.selection_set(first_template_id)
            self.template_listbox.see(first_template_id)
            
            # Trigger template selection to show preview
            # Create a fake event to pass to _on_template_select
            class FakeEvent:
                pass
            
            self._on_template_select(FakeEvent())
            print(f"[MonsterEditor] Auto-selected first template")
    
    def _on_tab_changed(self, event: Any) -> None:
        """Handle notebook tab change - cancel any pending confirmation."""
        # Cancel confirmation when tab changes
        self._cancel_confirmation()
    
    def _on_monster_select(self, event: Any) -> None:
        """Handle monster selection from Treeview."""
        # Cancel any pending confirmation when selection changes
        self._cancel_confirmation()
        
        if self.monster_listbox is None:
            return
        
        # Handle Treeview vs Listbox
        if isinstance(self.monster_listbox, ttk.Treeview):
            # Get selected item (Treeview uses selection() instead of curselection())
            selection = self.monster_listbox.selection()
            if not selection:
                # Disable delete button when no selection
                if self.delete_monster_button:
                    self.delete_monster_button.config(state='disabled')
                return
            
            # Enable delete button when has selection
            if self.delete_monster_button:
                self.delete_monster_button.config(state='normal')
            
            # Get the item id (which is the monster id)
            selected_id = selection[0]
            self.current_monster_id = selected_id
            
            # Find monster by id
            for monster in self.monsters:
                if monster.get('id') == selected_id:
                    # Populate form with monster data
                    self._populate_info_form(monster)
                    print(f"[MonsterEditor] Selected monster: {monster.get('name')}")
                    break
        else:
            # Legacy Listbox support
            selection_idx = self.monster_listbox.curselection()
            if not selection_idx:
                # Disable delete button when no selection
                if self.delete_monster_button:
                    self.delete_monster_button.config(state='disabled')
                return
            
            # Enable delete button when has selection
            if self.delete_monster_button:
                self.delete_monster_button.config(state='normal')
            
            index = selection_idx[0]
            if 0 <= index < len(self.monsters):
                monster = self.monsters[index]
                self.current_monster_id = monster.get('id')
                self._populate_info_form(monster)
                print(f"[MonsterEditor] Selected monster: {monster.get('name')}")
    
    def _toggle_edit_mode(self) -> None:
        """Toggle between locked and edit mode for form fields."""
        self.is_editing = not self.is_editing
        
        if self.is_editing:
            # Switch to edit mode
            self._set_fields_state('normal')
            
            # Note: Button is now icon-only, so we don't change text
            # Tooltip will guide users that it's now in "save" mode
            
            # Show editing badge at top-left of tab
            if self.editing_badge and not self.editing_badge.winfo_ismapped():
                self.editing_badge.pack(side='left')
                
            # Mark as dirty to enable save button
            self.set_monster_dirty(True)
        else:
            # Switch to locked mode (save changes)
            self._save_form_to_current_monster()
            self._set_fields_state('readonly')
            
            # Note: Button is now icon-only, so we don't change text
            
            # Hide editing badge
            if self.editing_badge and self.editing_badge.winfo_ismapped():
                self.editing_badge.pack_forget()
    
    def _toggle_template_edit_mode(self) -> None:
        """Toggle between locked and edit mode for template buttons."""
        self.is_editing = not self.is_editing
        
        if self.is_editing:
            # Switch to edit mode
            # Add button always enabled (can create new template anytime)
            if self.add_template_button:
                self.add_template_button.config(state='normal')
            
            # Delete and Test buttons depend on selection (handled by _on_template_select)
            
            # Enable preview action buttons (Capture, Browse)
            if hasattr(self, 'capture_button') and self.capture_button:
                self.capture_button.config(state='normal')
            if hasattr(self, 'browse_button') and self.browse_button:
                self.browse_button.config(state='normal')
            
            # Show editing badge
            if self.template_editing_badge and not self.template_editing_badge.winfo_ismapped():
                self.template_editing_badge.pack(side='left', padx=(0, 4))
                
            # Mark as dirty to enable save button
            self.set_monster_dirty(True)
        else:
            # Switch to locked mode
            # All buttons disabled in locked mode
            if self.add_template_button:
                self.add_template_button.config(state='disabled')
            if self.delete_template_button:
                self.delete_template_button.config(state='disabled')
            if self.test_template_button:
                self.test_template_button.config(state='disabled')
            
            # Disable preview action buttons
            if hasattr(self, 'capture_button') and self.capture_button:
                self.capture_button.config(state='disabled')
            if hasattr(self, 'browse_button') and self.browse_button:
                self.browse_button.config(state='disabled')
            
            # Hide editing badge
            if self.template_editing_badge and self.template_editing_badge.winfo_ismapped():
                self.template_editing_badge.pack_forget()
    
    def _toggle_column_visibility(self) -> None:
        """Toggle visibility of Treeview columns based on checkboxes."""
        if not isinstance(self.template_listbox, ttk.Treeview):
            return
        
        # Get current column configuration
        display_cols = []
        
        if self.col_image_visible.get():
            display_cols.append('image')
        if self.col_threshold_visible.get():
            display_cols.append('threshold')
        if self.col_path_visible.get():
            display_cols.append('name')
        
        # Update displaycolumns (empty tuple shows all, list shows selected)
        if len(display_cols) == 3:
            # Show all columns
            self.template_listbox.config(displaycolumns=('image', 'threshold', 'name'))
        else:
            # Show only selected columns
            self.template_listbox.config(displaycolumns=tuple(display_cols))
    
    def _on_column_visibility_change(self) -> None:
        """Handle column visibility checkbox changes - update display and save settings."""
        self._toggle_column_visibility()
        self._save_ui_settings()
    
    def _set_fields_state(self, state: str) -> None:
        """Set state of all form fields.
        
        Args:
            state: 'normal', 'readonly', or 'disabled'
        """
        # Entry widgets
        if self.name_entry:
            self.name_entry.config(state=state)  # type: ignore
        if self.hp_entry:
            self.hp_entry.config(state=state)  # type: ignore
        if self.damage_entry:
            self.damage_entry.config(state=state)  # type: ignore
        
        # Spinbox widgets (use 'readonly' for locked, 'normal' for edit)
        spinbox_state = 'readonly' if state == 'readonly' else state
        if self.level_spinbox:
            self.level_spinbox.config(state=spinbox_state)  # type: ignore
        if self.priority_spinbox:
            self.priority_spinbox.config(state=spinbox_state)  # type: ignore
        
        # Text widget (use 'disabled' for locked, 'normal' for edit)
        if self.desc_text:
            text_state = 'disabled' if state == 'readonly' else state
            self.desc_text.config(state=text_state)  # type: ignore
    
    def _save_form_to_current_monster(self) -> None:
        """Save current form values to the selected monster."""
        if not self.current_monster_id:
            return
        
        # Find current monster
        for monster in self.monsters:
            if monster.get('id') == self.current_monster_id:
                # Save form values
                if self.name_entry:
                    monster['name'] = self.name_entry.get().strip()
                if self.level_spinbox:
                    try:
                        monster['level'] = int(self.level_spinbox.get())
                    except:
                        pass
                if self.priority_spinbox:
                    try:
                        monster['priority'] = int(self.priority_spinbox.get())
                    except:
                        pass
                if self.hp_entry:
                    monster['hp'] = self.hp_entry.get().strip()
                if self.damage_entry:
                    monster['damage'] = self.damage_entry.get().strip()
                if self.desc_text:
                    monster['description'] = self.desc_text.get('1.0', 'end-1c').strip()
                
                self.is_dirty = True
                self._update_dirty_state_ui()
                self._refresh_monster_list()
                print(f"[MonsterEditor] Saved changes to monster: {monster.get('name')}")
                break
    
    # ============================================
    # Inline Confirmation System
    # ============================================
    # ============================================
    # Inline Confirmation System (using ConfirmationWidget)
    # ============================================
    
    def _show_confirmation(self, action_callback, message: str = "", auto_hide_seconds: int = 10) -> None:
        """Show inline confirmation widget for an action.
        
        Args:
            action_callback: Function to call if user clicks Yes
            message: Confirmation message to display
            auto_hide_seconds: Seconds before auto-hiding (default 10)
        """
        if not self.confirmation_widget or not hasattr(self, 'confirmation_frame'):
            # Fallback: execute action immediately if widget not available
            try:
                action_callback()
            except Exception as e:
                print(f"[MonsterEditor] Error executing action: {e}")
            return
        
        # Set message
        if hasattr(self, 'confirmation_message'):
            self.confirmation_message.config(text=message)
        
        # Set the callback (wraps with validation)
        def safe_callback():
            """Wrapper to validate state before executing action."""
            try:
                # Hide confirmation first
                self._hide_confirmation()
                
                # Execute the action
                action_callback()
            except Exception as e:
                print(f"[MonsterEditor] Error executing action: {e}")
                import traceback
                traceback.print_exc()
        
        def cancel_callback():
            """Cancel confirmation."""
            self._hide_confirmation()
        
        self.confirmation_widget.set_confirm_callback(safe_callback)
        self.confirmation_widget.set_cancel_callback(cancel_callback)
        
        # Show confirmation frame and widget
        if self.notebook:
            self.confirmation_frame.pack(fill='x', pady=(0, 5), before=self.notebook)
        else:
            self.confirmation_frame.pack(fill='x', pady=(0, 5))
        self.confirmation_widget.show(side='right', padx=(5, 0))
    
    def _hide_confirmation(self) -> None:
        """Hide inline confirmation widget and frame."""
        if self.confirmation_widget:
            self.confirmation_widget.hide()
        if hasattr(self, 'confirmation_frame'):
            self.confirmation_frame.pack_forget()
    
    def _cancel_confirmation(self) -> None:
        """Cancel confirmation - hide and clear callbacks without executing."""
        if self.confirmation_widget:
            self.confirmation_widget.cancel()
        # Also hide the confirmation frame
        if hasattr(self, 'confirmation_frame'):
            self.confirmation_frame.pack_forget()
    
    # ============================================
    # Monster CRUD Operations
    # ============================================
    
    def _on_add_monster(self) -> None:
        """Handle add monster button click."""
        # Create new monster with default values
        new_monster = {
            'id': str(uuid.uuid4()),
            'name': i18n_t('default_monster_name', ns='monster_editor', default='New Monster'),
            'level': 1,
            'priority': 1,
            'hp': 100,
            'damage_per_hit': 10,
            'templates': []
        }
        
        # Add to list
        self.monsters.append(new_monster)
        self.is_dirty = True
        
        # Refresh listbox
        self._refresh_monster_list()
        
        # Select new monster (Treeview uses selection_set with item id)
        if self.monster_listbox:
            try:
                self.monster_listbox.selection_set(new_monster['id'])
                self.monster_listbox.see(new_monster['id'])
            except:
                pass  # Item not found
        
        # Set as current
        self.current_monster_id = new_monster['id']
        
        # Populate form with new monster data
        self._populate_info_form(new_monster)
        
        print(f"[MonsterEditor] Added new monster: {new_monster['id']}")
    
    def _on_delete_monster(self) -> None:
        """Handle delete monster button click - show inline confirmation."""
        if self.monster_listbox is None:
            return
        
        # Handle Treeview vs Listbox
        if isinstance(self.monster_listbox, ttk.Treeview):
            selection = self.monster_listbox.selection()
            if not selection:
                # Button should be disabled, return silently
                return
            
            # Get selected item ID (which is the monster ID)
            item_id = selection[0]
            
            # Find monster by ID
            monster = None
            monster_index = -1
            for idx, m in enumerate(self.monsters):
                if m.get('id') == item_id:
                    monster = m
                    monster_index = idx
                    break
            
            if monster is None or monster_index < 0:
                return
        else:
            # Legacy Listbox support
            selection_idx = self.monster_listbox.curselection()
            if not selection_idx:
                # Button should be disabled, return silently
                return
            
            monster_index = selection_idx[0]
            if not (0 <= monster_index < len(self.monsters)):
                return
            monster = self.monsters[monster_index]
        
        # Show inline confirmation instead of popup
        def delete_action():
            """The actual delete action to execute if confirmed."""
            # Validate monster still exists before deletion
            if monster_index < 0 or monster_index >= len(self.monsters):
                return
            
            # Validate it's still the same monster
            if self.monsters[monster_index] != monster:
                return
            
            deleted_id = monster.get('id')
            deleted_name = monster.get('name', 'Unnamed')
            
            print(f"[MonsterEditor] Deleting monster: {deleted_name} (ID: {deleted_id})")
            print(f"[MonsterEditor] Monsters before delete: {len(self.monsters)}")
            
            # Perform deletion
            self.monsters.pop(monster_index)
            self.is_dirty = True
            
            print(f"[MonsterEditor] Monsters after delete: {len(self.monsters)}")
            
            # Clear form and current selection if deleted monster was selected
            if self.current_monster_id == deleted_id:
                self.current_monster_id = None
                self._clear_info_form()
            
            # Disable delete button (no selection after delete)
            if self.delete_monster_button:
                self.delete_monster_button.config(state='disabled')
            
            # Refresh listbox
            print("[MonsterEditor] Calling _refresh_monster_list()...")
            self._refresh_monster_list()
            print("[MonsterEditor] _refresh_monster_list() completed")
            
            # Save to file immediately
            print("[MonsterEditor] Saving monsters to file...")
            self._save_monsters()
            print("[MonsterEditor] Save completed")
            
            # Update dirty state UI
            self._update_dirty_state_ui()
            
            print(f"[MonsterEditor] Deleted monster: {deleted_name}")
        
        # Show inline confirmation with message
        monster_name = monster.get('name', 'Unnamed')
        message = f"⚠️ Xác nhận xóa Quái vật: {monster_name}?"
        self._show_confirmation(delete_action, message=message, auto_hide_seconds=10)
    
    def _populate_info_form(self, monster: Dict[str, Any]) -> None:
        """Populate Info tab form with monster data and keep fields locked."""
        if not all([self.name_entry, self.level_spinbox, self.priority_spinbox, 
                    self.hp_entry, self.damage_entry, self.desc_text]):
            return
        
        # Clear form first
        self._clear_info_form()
        
        # Reset edit mode to locked (always start locked when selecting a monster)
        if self.is_editing:
            self.is_editing = False
            # Note: Button is icon-only, no text change needed
            # Hide editing badge if showing
            if self.editing_badge and self.editing_badge.winfo_ismapped():
                self.editing_badge.pack_forget()
        
        # Temporarily enable fields to populate them
        self._set_fields_state('normal')
        
        # Populate fields (null checks already done above)
        assert self.name_entry is not None
        assert self.level_spinbox is not None
        assert self.priority_spinbox is not None
        assert self.hp_entry is not None
        assert self.damage_entry is not None
        assert self.desc_text is not None
        
        self.name_entry.insert(0, monster.get('name', ''))
        self.level_spinbox.delete(0, tk.END)
        self.level_spinbox.insert(0, str(monster.get('level', 1)))
        self.priority_spinbox.delete(0, tk.END)
        self.priority_spinbox.insert(0, str(monster.get('priority', 1)))
        self.hp_entry.insert(0, str(monster.get('hp', 100)))
        self.damage_entry.insert(0, str(monster.get('damage_per_hit', 10)))
        
        desc = monster.get('description', '')
        if desc:
            self.desc_text.insert('1.0', desc)
        
        # Lock fields after populating (readonly mode)
        self._set_fields_state('readonly')
        
        # Remove focus from name entry (no auto focus)
        if self.name_entry:
            self.focus_set()  # Set focus to window instead of entry
        
        # Refresh template list for this monster
        self._refresh_template_list()
    
    def _clear_info_form(self) -> None:
        """Clear all fields in Info tab form."""
        # Temporarily enable fields to clear them
        old_state = 'readonly' if not self.is_editing else 'normal'
        self._set_fields_state('normal')
        
        if self.name_entry:
            self.name_entry.delete(0, tk.END)
        if self.level_spinbox:
            self.level_spinbox.delete(0, tk.END)
            self.level_spinbox.insert(0, '1')
        if self.priority_spinbox:
            self.priority_spinbox.delete(0, tk.END)
            self.priority_spinbox.insert(0, '1')
        if self.hp_entry:
            self.hp_entry.delete(0, tk.END)
        if self.damage_entry:
            self.damage_entry.delete(0, tk.END)
        if self.desc_text:
            self.desc_text.delete('1.0', tk.END)
        
        # Restore previous state
        self._set_fields_state(old_state)
    
    def _on_info_change(self, event: Any = None) -> None:
        """Handle changes in Info tab form fields."""
        # Mark current monster as dirty and update UI
        self.set_monster_dirty(True)
        
        # Update current monster data in memory (if selected)
        if self.current_monster_id and self.monsters:
            for monster in self.monsters:
                if monster.get('id') == self.current_monster_id:
                    # Update monster data from form
                    if self.name_entry:
                        monster['name'] = self.name_entry.get()
                    if self.level_spinbox:
                        try:
                            monster['level'] = int(self.level_spinbox.get())
                        except ValueError:
                            pass
                    if self.priority_spinbox:
                        try:
                            monster['priority'] = int(self.priority_spinbox.get())
                        except ValueError:
                            pass
                    if self.hp_entry:
                        try:
                            monster['hp'] = int(self.hp_entry.get())
                        except ValueError:
                            pass
                    if self.damage_entry:
                        try:
                            monster['damage_per_hit'] = int(self.damage_entry.get())
                        except ValueError:
                            pass
                    if self.desc_text:
                        monster['description'] = self.desc_text.get('1.0', tk.END).strip()
                    
                    # Debounced refresh - cancel previous, schedule new
                    if self._refresh_list_after_id is not None:
                        self.after_cancel(self._refresh_list_after_id)
                    self._refresh_list_after_id = self.after(300, self._refresh_monster_list)
                    break

    # ========== Template Management Methods (Library Manager functions) ==========
    
    def _find_monster_by_id(self, monster_id: str) -> Optional[Dict[str, Any]]:
        """Find monster by ID from self.monsters list."""
        if not monster_id or not self.monsters:
            return None
        for monster in self.monsters:
            if monster.get('id') == monster_id:
                return monster
        return None
    
    def _sanitize_filename(self, name: str) -> str:
        """Sanitize a string for use as a filename."""
        # Remove invalid filename characters
        return re.sub(r'[<>:"/\\|?*]', '_', name)
    
    def _on_template_select(self, event: Any) -> None:
        """Handle template selection from Treeview - show preview and update threshold."""
        # Cancel any pending confirmation when selection changes
        self._cancel_confirmation()
        
        if self.template_listbox is None or not isinstance(self.template_listbox, ttk.Treeview):
            return
        
        # Get selected item
        selection = self.template_listbox.selection()
        
        # Update button states based on selection
        has_selection = bool(selection)
        
        # Enable/disable buttons based on selection
        if self.delete_template_button:
            self.delete_template_button.config(state='normal' if has_selection else 'disabled')
        if self.test_template_button:
            self.test_template_button.config(state='normal' if has_selection else 'disabled')
        
        # Browse and Capture buttons work differently:
        # - If has selection: update existing template
        # - If no selection: create new template
        # So they should always be enabled when monster is selected
        
        if not selection:
            # Clear preview when no selection
            if self.template_preview_label:
                self.template_preview_label.config(text='No template selected', image='')
            return
        
        # Get template data from selection
        item_id = selection[0]
        
        # Extract index from item_id (format: template_<idx>)
        try:
            idx = int(item_id.split('_')[-1])
        except (ValueError, IndexError):
            return
        
        # Get monster and template
        if not self.current_monster_id:
            return
        
        monster = self._find_monster_by_id(self.current_monster_id)
        if not monster:
            return
        
        templates = monster.get('templates', [])
        if idx >= len(templates):
            return
        
        template = templates[idx]
        
        # Update threshold slider
        threshold = template.get('threshold', 0.7)
        if self.threshold_scale:
            self.threshold_scale.set(threshold)
        
        # Load and display template image preview
        template_path = template.get('path', '')
        template_name = template.get('name', 'Unknown')
        
        if template_path and Path(template_path).exists():
            try:
                # Load image with PIL if available
                if PIL_AVAILABLE and Image and ImageTk:
                    img = Image.open(template_path)
                    
                    # Resize to fit preview (max 250x250, maintain aspect ratio)
                    max_size = (250, 250)
                    img.thumbnail(max_size, Image.Resampling.LANCZOS)
                    
                    # Convert to PhotoImage
                    photo = ImageTk.PhotoImage(img)
                    
                    # Update preview label
                    if self.template_preview_label:
                        self.template_preview_label.config(image=photo, text='')
                        # Keep reference to prevent garbage collection
                        self.template_preview_label.image = photo  # type: ignore
                else:
                    # Fallback if PIL not available
                    if self.template_preview_label:
                        self.template_preview_label.config(
                            text=f"Preview:\n{template_name}\n\n(PIL required for image preview)",
                            image=''
                        )
            except Exception as e:
                print(f"[MonsterEditor] Error loading template preview: {e}")
                if self.template_preview_label:
                    self.template_preview_label.config(
                        text=f"Error loading\n{template_name}",
                        image=''
                    )
        else:
            # No valid path
            if self.template_preview_label:
                self.template_preview_label.config(
                    text=f"No preview\n{template_name}",
                    image=''
                )
        
        print(f"[MonsterEditor] Selected template: {template_name} (threshold: {threshold:.2f})")
    
    def _add_template(self) -> None:
        """Add a new empty template to the current monster."""
        # Check if monster is selected
        if not self.current_monster_id:
            return
        
        # Find monster
        monster = self._find_monster_by_id(self.current_monster_id)
        if not monster:
            return
        
        # Create new template with placeholder data
        new_template = {
            'name': i18n_t('default_template_name', ns='monster_editor', default='New Template'),
            'path': '',
            'threshold': 0.7
        }
        
        # Add to templates list
        if 'templates' not in monster:
            monster['templates'] = []
        
        monster['templates'].append(new_template)
        
        # Mark as dirty
        self.set_dirty(True)
        
        # Refresh template list
        self._refresh_template_list()
        
        # Show info
        messagebox.showinfo(
            'Template Added' if get_lang() == 'en' else 'Đã Thêm Template',
            'Use Capture or Browse to set the template image.' if get_lang() == 'en' 
            else 'Dùng Chụp hoặc Chọn File để đặt ảnh template.'
        )
    
    def _capture_template(self) -> None:
        """Capture template image from a selected screen region.
        - If a template is selected: update that template's image
        - If no template selected: create new template
        """
        # Prevent concurrent captures
        if self._is_capturing:
            return
        
        # Check if monster is selected
        if not self.current_monster_id:
            return
        
        # Check PIL availability
        if not PIL_AVAILABLE or ImageGrab is None:
            messagebox.showerror(
                'Pillow Required' if get_lang() == 'en' else 'Cần Pillow',
                'This feature requires Pillow. Please install with:\n\npip install pillow' if get_lang() == 'en'
                else 'Tính năng này cần Pillow. Vui lòng cài đặt bằng:\n\npip install pillow'
            )
            return
        
        # Check if updating existing template or creating new
        selected_template_idx = None
        if self.template_listbox and isinstance(self.template_listbox, ttk.Treeview):
            selection = self.template_listbox.selection()
            if selection:
                item_id = selection[0]
                try:
                    selected_template_idx = int(item_id.split('_')[-1])
                except (ValueError, IndexError):
                    pass
        
        # Set flag
        self._is_capturing = True
        
        try:
            # Find monster
            monster = self._find_monster_by_id(self.current_monster_id)
            if not monster:
                return
            
            # Hide window and capture region
            try:
                self.withdraw()
                self.update_idletasks()
                time.sleep(0.15)
            except Exception:
                pass
            
            try:
                overlay = self._RegionCaptureOverlay(self)
                bbox = overlay.show_modal()
            except Exception:
                bbox = None
            finally:
                try:
                    self.deiconify()
                    self.lift()
                    self.focus_force()
                except Exception:
                    pass
            
            if not bbox:
                return
            
            # Capture image
            try:
                img = ImageGrab.grab(bbox=bbox)
            except Exception as e:
                messagebox.showerror(
                    'Capture Failed' if get_lang() == 'en' else 'Chụp Thất Bại',
                    f"Error: {e}"
                )
                return
            
            # Save image
            base = self._sanitize_filename(monster.get('name', 'monster'))
            ts = int(time.time())
            filename = f"{base}_capture_{ts}.png"
            assets_dir = Path("assets/images/monsters")
            assets_dir.mkdir(parents=True, exist_ok=True)
            save_path = assets_dir / filename
            
            try:
                img.save(save_path)
            except Exception as e:
                messagebox.showerror(
                    'Save Failed' if get_lang() == 'en' else 'Lưu Thất Bại',
                    f"Error: {e}"
                )
                return
            
            # Update existing template or create new
            if selected_template_idx is not None:
                # Update existing template
                templates = monster.setdefault('templates', [])
                if selected_template_idx < len(templates):
                    templates[selected_template_idx]['name'] = filename
                    templates[selected_template_idx]['path'] = f'assets/images/monsters/{filename}'
                    message = 'Template updated successfully.' if get_lang() == 'en' else 'Đã cập nhật template.'
                else:
                    # Index out of range, create new instead
                    tmpl = {'name': filename, 'path': f'assets/images/monsters/{filename}', 'threshold': 0.85}
                    templates.append(tmpl)
                    message = 'Template created successfully.' if get_lang() == 'en' else 'Đã tạo template mới.'
            else:
                # Create new template
                tmpl = {'name': filename, 'path': f'assets/images/monsters/{filename}', 'threshold': 0.85}
                monster.setdefault('templates', []).append(tmpl)
                message = 'Template created successfully.' if get_lang() == 'en' else 'Đã tạo template mới.'
            
            self.has_unsaved_changes = True
            self.set_dirty(True)
            
            # Refresh template list
            self._refresh_template_list()
            
            # Re-select the template if it was an update
            if selected_template_idx is not None and self.template_listbox:
                try:
                    item_id = f'template_{selected_template_idx}'
                    self.template_listbox.selection_set(item_id)
                    self.template_listbox.see(item_id)
                except:
                    pass
            
            messagebox.showinfo(
                'Success' if get_lang() == 'en' else 'Thành công',
                message
            )
        finally:
            # Always reset flag
            self._is_capturing = False
    
    def _browse_template_image(self) -> None:
        """Browse for template image file.
        - If a template is selected: update that template's image
        - If no template selected: create new template
        """
        # Prevent concurrent browse operations
        if self._is_browsing:
            return
        
        # Check if monster is selected
        if not self.current_monster_id:
            return
        
        # Check if updating existing template or creating new
        selected_template_idx = None
        if self.template_listbox and isinstance(self.template_listbox, ttk.Treeview):
            selection = self.template_listbox.selection()
            if selection:
                item_id = selection[0]
                try:
                    selected_template_idx = int(item_id.split('_')[-1])
                except (ValueError, IndexError):
                    pass
        
        # Set flag
        self._is_browsing = True
        
        try:
            file_path = filedialog.askopenfilename(
                title='Select Template Image' if get_lang() == 'en' else 'Chọn Ảnh Template',
                filetypes=[('Image files', '*.png *.jpg *.jpeg *.bmp'), ('All files', '*.*')]
            )
            
            if not file_path:
                return
            
            monster = self._find_monster_by_id(self.current_monster_id)
            if not monster:
                return
            
            # Copy file to assets directory
            import shutil
            filename = Path(file_path).name
            base_name = Path(filename).stem
            ext = Path(filename).suffix
            ts = int(time.time())
            new_filename = f"{base_name}_{ts}{ext}"
            
            assets_dir = Path("assets/images/monsters")
            assets_dir.mkdir(parents=True, exist_ok=True)
            dest_path = assets_dir / new_filename
            
            try:
                shutil.copy2(file_path, dest_path)
            except Exception as e:
                messagebox.showerror(
                    'Copy Failed' if get_lang() == 'en' else 'Sao Chép Thất Bại',
                    f"Error: {e}"
                )
                return
            
            # Update existing template or create new
            if selected_template_idx is not None:
                # Update existing template
                templates = monster.setdefault('templates', [])
                if selected_template_idx < len(templates):
                    templates[selected_template_idx]['name'] = new_filename
                    templates[selected_template_idx]['path'] = f'assets/images/monsters/{new_filename}'
                    message = 'Template updated successfully.' if get_lang() == 'en' else 'Đã cập nhật template.'
                else:
                    # Index out of range, create new instead
                    tmpl = {'name': new_filename, 'path': f'assets/images/monsters/{new_filename}', 'threshold': 0.85}
                    templates.append(tmpl)
                    message = 'Template created successfully.' if get_lang() == 'en' else 'Đã tạo template mới.'
            else:
                # Create new template
                tmpl = {'name': new_filename, 'path': f'assets/images/monsters/{new_filename}', 'threshold': 0.85}
                monster.setdefault('templates', []).append(tmpl)
                message = 'Template created successfully.' if get_lang() == 'en' else 'Đã tạo template mới.'
            
            self.has_unsaved_changes = True
            self.set_dirty(True)
            
            # Refresh template list
            self._refresh_template_list()
            
            # Re-select the template if it was an update
            if selected_template_idx is not None and self.template_listbox:
                try:
                    item_id = f'template_{selected_template_idx}'
                    self.template_listbox.selection_set(item_id)
                    self.template_listbox.see(item_id)
                except:
                    pass
            
            messagebox.showinfo(
                'Success' if get_lang() == 'en' else 'Thành công',
                message
            )
        finally:
            # Always reset flag
            self._is_browsing = False
    
    def _delete_template(self) -> None:
        """Delete selected template (with inline confirmation)."""
        # Prevent concurrent delete operations
        if self._is_deleting:
            return
        
        if not self.current_monster_id or not self.template_listbox:
            return
        
        # Get selection - handle both Listbox and Treeview
        if isinstance(self.template_listbox, ttk.Treeview):
            selection = self.template_listbox.selection()
            if not selection:
                # No selection - button should be disabled, so just return silently
                return
            # For Treeview, use item_id as index
            item_id = selection[0]
            idx = int(item_id.split('_')[-1]) if '_' in item_id else 0
        else:
            # Legacy Listbox support
            selection = self.template_listbox.curselection()
            if not selection:
                # No selection - button should be disabled, so just return silently
                return
            idx = selection[0]
        
        monster = self._find_monster_by_id(self.current_monster_id)
        if not monster:
            return
        
        templates = monster.get('templates', [])
        if idx >= len(templates):
            return
        
        template = templates[idx]
        
        # Show inline confirmation instead of popup
        def delete_action():
            """The actual delete action to execute if confirmed."""
            # Set flag to prevent concurrent operations
            self._is_deleting = True
            
            try:
                # Validate current_monster_id still exists
                if not self.current_monster_id:
                    return
                
                # Validate template still exists before deletion
                current_monster = self._find_monster_by_id(self.current_monster_id)
                if not current_monster:
                    return
                
                current_templates = current_monster.get('templates', [])
                if idx >= len(current_templates):
                    return
                
                # Validate it's still the same template
                if current_templates[idx] != template:
                    return
                
                # Perform deletion
                del current_templates[idx]
                self.has_unsaved_changes = True
                self.is_dirty = True
                
                # Refresh template list
                self._refresh_template_list()
                
                # Save to file immediately
                self._save_monsters()
                
                # Update dirty state UI
                self._update_dirty_state_ui()
            except Exception as e:
                print(f"[MonsterEditor] Error deleting template: {e}")
                import traceback
                traceback.print_exc()
            finally:
                # Always reset flag
                self._is_deleting = False
        
        # Show inline confirmation with message
        template_name = template.get('name', 'Unknown')
        message = f"⚠️ Xác nhận xóa Template: {template_name}?"
        self._show_confirmation(delete_action, message=message, auto_hide_seconds=10)
    
    def _test_template_recognition(self) -> None:
        """Test match for current template on screen."""
        # Prevent concurrent test operations
        if self._is_testing:
            return
        
        if not self.current_monster_id or not self.template_listbox:
            return
        
        if locate_template is None:
            messagebox.showerror(
                'Error' if get_lang() == 'en' else 'Lỗi',
                'template_matcher not available' if get_lang() == 'en' else 'template_matcher không khả dụng'
            )
            return
        
        # Set flag
        self._is_testing = True
        
        try:
            # Get selection - handle both Listbox and Treeview
            if isinstance(self.template_listbox, ttk.Treeview):
                selection = self.template_listbox.selection()
                if not selection:
                    messagebox.showinfo(
                        'Info' if get_lang() == 'en' else 'Thông báo',
                        'Please select a template to test.' if get_lang() == 'en' else 'Vui lòng chọn template để test.'
                    )
                    return
                # For Treeview, use item_id as index
                item_id = selection[0]
                idx = int(item_id.split('_')[-1]) if '_' in item_id else 0
            else:
                # Legacy Listbox support
                selection = self.template_listbox.curselection()
                if not selection:
                    messagebox.showinfo(
                        'Info' if get_lang() == 'en' else 'Thông báo',
                        'Please select a template to test.' if get_lang() == 'en' else 'Vui lòng chọn template để test.'
                    )
                    return
                idx = selection[0]
            
            monster = self._find_monster_by_id(self.current_monster_id)
            if not monster:
                return
            
            templates = monster.get('templates', [])
            if idx >= len(templates):
                return
            
            template = templates[idx]
            path = template.get('path', '')
            threshold = template.get('threshold', 0.85)
            
            if not path:
                messagebox.showinfo(
                    'Info' if get_lang() == 'en' else 'Thông báo',
                    'Template has no path.' if get_lang() == 'en' else 'Template không có đường dẫn.'
                )
                return
            
            # Minimize and test
            try:
                self.iconify()
            except Exception:
                pass
            self.update()
            time.sleep(0.4)
            
            try:
                box, conf = locate_template(path, region=None, threshold=threshold, method='auto')
            except Exception as exc:
                try:
                    self.deiconify()
                    self.lift()
                except Exception:
                    pass
                messagebox.showerror('Error' if get_lang() == 'en' else 'Lỗi', str(exc))
                return
            
            # Restore window
            try:
                self.deiconify()
                self.lift()
            except Exception:
                pass
            
            # Show results
            if box:
                x = int(box[0] + box[2] // 2)
                y = int(box[1] + box[3] // 2)
                if conf is None:
                    msg = f"Match found at ({x}, {y})" if get_lang() == 'en' else f"Tìm thấy tại ({x}, {y})"
                else:
                    msg = f"Match found at ({x}, {y}) - Confidence: {conf:.2f}" if get_lang() == 'en' else f"Tìm thấy tại ({x}, {y}) - Độ tin cậy: {conf:.2f}"
                messagebox.showinfo('Test Recognition' if get_lang() == 'en' else 'Test Nhận Diện', msg)
            else:
                messagebox.showinfo('Test Recognition' if get_lang() == 'en' else 'Test Nhận Diện', 'No match found' if get_lang() == 'en' else 'Không tìm thấy')
        finally:
            # Always reset flag
            self._is_testing = False
    
    def _refresh_template_list(self) -> None:
        """Refresh template list with current monster's templates."""
        if not self.template_listbox:
            return
        
        # Handle both Treeview and Listbox
        if isinstance(self.template_listbox, ttk.Treeview):
            # Clear Treeview
            for item in self.template_listbox.get_children():
                self.template_listbox.delete(item)
            
            # Populate with current monster's templates
            if self.current_monster_id:
                monster = self._find_monster_by_id(self.current_monster_id)
                if monster:
                    templates = monster.get('templates', [])
                    for idx, tmpl in enumerate(templates):
                        # Get template data
                        name = tmpl.get('name', 'Unknown')
                        threshold = tmpl.get('threshold', 0.7)
                        path = tmpl.get('path', '')
                        
                        # Icon placeholder (use emoji or load actual thumbnail)
                        icon = '🖼️'
                        
                        # Display threshold as percentage
                        threshold_display = f"{threshold:.0%}"
                        
                        # Insert row with item_id as template_<idx>
                        item_id = f"template_{idx}"
                        # Column order: image | threshold | path
                        self.template_listbox.insert('', 'end', iid=item_id, values=(icon, threshold_display, path))
        else:
            # Legacy Listbox support
            self.template_listbox.delete(0, tk.END)
            
            if self.current_monster_id:
                monster = self._find_monster_by_id(self.current_monster_id)
                if monster:
                    templates = monster.get('templates', [])
                    for tmpl in templates:
                        name = tmpl.get('name', 'Unknown')
                        self.template_listbox.insert(tk.END, name)
        
        # Update button states after refresh (no selection by default)
        if self.delete_template_button:
            self.delete_template_button.config(state='disabled')
        if self.test_template_button:
            self.test_template_button.config(state='disabled')
    
    # Inner class for region capture overlay
    class _RegionCaptureOverlay(tk.Toplevel):
        """Fullscreen overlay for selecting a screen region."""
        def __init__(self, parent):
            super().__init__(parent)
            self.parent = parent
            self.withdraw()
            self.overrideredirect(True)
            self.attributes('-topmost', True)
            try:
                self.attributes('-alpha', 0.25)
            except Exception:
                pass
            self.configure(bg='black')
            # Fullscreen size
            self.geometry(f"{self.winfo_screenwidth()}x{self.winfo_screenheight()}+0+0")
            # Canvas to draw selection
            self.canvas = tk.Canvas(self, bg='black', highlightthickness=0, cursor='crosshair')
            self.canvas.pack(fill='both', expand=True)
            # State
            self._start = None
            self._rect = None
            self._bbox = None
            self._size_text = None
            # Bindings
            self.canvas.bind('<ButtonPress-1>', self._on_press)
            self.canvas.bind('<B1-Motion>', self._on_drag)
            self.canvas.bind('<ButtonRelease-1>', self._on_release)
            self.bind('<Escape>', lambda e: self._cancel())
        
        def show_modal(self):
            self.deiconify()
            self.grab_set()
            self.focus_force()
            self.wait_window(self)
            return self._bbox
        
        def _on_press(self, event):
            self._start = (event.x, event.y, event.x_root, event.y_root)
            if self._rect is not None:
                self.canvas.delete(self._rect)
                self._rect = None
            self._rect = self.canvas.create_rectangle(event.x, event.y, event.x, event.y, outline='#00E5FF', width=2)
            if self._size_text:
                self.canvas.delete(self._size_text)
                self._size_text = None
        
        def _on_drag(self, event):
            if self._start and self._rect:
                x0, y0, _, _ = self._start
                x1, y1 = event.x, event.y
                self.canvas.coords(self._rect, x0, y0, x1, y1)
                # Live size label
                w = abs(x1 - x0)
                h = abs(y1 - y0)
                label = f"{w} x {h}"
                if self._size_text:
                    self.canvas.delete(self._size_text)
                self._size_text = self.canvas.create_text(x1 + 10, y1 + 10, text=label, fill='white', anchor='nw')
        
        def _on_release(self, event):
            if not self._start:
                self.destroy()
                return
            x0, y0, xr0, yr0 = self._start
            x1, y1 = event.x, event.y
            # Convert to screen coords using root deltas
            dx = xr0 - x0
            dy = yr0 - y0
            sx0 = x0 + dx
            sy0 = y0 + dy
            sx1 = x1 + dx
            sy1 = y1 + dy
            left = int(min(sx0, sx1))
            top = int(min(sy0, sy1))
            right = int(max(sx0, sx1))
            bottom = int(max(sy0, sy1))
            # Minimum size safeguard
            if right - left < 5 or bottom - top < 5:
                self._bbox = None
            else:
                self._bbox = (left, top, right, bottom)
            self.destroy()
        
        def _cancel(self):
            self._bbox = None
            self.destroy()


# Singleton instance
_quick_editor_instance: Optional[QuickMonsterEditor] = None


def show_quick_monster_editor(
    parent: Union[tk.Widget, tk.Tk],
    monster_id: Optional[str] = None,
    on_save: Optional[Callable] = None
) -> QuickMonsterEditor:
    """
    Show quick monster editor (singleton).
    
    Args:
        parent: Parent widget (can be tk.Tk or tk.Widget)
        monster_id: Monster to edit (None for new)
        on_save: Callback when saved
    
    Returns:
        QuickMonsterEditor: Editor instance
    """
    global _quick_editor_instance
    
    if _quick_editor_instance is not None and _quick_editor_instance.winfo_exists():
        _quick_editor_instance.lift()
        _quick_editor_instance.focus_force()
        return _quick_editor_instance
    else:
        _quick_editor_instance = QuickMonsterEditor(parent, monster_id, on_save)
        return _quick_editor_instance
