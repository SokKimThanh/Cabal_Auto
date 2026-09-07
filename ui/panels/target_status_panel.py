import tkinter as tk
from tkinter import ttk
from dataclasses import dataclass
from lib.ui_style_v2 import UIStyleV2 as UI
from ui.components.status_badge import StatusBadge

@dataclass
class TargetInfo:
    name: str = ""
    level: int = 0
    hp: int = 0
    max_hp: int = 0
    mp: int = 0
    max_mp: int = 0
    defense: int = 0
    state: str = "waiting" # "waiting" | "ready" | "hunting"

class TargetStatusPanel(ttk.LabelFrame):
    def __init__(self, parent, app, scale_factor=1.0, hunt_tab=None):
        padding = (int(8 * scale_factor), int(6 * scale_factor))
        super().__init__(parent, text="📊 Target Status", padding=padding)
        self.app = app
        self.scale_factor = scale_factor
        self.hunt_tab = hunt_tab

        self.font_ui = UI.resolve_font_family("ui")
        self.font_mono = UI.resolve_font_family("mono")

        # Legacy compatibility wrappers
        self._setup_legacy_wrappers()

        self._build_ui()

    def _setup_legacy_wrappers(self):
        """Creates dummy objects for legacy code that expects standard tkinter widgets"""
        self.app.hp_canvas = tk.Canvas(self)
        self.app.hp_percent_label = tk.Label(self)
        self.app.target_image_label = tk.Label(self)
        self.app.target_name_label = tk.Label(self)
        self.app.status_label = tk.Label(self)
        self.app.target_level_label = tk.Label(self)
        self.app.target_hp_label = tk.Label(self)
        self.app.target_def_label = tk.Label(self)
        self.app.recovery_frame = tk.Frame(self)
        self.app.hp_bg = self.app.hp_canvas.create_rectangle(0,0,1,1)
        self.app.hp_fill = self.app.hp_canvas.create_rectangle(0,0,1,1)
        self.app.hp_text = self.app.hp_canvas.create_text(0,0)

        self.app.hunt_status_badge = StatusBadge(self, status="waiting")
        self.app.hunt_status_label = self.app.hunt_status_badge
        self.app.hunt_target_info = tk.StringVar(value="")
        self.app.hunt_target_info_label = tk.Label(self, textvariable=self.app.hunt_target_info)

        self._current_info = TargetInfo()

        if getattr(self, "hunt_tab", None):
            for prop in ["target_image_label", "target_name_label", "status_label",
                         "target_level_label", "target_hp_label", "target_def_label",
                         "hp_canvas", "hp_percent_label", "recovery_frame", "hp_bg", "hp_fill", "hp_text",
                         "hunt_status_badge", "hunt_status_label"]:
                if hasattr(self.app, prop):
                    setattr(self.hunt_tab, prop, getattr(self.app, prop))

        def intercept_name(*args, **kwargs):
            if "text" in kwargs:
                self._current_info.name = kwargs["text"]
                if self._current_info.state == "waiting" and self._current_info.name and self._current_info.name != "UnknownMob":
                    self._current_info.state = "ready"
                elif not self._current_info.name or self._current_info.name == "UnknownMob":
                    self._current_info.state = "waiting"
                self.update_target(self._current_info)
            return tk.Label.config(self.app.target_name_label, *args, **kwargs)
        self.app.target_name_label.config = intercept_name

        def intercept_level(*args, **kwargs):
            if "text" in kwargs:
                try: self._current_info.level = int(kwargs["text"])
                except: pass
                self.update_target(self._current_info)
            return tk.Label.config(self.app.target_level_label, *args, **kwargs)
        self.app.target_level_label.config = intercept_level

        def intercept_max_hp(*args, **kwargs):
            if "text" in kwargs:
                try:
                    self._current_info.max_hp = int(kwargs["text"])
                    if self._current_info.hp == 0:
                        self._current_info.hp = self._current_info.max_hp # initialize full
                except: pass
                self.update_target(self._current_info)
            return tk.Label.config(self.app.target_hp_label, *args, **kwargs)
        self.app.target_hp_label.config = intercept_max_hp

        def intercept_def(*args, **kwargs):
            if "text" in kwargs:
                try: self._current_info.defense = int(kwargs["text"])
                except: pass
                self.update_target(self._current_info)
            return tk.Label.config(self.app.target_def_label, *args, **kwargs)
        self.app.target_def_label.config = intercept_def

        def intercept_status(*args, **kwargs):
            if "status" in kwargs:
                if kwargs["status"] == "hunting": self._current_info.state = "hunting"
                elif kwargs["status"] == "waiting": self._current_info.state = "waiting"
                else: self._current_info.state = "ready"
                self.update_target(self._current_info)
            return tk.Label.config(self.app.status_label, *args, **kwargs)
        self.app.status_label.config = intercept_status

        # Intercept hp_canvas itemconfig for HP updates
        orig_itemconfig = self.app.hp_canvas.itemconfig
        def intercept_hp_canvas_itemconfig(tagOrId, **kwargs):
            if tagOrId == self.app.hp_fill and "fill" in kwargs:
                color = kwargs["fill"]
                if color == "#52525B": # dead
                    self._current_info.hp = 0
                    self._current_info.state = "waiting"
                    self.update_target(self._current_info)
                elif color == UI.ACCENT_GREEN: # hunting / full
                    self._current_info.state = "hunting"
                    self.update_target(self._current_info)
            return orig_itemconfig(tagOrId, **kwargs)
        self.app.hp_canvas.itemconfig = intercept_hp_canvas_itemconfig

        # Intercept coords to update HP ratio
        orig_coords = self.app.hp_canvas.coords
        def intercept_hp_canvas_coords(tagOrId, *args):
            if tagOrId == self.app.hp_fill and len(args) == 4:
                # args are x1, y1, x2, y2
                width = args[2] - args[0]
                total_width = self.app.hp_canvas.winfo_width()
                if total_width > 0:
                    ratio = width / total_width
                    self._current_info.hp = int(self._current_info.max_hp * ratio)
                    self.update_target(self._current_info)
            return orig_coords(tagOrId, *args)
        self.app.hp_canvas.coords = intercept_hp_canvas_coords


    def _build_ui(self):
        # --- SECTION 1: Header bar ---
        header_frame = tk.Frame(self, bg=UI.BG_ELEVATED)
        header_frame.pack(side="top", fill="x")
        header_frame.grid_columnconfigure(0, weight=1)
        header_frame.grid_columnconfigure(1, weight=1)

        # Add padding frame inside header
        header_inner = tk.Frame(header_frame, bg=UI.BG_ELEVATED)
        header_inner.pack(fill="x", padx=UI.SPACE_LG, pady=UI.SPACE_SM)
        header_inner.grid_columnconfigure(0, weight=1)

        title_label = tk.Label(
            header_inner,
            text="⊕ TARGET STATUS",
            font=(self.font_mono, UI.SIZE_TINY, "bold"),
            fg=UI.TEXT_MUTED,
            bg=UI.BG_ELEVATED,
            anchor="w"
        )
        title_label.grid(row=0, column=0, sticky="w")

        self.badge_label = tk.Label(
            header_inner,
            font=(self.font_mono, UI.SIZE_TINY, "bold"),
            padx=UI.SPACE_SM,
            pady=2
        )
        self.badge_label.grid(row=0, column=1, sticky="e")

        ttk.Separator(self, orient="horizontal").pack(fill="x")

        # --- SECTION 2: Target identity ---
        self.identity_frame = tk.Frame(self, bg=UI.BG_SURFACE)
        self.identity_frame.pack(side="top", fill="x", padx=UI.SPACE_LG, pady=UI.SPACE_MD)

        # Empty state container
        self.empty_identity_frame = tk.Frame(self.identity_frame, bg=UI.BG_SURFACE)

        # Draw dashed circle
        empty_canvas = tk.Canvas(self.empty_identity_frame, width=32, height=32, bg=UI.BG_SURFACE, highlightthickness=0)
        empty_canvas.pack(pady=(0, UI.SPACE_SM))
        # Draw a simple dashed circle
        empty_canvas.create_oval(2, 2, 30, 30, outline=UI.BORDER_PRIMARY, width=1, dash=(4, 4))
        empty_canvas.create_oval(14, 14, 18, 18, outline=UI.BORDER_PRIMARY, width=1) # center dot

        tk.Label(
            self.empty_identity_frame,
            text="Chưa có mục tiêu",
            font=(self.font_mono, UI.SIZE_SMALL),
            fg=UI.TEXT_MUTED,
            bg=UI.BG_SURFACE
        ).pack()

        from ui.components.empty_state import EmptyState
        self.empty_state_comp = EmptyState(
            self.empty_identity_frame,
            icon="ℹ️",
            message="Chưa có mục tiêu",
            submessage="Bắt đầu săn để hiển thị thông tin mục tiêu ở đây."
        )
        self.empty_state_comp.pack(fill="both", expand=True)

        # Active state container
        self.active_identity_frame = tk.Frame(self.identity_frame, bg=UI.BG_SURFACE)
        self.active_identity_frame.grid_columnconfigure(0, weight=1)

        left_col = tk.Frame(self.active_identity_frame, bg=UI.BG_SURFACE)
        left_col.grid(row=0, column=0, sticky="w")

        self.target_name_disp = tk.Label(
            left_col,
            font=(self.font_ui, UI.SIZE_HEADER, "bold"),
            fg=UI.TEXT_PRIMARY,
            bg=UI.BG_SURFACE,
            anchor="w"
        )
        self.target_name_disp.pack(anchor="w")

        self.target_sub_disp = tk.Label(
            left_col,
            font=(self.font_mono, UI.SIZE_SMALL),
            fg=UI.TEXT_SECONDARY,
            bg=UI.BG_SURFACE,
            anchor="w"
        )
        self.target_sub_disp.pack(anchor="w")

        right_col = tk.Frame(self.active_identity_frame, bg=UI.BG_SURFACE)
        right_col.grid(row=0, column=1, sticky="e")

        tk.Label(
            right_col,
            text="CẤP",
            font=(self.font_mono, UI.SIZE_TINY),
            fg=UI.TEXT_MUTED,
            bg=UI.BG_SURFACE,
            anchor="e"
        ).pack(anchor="e")

        self.target_level_disp = tk.Label(
            right_col,
            font=(self.font_mono, UI.SIZE_TITLE, "bold"),
            fg=UI.ACCENT_GREEN,
            bg=UI.BG_SURFACE,
            anchor="e"
        )
        self.target_level_disp.pack(anchor="e")

        self.empty_identity_frame.pack(fill="both", expand=True)
        # active_identity_frame is packed when state changes

        ttk.Separator(self, orient="horizontal").pack(fill="x")

        # --- SECTION 3: HP / MP bars ---
        bars_frame = tk.Frame(self, bg=UI.BG_SURFACE)
        bars_frame.pack(side="top", fill="x", padx=UI.SPACE_LG, pady=UI.SPACE_MD)

        self.hp_val_lbl, self.hp_bar_canvas, self.hp_fill_rect = self._make_stat_bar(bars_frame, "HP", UI.DANGER)
        tk.Frame(bars_frame, height=UI.SPACE_MD, bg=UI.BG_SURFACE).pack() # spacer
        self.mp_val_lbl, self.mp_bar_canvas, self.mp_fill_rect = self._make_stat_bar(bars_frame, "MP", UI.ACCENT_BLUE)

        ttk.Separator(self, orient="horizontal").pack(fill="x")

        # --- SECTION 4: Stats row ---
        stats_row = tk.Frame(self, bg=UI.BG_SURFACE)
        stats_row.pack(side="top", fill="x", padx=UI.SPACE_LG, pady=UI.SPACE_SM)
        stats_row.grid_columnconfigure(0, weight=1)
        stats_row.grid_columnconfigure(1, weight=1)
        stats_row.grid_columnconfigure(2, weight=1)

        self.def_val_lbl = self._make_stat_pill(stats_row, "PHÒNG THỦ", 0)
        self.type_val_lbl = self._make_stat_pill(stats_row, "LOẠI", 1)
        self.drop_val_lbl = self._make_stat_pill(stats_row, "DROP", 2)

        # Set initial state
        self.update_target(TargetInfo())

    def _make_stat_bar(self, parent, label, color):
        frame = tk.Frame(parent, bg=UI.BG_SURFACE)
        frame.pack(fill="x")
        frame.grid_columnconfigure(1, weight=1)

        # Row 0: Labels
        lbl_frame = tk.Frame(frame, bg=UI.BG_SURFACE)
        lbl_frame.pack(fill="x")

        name_lbl = tk.Label(
            lbl_frame,
            text=label,
            font=(self.font_mono, UI.SIZE_TINY),
            fg=UI.TEXT_MUTED,
            bg=UI.BG_SURFACE,
            anchor="w"
        )
        name_lbl.pack(side="left")

        val_lbl = tk.Label(
            lbl_frame,
            text="— / —",
            font=(self.font_mono, UI.SIZE_SMALL),
            fg=UI.TEXT_SUBTLE,
            bg=UI.BG_SURFACE,
            anchor="e"
        )
        val_lbl.pack(side="right")

        # Row 1: Real Progress Bar (Thicker, more visible)
        bar_height = 16
        canvas = tk.Canvas(frame, height=bar_height, bg=UI.BG_SUBTLE, highlightthickness=0)
        canvas.pack(fill="x", pady=(4, 0))

        # We need to bind configure to update the fill width correctly
        def _on_resize(event):
            # Track width is event.width
            canvas.coords(track, 0, 0, event.width, bar_height)
            # Fill width needs to be calculated based on current ratio
            if hasattr(canvas, 'current_ratio'):
                canvas.coords(fill_rect, 0, 0, event.width * canvas.current_ratio, bar_height)
            else:
                canvas.coords(fill_rect, 0, 0, 0, bar_height)

        canvas.bind("<Configure>", _on_resize)

        track = canvas.create_rectangle(0, 0, 1, bar_height, fill=UI.BG_SUBTLE, outline=UI.BG_SUBTLE)
        fill_rect = canvas.create_rectangle(0, 0, 0, bar_height, fill=color, outline=color)
        canvas.current_ratio = 0.0

        return val_lbl, canvas, fill_rect

    def _make_stat_pill(self, parent, label_text, col):
        pill = tk.Frame(
            parent,
            bg=UI.BG_ELEVATED,
            highlightbackground=UI.BORDER_SUBTLE,
            highlightthickness=1,
            padx=UI.SPACE_SM,
            pady=UI.SPACE_XS
        )
        pill.grid(row=0, column=col, sticky="nsew", padx=2)

        tk.Label(
            pill,
            text=label_text,
            font=(self.font_mono, 9),
            fg=UI.TEXT_SUBTLE,
            bg=UI.BG_ELEVATED,
            anchor="w"
        ).pack(anchor="w")

        val_lbl = tk.Label(
            pill,
            text="—",
            font=(self.font_mono, UI.SIZE_BODY, "bold"),
            fg=UI.TEXT_PRIMARY,
            bg=UI.BG_ELEVATED,
            anchor="w"
        )
        val_lbl.pack(anchor="w")

        return val_lbl

    def update_target(self, info: TargetInfo) -> None:
        """Cập nhật toàn bộ UI từ TargetInfo mới."""

        # 1. Cập nhật badge state (header)
        badge_style = UI.get_badge_style(info.state)

        badge_text = "● CHỜ"
        if info.state == "ready":
            badge_text = "● KHÓA MỤC TIÊU"
        elif info.state == "hunting":
            badge_text = "● ĐANG CHIẾN ĐẤU"

        self.badge_label.config(
            text=badge_text,
            bg=badge_style["bg"],
            fg=badge_style["fg"],
            highlightbackground=badge_style["fg"],
            highlightthickness=1
        )

        # 2. Show/hide empty vs active identity section
        if info.state == "waiting" or not info.name:
            self.active_identity_frame.pack_forget()
            self.empty_identity_frame.pack(fill="both", expand=True)

            # Reset values
            self.hp_val_lbl.config(text="— / —", fg=UI.TEXT_SUBTLE)
            self.hp_bar_canvas.current_ratio = 0.0
            self.hp_bar_canvas.coords(self.hp_fill_rect, 0, 0, 0, 5)

            self.mp_val_lbl.config(text="— / —", fg=UI.TEXT_SUBTLE)
            self.mp_bar_canvas.current_ratio = 0.0
            self.mp_bar_canvas.coords(self.mp_fill_rect, 0, 0, 0, 5)

            self.def_val_lbl.config(text="—")
            self.type_val_lbl.config(text="—")
            self.drop_val_lbl.config(text="—")
        else:
            self.empty_identity_frame.pack_forget()
            self.active_identity_frame.pack(fill="both", expand=True)

            self.target_name_disp.config(text=info.name)
            self.target_sub_disp.config(text=f"ID #{info.level} · Vùng chưa rõ") # Assuming ID/Region mapping not in TargetInfo yet
            self.target_level_disp.config(text=str(info.level))

            # 3. Cập nhật canvas bar HP và MP
            def format_stat(val, max_val):
                if max_val == 0: return "— / —"
                v_str = f"{val/1000:.1f}k" if val >= 1000 else str(val)
                m_str = f"{max_val/1000:.1f}k" if max_val >= 1000 else str(max_val)
                return f"{v_str} / {m_str}"

            self.hp_val_lbl.config(text=format_stat(info.hp, info.max_hp), fg=UI.TEXT_PRIMARY)
            hp_ratio = info.hp / info.max_hp if info.max_hp > 0 else 0
            self.hp_bar_canvas.current_ratio = hp_ratio
            width = self.hp_bar_canvas.winfo_width()
            self.hp_bar_canvas.coords(self.hp_fill_rect, 0, 0, width * hp_ratio, 16)

            self.mp_val_lbl.config(text=format_stat(info.mp, info.max_mp), fg=UI.TEXT_PRIMARY)
            mp_ratio = info.mp / info.max_mp if info.max_mp > 0 else 0
            self.mp_bar_canvas.current_ratio = mp_ratio
            width = self.mp_bar_canvas.winfo_width()
            self.mp_bar_canvas.coords(self.mp_fill_rect, 0, 0, width * mp_ratio, 16)

            # 4. Cập nhật 3 stat pills
            self.def_val_lbl.config(text=f"{info.defense:,}")
            self.type_val_lbl.config(text="Unknown") # If type isn't provided
            self.drop_val_lbl.config(text="★★★") # If drop isn't provided

if __name__ == "__main__":
    # Demo runner
    root = tk.Tk()
    root.configure(bg=UI.BG_BASE)

    # Need mock app for font resolution if needed, but UIStyleV2 might handle it directly
    class MockApp:
        def _t(self, key): return key

    panel = TargetStatusPanel(root, app=MockApp())
    panel.pack(padx=40, pady=40, fill="both", expand=True)

    demo = TargetInfo(
        name="Ruina Master", level=180,
        hp=148200, max_hp=280000,
        mp=3200, max_mp=8000,
        defense=4820, state="hunting"
    )
    root.after(2000, lambda: panel.update_target(demo))
    root.mainloop()
