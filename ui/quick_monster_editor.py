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
        parent: tk.Widget,
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
        self.name_entry: Optional[tk.Entry] = None
        self.level_spinbox: Optional[tk.Spinbox] = None
        self.threshold_scale: Optional[tk.Scale] = None
        self.threshold_label: Optional[tk.Label] = None
        self.progress_label: Optional[tk.Label] = None
        self.save_button: Optional[tk.Button] = None
        self.cancel_button: Optional[tk.Button] = None
        self.capture_button: Optional[tk.Button] = None
        self.test_button: Optional[tk.Button] = None
        
        # Window configuration
        title = i18n_t('quick_editor_title', ns='monster_editor', default='Quick Monster Editor')
        self.title(title)
        self.geometry("500x400")
        self.resizable(False, False)
        self.attributes('-topmost', True)
        
        # Center window on screen
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.winfo_screenheight() // 2) - (400 // 2)
        self.geometry(f"+{x}+{y}")
        
        # Setup
        self._load_monster()
        self._setup_ui()
        self._bind_events()
        self._start_queue_monitor()
    
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
        
        # Center: Form Fields
        self._create_center_panel()
        
        # Bottom: Capture/Test + Progress
        self._create_bottom_panel()
    
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
    
    def _create_center_panel(self) -> None:
        """Create center panel with form fields."""
        center_frame = tk.Frame(self, bg=UI.BG_DEFAULT)
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
    
    def _create_bottom_panel(self) -> None:
        """Create bottom panel with capture/test buttons and progress."""
        bottom_frame = tk.Frame(self, bg=UI.BG_PANEL, height=80)
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
        """Handle save button click."""
        try:
            # Validate input
            if not self._validate():
                return
            
            # Collect data
            if self.name_entry is not None:
                self.monster_data['name'] = self.name_entry.get().strip()
            
            if self.level_spinbox is not None:
                try:
                    self.monster_data['level'] = int(self.level_spinbox.get())
                except ValueError:
                    self.monster_data['level'] = 1
            
            if self.threshold_scale is not None:
                self.monster_data['threshold'] = self.threshold_scale.get()
            
            # TODO: Save to monster_manager when implemented
            print(f"[QuickEditor] Saving monster: {self.monster_data}")
            
            # Show success message
            success_msg = i18n_t('msg_monster_created', ns='monster_editor', default='Monster created successfully')
            messagebox.showinfo('Success', success_msg)
            
            # Call callback
            if self.on_save_callback is not None:
                self.on_save_callback(self.monster_id or 'new', self.monster_data)
            
            # Close window
            self.destroy()
            
        except Exception as e:
            print(f"[QuickEditor] Error saving: {e}")
            messagebox.showerror('Error', f'Failed to save: {e}')
    
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
