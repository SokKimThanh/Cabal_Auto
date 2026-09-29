import tkinter as tk
from tkinter import ttk
import time
from lib.ui_style_v2 import UIStyleV2 as UI
from lib.ui.animation_manager import UIAnimationManager

class ComboRhythmBar(ttk.Frame):
    SWEET_SPOT_RATIO = 0.78
    DEBOUNCE_MS = 200

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.is_visible = tk.BooleanVar(value=True)
        self.last_trigger_time = 0
        self.animation_manager = UIAnimationManager()
        self.animation_target_id = f"combo_rhythm_{id(self)}"

        self.base_color = UI.BG_ELEVATED
        self.accent_color = UI.ACCENT_AMBER

        # UI state
        self.current_color = self.base_color
        self.sweet_spot_rect = None
        self.last_toggle_time = 0

        self._build_ui()

    def _build_ui(self):
        # Header/Control Frame
        self.control_frame = tk.Frame(self, bg=UI.BG_SURFACE)
        self.control_frame.pack(side="top", fill="x", pady=(0, UI.SPACE_SM))

        self.toggle_btn = tk.Checkbutton(
            self.control_frame,
            text="Hiển thị Rhythm Bar",
            variable=self.is_visible,
            command=self._on_toggle_visibility,
            bg=UI.BG_SURFACE,
            fg=UI.TEXT_PRIMARY,
            selectcolor=UI.BG_ELEVATED,
            activebackground=UI.BG_SURFACE,
            activeforeground=UI.TEXT_PRIMARY,
            font=UI.FONT_SMALL
        )
        self.toggle_btn.pack(side="left")

        # Rhythm Bar Canvas Container
        self.bar_container = tk.Frame(self, bg=UI.BG_SURFACE)
        self.bar_container.pack(side="top", fill="x", expand=True)

        self.canvas_width = 300
        self.canvas_height = 20
        self.canvas = tk.Canvas(
            self.bar_container,
            height=self.canvas_height,
            bg=UI.BG_ELEVATED,
            highlightthickness=1,
            highlightbackground=UI.BORDER_PRIMARY
        )
        self.canvas.pack(fill="x", expand=True, padx=UI.SPACE_SM, pady=UI.SPACE_SM)

        # We need to bind configure event to redraw when width changes
        self.canvas.bind("<Configure>", self._on_canvas_resize)

    def _on_toggle_visibility(self):
        current_time = time.time()
        # Prevent layout thrashing from toggle spam
        if (current_time - self.last_toggle_time) * 1000 < self.DEBOUNCE_MS:
            # Revert the checkbox visually to match current underlying state
            self.is_visible.set(not self.is_visible.get())
            return

        self.last_toggle_time = current_time

        if self.is_visible.get():
            self.bar_container.pack(side="top", fill="x", expand=True)
        else:
            self.bar_container.pack_forget()

    def _on_canvas_resize(self, event):
        self.canvas_width = event.width
        self.draw_rhythm_bar()

    def draw_rhythm_bar(self):
        self.canvas.delete("all")

        # Vẽ vùng sweet spot
        sweet_spot_x = self.canvas_width * self.SWEET_SPOT_RATIO
        sweet_spot_width = 10 # 10px width for the sweet spot marker

        self.sweet_spot_rect = self.canvas.create_rectangle(
            sweet_spot_x - sweet_spot_width/2,
            0,
            sweet_spot_x + sweet_spot_width/2,
            self.canvas_height,
            fill=self.current_color,
            outline=""
        )

    def trigger_hit(self):
        """Called when CabalComboDetector hits the sweet spot."""
        current_time = time.time()

        # Hard Debounce (200ms)
        if (current_time - self.last_trigger_time) * 1000 < self.DEBOUNCE_MS:
            return

        self.last_trigger_time = current_time

        # Update base color immediately
        self.current_color = self.accent_color
        if self.is_visible.get():
            self._update_color(1.0) # start at fully bright

            # Trigger fade animation using UIAnimationManager
            self.animation_manager.register_tween(
                target_id=self.animation_target_id,
                widget=self,
                start_val=1.0,
                end_val=0.0,
                duration_ms=self.DEBOUNCE_MS,
                update_func=self._update_color
            )

    def _update_color(self, progress: float):
        """Callback for UIAnimationManager tweening."""
        try:
            if not self.winfo_exists() or not hasattr(self, 'canvas') or not self.canvas.winfo_exists():
                return
            if not self.sweet_spot_rect:
                return

            # Blend from Accent Amber to Base Elevated based on progress
            blended_color = UI.blend_alpha_to_hex(progress, self.base_color, self.accent_color)
            self.current_color = blended_color
            self.canvas.itemconfig(self.sweet_spot_rect, fill=blended_color)
        except tk.TclError:
            pass # Widget might have been destroyed
