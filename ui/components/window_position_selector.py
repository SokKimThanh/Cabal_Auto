"""
Window Position Selector Component

Generic component for controlling window position and behavior.
Can be used for app window, game window, or any window positioning needs.

Features:
- Multiple position modes (topmost, normal, minimized, below, above, custom)
- Auto-save to config file
- Icon-based visual feedback
- Tooltip support
- Callback on mode change
- Support for different config keys
- Fully reusable

Usage:
    from ui.components.window_position_selector import create_window_position_selector
    
    # For app window
    app_selector = create_window_position_selector(
        parent=frame,
        config_path="lib/data/app_config.json",
        config_key="app_window_mode",
        window_type="app",
        label_text="App:",
        modes=['normal', 'topmost', 'minimized']
    )
    
    # For game window
    game_selector = create_window_position_selector(
        parent=frame,
        config_path="lib/data/hunt_config.json",
        config_key="game_window_mode",
        window_type="game",
        label_text="Game:",
        modes=['none', 'below', 'above']
    )

Author: SokKimThanh
Created: 2025-10-24
"""
import json
import tkinter as tk
from tkinter import ttk
from pathlib import Path
from typing import Optional, Callable, Any, List, Dict


class WindowPositionSelector:
    """
    Generic window position selector with icon feedback and auto-save.
    
    Supports various window positioning modes with flexible configuration.
    """
    
    # Default mode configurations
    MODE_CONFIGS = {
        'none': {'icon': '🚫', 'label': 'None'},
        'normal': {'icon': '🪟', 'label': 'Normal'},
        'topmost': {'icon': '📌', 'label': 'Topmost'},
        'minimized': {'icon': '➖', 'label': 'Minimized'},
        'maximized': {'icon': '⬜', 'label': 'Maximized'},
        'below': {'icon': '⬇️', 'label': 'Below'},
        'above': {'icon': '⬆️', 'label': 'Above'},
        'left': {'icon': '⬅️', 'label': 'Left'},
        'right': {'icon': '➡️', 'label': 'Right'},
        'center': {'icon': '🎯', 'label': 'Center'},
        'fullscreen': {'icon': '🖥️', 'label': 'Fullscreen'},
        'hidden': {'icon': '👁️‍🗨️', 'label': 'Hidden'},
    }
    
    def __init__(
        self,
        parent: Any,
        config_path: str = "lib/data/hunt_config.json",
        config_key: str = "window_mode",
        modes: Optional[List[str]] = None,
        on_mode_change: Optional[Callable[[str], None]] = None,
        initial_mode: str = "normal",
        icon_size: int = 16,
        show_label: bool = True,
        label_text: str = "Window:",
        tooltip_text: Optional[str] = None,
        window_type: str = "window"
    ):
        """
        Initialize window position selector.
        
        Args:
            parent: Parent widget
            config_path: Path to config JSON file
            config_key: Key name in config file (e.g., 'app_window_mode', 'game_window_mode')
            modes: List of available modes (default: ['normal', 'topmost', 'minimized'])
            on_mode_change: Callback function(mode: str) when mode changes
            initial_mode: Initial mode (default: 'normal')
            icon_size: Size of mode icons
            show_label: Whether to show label
            label_text: Text for label
            tooltip_text: Tooltip text (auto-generated if None)
            window_type: Type of window for tooltip generation ('app', 'game', 'window')
        """
        self.parent = parent
        self.config_path = Path(config_path)
        self.config_key = config_key
        self.modes = modes or ['normal', 'topmost', 'minimized']
        self.on_mode_change_callback = on_mode_change
        self.icon_size = icon_size
        self.window_type = window_type
        
        # Validate modes
        for mode in self.modes:
            if mode not in self.MODE_CONFIGS:
                print(f"[WindowPositionSelector] Warning: Unknown mode '{mode}'")
        
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
            values=self.modes,
            state='readonly',
            width=max(len(m) for m in self.modes) + 2,
            font=('Segoe UI', 9)
        )
        self.mode_combo.pack(side='left')
        self.mode_combo.bind('<<ComboboxSelected>>', self._on_mode_selected)
        
        # Icon indicator
        self.icon_label = tk.Label(
            self.container,
            text=self._get_mode_icon(self.current_mode.get()),
            font=('Segoe UI', icon_size),
            bg=self._get_bg_color()
        )
        self.icon_label.pack(side='left', padx=(5, 0))
        
        # Tooltip
        tooltip = tooltip_text or self._generate_tooltip()
        self._attach_tooltip(self.mode_combo, tooltip)
        self._attach_tooltip(self.icon_label, tooltip)
    
    def _get_bg_color(self) -> str:
        """Get background color from parent or default."""
        try:
            return self.parent.cget('bg')
        except:
            return '#F5F5F5'
    
    def _generate_tooltip(self) -> str:
        """Generate default tooltip based on window type."""
        tooltips = {
            'app': 'Điều khiển vị trí cửa sổ ứng dụng\n• Normal: Bình thường\n• Topmost: Luôn ở trên\n• Minimized: Thu nhỏ\n• Maximized: Phóng to',
            'game': 'Điều khiển vị trí cửa sổ game\n• None: Không làm gì\n• Below: Đặt dưới app\n• Above: Đặt trên tất cả',
            'window': 'Chọn chế độ hiển thị cửa sổ'
        }
        return tooltips.get(self.window_type, tooltips['window'])
    
    def _get_mode_icon(self, mode: str) -> str:
        """Get icon for mode."""
        return self.MODE_CONFIGS.get(mode, {}).get('icon', '❓')
    
    def _load_mode_from_config(self) -> None:
        """Load mode from config file."""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                mode = config.get(self.config_key, self.modes[0])
                # Validate mode is in available modes
                if mode in self.modes:
                    self.current_mode.set(mode)
                else:
                    print(f"[WindowPositionSelector] Invalid mode '{mode}' in config, using '{self.modes[0]}'")
                    self.current_mode.set(self.modes[0])
                print(f"[WindowPositionSelector] Loaded {self.config_key}: {mode}")
            else:
                print(f"[WindowPositionSelector] Config not found, using default '{self.modes[0]}'")
                self.current_mode.set(self.modes[0])
        except Exception as e:
            print(f"[WindowPositionSelector] Error loading config: {e}")
    
    def _save_mode_to_config(self, mode: str) -> None:
        """Save mode to config file."""
        try:
            # Load existing config
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            else:
                config = {}
            
            # Update mode
            config[self.config_key] = mode
            
            # Save back
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            print(f"[WindowPositionSelector] Saved {self.config_key}='{mode}' to config")
        except Exception as e:
            print(f"[WindowPositionSelector] Error saving config: {e}")
    
    def _on_mode_selected(self, event: Any = None) -> None:
        """Handle mode selection."""
        new_mode = self.current_mode.get()
        print(f"[WindowPositionSelector] {self.config_key} changed to: {new_mode}")
        
        # Update icon
        self.icon_label.config(text=self._get_mode_icon(new_mode))
        
        # Save to config
        self._save_mode_to_config(new_mode)
        
        # Call user callback
        if self.on_mode_change_callback:
            try:
                self.on_mode_change_callback(new_mode)
            except Exception as e:
                print(f"[WindowPositionSelector] Error in callback: {e}")
    
    def _attach_tooltip(self, widget: Any, text: str) -> None:
        """Attach tooltip to widget."""
        def on_enter(event):
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
            widget._tooltip = tooltip
        
        def on_leave(event):
            if hasattr(widget, '_tooltip'):
                try:
                    widget._tooltip.destroy()
                except:
                    pass
                delattr(widget, '_tooltip')
        
        widget.bind('<Enter>', on_enter)
        widget.bind('<Leave>', on_leave)
    
    def get_mode(self) -> str:
        """Get current mode."""
        return self.current_mode.get()
    
    def set_mode(self, mode: str) -> None:
        """Set mode programmatically."""
        if mode in self.modes:
            self.current_mode.set(mode)
            self.icon_label.config(text=self._get_mode_icon(mode))
            self._save_mode_to_config(mode)
        else:
            print(f"[WindowPositionSelector] Invalid mode: {mode}")
    
    def pack(self, **kwargs) -> None:
        """Pack the container."""
        self.container.pack(**kwargs)
    
    def grid(self, **kwargs) -> None:
        """Grid the container."""
        self.container.grid(**kwargs)
    
    def place(self, **kwargs) -> None:
        """Place the container."""
        self.container.place(**kwargs)


def create_window_position_selector(
    parent: Any,
    config_path: str = "lib/data/hunt_config.json",
    config_key: str = "window_mode",
    modes: Optional[List[str]] = None,
    on_mode_change: Optional[Callable[[str], None]] = None,
    initial_mode: str = "normal",
    icon_size: int = 16,
    show_label: bool = True,
    label_text: str = "Window:",
    tooltip_text: Optional[str] = None,
    window_type: str = "window"
) -> WindowPositionSelector:
    """
    Factory function to create window position selector.
    
    Args:
        parent: Parent widget
        config_path: Path to config JSON
        config_key: Key in config file
        modes: Available modes list
        on_mode_change: Callback when mode changes
        initial_mode: Initial mode
        icon_size: Icon size
        show_label: Show label
        label_text: Label text
        tooltip_text: Tooltip text
        window_type: Window type for tooltip
    
    Returns:
        WindowPositionSelector instance
    
    Examples:
        # App window selector
        app_sel = create_window_position_selector(
            parent=frame,
            config_key="app_window_mode",
            modes=['normal', 'topmost', 'minimized'],
            label_text="App:",
            window_type="app"
        )
        
        # Game window selector
        game_sel = create_window_position_selector(
            parent=frame,
            config_key="game_window_mode",
            modes=['none', 'below', 'above'],
            label_text="Game:",
            window_type="game"
        )
    """
    return WindowPositionSelector(
        parent=parent,
        config_path=config_path,
        config_key=config_key,
        modes=modes,
        on_mode_change=on_mode_change,
        initial_mode=initial_mode,
        icon_size=icon_size,
        show_label=show_label,
        label_text=label_text,
        tooltip_text=tooltip_text,
        window_type=window_type
    )


# Convenience functions for common use cases
def create_app_window_selector(
    parent: Any,
    config_path: str = "lib/data/app_config.json",
    on_mode_change: Optional[Callable[[str], None]] = None,
    **kwargs
) -> WindowPositionSelector:
    """Create selector for app window positioning."""
    return create_window_position_selector(
        parent=parent,
        config_path=config_path,
        config_key="app_window_mode",
        modes=['normal', 'topmost', 'minimized', 'maximized'],
        show_label=False,  # No label
        window_type="app",
        on_mode_change=on_mode_change,
        **kwargs
    )


def create_game_window_selector(
    parent: Any,
    config_path: str = "lib/data/hunt_config.json",
    on_mode_change: Optional[Callable[[str], None]] = None,
    **kwargs
) -> WindowPositionSelector:
    """Create selector for game window positioning."""
    return create_window_position_selector(
        parent=parent,
        config_path=config_path,
        config_key="game_window_mode",
        modes=['none', 'below', 'above'],
        show_label=False,  # No label
        window_type="game",
        on_mode_change=on_mode_change,
        **kwargs
    )
