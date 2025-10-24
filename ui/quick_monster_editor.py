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
from typing import Optional, Dict, Any, Callable, List
import queue
import threading
import json
import uuid
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
    from lib.ui.tooltip import attach_i18n_tooltip
except ImportError:
    def attach_i18n_tooltip(widget, key: str, ns: Optional[str], lang_provider: Callable, delay: int = 400) -> Any:
        pass

try:
    from lib.ui_style import UIStyle as UI
except ImportError:
    class UIStyle:
        FONT_TITLE = ('Segoe UI', 12, 'bold')
        FONT_SECTION = ('Segoe UI', 11, 'bold')
        FONT_LABEL = ('Segoe UI', 10)
        FONT_TEXT = ('Segoe UI', 10)
        FONT_BUTTON = ('Segoe UI', 10)
        FONT_SMALL = ('Segoe UI', 8)
        COLOR_PRIMARY = '#2196F3'
        COLOR_PRIMARY_TEXT = '#0D47A1'
        COLOR_TEXT = '#212121'
        COLOR_SUBTEXT = '#666666'
        COLOR_ACCENT = '#4CAF50'
        COLOR_DANGER = '#F44336'
        COLOR_WARNING = '#FF7043'
        BG_DEFAULT = '#FFFFFF'
        BG_PANEL = '#F5F5F5'
    UI = UIStyle

try:
    from lib.ui.icon_helper import IconHelper
    icon_helper = IconHelper()
except ImportError:
    class MockIconHelper:
        def get_icon(self, name: str, fallback: str = '', size: int = 16) -> str:
            return fallback
    icon_helper = MockIconHelper()

try:
    from lib.ui.capture_helper import capture_region_and_save
    PIL_AVAILABLE = True
except ImportError:
    capture_region_and_save = None
    PIL_AVAILABLE = False

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
        
        # Result queue for worker thread communication
        self.result_queue: queue.Queue = queue.Queue()
        self.is_working = False
        
        # Data
        self.monster_data: Dict[str, Any] = {
            'name': '',
            'level': 1,
            'threshold': 0.7,
            'templates': []
        }
        
        # Widgets (initialized in setup_ui)
        # Left panel
        self.monster_listbox: Optional[tk.Listbox] = None
        self.add_monster_button: Optional[tk.Button] = None
        self.delete_monster_button: Optional[tk.Button] = None
        
        # Right panel - Notebook tabs
        self.notebook: Optional[ttk.Notebook] = None
        self.info_tab: Optional[tk.Frame] = None
        self.templates_tab: Optional[tk.Frame] = None
        
        # Info tab widgets
        self.name_entry: Optional[tk.Entry] = None
        self.level_spinbox: Optional[tk.Spinbox] = None
        self.priority_spinbox: Optional[tk.Spinbox] = None
        self.hp_entry: Optional[tk.Entry] = None
        self.damage_entry: Optional[tk.Entry] = None
        self.desc_text: Optional[tk.Text] = None
        
        # Templates tab widgets
        self.template_listbox: Optional[tk.Listbox] = None
        self.template_scrollbar: Optional[tk.Scrollbar] = None
        self.capture_button: Optional[tk.Button] = None
        self.browse_button: Optional[tk.Button] = None
        self.delete_template_button: Optional[tk.Button] = None
        self.test_template_button: Optional[tk.Button] = None
        # Legacy widgets (from quick editor, may be removed later)
        self.progress_label: Optional[tk.Label] = None
        self.save_button: Optional[tk.Button] = None
        self.cancel_button: Optional[tk.Button] = None
        self.capture_button: Optional[tk.Button] = None
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
        self._load_monster()
        self._setup_ui()
        self._bind_events()
        self._start_queue_monitor()
        
        # Update UI to reflect initial dirty state
        self._update_dirty_state_ui()
    
    def _load_monsters(self) -> None:
        """Load monsters from JSON file."""
        try:
            if DATA_PATH.exists():
                with open(DATA_PATH, 'r', encoding='utf-8') as f:
                    self.monsters = json.load(f)
                # Ensure all monsters have ID
                for monster in self.monsters:
                    if 'id' not in monster:
                        monster['id'] = str(uuid.uuid4())
            else:
                self.monsters = []
                # Create empty file
                DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
                with open(DATA_PATH, 'w', encoding='utf-8') as f:
                    json.dump([], f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[MonsterEditor] Error loading monsters: {e}")
            self.monsters = []
    
    def set_dirty(self, value: bool = True) -> None:
        """Set dirty state and update UI."""
        self.is_dirty = value
        self._update_dirty_state_ui()

    def set_monster_dirty(self, value: bool = True) -> None:
        """Set monster dirty state and update UI."""
        self.is_monster_dirty = value
        self.set_dirty(value)
    
    def _update_dirty_state_ui(self) -> None:
        """Update status label and Save button based on dirty state."""
        if not hasattr(self, 'status_label') or self.status_label is None:
            return
        
        if self.is_dirty:
            # Show unsaved status
            status_text = i18n_t('status_unsaved', ns='monster_editor', default='Unsaved changes')
            self.status_label.config(text=f"● {status_text}", fg=UI.COLOR_WARNING)
            if self.save_button is not None:
                self.save_button.config(state='normal')
        else:
            # Show saved status
            status_text = i18n_t('status_saved', ns='monster_editor', default='All saved')
            self.status_label.config(text=status_text, fg=UI.COLOR_ACCENT)
            if self.save_button is not None:
                self.save_button.config(state='disabled')

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
            messagebox.showerror('Error', f'Failed to save: {e}')
            return False
    
    def _load_monster(self) -> None:
        """Load monster data if editing existing monster."""
        if self.monster_id is None:
            return
        
        # TODO: Load from monster_manager when implemented
        # For now, use default data
        print(f"[QuickEditor] Loading monster: {self.monster_id}")
    
    def _setup_ui(self) -> None:
        """Create UI components with dock layout."""
        # Top: Title + Action Buttons
        self._create_top_panel()
        
        # Create main container for left + right panels
        main_container = tk.Frame(self, bg=UI.BG_DEFAULT)
        main_container.pack(side='top', fill='both', expand=True)
        
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

        # Status label (dirty state)
        self.status_label = tk.Label(
            top_frame,
            text='',
            font=UI.FONT_SMALL,
            fg=UI.COLOR_WARNING,
            bg=UI.BG_PANEL
        )
        self.status_label.pack(side='left', padx=(5, 0), pady=15)
        
        # Action buttons (right side)
        button_frame = tk.Frame(top_frame, bg=UI.BG_PANEL)
        button_frame.pack(side='right', padx=15, pady=15)
        
        # Save button
        save_text = i18n_t('btn_save', ns='monster_editor', default='Save')
        self.save_button = tk.Button(
            button_frame,
            text=save_text,
            font=UI.FONT_BUTTON,
            bg=UI.COLOR_ACCENT,
            fg='#FFFFFF',
            width=10,
            command=self._on_save
        )
        self.save_button.pack(side='left', padx=5)
        
        # Tooltip
        attach_i18n_tooltip(
            self.save_button,
            'tooltip_save',
            ns='monster_editor',
            lang_provider=get_lang
        )
        
        # Cancel button
        cancel_text = i18n_t('btn_cancel', ns='monster_editor', default='Cancel')
        self.cancel_button = tk.Button(
            button_frame,
            text=cancel_text,
            font=UI.FONT_BUTTON,
            bg=UI.BG_PANEL,
            width=10,
            command=self._on_cancel
        )
        self.cancel_button.pack(side='left', padx=5)
        
        # Tooltip
        attach_i18n_tooltip(
            self.cancel_button,
            'tooltip_cancel',
            ns='monster_editor',
            lang_provider=get_lang
        )
    
    def _create_left_panel(self, parent: Any) -> None:
        """Create left panel with monster list and CRUD buttons."""
        left_frame = tk.Frame(parent, bg=UI.BG_PANEL, width=250)
        left_frame.pack(side='left', fill='y', padx=0, pady=0)
        left_frame.pack_propagate(False)
        
        # Title
        title_text = i18n_t('label_monster_list', ns='monster_editor', default='Monster List')
        title_label = tk.Label(
            left_frame,
            text=title_text,
            font=UI.FONT_SECTION,
            fg=UI.COLOR_PRIMARY_TEXT,
            bg=UI.BG_PANEL
        )
        title_label.pack(side='top', padx=10, pady=(10, 5))
        
        # Monster listbox with scrollbar
        listbox_frame = tk.Frame(left_frame, bg=UI.BG_PANEL)
        listbox_frame.pack(side='top', fill='both', expand=True, padx=10, pady=5)
        
        scrollbar = tk.Scrollbar(listbox_frame, orient=tk.VERTICAL)
        scrollbar.pack(side='right', fill='y')
        
        self.monster_listbox = tk.Listbox(
            listbox_frame,
            font=UI.FONT_TEXT,
            yscrollcommand=scrollbar.set,
            selectmode=tk.SINGLE,
            height=15
        )
        self.monster_listbox.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=self.monster_listbox.yview)
        
        # Bind selection event
        self.monster_listbox.bind('<<ListboxSelect>>', self._on_monster_select)
        
        # Button container
        button_frame = tk.Frame(left_frame, bg=UI.BG_PANEL)
        button_frame.pack(side='top', fill='x', padx=10, pady=(5, 10))
        
        # Add Monster button
        add_icon = icon_helper.get_icon('add', fallback='➕', size=16)
        add_text = i18n_t('btn_add_monster', ns='monster_editor', default='Add Monster')
        self.add_monster_button = tk.Button(
            button_frame,
            text=f"{add_icon} {add_text}",
            font=UI.FONT_BUTTON,
            bg=UI.COLOR_ACCENT,
            fg='#FFFFFF',
            command=self._on_add_monster
        )
        self.add_monster_button.pack(side='top', fill='x', pady=2)
        
        # Delete Monster button
        delete_icon = icon_helper.get_icon('delete', fallback='🗑️', size=16)
        delete_text = i18n_t('btn_delete', ns='monster_editor', default='Delete')
        self.delete_monster_button = tk.Button(
            button_frame,
            text=f"{delete_icon} {delete_text}",
            font=UI.FONT_BUTTON,
            bg=UI.COLOR_DANGER,
            fg='#FFFFFF',
            command=self._on_delete_monster
        )
        self.delete_monster_button.pack(side='top', fill='x', pady=2)
        
        # Initial load
        self._refresh_monster_list()
    
    def _create_right_panel(self, parent: Any) -> None:
        """Create right panel with tabbed interface."""
        right_container = tk.Frame(parent, bg=UI.BG_DEFAULT)
        right_container.pack(side='right', fill='both', expand=True, padx=10, pady=10)
        
        # Create notebook (tabs)
        self.notebook = ttk.Notebook(right_container)
        self.notebook.pack(fill='both', expand=True)
        
        # Create tabs
        self._create_info_tab()
        self._create_templates_tab()
    
    def _create_info_tab(self) -> None:
        """Create Monster Info tab."""
        if self.notebook is None:
            return
        
        # Create tab frame
        self.info_tab = tk.Frame(self.notebook, bg=UI.BG_DEFAULT)
        
        # Add to notebook
        tab_text = i18n_t('tab_info', ns='monster_editor', default='Monster Info')
        self.notebook.add(self.info_tab, text=tab_text)
        
        # Create scrollable container
        canvas = tk.Canvas(self.info_tab, bg=UI.BG_DEFAULT, highlightthickness=0)
        scrollbar = tk.Scrollbar(self.info_tab, orient='vertical', command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=UI.BG_DEFAULT)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        scrollbar.pack(side='right', fill='y')
        
        # Form content
        form_frame = tk.Frame(scrollable_frame, bg=UI.BG_DEFAULT)
        form_frame.pack(fill='both', expand=True)
        
        # Monster Name
        name_label_text = i18n_t('monster_name_label', ns='monster_editor', default='Monster name:')
        tk.Label(
            form_frame,
            text=name_label_text,
            font=UI.FONT_LABEL,
            fg=UI.COLOR_TEXT,
            bg=UI.BG_DEFAULT
        ).grid(row=0, column=0, sticky='w', pady=5)
        
        self.name_entry = tk.Entry(
            form_frame,
            font=UI.FONT_TEXT,
            width=30
        )
        self.name_entry.grid(row=0, column=1, sticky='ew', pady=5, padx=(10, 0))
        self.name_entry.bind('<KeyRelease>', self._on_info_change)
        
        # Level
        level_label_text = i18n_t('monster_level_label', ns='monster_editor', default='Level:')
        tk.Label(
            form_frame,
            text=level_label_text,
            font=UI.FONT_LABEL,
            fg=UI.COLOR_TEXT,
            bg=UI.BG_DEFAULT
        ).grid(row=1, column=0, sticky='w', pady=5)
        
        self.level_spinbox = tk.Spinbox(
            form_frame,
            from_=1,
            to=999,
            font=UI.FONT_TEXT,
            width=10
        )
        self.level_spinbox.grid(row=1, column=1, sticky='w', pady=5, padx=(10, 0))
        self.level_spinbox.bind('<KeyRelease>', self._on_info_change)
        self.level_spinbox.bind('<<Increment>>', self._on_info_change)
        self.level_spinbox.bind('<<Decrement>>', self._on_info_change)
        
        # Priority
        priority_label_text = i18n_t('monster_priority_label', ns='monster_editor', default='Priority:')
        tk.Label(
            form_frame,
            text=priority_label_text,
            font=UI.FONT_LABEL,
            fg=UI.COLOR_TEXT,
            bg=UI.BG_DEFAULT
        ).grid(row=2, column=0, sticky='w', pady=5)
        
        self.priority_spinbox = tk.Spinbox(
            form_frame,
            from_=1,
            to=10,
            font=UI.FONT_TEXT,
            width=10
        )
        self.priority_spinbox.grid(row=2, column=1, sticky='w', pady=5, padx=(10, 0))
        self.priority_spinbox.bind('<KeyRelease>', self._on_info_change)
        self.priority_spinbox.bind('<<Increment>>', self._on_info_change)
        self.priority_spinbox.bind('<<Decrement>>', self._on_info_change)
        
        # HP
        hp_label_text = i18n_t('monster_hp_label', ns='monster_editor', default='HP:')
        tk.Label(
            form_frame,
            text=hp_label_text,
            font=UI.FONT_LABEL,
            fg=UI.COLOR_TEXT,
            bg=UI.BG_DEFAULT
        ).grid(row=3, column=0, sticky='w', pady=5)
        
        self.hp_entry = tk.Entry(
            form_frame,
            font=UI.FONT_TEXT,
            width=15
        )
        self.hp_entry.grid(row=3, column=1, sticky='w', pady=5, padx=(10, 0))
        self.hp_entry.bind('<KeyRelease>', self._on_info_change)
        
        # Damage per hit
        damage_label_text = i18n_t('monster_damage_label', ns='monster_editor', default='Damage per hit:')
        tk.Label(
            form_frame,
            text=damage_label_text,
            font=UI.FONT_LABEL,
            fg=UI.COLOR_TEXT,
            bg=UI.BG_DEFAULT
        ).grid(row=4, column=0, sticky='w', pady=5)
        
        self.damage_entry = tk.Entry(
            form_frame,
            font=UI.FONT_TEXT,
            width=15
        )
        self.damage_entry.grid(row=4, column=1, sticky='w', pady=5, padx=(10, 0))
        self.damage_entry.bind('<KeyRelease>', self._on_info_change)
        
        # Description
        desc_label_text = i18n_t('monster_desc_label', ns='monster_editor', default='Description:')
        tk.Label(
            form_frame,
            text=desc_label_text,
            font=UI.FONT_LABEL,
            fg=UI.COLOR_TEXT,
            bg=UI.BG_DEFAULT
        ).grid(row=5, column=0, sticky='nw', pady=5)
        
        desc_frame = tk.Frame(form_frame, bg=UI.BG_DEFAULT)
        desc_frame.grid(row=5, column=1, sticky='ew', pady=5, padx=(10, 0))
        
        self.desc_text = tk.Text(
            desc_frame,
            font=UI.FONT_TEXT,
            width=30,
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
        """Create Templates tab."""
        if self.notebook is None:
            return
        
        # Create tab frame
        self.templates_tab = tk.Frame(self.notebook, bg=UI.BG_DEFAULT)
        
        # Add to notebook
        tab_text = i18n_t('tab_templates', ns='monster_editor', default='Templates')
        self.notebook.add(self.templates_tab, text=tab_text)
        
        # Layout: left (list), right (controls)
        main_frame = tk.Frame(self.templates_tab, bg=UI.BG_DEFAULT)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Template listbox with scrollbar
        list_frame = tk.Frame(main_frame, bg=UI.BG_PANEL)
        list_frame.pack(side='left', fill='y', padx=(0, 10), pady=0, anchor='n')

        list_label = tk.Label(
            list_frame,
            text=i18n_t('template_list_title', ns='monster_editor', default='Template List:'),
            font=UI.FONT_LABEL,
            fg=UI.COLOR_PRIMARY_TEXT,
            bg=UI.BG_PANEL
        )
        list_label.pack(side='top', anchor='w', pady=(0, 5))

        self.template_scrollbar = tk.Scrollbar(list_frame, orient='vertical')
        self.template_listbox = tk.Listbox(
            list_frame,
            font=UI.FONT_TEXT,
            yscrollcommand=self.template_scrollbar.set,
            selectmode=tk.SINGLE,
            height=10,
            width=28
        )
        self.template_listbox.pack(side='left', fill='y', expand=False)
        self.template_scrollbar.config(command=self.template_listbox.yview)
        self.template_scrollbar.pack(side='right', fill='y')

        # Controls frame (right)
        controls_frame = tk.Frame(main_frame, bg=UI.BG_DEFAULT)
        controls_frame.pack(side='left', fill='both', expand=True, padx=0, pady=0)

        # Capture Template button
        self.capture_button = tk.Button(
            controls_frame,
            text=i18n_t('btn_capture', ns='monster_editor', default='Capture Template'),
            font=UI.FONT_BUTTON,
            bg=UI.COLOR_ACCENT,
            fg='#FFFFFF',
            width=18
        )
        self.capture_button.pack(side='top', fill='x', pady=4)

        # Browse File button
        self.browse_button = tk.Button(
            controls_frame,
            text=i18n_t('btn_browse', ns='monster_editor', default='Browse File'),
            font=UI.FONT_BUTTON,
            bg=UI.BG_PANEL,
            width=18
        )
        self.browse_button.pack(side='top', fill='x', pady=4)

        # Delete Template button
        self.delete_template_button = tk.Button(
            controls_frame,
            text=i18n_t('btn_delete_template', ns='monster_editor', default='Delete Template'),
            font=UI.FONT_BUTTON,
            bg=UI.COLOR_DANGER,
            fg='#FFFFFF',
            width=18
        )
        self.delete_template_button.pack(side='top', fill='x', pady=4)

        # Test Recognition button
        self.test_template_button = tk.Button(
            controls_frame,
            text=i18n_t('btn_test', ns='monster_editor', default='Test Recognition'),
            font=UI.FONT_BUTTON,
            bg=UI.COLOR_PRIMARY,
            fg='#FFFFFF',
            width=18
        )
        self.test_template_button.pack(side='top', fill='x', pady=4)

        # Threshold slider
        threshold_label_text = i18n_t('monster_threshold_label', ns='monster_editor', default='Recognition Threshold:')
        self.threshold_label = tk.Label(
            controls_frame,
            text=threshold_label_text,
            font=UI.FONT_LABEL,
            fg=UI.COLOR_TEXT,
            bg=UI.BG_DEFAULT
        )
        self.threshold_label.pack(side='top', anchor='w', pady=(12, 2))

        self.threshold_scale = tk.Scale(
            controls_frame,
            from_=0.0,
            to=1.0,
            resolution=0.01,
            orient='horizontal',
            length=180,
            showvalue=True
        )
        self.threshold_scale.set(0.7)
        self.threshold_scale.pack(side='top', fill='x', pady=(0, 8))
    
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
        self.capture_button = tk.Button(
            button_container,
            text=capture_text,
            font=UI.FONT_BUTTON,
            bg=UI.COLOR_PRIMARY,
            fg='#FFFFFF',
            width=15,
            command=self._on_capture
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
        self.test_button = tk.Button(
            button_container,
            text=test_text,
            font=UI.FONT_BUTTON,
            bg=UI.COLOR_PRIMARY,
            fg='#FFFFFF',
            width=15,
            command=self._on_test
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
        
        # Focus name entry
        self.name_entry.focus_set() if self.name_entry else None
    
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
            messagebox.showerror('Error', error_msg.format(error))
            return
        
        if result_type == 'capture':
            # Handle capture result
            success_msg = i18n_t('msg_template_added', ns='monster_editor', default='Template added successfully')
            messagebox.showinfo('Success', success_msg)
            
        elif result_type == 'test':
            # Handle test result
            matches = data.get('matches', 0)
            confidence = data.get('confidence', 0.0)
            
            if matches > 0:
                success_msg = i18n_t('msg_test_success', ns='monster_editor', default='Found {} matches (confidence: {:.1%})')
                messagebox.showinfo('Test Result', success_msg.format(matches, confidence))
            else:
                fail_msg = i18n_t('msg_test_failed', ns='monster_editor', default='No matches found')
                messagebox.showinfo('Test Result', fail_msg)
    
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
            
            # Disable buttons
            if self.capture_button is not None:
                self.capture_button.config(state='disabled')
            if self.test_button is not None:
                self.test_button.config(state='disabled')
            if self.save_button is not None:
                self.save_button.config(state='disabled')
        else:
            # Hide progress
            if self.progress_label is not None:
                self.progress_label.config(text='')
            
            # Enable buttons
            if self.capture_button is not None:
                self.capture_button.config(state='normal')
            if self.test_button is not None:
                self.test_button.config(state='normal')
            if self.save_button is not None:
                self.save_button.config(state='normal')
    
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
            messagebox.showwarning('Warning', error_msg)
            return
        
        # Validate all monsters before saving
        for idx, monster in enumerate(self.monsters):
            # Rule 2: Check monster is dict
            if not isinstance(monster, dict):
                messagebox.showerror('Error', f'Invalid monster data at index {idx}')
                return
            
            # Rule 1: Validate required fields
            name = monster.get('name', '').strip()
            if not name:
                messagebox.showerror('Error', f'Monster at index {idx} has no name')
                return
        
        # Rule 5: Call save once, cache result
        success = self._save_monsters()
        
        if success:
            # Show success message
            success_msg = i18n_t('msg_save_success', ns='monster_editor', default='Monsters saved successfully')
            messagebox.showinfo('Success', success_msg)
        else:
            # Error already shown by _save_monsters()
            pass
    
    def _on_cancel(self) -> None:
        """Handle cancel button click."""
        self.destroy()
    
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
            messagebox.showerror('Error', f'Capture failed: {e}')
    
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
            messagebox.showerror('Error', f'Test failed: {e}')
    
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
                messagebox.showerror('Validation Error', error_msg)
                return False
        
        # Check level is positive integer
        if self.level_spinbox is not None:
            try:
                level = int(self.level_spinbox.get())
                if level < 1:
                    raise ValueError()
            except ValueError:
                error_msg = i18n_t('error_level_invalid', ns='monster_editor', default='Level must be a positive integer')
                messagebox.showerror('Validation Error', error_msg)
                return False
        
        return True
    
    def _refresh_monster_list(self) -> None:
        """Refresh the monster listbox with current monsters."""
        if self.monster_listbox is None:
            return
        
        # Clear listbox
        self.monster_listbox.delete(0, tk.END)
        
        # Load monsters if not already loaded
        if not self.monsters:
            self._load_monsters()
        
        # Populate listbox
        for monster in self.monsters:
            name = monster.get('name', 'Unnamed')
            level = monster.get('level', 1)
            display_text = f"{name} (Lv.{level})"
            self.monster_listbox.insert(tk.END, display_text)
        
        # Select current monster if editing
        if self.current_monster_id:
            for i, monster in enumerate(self.monsters):
                if monster.get('id') == self.current_monster_id:
                    self.monster_listbox.selection_set(i)
                    self.monster_listbox.see(i)
                    break
    
    def _on_monster_select(self, event: Any) -> None:
        """Handle monster selection from listbox."""
        if self.monster_listbox is None:
            return
        
        selection = self.monster_listbox.curselection()
        if not selection:
            return
        
        index = selection[0]
        if 0 <= index < len(self.monsters):
            selected_monster = self.monsters[index]
            self.current_monster_id = selected_monster.get('id')
            
            # Populate form with monster data
            self._populate_info_form(selected_monster)
            
            print(f"[MonsterEditor] Selected monster: {selected_monster.get('name')}")
    
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
        
        # Select new monster
        if self.monster_listbox:
            self.monster_listbox.selection_clear(0, tk.END)
            self.monster_listbox.selection_set(len(self.monsters) - 1)
            self.monster_listbox.see(len(self.monsters) - 1)
        
        # Set as current
        self.current_monster_id = new_monster['id']
        
        # Populate form with new monster data
        self._populate_info_form(new_monster)
        
        print(f"[MonsterEditor] Added new monster: {new_monster['id']}")
    
    def _on_delete_monster(self) -> None:
        """Handle delete monster button click."""
        if self.monster_listbox is None:
            return
        
        selection = self.monster_listbox.curselection()
        if not selection:
            messagebox.showwarning(
                'No Selection',
                i18n_t('warning_no_monster_selected', ns='monster_editor', default='Please select a monster to delete.')
            )
            return
        
        index = selection[0]
        if 0 <= index < len(self.monsters):
            monster = self.monsters[index]
            
            # Confirm deletion
            confirm = messagebox.askyesno(
                'Confirm Deletion',
                i18n_t(
                    'confirm_delete_monster',
                    ns='monster_editor',
                    default=f"Are you sure you want to delete '{monster.get('name', 'Unnamed')}'?"
                )
            )
            
            if confirm:
                # Delete monster
                self.monsters.pop(index)
                self.is_dirty = True
                
                # Clear current selection if deleted
                if self.current_monster_id == monster.get('id'):
                    self.current_monster_id = None
                
                # Refresh listbox
                self._refresh_monster_list()
                
                print(f"[MonsterEditor] Deleted monster: {monster.get('name')}")
    
    def _populate_info_form(self, monster: Dict[str, Any]) -> None:
        """Populate Info tab form with monster data."""
        if not all([self.name_entry, self.level_spinbox, self.priority_spinbox, 
                    self.hp_entry, self.damage_entry, self.desc_text]):
            return
        
        # Clear form first
        self._clear_info_form()
        
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
    
    def _clear_info_form(self) -> None:
        """Clear all fields in Info tab form."""
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
                    
                    # Refresh list to show updated name
                    self._refresh_monster_list()
                    break


# Singleton instance
_quick_editor_instance: Optional[QuickMonsterEditor] = None


def show_quick_monster_editor(
    parent: tk.Widget,
    monster_id: Optional[str] = None,
    on_save: Optional[Callable] = None
) -> QuickMonsterEditor:
    """
    Show quick monster editor (singleton).
    
    Args:
        parent: Parent widget
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
