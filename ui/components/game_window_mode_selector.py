"""
Game Window Mode Selector Component

Reusable component for controlling game window display position relative to app.

Features:
- 3 modes: none (no window), below (under app), above (topmost)
- Auto-save to hunt_config.json
- Icon-based visual feedback
- Tooltip support
- Callback on mode change
- Fully encapsulated and reusable

Usage:
    from ui.components.game_window_mode_selector import create_game_window_mode_selector
    
    # Simple usage
    selector = create_game_window_mode_selector(
        parent=frame,
        config_path="lib/data/hunt_config.json"
    )
    
    # Advanced usage with callback
    def on_mode_changed(mode: str):
        print(f"Game window mode changed to: {mode}")
        if mode == "above":
            launch_game_topmost()
        elif mode == "below":
            launch_game_below()
    
    selector = create_game_window_mode_selector(
        parent=frame,
        config_path="lib/data/hunt_config.json",
        on_mode_change=on_mode_changed,
        initial_mode="none",
        icon_size=16
    )

Author: SokKimThanh
Created: 2025-10-24
"""
import json
import tkinter as tk
from tkinter import ttk
from pathlib import Path
from typing import Optional, Callable, Any


class GameWindowModeSelector:
    """
    Game window mode selector with icon feedback and auto-save.
    
    Manages three display modes for game window:
    - none: No game window
    - below: Game window below app
    - above: Game window topmost (above app)
    """
    
    def __init__(
        self,
        parent: Any,
        config_path: str = "lib/data/hunt_config.json",
        on_mode_change: Optional[Callable[[str], None]] = None,
        initial_mode: str = "none",
        icon_size: int = 16,
        show_label: bool = True,
        label_text: str = "Game:",
        tooltip_text: str = "Chọn cách hiển thị cửa sổ game so với app"
    ):
        """
        Initialize game window mode selector.
        
        Args:
            parent: Parent widget to attach to
            config_path: Path to hunt_config.json
            on_mode_change: Callback function(mode: str) when mode changes
            initial_mode: Initial mode ('none', 'below', 'above')
            icon_size: Size of mode icons
            show_label: Whether to show "Game:" label
            label_text: Text for label
            tooltip_text: Tooltip text
        """
        self.parent = parent
        self.config_path = Path(config_path)
        self.on_mode_change_callback = on_mode_change
        self.icon_size = icon_size
        
        # Mode state
        self.current_mode = tk.StringVar(value=initial_mode)
        
        # Load initial mode from config
        self._load_mode_from_config()
        
        # Create UI
        self.container = tk.Frame(parent, bg=self._get_bg_color())
        
        # Label (optional)
        if show_label:
            self.label = tk.Label(
                self.container,
                text=label_text,
                font=('Segoe UI', 9),
                bg=self._get_bg_color()
            )
            self.label.pack(side='left', padx=(0, 5))
        
        # Mode selector combobox
        self.mode_combo = ttk.Combobox(
            self.container,
            textvariable=self.current_mode,
            values=['none', 'below', 'above'],
            state='readonly',
            width=10,
            font=('Segoe UI', 9)
        )
        self.mode_combo.pack(side='left')
        self.mode_combo.bind('<<ComboboxSelected>>', self._on_mode_selected)
        
        # Icon indicator (shows current mode visually)
        self.icon_label = tk.Label(
            self.container,
            text=self._get_mode_icon(self.current_mode.get()),
            font=('Segoe UI', icon_size),
            bg=self._get_bg_color()
        )
        self.icon_label.pack(side='left', padx=(5, 0))
        
        # Tooltip
        self._attach_tooltip(self.mode_combo, tooltip_text)
        self._attach_tooltip(self.icon_label, tooltip_text)
    
    def _get_bg_color(self) -> str:
        """Get background color from parent or default."""
        try:
            return self.parent.cget('bg')
        except:
            return '#F5F5F5'
    
    def _get_mode_icon(self, mode: str) -> str:
        """
        Get icon emoji for current mode.
        
        Args:
            mode: Current mode string
            
        Returns:
            Icon emoji string
        """
        icons = {
            'none': '🚫',      # Screen off
            'below': '⬇️',     # Below app
            'above': '⬆️'      # Above/topmost
        }
        return icons.get(mode, '❓')
    
    def _load_mode_from_config(self) -> None:
        """Load game_window_mode from hunt_config.json."""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                mode = config.get('game_window_mode', 'none')
                self.current_mode.set(mode)
                print(f"[GameWindowMode] Loaded mode: {mode}")
            else:
                print(f"[GameWindowMode] Config not found, using default 'none'")
        except Exception as e:
            print(f"[GameWindowMode] Error loading config: {e}")
    
    def _save_mode_to_config(self, mode: str) -> None:
        """
        Save game_window_mode to hunt_config.json.
        
        Args:
            mode: Mode to save
        """
        try:
            # Load existing config
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            else:
                config = {}
            
            # Update mode
            config['game_window_mode'] = mode
            
            # Save back
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            print(f"[GameWindowMode] Saved mode '{mode}' to config")
        except Exception as e:
            print(f"[GameWindowMode] Error saving config: {e}")
    
    def _on_mode_selected(self, event: Any = None) -> None:
        """
        Handle mode selection from combobox.
        
        Args:
            event: Combobox event (unused)
        """
        new_mode = self.current_mode.get()
        print(f"[GameWindowMode] Mode changed to: {new_mode}")
        
        # Update icon
        self.icon_label.config(text=self._get_mode_icon(new_mode))
        
        # Save to config
        self._save_mode_to_config(new_mode)
        
        # Call user callback
        if self.on_mode_change_callback:
            try:
                self.on_mode_change_callback(new_mode)
            except Exception as e:
                print(f"[GameWindowMode] Error in callback: {e}")
    
    def _attach_tooltip(self, widget: Any, text: str) -> None:
        """
        Attach simple tooltip to widget.
        
        Args:
            widget: Widget to attach tooltip to
            text: Tooltip text
        """
        def on_enter(event):
            # Create tooltip window
            tooltip = tk.Toplevel(widget)
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            
            label = tk.Label(
                tooltip,
                text=text,
                font=('Segoe UI', 8),
                bg='#FFFFE0',
                fg='#000000',
                relief='solid',
                borderwidth=1,
                padx=5,
                pady=2
            )
            label.pack()
            
            # Store reference
            widget._tooltip = tooltip
        
        def on_leave(event):
            # Destroy tooltip
            if hasattr(widget, '_tooltip'):
                try:
                    widget._tooltip.destroy()
                except:
                    pass
                delattr(widget, '_tooltip')
        
        widget.bind('<Enter>', on_enter)
        widget.bind('<Leave>', on_leave)
    
    def get_mode(self) -> str:
        """
        Get current mode.
        
        Returns:
            Current mode string
        """
        return self.current_mode.get()
    
    def set_mode(self, mode: str) -> None:
        """
        Set mode programmatically.
        
        Args:
            mode: Mode to set ('none', 'below', 'above')
        """
        if mode in ['none', 'below', 'above']:
            self.current_mode.set(mode)
            self.icon_label.config(text=self._get_mode_icon(mode))
            self._save_mode_to_config(mode)
        else:
            print(f"[GameWindowMode] Invalid mode: {mode}")
    
    def pack(self, **kwargs) -> None:
        """Pack the container frame."""
        self.container.pack(**kwargs)
    
    def grid(self, **kwargs) -> None:
        """Grid the container frame."""
        self.container.grid(**kwargs)
    
    def place(self, **kwargs) -> None:
        """Place the container frame."""
        self.container.place(**kwargs)


def create_game_window_mode_selector(
    parent: Any,
    config_path: str = "lib/data/hunt_config.json",
    on_mode_change: Optional[Callable[[str], None]] = None,
    initial_mode: str = "none",
    icon_size: int = 16,
    show_label: bool = True,
    label_text: str = "Game:",
    tooltip_text: str = "Chọn cách hiển thị cửa sổ game so với app"
) -> GameWindowModeSelector:
    """
    Factory function to create game window mode selector.
    
    Args:
        parent: Parent widget
        config_path: Path to hunt_config.json
        on_mode_change: Callback when mode changes
        initial_mode: Initial mode
        icon_size: Icon size
        show_label: Show "Game:" label
        label_text: Label text
        tooltip_text: Tooltip text
    
    Returns:
        GameWindowModeSelector instance
    
    Example:
        selector = create_game_window_mode_selector(
            parent=frame,
            on_mode_change=lambda mode: print(f"Mode: {mode}")
        )
        selector.pack(side='left', padx=10)
    """
    return GameWindowModeSelector(
        parent=parent,
        config_path=config_path,
        on_mode_change=on_mode_change,
        initial_mode=initial_mode,
        icon_size=icon_size,
        show_label=show_label,
        label_text=label_text,
        tooltip_text=tooltip_text
    )
