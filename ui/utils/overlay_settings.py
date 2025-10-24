"""
Overlay Settings Dialog - Configuration UI for overlay system
Sprint 23 Phase 5 Enhancements

Features:
- Alpha/transparency slider
- RGB color pickers for each state
- FPS limit slider
- Trail effect toggle and length
- Stats HUD toggle
- Live preview

Usage:
    from ui.utils.overlay_settings import OverlaySettingsDialog
    
    dialog = OverlaySettingsDialog(
        parent=main_app,
        current_config=overlay_config,
        lang='vi',
        on_apply=lambda new_config: apply_settings(new_config)
    )
    dialog.show()
"""

import tkinter as tk
from tkinter import ttk, colorchooser
from typing import Dict, Any, Optional, Callable
import json

# Global translations and tooltip support
from lib.i18n import t as i18n_t
from ui.helpers.tooltip import attach_i18n_tooltip
from lib.ui_style import UIStyle as UI


class OverlaySettingsDialog:
    """
    Settings dialog for overlay configuration.
    
    Provides UI controls for:
    - Transparency (alpha)
    - State colors (searching, detected, tracking)
    - FPS limit
    - Trail effects
    - Stats display
    """
    
    def __init__(
        self,
        parent: tk.Tk,
        current_config: Optional[Dict[str, Any]] = None,
        lang: str = 'vi',
        on_apply: Optional[Callable[[Dict[str, Any]], None]] = None
    ):
        """
        Initialize settings dialog.
        
        Args:
            parent: Parent window
            current_config: Current overlay configuration
            lang: Language ('en' or 'vi')
            on_apply: Callback when settings applied - receives new config dict
        """
        self.parent = parent
        self.lang = lang
        self.on_apply = on_apply
        
        # Default config
        self.default_config = {
            'alpha': 0.7,
            'fps_limit': 15,
            'colors': {
                'searching': [255, 0, 0],    # Red
                'detected': [0, 255, 0],     # Green
                'tracking': [0, 0, 255],     # Blue
            },
            'trail': {
                'enabled': False,
                'length': 5,
                'fade': True
            },
            'stats': {
                'show_fps': False,
                'show_count': False,
                'show_memory': False
            }
        }
        
        # Merge with current config
        self.config = self._merge_config(current_config or {})
        
        # Working copy for editing
        self.working_config = json.loads(json.dumps(self.config))  # Deep copy
        
        # UI elements
        self.dialog: Optional[tk.Toplevel] = None
        self.alpha_var = tk.DoubleVar(value=self.config['alpha'])
        self.fps_var = tk.IntVar(value=self.config['fps_limit'])
        self.trail_enabled_var = tk.BooleanVar(value=self.config['trail']['enabled'])
        self.trail_length_var = tk.IntVar(value=self.config['trail']['length'])
        self.stats_fps_var = tk.BooleanVar(value=self.config['stats']['show_fps'])
        self.stats_count_var = tk.BooleanVar(value=self.config['stats']['show_count'])
        
        # Color buttons and labels
        self.color_buttons: Dict[str, Any] = {}  # Holds both buttons and labels
    
    def _merge_config(self, user_config: Dict[str, Any]) -> Dict[str, Any]:
        """Merge user config with defaults."""
        merged = json.loads(json.dumps(self.default_config))  # Deep copy defaults
        
        if 'alpha' in user_config:
            merged['alpha'] = user_config['alpha']
        if 'fps_limit' in user_config:
            merged['fps_limit'] = user_config['fps_limit']
        if 'colors' in user_config:
            merged['colors'].update(user_config['colors'])
        if 'trail' in user_config:
            merged['trail'].update(user_config['trail'])
        if 'stats' in user_config:
            merged['stats'].update(user_config['stats'])
        
        return merged
    
    def _t(self, key: str) -> str:
        """Translate using global i18n system with fallback to local."""
        try:
            # Try global translations first
            return i18n_t(key, lang=self.lang)
        except Exception:
            # Fallback to local translations
            translations = {
                'en': {
                    'title': 'Overlay Settings',
                    'tab_appearance': 'Appearance',
                    'tab_performance': 'Performance',
                    'tab_effects': 'Effects',
                    'alpha_label': 'Transparency (Alpha):',
                    'alpha_opaque': 'Opaque',
                    'alpha_transparent': 'Transparent',
                    'fps_label': 'FPS Limit:',
                    'colors_label': 'State Colors:',
                    'color_searching': 'Searching:',
                    'color_detected': 'Detected:',
                    'color_tracking': 'Tracking:',
                    'pick_color': 'Pick Color',
                    'reset_colors': 'Reset to Defaults',
                    'trail_enabled': 'Enable detection trails',
                    'trail_length': 'Trail length:',
                    'stats_label': 'Show Statistics:',
                    'stats_fps': 'FPS counter',
                    'stats_count': 'Detection count',
                    'stats_memory': 'Memory usage',
                    'btn_apply': 'Apply',
                    'btn_cancel': 'Cancel',
                    'btn_reset': 'Reset All',
                    'preview_label': 'Preview',
                },
                'vi': {
                    'title': 'Cấu Hình Overlay',
                    'tab_appearance': 'Giao Diện',
                    'tab_performance': 'Hiệu Năng',
                    'tab_effects': 'Hiệu Ứng',
                    'alpha_label': 'Độ Trong Suốt (Alpha):',
                    'alpha_opaque': 'Đục',
                    'alpha_transparent': 'Trong Suốt',
                    'fps_label': 'Giới Hạn FPS:',
                    'colors_label': 'Màu Trạng Thái:',
                    'color_searching': 'Đang Tìm:',
                    'color_detected': 'Đã Phát Hiện:',
                    'color_tracking': 'Đang Theo Dõi:',
                    'pick_color': 'Chọn Màu',
                    'reset_colors': 'Khôi Phục Mặc Định',
                    'trail_enabled': 'Bật hiệu ứng đuôi',
                    'trail_length': 'Độ dài đuôi:',
                    'stats_label': 'Hiển Thị Thống Kê:',
                    'stats_fps': 'Bộ đếm FPS',
                    'stats_count': 'Số lượng phát hiện',
                    'stats_memory': 'Sử dụng bộ nhớ',
                    'btn_apply': 'Áp Dụng',
                    'btn_cancel': 'Hủy',
                    'btn_reset': 'Khôi Phục Tất Cả',
                    'preview_label': 'Xem Trước',
                }
            }
            return translations.get(self.lang, translations['en']).get(key, key)
    
    def show(self) -> None:
        """Show the settings dialog."""
        if self.dialog is not None:
            self.dialog.lift()
            return
        
        # Create dialog
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title(self._t('title'))
        self.dialog.geometry('600x500')
        self.dialog.resizable(False, False)
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Center dialog
        self._center_window()
        
        # Build UI
        self._build_ui()
        
        # Handle close
        self.dialog.protocol("WM_DELETE_WINDOW", self._on_cancel)
    
    def _center_window(self) -> None:
        """Center dialog on parent."""
        if self.dialog is None:
            return
        
        self.dialog.update_idletasks()
        x = self.parent.winfo_x() + (self.parent.winfo_width() - self.dialog.winfo_width()) // 2
        y = self.parent.winfo_y() + (self.parent.winfo_height() - self.dialog.winfo_height()) // 2
        self.dialog.geometry(f'+{x}+{y}')
    
    def _build_ui(self) -> None:
        """Build the dialog UI."""
        if self.dialog is None:
            return
        
        # Create notebook (tabs)
        notebook = ttk.Notebook(self.dialog)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tab 1: Appearance
        tab_appearance = ttk.Frame(notebook)
        notebook.add(tab_appearance, text=self._t('tab_appearance'))
        self._build_appearance_tab(tab_appearance)
        
        # Tab 2: Performance
        tab_performance = ttk.Frame(notebook)
        notebook.add(tab_performance, text=self._t('tab_performance'))
        self._build_performance_tab(tab_performance)
        
        # Tab 3: Effects
        tab_effects = ttk.Frame(notebook)
        notebook.add(tab_effects, text=self._t('tab_effects'))
        self._build_effects_tab(tab_effects)
        
        # Bottom buttons
        self._build_button_bar()
    
    def _build_appearance_tab(self, parent: ttk.Frame) -> None:
        """Build appearance settings tab."""
        # Alpha slider
        alpha_frame = ttk.LabelFrame(parent, text=self._t('alpha_label'), padding=10)
        alpha_frame.pack(fill=tk.X, padx=10, pady=10)
        
        slider_frame = ttk.Frame(alpha_frame)
        slider_frame.pack(fill=tk.X)
        
        ttk.Label(slider_frame, text=self._t('alpha_transparent')).pack(side=tk.LEFT)
        
        alpha_slider = ttk.Scale(
            slider_frame,
            from_=0.0,
            to=1.0,
            orient=tk.HORIZONTAL,
            variable=self.alpha_var,
            command=lambda v: self._on_alpha_change()
        )
        alpha_slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        
        # Add tooltip for alpha slider
        attach_i18n_tooltip(
            alpha_slider,
            "overlay_alpha_tooltip",
            ns=None,
            lang_provider=lambda: self.lang
        )
        
        ttk.Label(slider_frame, text=self._t('alpha_opaque')).pack(side=tk.RIGHT)
        
        # Alpha value label
        self.alpha_value_label = ttk.Label(alpha_frame, text=f"{self.alpha_var.get():.2f}")
        self.alpha_value_label.pack()
        
        # Color pickers
        color_frame = ttk.LabelFrame(parent, text=self._t('colors_label'), padding=10)
        color_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Searching color
        self._build_color_picker(color_frame, 'searching', self._t('color_searching'))
        
        # Detected color
        self._build_color_picker(color_frame, 'detected', self._t('color_detected'))
        
        # Tracking color
        self._build_color_picker(color_frame, 'tracking', self._t('color_tracking'))
        
        # Reset colors button
        reset_btn = ttk.Button(
            color_frame,
            text=self._t('reset_colors'),
            command=self._reset_colors
        )
        reset_btn.pack(pady=5)
    
    def _build_performance_tab(self, parent: ttk.Frame) -> None:
        """Build performance settings tab."""
        # FPS limit
        fps_frame = ttk.LabelFrame(parent, text=self._t('fps_label'), padding=10)
        fps_frame.pack(fill=tk.X, padx=10, pady=10)
        
        slider_frame = ttk.Frame(fps_frame)
        slider_frame.pack(fill=tk.X)
        
        ttk.Label(slider_frame, text="1").pack(side=tk.LEFT)
        
        fps_slider = ttk.Scale(
            slider_frame,
            from_=1,
            to=60,
            orient=tk.HORIZONTAL,
            variable=self.fps_var,
            command=lambda v: self._on_fps_change()
        )
        fps_slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        
        # Add tooltip for FPS slider
        attach_i18n_tooltip(
            fps_slider,
            "overlay_fps_tooltip",
            ns=None,
            lang_provider=lambda: self.lang
        )
        
        ttk.Label(slider_frame, text="60").pack(side=tk.RIGHT)
        
        # FPS value label
        self.fps_value_label = ttk.Label(fps_frame, text=f"{self.fps_var.get()} FPS")
        self.fps_value_label.pack()
        
        # Info text
        info_text = "Lower FPS = less CPU usage\nHigher FPS = smoother animation" if self.lang == 'en' else \
                    "FPS thấp = ít CPU hơn\nFPS cao = mượt mà hơn"
        ttk.Label(fps_frame, text=info_text, foreground='gray').pack(pady=5)
    
    def _build_effects_tab(self, parent: ttk.Frame) -> None:
        """Build effects settings tab."""
        # Trail effects
        trail_frame = ttk.LabelFrame(parent, text=self._t('trail_enabled'), padding=10)
        trail_frame.pack(fill=tk.X, padx=10, pady=10)
        
        trail_check = ttk.Checkbutton(
            trail_frame,
            text=self._t('trail_enabled'),
            variable=self.trail_enabled_var,
            command=self._on_trail_toggle
        )
        trail_check.pack(anchor=tk.W)
        
        # Trail length slider
        trail_slider_frame = ttk.Frame(trail_frame)
        trail_slider_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(trail_slider_frame, text=self._t('trail_length')).pack(side=tk.LEFT)
        
        trail_slider = ttk.Scale(
            trail_slider_frame,
            from_=1,
            to=20,
            orient=tk.HORIZONTAL,
            variable=self.trail_length_var,
            command=lambda v: self._on_trail_length_change()
        )
        trail_slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        
        self.trail_length_label = ttk.Label(trail_slider_frame, text=f"{self.trail_length_var.get()}")
        self.trail_length_label.pack(side=tk.RIGHT)
        
        # Enable/disable trail slider based on checkbox
        self._on_trail_toggle()
        
        # Stats display
        stats_frame = ttk.LabelFrame(parent, text=self._t('stats_label'), padding=10)
        stats_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Checkbutton(
            stats_frame,
            text=self._t('stats_fps'),
            variable=self.stats_fps_var
        ).pack(anchor=tk.W)
        
        ttk.Checkbutton(
            stats_frame,
            text=self._t('stats_count'),
            variable=self.stats_count_var
        ).pack(anchor=tk.W)
    
    def _build_color_picker(self, parent: Any, state: str, label: str) -> None:
        """Build a color picker row."""
        row = ttk.Frame(parent)
        row.pack(fill=tk.X, pady=5)
        
        ttk.Label(row, text=label, width=15).pack(side=tk.LEFT)
        
        # Color preview button
        color = self.working_config['colors'][state]
        color_hex = f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}"
        
        btn = tk.Button(
            row,
            text="   ",
            bg=color_hex,
            width=5,
            relief=tk.RAISED,
            command=lambda: self._pick_color(state)
        )
        btn.pack(side=tk.LEFT, padx=5)
        
        # RGB label
        rgb_label = ttk.Label(row, text=f"RGB({color[0]}, {color[1]}, {color[2]})")
        rgb_label.pack(side=tk.LEFT)
        
        # Store references
        self.color_buttons[state] = btn
        self.color_buttons[f"{state}_label"] = rgb_label
    
    def _build_button_bar(self) -> None:
        """Build bottom button bar."""
        if self.dialog is None:
            return
        
        btn_frame = ttk.Frame(self.dialog)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Reset all
        ttk.Button(
            btn_frame,
            text=self._t('btn_reset'),
            command=self._reset_all
        ).pack(side=tk.LEFT)
        
        # Spacer
        ttk.Frame(btn_frame).pack(side=tk.LEFT, expand=True)
        
        # Cancel
        ttk.Button(
            btn_frame,
            text=self._t('btn_cancel'),
            command=self._on_cancel
        ).pack(side=tk.RIGHT, padx=5)
        
        # Apply
        ttk.Button(
            btn_frame,
            text=self._t('btn_apply'),
            command=self._on_apply_clicked
        ).pack(side=tk.RIGHT)
    
    def _on_alpha_change(self) -> None:
        """Handle alpha slider change."""
        value = self.alpha_var.get()
        self.alpha_value_label.config(text=f"{value:.2f}")
        self.working_config['alpha'] = value
    
    def _on_fps_change(self) -> None:
        """Handle FPS slider change."""
        value = int(self.fps_var.get())
        self.fps_value_label.config(text=f"{value} FPS")
        self.working_config['fps_limit'] = value
    
    def _on_trail_toggle(self) -> None:
        """Handle trail checkbox toggle."""
        enabled = self.trail_enabled_var.get()
        self.working_config['trail']['enabled'] = enabled
        
        # Enable/disable trail length slider (if it exists)
        # (Will be implemented when slider is created)
    
    def _on_trail_length_change(self) -> None:
        """Handle trail length slider change."""
        value = int(self.trail_length_var.get())
        self.trail_length_label.config(text=f"{value}")
        self.working_config['trail']['length'] = value
    
    def _pick_color(self, state: str) -> None:
        """Open color picker for state."""
        current_color = self.working_config['colors'][state]
        color_hex = f"#{current_color[0]:02x}{current_color[1]:02x}{current_color[2]:02x}"
        
        # Show color picker
        result = colorchooser.askcolor(
            color=color_hex,
            title=f"Pick color for {state}"
        )
        
        if result[0] is not None:
            # Update config
            rgb = [int(result[0][0]), int(result[0][1]), int(result[0][2])]
            self.working_config['colors'][state] = rgb
            
            # Update button color
            color_hex = f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
            self.color_buttons[state].config(bg=color_hex)
            self.color_buttons[f"{state}_label"].config(text=f"RGB({rgb[0]}, {rgb[1]}, {rgb[2]})")
    
    def _reset_colors(self) -> None:
        """Reset colors to defaults."""
        default_colors = self.default_config['colors']
        self.working_config['colors'] = json.loads(json.dumps(default_colors))
        
        # Update UI
        for state in ['searching', 'detected', 'tracking']:
            color = default_colors[state]
            color_hex = f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}"
            self.color_buttons[state].config(bg=color_hex)
            self.color_buttons[f"{state}_label"].config(text=f"RGB({color[0]}, {color[1]}, {color[2]})")
    
    def _reset_all(self) -> None:
        """Reset all settings to defaults."""
        self.working_config = json.loads(json.dumps(self.default_config))
        
        # Update UI
        self.alpha_var.set(self.working_config['alpha'])
        self.fps_var.set(self.working_config['fps_limit'])
        self.trail_enabled_var.set(self.working_config['trail']['enabled'])
        self.trail_length_var.set(self.working_config['trail']['length'])
        self.stats_fps_var.set(self.working_config['stats']['show_fps'])
        self.stats_count_var.set(self.working_config['stats']['show_count'])
        
        self._reset_colors()
        self._on_alpha_change()
        self._on_fps_change()
    
    def _on_apply_clicked(self) -> None:
        """Handle apply button click."""
        # Update main config
        self.config = json.loads(json.dumps(self.working_config))
        
        # Update stats from vars
        self.config['stats']['show_fps'] = self.stats_fps_var.get()
        self.config['stats']['show_count'] = self.stats_count_var.get()
        
        # Call callback
        if self.on_apply is not None:
            try:
                self.on_apply(self.config)
            except Exception as e:
                print(f"[OverlaySettings] Apply callback error: {e}")
        
        # Close dialog
        self._close()
    
    def _on_cancel(self) -> None:
        """Handle cancel button click."""
        self._close()
    
    def _close(self) -> None:
        """Close the dialog."""
        if self.dialog is not None:
            self.dialog.destroy()
            self.dialog = None


# =====================================================================
# Demo / Testing
# =====================================================================

if __name__ == "__main__":
    """Demo overlay settings dialog."""
    
    root = tk.Tk()
    root.title("Overlay Settings Demo")
    root.geometry("400x300")
    
    def on_apply(config: Dict[str, Any]) -> None:
        """Handle settings applied."""
        print("[Demo] Settings applied:")
        print(json.dumps(config, indent=2))
    
    # Test with default config
    test_config = {
        'alpha': 0.7,
        'fps_limit': 15,
        'colors': {
            'searching': [255, 0, 0],
            'detected': [0, 255, 0],
            'tracking': [0, 0, 255],
        }
    }
    
    def show_settings():
        dialog = OverlaySettingsDialog(
            parent=root,
            current_config=test_config,
            lang='vi',
            on_apply=on_apply
        )
        dialog.show()
    
    # Button to open settings
    btn = tk.Button(
        root,
        text="Open Overlay Settings",
        command=show_settings,
        width=20,
        height=2
    )
    btn.pack(pady=50)
    
    info = tk.Label(
        root,
        text="Click button to test settings dialog\nCheck console for applied settings",
        justify=tk.LEFT
    )
    info.pack(pady=20)
    
    root.mainloop()
