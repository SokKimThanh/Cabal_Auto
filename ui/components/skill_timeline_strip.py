import tkinter as tk
from tkinter import ttk
from lib.ui_style_v2 import UIStyleV2 as UI
from lib.events.event_bus import EventBus
import time
from typing import List, Dict, Any, Optional

class SkillSlotCanvas(tk.Canvas):
    SLOT_SIZE = 48

    def __init__(self, parent, skill_data: Dict[str, Any], on_drag_start, on_drag_motion, on_drag_release, *args, **kwargs):
        kwargs['width'] = self.SLOT_SIZE
        kwargs['height'] = self.SLOT_SIZE
        kwargs['bg'] = UI.BG_ELEVATED
        kwargs['highlightthickness'] = 1
        kwargs['highlightbackground'] = UI.BORDER_PRIMARY
        super().__init__(parent, *args, **kwargs)

        self.skill_data = skill_data
        self.skill_name = skill_data.get('name', 'Unknown')
        self.icon_key = skill_data.get('icon_key', 'unknown')
        self.hotkey = skill_data.get('hotkey', '')

        # Keep strong references to photo images so GC doesn't destroy them
        self._images = {}
        self.cooldown_rect = None
        self.cooldown_border = None

        self.on_drag_start = on_drag_start
        self.on_drag_motion = on_drag_motion
        self.on_drag_release = on_drag_release

        self._build_slot()
        self._bind_events()

    def _build_slot(self):
        # 1. Draw Icon
        # In a real app we'd load via ImageLibraryComponent,
        # but for this component, we simulate it with text/emoji if no image is available.
        # We will mock it here using text for simplicity unless an image is explicitly given in data.
        from ui.helpers.icon_helper import IconHelper
        icon_helper = IconHelper()
        if 'image_obj' in self.skill_data:
            img = self.skill_data['image_obj']
            self._images['icon'] = img
            self.create_image(self.SLOT_SIZE//2, self.SLOT_SIZE//2, image=img, tags="icon")
        elif self.icon_key != 'unknown':
            img = icon_helper.get_icon(self.icon_key, size=(24, 24))
            if img:
                self._images['icon'] = img
                self.create_image(self.SLOT_SIZE//2, self.SLOT_SIZE//2 - 4, image=img, tags="icon")
            else:
                self.create_text(
                    self.SLOT_SIZE//2,
                    self.SLOT_SIZE//2 - 4,
                    text=self.skill_name[:2].upper(),
                    fill=UI.TEXT_PRIMARY,
                    font=UI.get_font(role="header"),
                    tags="icon"
                )
        else:
            # Fallback text icon
            self.create_text(
                self.SLOT_SIZE//2,
                self.SLOT_SIZE//2 - 4,
                text=self.skill_name[:2].upper(),
                fill=UI.TEXT_PRIMARY,
                font=UI.get_font(role="header"),
                tags="icon"
            )

        # 2. Draw Hotkey (bottom right)
        self.create_text(
            self.SLOT_SIZE - 4,
            self.SLOT_SIZE - 4,
            text=str(self.hotkey),
            fill=UI.TEXT_MUTED,
            font=UI.get_font(role="tiny", weight="bold"),
            anchor="se",
            tags="hotkey"
        )

        # 3. Create hidden cooldown overlay (gray50 stipple)
        self.cooldown_rect = self.create_rectangle(
            0, self.SLOT_SIZE, self.SLOT_SIZE, self.SLOT_SIZE, # Initially 0 height (bottom up)
            fill="gray", stipple="gray50", outline="", state="hidden", tags="cooldown"
        )

    def _bind_events(self):
        # Bind Drag and Drop events
        self.bind("<ButtonPress-1>", self._on_press)
        self.bind("<B1-Motion>", self._on_motion)
        self.bind("<ButtonRelease-1>", self._on_release)

    def _on_press(self, event):
        self.on_drag_start(self, event)

    def _on_motion(self, event):
        self.on_drag_motion(self, event)

    def _on_release(self, event):
        self.on_drag_release(self, event)

    def update_cooldown(self, ratio: float):
        """Update cooldown visual overlay. Ratio should be between 0.0 and 1.0"""
        ratio = max(0.0, min(1.0, float(ratio)))

        if ratio <= 0.0 or ratio >= 1.0:
            self.itemconfig(self.cooldown_rect, state="hidden")
            self.config(highlightbackground=UI.BORDER_PRIMARY)
        else:
            self.itemconfig(self.cooldown_rect, state="normal")
            # Calculate height based on ratio (bottom up)
            y_top = self.SLOT_SIZE * (1.0 - ratio)
            self.coords(self.cooldown_rect, 0, y_top, self.SLOT_SIZE, self.SLOT_SIZE)
            self.config(highlightbackground=UI.ACCENT_AMBER)


class SkillTimelineStrip(ttk.Frame):
    MAX_SLOTS = 8

    def __init__(self, parent, skills: List[Dict[str, Any]] = None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.skills = skills or []

        # State tracking for Undo
        self._history: List[List[Dict[str, Any]]] = []
        self._slots: List[SkillSlotCanvas] = []

        # Drag state
        self._drag_data = {"x": 0, "y": 0, "item": None, "original_index": -1}

        self._build_ui()
        self.render_skills()

    def _build_ui(self):
        # Header/Controls
        self.header_frame = tk.Frame(self, bg=UI.BG_SURFACE)
        self.header_frame.pack(side="top", fill="x", pady=(0, UI.SPACE_SM))

        self.title_label = tk.Label(
            self.header_frame,
            text="Skill Timeline",
            font=UI.get_font(role="label", weight="bold"),
            bg=UI.BG_SURFACE, fg=UI.TEXT_PRIMARY
        )
        self.title_label.pack(side="left")

        self.undo_btn = tk.Button(
            self.header_frame,
            text="Undo",
            command=self.undo,
            **UI.get_button_style("neutral")
        )
        self.undo_btn.pack(side="right")
        self.undo_btn.config(state="disabled")

        # Canvas & Scrollbar setup
        self.canvas_frame = tk.Frame(self, bg=UI.BG_SURFACE)
        self.canvas_frame.pack(side="top", fill="x", expand=True)

        self.canvas = tk.Canvas(
            self.canvas_frame,
            height=SkillSlotCanvas.SLOT_SIZE + 4,
            bg=UI.BG_SURFACE,
            highlightthickness=0
        )

        self.scrollbar = ttk.Scrollbar(self.canvas_frame, orient="horizontal", command=self.canvas.xview)
        self.canvas.configure(xscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="top", fill="x", expand=True)
        # Only show scrollbar if needed, we'll pack it in render_skills if > 8 items

        # Inner frame to hold the slots
        self.slots_frame = tk.Frame(self.canvas, bg=UI.BG_SURFACE)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.slots_frame, anchor="nw")

        self.slots_frame.bind("<Configure>", self._on_frame_configure)

    def _on_frame_configure(self, event=None):
        """Reset the scroll region to encompass the inner frame"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def update_skills(self, skills: List[Dict[str, Any]]):
        """Update the list of skills and re-render."""
        self.skills = skills
        self.render_skills()

    def render_skills(self):
        """Render the list of skills into slots."""
        # Clear existing
        for slot in self._slots:
            slot.destroy()
        self._slots.clear()

        # Update Scrollbar visibility
        if len(self.skills) > self.MAX_SLOTS:
            self.scrollbar.pack(side="bottom", fill="x")
        else:
            self.scrollbar.pack_forget()

        # Render each skill
        for i, skill in enumerate(self.skills):
            slot = SkillSlotCanvas(
                self.slots_frame,
                skill_data=skill,
                on_drag_start=self._on_drag_start,
                on_drag_motion=self._on_drag_motion,
                on_drag_release=self._on_drag_release
            )
            slot.pack(side="left", padx=UI.SPACE_XS)
            self._slots.append(slot)

        self._update_undo_state()

    def update_cooldown(self, skill_name: str, ratio: float):
        """Update cooldown for a specific skill."""
        for slot in self._slots:
            if slot.skill_name == skill_name:
                slot.update_cooldown(ratio)
                break

    # --- Drag & Drop Logic ---

    def _on_drag_start(self, slot: SkillSlotCanvas, event):
        """Record drag start position and slot."""
        self._drag_data["item"] = slot
        self._drag_data["x"] = event.x_root
        self._drag_data["y"] = event.y_root
        self._drag_data["original_index"] = self._slots.index(slot)

        # Save current state for undo (copy)
        self._history = [list(self.skills)]

        # Lift visual appearance
        slot.config(highlightbackground=UI.ACCENT_GREEN)

    def _on_drag_motion(self, slot: SkillSlotCanvas, event):
        """Handle visual feedback or potential reorder hint (simplified)."""
        pass # Actual reorder happens on release for simplicity in this implementation

    def _on_drag_release(self, slot: SkillSlotCanvas, event):
        """Handle dropping logic to swap/reorder."""
        if not self._drag_data["item"]:
            return

        # Reset visual
        slot.config(highlightbackground=UI.BORDER_PRIMARY)

        # Determine target index based on x coordinate relative to slots_frame
        x_in_frame = self.slots_frame.winfo_pointerx() - self.slots_frame.winfo_rootx()

        # Approximate index based on slot width and padding
        slot_total_width = SkillSlotCanvas.SLOT_SIZE + UI.SPACE_XS * 2
        target_index = max(0, min(len(self.skills) - 1, x_in_frame // slot_total_width))

        old_index = self._drag_data["original_index"]

        if old_index != target_index and old_index >= 0:
            # Reorder skills array
            skill_to_move = self.skills.pop(old_index)
            self.skills.insert(target_index, skill_to_move)

            # Re-render
            self.render_skills()
            self._update_undo_state()

        self._drag_data = {"x": 0, "y": 0, "item": None, "original_index": -1}

    # --- Undo Logic ---

    def undo(self):
        """Restore previous state."""
        if self._history:
            self.skills = self._history.pop()
            self.render_skills()
            self._update_undo_state()

    def _update_undo_state(self):
        if self._history:
            self.undo_btn.config(state="normal")
        else:
            self.undo_btn.config(state="disabled")
