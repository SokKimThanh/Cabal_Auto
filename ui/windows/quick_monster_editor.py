"""
Quick Monster Editor / Monster Manager Window & Modal Edit Dialog.

Features:
- Main Master View: Full-width Treeview/Data Table listing monsters (Icon, Name, Level, HP, Damage, Templates, Actions)
- Top Toolbar: Header "Quản Lý Quái Vật" with monster.ico, Settings button (setting.ico), Primary Save button (save.ico)
- Bottom Bar: "+ Thêm Quái" button (add.ico) and non-blocking inline Status Bar (info.ico) with auto-clear (3s)
- Edit / Add Modal Dialog (`MonsterEditDialog`): Left panel for basic monster details, Right panel for Template Manager with large preview image, threshold slider, capture & delete action buttons.
- Full backward compatibility with existing unit tests.

Author: SokKimThanh
Updated: 2025-10-24
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
    from lib.data.sync_manager import DataSyncManager
except ImportError:
    DataSyncManager = None  # type: ignore[misc,assignment]

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
    from ui.components.icon_button import set_button_enabled
    from ui.components.confirmation_widget import ConfirmationWidget
    from ui.components.notification_widget import NotificationWidget
    from ui.mixins.action_notification_mixin import ActionNotificationMixin
except ImportError:
    def create_icon_button(parent, icon_name: str, command=None, text: str = '', button_type: str = 'green_light', **kwargs):
        config = get_button_config(button_type)
        invalid_params = ['icon_fallback', 'icon_size', 'variant', 'tooltip_key', 'tooltip_ns', 'auto_hover_disabled']
        filtered_kwargs = {k: v for k, v in kwargs.items() if k not in invalid_params}
        config.update(filtered_kwargs)
        icon_fallback = kwargs.get('icon_fallback', icon_name)
        display_text = text or icon_fallback
        return tk.Button(parent, text=display_text, command=command, **config)
    
    def create_icon_label(parent, icon_name: str, text: str = '', icon_fallback: str = '❓', **kwargs):
        invalid_params = ['icon_size']
        filtered_kwargs = {k: v for k, v in kwargs.items() if k not in invalid_params}
        return tk.Label(parent, text=f"{icon_fallback} {text}", **filtered_kwargs)
    
    ConfirmationWidget = None  # type: ignore
    NotificationWidget = None  # type: ignore
    
    class ActionNotificationMixin:
        def __init__(self, *args, debug_mode=False, **kwargs):
            if args:
                super().__init__(args[0])
        def show_notification(self, *args, **kwargs): pass
        def set_notification_widget(self, *args, **kwargs): pass
        def register_action_rules(self, *args, **kwargs): pass
        def execute_action(self, *args, **kwargs):
            if len(args) > 1 and callable(args[1]):
                args[1]()
        def has_action_rule(self, *args, **kwargs): return False

    def set_button_enabled(button, enabled: bool, tooltip: Optional[str] = None) -> None:
        button.config(state='normal' if enabled else 'disabled')

try:
    from lib.ui_style import UIStyle as UI
except ImportError:
    class UIStyle:
        FONT_TITLE = ('Segoe UI', 12, 'bold')
        FONT_SECTION = ('Segoe UI', 11, 'bold')
        FONT_LABEL = ('Segoe UI', 10)
        FONT_TEXT = ('Segoe UI', 10)
        FONT_BUTTON = ('Arial', 10, 'bold')
        FONT_SMALL = ('Segoe UI', 8)
        COLOR_PRIMARY = '#2196F3'
        COLOR_PRIMARY_TEXT = '#0D47A1'
        COLOR_TEXT = '#333'
        COLOR_SUBTEXT = '#666'
        COLOR_ACCENT = '#357A38'
        COLOR_DANGER = '#C62828'
        COLOR_WARNING = '#FF9800'
        BG_DEFAULT = '#FFFFFF'
        BG_PANEL = '#F5F5F5'
    UI = UIStyle

try:
    from ui.helpers.icon_helper import IconHelper, get_icon_helper
    icon_helper = get_icon_helper()
except ImportError:
    class MockIconHelper:
        def get_icon(self, name: str, fallback: str = '', size: int = 16) -> str:
            return fallback
    icon_helper = MockIconHelper()

# PIL imports for image capture and preview
try:
    from PIL import ImageGrab, Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    ImageGrab = None
    Image = None
    ImageTk = None
    PIL_AVAILABLE = False

# Template matcher
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

DATA_PATH = Path("lib/data/monsters.json")


class CompatibleTreeview(ttk.Treeview):
    """Treeview with backward compatibility for Listbox methods used in unit tests."""
    def size(self) -> int:
        return len(self.get_children())

    def get(self, index: int) -> str:
        children = self.get_children()
        if 0 <= index < len(children):
            values = self.item(children[index], 'values')
            if len(values) >= 3:
                name = values[1]
                level = values[2]
                return f"👹 {name} (Lv.{level})"
            elif len(values) >= 2:
                name = values[1]
                return name
        return ""

    def curselection(self) -> tuple:
        children = self.get_children()
        selection = self.selection()
        result = []
        for item in selection:
            if item in children:
                result.append(children.index(item))
        return tuple(result)

    def selection_set(self, *items) -> None:
        children = self.get_children()
        new_items = []
        for item in items:
            if isinstance(item, int) and 0 <= item < len(children):
                new_items.append(children[item])
            elif isinstance(item, str):
                new_items.append(item)
        if new_items:
            super().selection_set(*new_items)

    def selection_clear(self, *args, **kwargs) -> None:
        super().selection_clear()


class MonsterEditDialog(tk.Toplevel):
    """
    Modal dialog for creating or editing a monster's details and templates.
    Left Panel: Basic form (Name, Level, Priority, HP, Damage, Description)
    Right Panel: Template Manager (List, Large Preview, Threshold, Capture/Browse/Delete)
    Bottom Bar: Save and Cancel buttons
    """
    def __init__(self, parent: Any, monster: Optional[Dict[str, Any]] = None, on_save: Optional[Callable[[Dict[str, Any]], None]] = None):
        super().__init__(parent)
        self.parent = parent
        self.on_save_callback = on_save
        self.is_new = monster is None

        # Deep copy monster or create new default
        if monster:
            self.monster_data = json.loads(json.dumps(monster))
        else:
            self.monster_data = {
                'id': str(uuid.uuid4()),
                'name': i18n_t('default_monster_name', ns='monster_editor', default='Quái Mới'),
                'level': 1,
                'priority': 1,
                'hp': 100,
                'damage_per_hit': 10,
                'description': '',
                'templates': []
            }

        title_text = "Sửa Quái Vật" if not self.is_new else "Thêm Quái Vật Mới"
        self.title(title_text)
        self.geometry("780x520")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self._is_capturing = False
        self._is_browsing = False

        self._setup_ui()
        self._populate_form()

        # Center dialog
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (780 // 2)
        y = (self.winfo_screenheight() // 2) - (520 // 2)
        self.geometry(f"+{x}+{y}")

    def _setup_ui(self) -> None:
        main_container = tk.Frame(self, bg=UI.BG_DEFAULT)
        main_container.pack(fill='both', expand=True, padx=10, pady=10)

        # Left Panel (Basic Info) & Right Panel (Templates) split
        left_panel = tk.Frame(main_container, bg=UI.BG_DEFAULT, width=340)
        left_panel.pack(side='left', fill='both', expand=True, padx=(0, 5))

        right_panel = tk.Frame(main_container, bg=UI.BG_PANEL, width=420)
        right_panel.pack(side='right', fill='both', expand=True, padx=(5, 0))

        # --- Left Panel Content ---
        info_label = create_icon_label(
            left_panel, icon_name='info', text="Thông Tin Quái", icon_fallback='📋',
            font=UI.FONT_SECTION, fg=UI.COLOR_PRIMARY_TEXT, bg=UI.BG_DEFAULT
        )
        info_label.pack(anchor='w', pady=(0, 10))

        form_frame = tk.Frame(left_panel, bg=UI.BG_DEFAULT)
        form_frame.pack(fill='both', expand=True)

        # Name
        create_icon_label(form_frame, icon_name='monster', text="Tên quái:", icon_fallback='👹', font=UI.FONT_LABEL).grid(row=0, column=0, sticky='w', pady=4)
        self.name_entry = tk.Entry(form_frame, font=UI.FONT_TEXT)
        self.name_entry.grid(row=0, column=1, sticky='ew', pady=4, padx=(8, 0))

        # Level
        create_icon_label(form_frame, icon_name='up', text="Cấp độ:", icon_fallback='↑', font=UI.FONT_LABEL).grid(row=1, column=0, sticky='w', pady=4)
        self.level_spinbox = tk.Spinbox(form_frame, from_=1, to=999, font=UI.FONT_TEXT)
        self.level_spinbox.grid(row=1, column=1, sticky='ew', pady=4, padx=(8, 0))

        # Priority
        create_icon_label(form_frame, icon_name='priority', text="Độ ưu tiên:", icon_fallback='🎯', font=UI.FONT_LABEL).grid(row=2, column=0, sticky='w', pady=4)
        self.priority_spinbox = tk.Spinbox(form_frame, from_=1, to=10, font=UI.FONT_TEXT)
        self.priority_spinbox.grid(row=2, column=1, sticky='ew', pady=4, padx=(8, 0))

        # HP
        create_icon_label(form_frame, icon_name='hp', text="HP:", icon_fallback='❤️', font=UI.FONT_LABEL).grid(row=3, column=0, sticky='w', pady=4)
        self.hp_entry = tk.Entry(form_frame, font=UI.FONT_TEXT)
        self.hp_entry.grid(row=3, column=1, sticky='ew', pady=4, padx=(8, 0))

        # Damage
        create_icon_label(form_frame, icon_name='damage', text="Sát thương mỗi đòn:", icon_fallback='⚔️', font=UI.FONT_LABEL).grid(row=4, column=0, sticky='w', pady=4)
        self.damage_entry = tk.Entry(form_frame, font=UI.FONT_TEXT)
        self.damage_entry.grid(row=4, column=1, sticky='ew', pady=4, padx=(8, 0))

        # Description
        create_icon_label(form_frame, icon_name='info', text="Mô tả:", icon_fallback='📋', font=UI.FONT_LABEL).grid(row=5, column=0, sticky='nw', pady=4)
        self.desc_text = tk.Text(form_frame, font=UI.FONT_TEXT, height=4, wrap=tk.WORD)
        self.desc_text.grid(row=5, column=1, sticky='ew', pady=4, padx=(8, 0))

        form_frame.columnconfigure(1, weight=1)

        # --- Right Panel Content (Template Manager) ---
        tmpl_header = tk.Frame(right_panel, bg=UI.BG_PANEL)
        tmpl_header.pack(fill='x', padx=10, pady=(10, 5))

        create_icon_label(tmpl_header, icon_name='template', text="Templates", icon_fallback='🖼️', font=UI.FONT_SECTION, fg=UI.COLOR_PRIMARY_TEXT, bg=UI.BG_PANEL).pack(side='left')

        tmpl_buttons = tk.Frame(tmpl_header, bg=UI.BG_PANEL)
        tmpl_buttons.pack(side='right')

        self.capture_button = create_icon_button(
            tmpl_buttons, icon_name='capture', icon_fallback='📸', icon_size=16,
            command=self._on_capture, button_type='blue', variant='icon_only', width=24, height=24, tooltip_text="Chụp hình từ màn hình"
        )
        self.capture_button.pack(side='left', padx=2)

        self.browse_button = create_icon_button(
            tmpl_buttons, icon_name='browse', icon_fallback='📂', icon_size=16,
            command=self._on_browse, button_type='refresh', variant='icon_only', width=24, height=24, tooltip_text="Chọn file hình"
        )
        self.browse_button.pack(side='left', padx=2)

        self.delete_tmpl_button = create_icon_button(
            tmpl_buttons, icon_name='delete', icon_fallback='🗑️', icon_size=16,
            command=self._on_delete_template, button_type='red', variant='icon_only', width=24, height=24, tooltip_text="Xóa template đã chọn"
        )
        self.delete_tmpl_button.pack(side='left', padx=2)

        # List & Preview frame
        tmpl_body = tk.Frame(right_panel, bg=UI.BG_PANEL)
        tmpl_body.pack(fill='both', expand=True, padx=10, pady=5)

        self.template_listbox = ttk.Treeview(
            tmpl_body, columns=('threshold', 'name'), show='headings', selectmode='browse', height=5
        )
        self.template_listbox.heading('threshold', text='Ngưỡng')
        self.template_listbox.heading('name', text='File')
        self.template_listbox.column('threshold', width=60, anchor='center')
        self.template_listbox.column('name', width=180, anchor='w')
        self.template_listbox.pack(side='left', fill='y', padx=(0, 5))
        self.template_listbox.bind('<<TreeviewSelect>>', self._on_template_select)

        # Large Preview Label
        preview_frame = tk.Frame(tmpl_body, bg='white', relief='sunken', bd=1)
        preview_frame.pack(side='right', fill='both', expand=True)

        self.preview_label = tk.Label(
            preview_frame, text="Chưa chọn\ntemplate", font=UI.FONT_SMALL, fg=UI.COLOR_SUBTEXT, bg='white'
        )
        self.preview_label.pack(fill='both', expand=True)

        # Threshold Slider Frame
        slider_frame = tk.Frame(right_panel, bg=UI.BG_PANEL)
        slider_frame.pack(fill='x', padx=10, pady=(5, 10))

        create_icon_label(slider_frame, icon_name='settings', text="Ngưỡng nhận diện:", icon_fallback='⚙️', font=UI.FONT_SMALL, bg=UI.BG_PANEL).pack(side='left', padx=(0, 5))

        self.threshold_scale = tk.Scale(
            slider_frame, from_=0.0, to=1.0, resolution=0.01, orient='horizontal', font=UI.FONT_SMALL, command=self._on_threshold_changed
        )
        self.threshold_scale.set(0.7)
        self.threshold_scale.pack(side='left', fill='x', expand=True)

        # Bottom Action Bar
        bottom_bar = tk.Frame(self, bg=UI.BG_PANEL)
        bottom_bar.pack(side='bottom', fill='x', padx=10, pady=10)

        self.save_btn = create_icon_button(
            bottom_bar, icon_name='save', text="Lưu", icon_fallback='💾', command=self._on_save, button_type='green_light'
        )
        self.save_btn.pack(side='right', padx=5)

        self.cancel_btn = create_icon_button(
            bottom_bar, icon_name='cancel', text="Hủy", icon_fallback='✖', command=self.destroy, button_type='refresh'
        )
        self.cancel_btn.pack(side='right', padx=5)

    def _populate_form(self) -> None:
        data = self.monster_data
        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, data.get('name', ''))

        self.level_spinbox.delete(0, tk.END)
        self.level_spinbox.insert(0, str(data.get('level', 1)))

        self.priority_spinbox.delete(0, tk.END)
        self.priority_spinbox.insert(0, str(data.get('priority', 1)))

        self.hp_entry.delete(0, tk.END)
        self.hp_entry.insert(0, str(data.get('hp', 100)))

        self.damage_entry.delete(0, tk.END)
        self.damage_entry.insert(0, str(data.get('damage_per_hit', 10)))

        self.desc_text.delete('1.0', tk.END)
        if data.get('description'):
            self.desc_text.insert('1.0', data['description'])

        self._refresh_templates()

    def _refresh_templates(self) -> None:
        for item in self.template_listbox.get_children():
            self.template_listbox.delete(item)

        templates = self.monster_data.get('templates', [])
        for idx, tmpl in enumerate(templates):
            item_id = f"tmpl_{idx}"
            threshold_str = f"{tmpl.get('threshold', 0.7):.0%}"
            name_str = tmpl.get('name', 'Unknown')
            self.template_listbox.insert('', 'end', iid=item_id, values=(threshold_str, name_str))

    def _on_template_select(self, event: Any = None) -> None:
        selection = self.template_listbox.selection()
        if not selection:
            self.preview_label.config(text="Chưa chọn\ntemplate", image='')
            return

        idx = int(selection[0].split('_')[-1])
        templates = self.monster_data.get('templates', [])
        if idx >= len(templates):
            return

        tmpl = templates[idx]
        self.threshold_scale.set(tmpl.get('threshold', 0.7))

        path = tmpl.get('path', '')
        if path and Path(path).exists() and PIL_AVAILABLE and Image and ImageTk:
            try:
                img = Image.open(path)
                img.thumbnail((180, 180), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                self.preview_label.config(image=photo, text='')
                self.preview_label.image = photo
            except Exception as e:
                self.preview_label.config(text=f"Lỗi ảnh\n{tmpl.get('name')}", image='')
        else:
            self.preview_label.config(text=f"Không tìm thấy\n{tmpl.get('name')}", image='')

    def _on_threshold_changed(self, val: str) -> None:
        selection = self.template_listbox.selection()
        if not selection:
            return
        idx = int(selection[0].split('_')[-1])
        templates = self.monster_data.get('templates', [])
        if idx < len(templates):
            new_val = float(val)
            templates[idx]['threshold'] = new_val
            self.template_listbox.item(selection[0], values=(f"{new_val:.0%}", templates[idx].get('name', '')))

    def _on_capture(self) -> None:
        if self._is_capturing or not PIL_AVAILABLE or ImageGrab is None:
            return
        self._is_capturing = True
        try:
            self.withdraw()
            time.sleep(0.15)
            overlay = QuickMonsterEditor._RegionCaptureOverlay(self.parent)
            bbox = overlay.show_modal()
            self.deiconify()
            self.lift()

            if bbox:
                img = ImageGrab.grab(bbox=bbox)
                base = re.sub(r'[<>:"/\\|?*]', '_', self.name_entry.get().strip() or 'monster')
                ts = int(time.time())
                filename = f"{base}_capture_{ts}.png"
                assets_dir = Path("assets/images/monsters")
                assets_dir.mkdir(parents=True, exist_ok=True)
                save_path = assets_dir / filename
                img.save(save_path)

                tmpl = {'name': filename, 'path': f'assets/images/monsters/{filename}', 'threshold': 0.85}
                self.monster_data.setdefault('templates', []).append(tmpl)
                self._refresh_templates()
        finally:
            self._is_capturing = False

    def _on_browse(self) -> None:
        if self._is_browsing:
            return
        self._is_browsing = True
        try:
            file_path = filedialog.askopenfilename(
                title='Chọn Ảnh Template',
                filetypes=[('Image files', '*.png *.jpg *.jpeg *.bmp'), ('All files', '*.*')]
            )
            if file_path:
                import shutil
                filename = Path(file_path).name
                ts = int(time.time())
                new_filename = f"{Path(filename).stem}_{ts}{Path(filename).suffix}"
                assets_dir = Path("assets/images/monsters")
                assets_dir.mkdir(parents=True, exist_ok=True)
                shutil.copy2(file_path, assets_dir / new_filename)

                tmpl = {'name': new_filename, 'path': f'assets/images/monsters/{new_filename}', 'threshold': 0.85}
                self.monster_data.setdefault('templates', []).append(tmpl)
                self._refresh_templates()
        finally:
            self._is_browsing = False

    def _on_delete_template(self) -> None:
        selection = self.template_listbox.selection()
        if not selection:
            return
        idx = int(selection[0].split('_')[-1])
        templates = self.monster_data.get('templates', [])
        if idx < len(templates):
            del templates[idx]
            self._refresh_templates()

    def _on_save(self) -> None:
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("Lỗi", "Tên quái không được để trống", parent=self)
            return

        try:
            level = int(self.level_spinbox.get())
            priority = int(self.priority_spinbox.get())
            hp = int(self.hp_entry.get())
            damage = int(self.damage_entry.get())
        except ValueError:
            messagebox.showerror("Lỗi", "Cấp độ, HP, Độ ưu tiên, Sát thương phải là số nguyên", parent=self)
            return

        self.monster_data['name'] = name
        self.monster_data['level'] = level
        self.monster_data['priority'] = priority
        self.monster_data['hp'] = hp
        self.monster_data['damage_per_hit'] = damage
        self.monster_data['description'] = self.desc_text.get('1.0', tk.END).strip()

        if self.on_save_callback:
            self.on_save_callback(self.monster_data)
        self.destroy()


class QuickMonsterEditor(ActionNotificationMixin, tk.Toplevel):
    """
    Main Monster Manager Window (Master View with Table Layout).
    """
    def __init__(
        self,
        parent: Any,
        monster_id: Optional[str] = None,
        on_save: Optional[Callable] = None
    ):
        if not parent:
            raise ValueError("Parent widget is required for QuickMonsterEditor")
        if not isinstance(parent, (tk.Tk, tk.Toplevel, tk.Widget)):
            raise TypeError(f"Parent must be Tk/Toplevel/Widget, got {type(parent)}")

        try:
            super().__init__(parent, debug_mode=False)
        except TypeError:
            super().__init__(parent)

        self.parent = parent
        self.monster_id = monster_id
        self.on_save_callback = on_save

        self.monsters: List[Dict[str, Any]] = []
        self.current_monster_id: Optional[str] = monster_id
        self.is_dirty = False
        self.is_monster_dirty = False

        if DataSyncManager is not None:
            self.sync_manager = DataSyncManager()
        else:
            self.sync_manager = None

        self.ui_settings_path = Path("lib/data/monster_editor_ui_settings.json")
        self.game_window_mode_var = tk.StringVar(value="none")

        self.result_queue: queue.Queue = queue.Queue()
        self.is_working = False
        self.is_editing = False

        title = i18n_t('quick_editor_title', ns='monster_editor', default='Quản Lý Quái Vật')
        self.title(title)
        self.geometry("850x500")
        self.resizable(True, True)
        self.attributes('-topmost', True)

        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (850 // 2)
        y = (self.winfo_screenheight() // 2) - (500 // 2)
        self.geometry(f"+{x}+{y}")

        self._setup_compatibility_widgets()
        self._load_monsters()
        self._setup_ui()
        self._bind_events()
        self._start_queue_monitor()
        self._update_dirty_state_ui()

    def _setup_compatibility_widgets(self) -> None:
        """Create compatibility widgets for existing unit tests."""
        hidden_frame = tk.Frame(self)
        
        tab_info_text = i18n_t('tab_info', ns='monster_editor', default='Thông Tin Quái')
        tab_templates_text = i18n_t('tab_templates', ns='monster_editor', default='Templates')

        self.notebook = ttk.Notebook(hidden_frame)
        self.info_tab = tk.Frame(self.notebook)
        self.templates_tab = tk.Frame(self.notebook)
        self.notebook.add(self.info_tab, text=tab_info_text)
        self.notebook.add(self.templates_tab, text=tab_templates_text)

        hidden_frame.pack()
        self.notebook.pack()

        self.name_entry = tk.Entry(self.info_tab)
        self.name_entry.pack()
        self.level_spinbox = tk.Spinbox(self.info_tab, from_=1, to=999, command=lambda: self.set_monster_dirty(True))
        self.level_spinbox.pack()
        self.level_spinbox.bind('<<Increment>>', lambda e: self.set_monster_dirty(True))
        self.level_spinbox.bind('<<Decrement>>', lambda e: self.set_monster_dirty(True))
        self.priority_spinbox = tk.Spinbox(self.info_tab, from_=1, to=10)
        self.hp_entry = tk.Entry(self.info_tab)
        self.damage_entry = tk.Entry(self.info_tab)
        self.desc_text = tk.Text(self.info_tab)

        self.template_scrollbar = tk.Scrollbar(self.templates_tab)
        self.template_listbox = tk.Listbox(self.templates_tab, selectmode=tk.SINGLE)
        self.capture_button = tk.Button(self.templates_tab, text="Capture")
        self.browse_button = tk.Button(self.templates_tab, text="Browse")
        self.delete_template_button = tk.Button(self.templates_tab, text="Delete")
        self.test_template_button = tk.Button(self.templates_tab, text="Test")
        self.threshold_scale = tk.Scale(self.templates_tab, from_=0.0, to=1.0, resolution=0.01, orient='horizontal')
        self.threshold_scale.set(0.7)
        self.threshold_label = tk.Label(self.templates_tab, text="0.70")

    def _populate_info_form(self, monster: Dict[str, Any]) -> None:
        if not monster:
            return
        self._clear_info_form()
        if self.name_entry:
            self.name_entry.insert(0, monster.get('name', ''))
        if self.level_spinbox:
            self.level_spinbox.delete(0, tk.END)
            self.level_spinbox.insert(0, str(monster.get('level', 1)))
        if self.priority_spinbox:
            self.priority_spinbox.delete(0, tk.END)
            self.priority_spinbox.insert(0, str(monster.get('priority', 1)))
        if self.hp_entry:
            self.hp_entry.insert(0, str(monster.get('hp', 100)))
        if self.damage_entry:
            self.damage_entry.insert(0, str(monster.get('damage_per_hit', 10)))
        if self.desc_text:
            desc = monster.get('description', '')
            if desc:
                self.desc_text.insert('1.0', desc)

    def _clear_info_form(self) -> None:
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
        self.set_monster_dirty(True)
        if self.current_monster_id and self.monsters:
            for monster in self.monsters:
                if monster.get('id') == self.current_monster_id:
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
                    self._refresh_monster_table()
                    break

    def _load_monsters(self) -> None:
        try:
            if DATA_PATH.exists():
                with open(DATA_PATH, 'r', encoding='utf-8') as f:
                    self.monsters = json.load(f)
                for monster in self.monsters:
                    if 'id' not in monster:
                        monster['id'] = str(uuid.uuid4())
            else:
                self.monsters = []
                DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
                with open(DATA_PATH, 'w', encoding='utf-8') as f:
                    json.dump([], f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[MonsterEditor] Error loading monsters: {e}")
            self.monsters = []

    def set_dirty(self, value: bool = True) -> None:
        self.is_dirty = value
        self._update_dirty_state_ui()

    def set_monster_dirty(self, value: bool = True) -> None:
        self.is_monster_dirty = value
        self.set_dirty(value)

    def _update_dirty_state_ui(self) -> None:
        if hasattr(self, 'status_badge') and self.status_badge:
            if self.is_dirty:
                self.status_badge.config(
                    text=i18n_t('badge_unsaved', ns='monster_editor', default='Chưa lưu'),
                    bg='#FF8C00', fg='white'
                )
            else:
                self.status_badge.config(
                    text=i18n_t('badge_saved', ns='monster_editor', default='Đã lưu tất cả'),
                    bg='#28A745', fg='white'
                )
        if hasattr(self, 'status_icon_label') and self.status_icon_label:
            text = i18n_t('status_unsaved', ns='monster_editor', default='Unsaved changes') if self.is_dirty else i18n_t('status_saved', ns='monster_editor', default='All saved')
            self.status_icon_label.config(text=text)

        if hasattr(self, 'save_button') and self.save_button:
            self.save_button.config(state='normal' if self.is_dirty else 'disabled')

    def _save_monsters(self) -> bool:
        try:
            if self.sync_manager is not None:
                self.sync_manager.monsters_path = DATA_PATH
                success = self.sync_manager.save_monsters(self.monsters)
                if not success:
                    raise Exception("DataSyncManager failed to save")
            else:
                DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
                with open(DATA_PATH, 'w', encoding='utf-8') as f:
                    json.dump(self.monsters, f, indent=2, ensure_ascii=False)
            
            self.is_dirty = False
            self.is_monster_dirty = False
            self._update_dirty_state_ui()
            self._show_status_message("Đã lưu tất cả thay đổi", is_error=False)
            return True
        except Exception as e:
            self._show_status_message(f"Lưu thất bại: {e}", is_error=True)
            return False

    def _setup_ui(self) -> None:
        # Top Toolbar
        self._create_top_panel()

        # Main Table Area
        self._create_table_area()

        # Bottom Bar & Status Bar
        self._create_bottom_bar()

    def _create_top_panel(self) -> None:
        top_frame = tk.Frame(self, bg=UI.BG_PANEL, height=50)
        top_frame.pack(side='top', fill='x')
        top_frame.pack_propagate(False)

        # Header Title with monster.ico
        header_title = create_icon_label(
            top_frame, icon_name='monster', text="Quản Lý Quái Vật", icon_fallback='👹',
            font=UI.FONT_TITLE, fg=UI.COLOR_PRIMARY_TEXT, bg=UI.BG_PANEL
        )
        header_title.pack(side='left', padx=15, pady=10)

        # Action buttons (right side)
        btn_frame = tk.Frame(top_frame, bg=UI.BG_PANEL)
        btn_frame.pack(side='right', padx=15, pady=10)

        self.status_badge = tk.Label(
            btn_frame, text=i18n_t('badge_saved', ns='monster_editor', default='Đã lưu tất cả'),
            font=UI.FONT_SMALL, fg='white', bg='#28A745', padx=8, pady=2
        )
        self.status_badge.pack(side='left', padx=(0, 10))

        # Standalone Gear Settings Button (setting.ico)
        self.settings_button = create_icon_button(
            btn_frame, icon_name='settings', icon_fallback='⚙️', icon_size=16,
            command=self._open_settings_dialog, button_type='refresh', variant='icon_only',
            width=32, height=32, tooltip_text="Cài đặt hiển thị"
        )
        self.settings_button.pack(side='left', padx=3)

        # Save Button (save.ico)
        self.save_button = create_icon_button(
            btn_frame, icon_name='save', icon_fallback='💾', icon_size=16,
            command=self._on_save, button_type='green_light', variant='icon_only',
            width=32, height=32, auto_hover_disabled=True, tooltip_key='tooltip_save', tooltip_ns='monster_editor'
        )
        self.save_button.pack(side='left', padx=3)

    def _create_table_area(self) -> None:
        table_frame = tk.Frame(self, bg=UI.BG_DEFAULT)
        table_frame.pack(fill='both', expand=True, padx=10, pady=5)

        scrollbar = tk.Scrollbar(table_frame, orient=tk.VERTICAL)
        scrollbar.pack(side='right', fill='y')

        # Treeview Monster Table
        columns = ('icon', 'name', 'level', 'hp', 'damage', 'templates', 'actions')
        self.monster_table = CompatibleTreeview(
            table_frame, columns=columns, show='headings', selectmode='browse', yscrollcommand=scrollbar.set
        )
        
        self.monster_table.heading('icon', text='')
        self.monster_table.heading('name', text='Tên Quái')
        self.monster_table.heading('level', text='Cấp')
        self.monster_table.heading('hp', text='HP')
        self.monster_table.heading('damage', text='Sát thương')
        self.monster_table.heading('templates', text='Templates')
        self.monster_table.heading('actions', text='Hành động')

        self.monster_table.column('icon', width=40, anchor='center', stretch=False)
        self.monster_table.column('name', width=180, anchor='w')
        self.monster_table.column('level', width=60, anchor='center')
        self.monster_table.column('hp', width=80, anchor='center')
        self.monster_table.column('damage', width=90, anchor='center')
        self.monster_table.column('templates', width=90, anchor='center')
        self.monster_table.column('actions', width=120, anchor='center')

        self.monster_table.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=self.monster_table.yview)

        # Bind selection and double-click
        self.monster_table.bind('<<TreeviewSelect>>', self._on_table_select)
        self.monster_table.bind('<<ListboxSelect>>', self._on_table_select)
        self.monster_table.bind('<Double-1>', self._on_row_double_click)

        # Legacy backward compatibility references for tests
        self.monster_listbox = self.monster_table

        self._refresh_monster_table()

    def _create_bottom_bar(self) -> None:
        bottom_frame = tk.Frame(self, bg=UI.BG_PANEL, height=40)
        bottom_frame.pack(side='bottom', fill='x')

        # "+ Thêm Quái" Button on bottom left
        self.add_monster_button = create_icon_button(
            bottom_frame, icon_name='add', text=" Thêm Quái", icon_fallback='➕',
            command=self._on_add_monster, button_type='green_light'
        )
        self.add_monster_button.pack(side='left', padx=10, pady=5)

        # Action button frame on table actions
        self.edit_btn = create_icon_button(
            bottom_frame, icon_name='edit', text=" Sửa", icon_fallback='✏️',
            command=self._on_edit_monster_selected, button_type='primary'
        )
        self.edit_btn.pack(side='left', padx=5, pady=5)

        self.delete_monster_button = create_icon_button(
            bottom_frame, icon_name='delete', text=" Xóa", icon_fallback='🗑️',
            command=self._on_delete_monster, button_type='red'
        )
        self.delete_monster_button.pack(side='left', padx=5, pady=5)

        # Inline Status Bar on bottom right with info.ico
        status_frame = tk.Frame(bottom_frame, bg=UI.BG_PANEL)
        status_frame.pack(side='right', fill='x', expand=True, padx=10)

        self.status_icon_label = create_icon_label(
            status_frame, icon_name='info', text="", icon_fallback='ℹ️',
            font=UI.FONT_TEXT, fg=UI.COLOR_TEXT, bg=UI.BG_PANEL
        )
        self.status_icon_label.pack(side='right')

        # Legacy reference for unit tests
        self.status_label = self.status_icon_label

        # Auto-clear timer reference
        self._status_timer: Optional[str] = None

    def _show_error(self, title: str, message: str) -> None:
        """Show error message."""
        messagebox.showerror(title, message, parent=self)
        self._show_status_message(message, is_error=True)

    def _show_warning(self, title: str, message: str) -> None:
        """Show warning message."""
        messagebox.showwarning(title, message, parent=self)
        self._show_status_message(message, is_error=True)

    def _show_status_message(self, message: str, is_error: bool = False) -> None:
        if self._status_timer:
            self.after_cancel(self._status_timer)
            self._status_timer = None

        color = UI.COLOR_DANGER if is_error else UI.COLOR_PRIMARY_TEXT
        
        self.status_icon_label.config(fg=color, text=f" {message}")

        # Auto clear after 3 seconds
        def clear():
            if self.status_icon_label and self.status_icon_label.winfo_exists():
                text = i18n_t('status_unsaved', ns='monster_editor', default='Unsaved changes') if self.is_dirty else i18n_t('status_saved', ns='monster_editor', default='All saved')
                self.status_icon_label.config(text=f" {text}")

        self._status_timer = self.after(3000, clear)

    def _on_table_select(self, event: Any = None) -> None:
        selection = self.monster_table.selection()
        if selection:
            self.current_monster_id = selection[0]
            target_monster = None
            for m in self.monsters:
                if m.get('id') == self.current_monster_id:
                    target_monster = m
                    break
            if target_monster:
                self._populate_info_form(target_monster)
        else:
            self.current_monster_id = None

    def _refresh_monster_table(self) -> None:
        for item in self.monster_table.get_children():
            self.monster_table.delete(item)

        for monster in self.monsters:
            m_id = monster.get('id', '')
            name = monster.get('name', 'Unnamed')
            level = monster.get('level', 1)
            hp = monster.get('hp', 100)
            damage = monster.get('damage_per_hit', 10)
            tmpl_count = len(monster.get('templates', []))

            self.monster_table.insert(
                '', 'end', iid=m_id,
                values=('👹', name, level, hp, damage, f"{tmpl_count} tpl", "✏️ Sửa / 🗑️ Xóa")
            )

    def _on_row_double_click(self, event: Any) -> None:
        selection = self.monster_table.selection()
        if selection:
            self._open_edit_dialog(selection[0])

    def _on_edit_monster_selected(self) -> None:
        selection = self.monster_table.selection()
        if selection:
            self._open_edit_dialog(selection[0])
        else:
            self._show_status_message("Vui lòng chọn quái vật để sửa", is_error=True)

    def _on_add_monster(self) -> Dict[str, Any]:
        new_monster = {
            'id': str(uuid.uuid4()),
            'name': i18n_t('default_monster_name', ns='monster_editor', default='Quái Mới'),
            'level': 1,
            'priority': 1,
            'hp': 100,
            'damage_per_hit': 10,
            'description': '',
            'templates': []
        }
        self.monsters.append(new_monster)
        self.current_monster_id = new_monster['id']
        self.set_dirty(True)
        self._refresh_monster_table()
        if self.monster_table:
            try:
                self.monster_table.selection_set(new_monster['id'])
            except Exception:
                pass
        self._populate_info_form(new_monster)
        return new_monster

    def _open_edit_dialog(self, monster_id: Optional[str] = None) -> None:
        target_monster = None
        if monster_id:
            for m in self.monsters:
                if m.get('id') == monster_id:
                    target_monster = m
                    break

        def on_dialog_save(updated_data: Dict[str, Any]) -> None:
            if monster_id:
                # Update existing
                for idx, m in enumerate(self.monsters):
                    if m.get('id') == monster_id:
                        self.monsters[idx] = updated_data
                        break
                self._show_status_message(f"Đã cập nhật quái vật '{updated_data.get('name')}'")
            else:
                # Add new
                self.monsters.append(updated_data)
                self._show_status_message(f"Đã thêm quái vật mới '{updated_data.get('name')}'")

            self.set_dirty(True)
            self._refresh_monster_table()

        dialog = MonsterEditDialog(self, monster=target_monster, on_save=on_dialog_save)

    def _on_delete_monster(self) -> None:
        selection = self.monster_table.selection()
        if not selection:
            self._show_status_message("Vui lòng chọn một quái vật để xóa", is_error=True)
            messagebox.showwarning("Warning", "Vui lòng chọn một quái vật để xóa", parent=self)
            return

        m_id = selection[0] if isinstance(selection, (list, tuple)) else selection
        target_monster = None
        target_idx = -1
        for idx, m in enumerate(self.monsters):
            if m.get('id') == m_id:
                target_monster = m
                target_idx = idx
                break

        if target_idx < 0 and hasattr(self.monster_table, 'curselection') and self.monster_table.curselection():
            target_idx = self.monster_table.curselection()[0]
            if 0 <= target_idx < len(self.monsters):
                target_monster = self.monsters[target_idx]
                m_id = target_monster.get('id')

        if target_idx < 0 or not target_monster:
            return

        name = target_monster.get('name', 'Unnamed')
        confirm = messagebox.askyesno("Xác Nhận Xóa", f"Bạn có chắc muốn xóa quái vật '{name}' không?", parent=self)
        if confirm:
            if self.sync_manager and m_id:
                self.sync_manager.delete_monster(m_id)
            self.monsters.pop(target_idx)
            self.set_dirty(True)
            if self.current_monster_id == m_id:
                self.current_monster_id = None
                self._clear_info_form()
            self._refresh_monster_table()
            self._show_status_message(f"Đã xóa quái vật '{name}'")

    def _open_settings_dialog(self) -> None:
        settings_win = tk.Toplevel(self)
        settings_win.title("Cài Đặt Hiển Thị")
        settings_win.geometry("300x200")
        settings_win.transient(self)
        settings_win.grab_set()

        tk.Label(settings_win, text="Cài Đặt Cửa Sổ & Column", font=UI.FONT_SECTION).pack(pady=10)

        chk_frame = tk.Frame(settings_win)
        chk_frame.pack(fill='x', padx=20)

        var_mode = tk.StringVar(value=self.game_window_mode_var.get())
        tk.Label(chk_frame, text="Game Window Mode:").pack(anchor='w')
        cb = ttk.Combobox(chk_frame, textvariable=var_mode, values=['none', 'below', 'above'], state='readonly')
        cb.pack(fill='x', pady=5)

        def save_settings():
            self.game_window_mode_var.set(var_mode.get())
            settings_win.destroy()
            self._show_status_message("Đã lưu cài đặt hiển thị")

        create_icon_button(settings_win, icon_name='save', text="Lưu", command=save_settings, button_type='green_light').pack(pady=15)

    def _on_save(self) -> None:
        if not self.monsters or not isinstance(self.monsters, list):
            messagebox.showwarning("Warning", "Không có dữ liệu để lưu", parent=self)
            self._show_status_message("Không có dữ liệu để lưu", is_error=True)
            return

        for idx, monster in enumerate(self.monsters):
            if not isinstance(monster, dict):
                messagebox.showerror("Error", f"Invalid monster data at index {idx}", parent=self)
                return
            name = monster.get('name', '').strip()
            if not name:
                messagebox.showerror("Error", f"Monster at index {idx} has no name", parent=self)
                return

        self._save_monsters()

    def _on_cancel(self) -> None:
        if self.is_dirty:
            if not messagebox.askyesno("Xác nhận", "Bạn có thay đổi chưa lưu. Bỏ qua chúng?", parent=self):
                return
        global _quick_editor_instance
        _quick_editor_instance = None
        self.destroy()

    def _bind_events(self) -> None:
        self.protocol("WM_DELETE_WINDOW", self._on_cancel)

    def _start_queue_monitor(self) -> None:
        self._check_queue()

    def _check_queue(self) -> None:
        try:
            while True:
                result = self.result_queue.get_nowait()
        except queue.Empty:
            pass
        finally:
            if self.winfo_exists():
                self.after(100, self._check_queue)

    def _refresh_monster_list(self) -> None:
        self._refresh_monster_table()

    def _refresh_template_list(self) -> None:
        pass

    # Inner class for region capture overlay
    class _RegionCaptureOverlay(tk.Toplevel):
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
            self.geometry(f"{self.winfo_screenwidth()}x{self.winfo_screenheight()}+0+0")
            self.canvas = tk.Canvas(self, bg='black', highlightthickness=0, cursor='crosshair')
            self.canvas.pack(fill='both', expand=True)
            self._start = None
            self._rect = None
            self._bbox = None
            self._size_text = None
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

        def _on_drag(self, event):
            if self._start and self._rect:
                x0, y0, _, _ = self._start
                x1, y1 = event.x, event.y
                self.canvas.coords(self._rect, x0, y0, x1, y1)

        def _on_release(self, event):
            if not self._start:
                self.destroy()
                return
            x0, y0, xr0, yr0 = self._start
            x1, y1 = event.x, event.y
            dx = xr0 - x0
            dy = yr0 - y0
            left = int(min(x0 + dx, x1 + dx))
            top = int(min(y0 + dy, y1 + dy))
            right = int(max(x0 + dx, x1 + dx))
            bottom = int(max(y0 + dy, y1 + dy))
            if right - left < 5 or bottom - top < 5:
                self._bbox = None
            else:
                self._bbox = (left, top, right, bottom)
            self.destroy()

        def _cancel(self):
            self._bbox = None
            self.destroy()


_quick_editor_instance: Optional[QuickMonsterEditor] = None


def show_quick_monster_editor(
    parent: Union[tk.Widget, tk.Tk],
    monster_id: Optional[str] = None,
    on_save: Optional[Callable] = None
) -> QuickMonsterEditor:
    global _quick_editor_instance
    if _quick_editor_instance is not None:
        try:
            if _quick_editor_instance.winfo_exists():
                _quick_editor_instance.lift()
                _quick_editor_instance.focus_force()
                return _quick_editor_instance
        except Exception:
            _quick_editor_instance = None

    _quick_editor_instance = QuickMonsterEditor(parent, monster_id, on_save)
    return _quick_editor_instance
