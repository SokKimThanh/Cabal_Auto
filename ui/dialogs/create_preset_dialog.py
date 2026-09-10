import tkinter as tk
from tkinter import ttk, messagebox
from lib.ui_style_v2 import UIStyleV2 as UI


class CreatePresetDialog(tk.Toplevel):
    """Dialog to create a new custom preset from current skill slots."""

    def __init__(self, parent, class_id: int, skill_summary: dict, on_save_callback):
        super().__init__(parent)
        self.title("Create Preset")

        # Make modal
        self.transient(parent)
        self.grab_set()

        # Dimensions
        self.geometry("400x500")
        self.minsize(350, 450)
        self.configure(bg=UI.BG_BASE)

        self.class_id = class_id
        self.skill_summary = skill_summary
        self.on_save_callback = on_save_callback

        self.widgets = {}
        self._build_ui()

        # Center the dialog relative to parent
        self.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() - self.winfo_width()) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")

    def _build_ui(self):
        main_frame = tk.Frame(self, bg=UI.BG_BASE)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # --- Header ---
        header_lbl = tk.Label(
            main_frame,
            text="Lưu cấu hình kỹ năng (Preset)",
            font=UI.FONT_LARGE,
            bg=UI.BG_BASE,
            fg=UI.TEXT_PRIMARY
        )
        header_lbl.pack(anchor="w", pady=(0, 15))

        # --- Form Area ---
        form_frame = tk.Frame(main_frame, bg=UI.BG_SURFACE)
        form_frame.pack(fill="x", pady=10)

        # Class ID (Read Only)
        tk.Label(
            form_frame,
            text="Class ID:",
            bg=UI.BG_SURFACE,
            fg=UI.TEXT_MUTED,
            font=UI.FONT_NORMAL
        ).grid(row=0, column=0, sticky="w", padx=10, pady=10)

        class_lbl = tk.Label(
            form_frame,
            text=str(self.class_id),
            bg=UI.BG_SURFACE,
            fg=UI.TEXT_PRIMARY,
            font=UI.FONT_BOLD
        )
        class_lbl.grid(row=0, column=1, sticky="w", padx=10, pady=10)

        # Preset Name (Input)
        tk.Label(
            form_frame,
            text="Tên Preset (*):",
            bg=UI.BG_SURFACE,
            fg=UI.TEXT_MUTED,
            font=UI.FONT_NORMAL
        ).grid(row=1, column=0, sticky="w", padx=10, pady=10)

        self.name_var = tk.StringVar()
        name_entry = ttk.Entry(
            form_frame,
            textvariable=self.name_var,
            width=30
        )
        name_entry.grid(row=1, column=1, sticky="w", padx=10, pady=10)
        name_entry.focus_set()

        # --- Summary Area ---
        summary_lbl = tk.Label(
            main_frame,
            text="Tóm tắt Kỹ năng (Sẽ được lưu):",
            font=UI.FONT_NORMAL,
            bg=UI.BG_BASE,
            fg=UI.TEXT_PRIMARY
        )
        summary_lbl.pack(anchor="w", pady=(15, 5))

        summary_frame = tk.Frame(
            main_frame,
            bg=UI.BG_SURFACE,
            highlightbackground=UI.BORDER_PRIMARY,
            highlightthickness=1
        )
        summary_frame.pack(fill="both", expand=True, pady=5)

        canvas = tk.Canvas(summary_frame, bg=UI.BG_SURFACE, highlightthickness=0)
        scrollbar = ttk.Scrollbar(summary_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=UI.BG_SURFACE)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar.pack(side="right", fill="y")

        # Bind scrolling events
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        def _on_scroll_linux(event, dir):
            canvas.yview_scroll(dir, "units")

        canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", _on_mousewheel))
        canvas.bind("<Enter>", lambda e: canvas.bind_all("<Button-4>", lambda e: _on_scroll_linux(e, -1)), add="+")
        canvas.bind("<Enter>", lambda e: canvas.bind_all("<Button-5>", lambda e: _on_scroll_linux(e, 1)), add="+")
        canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))
        canvas.bind("<Leave>", lambda e: canvas.unbind_all("<Button-4>"))
        canvas.bind("<Leave>", lambda e: canvas.unbind_all("<Button-5>"))

        # Populate summary content
        if not self.skill_summary:
            tk.Label(
                scrollable_frame,
                text="Không có kỹ năng nào được chọn",
                bg=UI.BG_SURFACE,
                fg=UI.TEXT_MUTED,
                font=UI.FONT_SMALL
            ).pack(anchor="w", padx=10, pady=10)
        else:
            for lane, skills in self.skill_summary.items():
                lane_display = lane.replace("_", " ").title()
                tk.Label(
                    scrollable_frame,
                    text=f"• {lane_display}:",
                    bg=UI.BG_SURFACE,
                    fg=UI.ACCENT_GREEN,
                    font=UI.FONT_BOLD
                ).pack(anchor="w", padx=10, pady=(10, 2))

                if not skills:
                    tk.Label(
                        scrollable_frame,
                        text="  (Trống)",
                        bg=UI.BG_SURFACE,
                        fg=UI.TEXT_MUTED,
                        font=UI.FONT_SMALL
                    ).pack(anchor="w", padx=20, pady=2)
                else:
                    for s_name in skills:
                        tk.Label(
                            scrollable_frame,
                            text=f"  - {s_name}",
                            bg=UI.BG_SURFACE,
                            fg=UI.TEXT_PRIMARY,
                            font=UI.FONT_SMALL
                        ).pack(anchor="w", padx=20, pady=2)

        # --- Bottom Actions ---
        action_frame = tk.Frame(main_frame, bg=UI.BG_BASE)
        action_frame.pack(fill="x", pady=(20, 0))

        btn_cancel = tk.Button(
            action_frame,
            text="Hủy",
            command=self.destroy,
            **UI.get_button_style("secondary")
        )
        btn_cancel.pack(side="right", padx=(10, 0))

        btn_save = tk.Button(
            action_frame,
            text="💾 Save",
            command=self._on_save,
            **UI.get_button_style("primary")
        )
        btn_save.pack(side="right")

    def _on_save(self):
        preset_name = self.name_var.get().strip()
        if not preset_name:
            messagebox.showwarning("Warning", "Vui lòng nhập tên Preset!", parent=self)
            return

        self.on_save_callback(preset_name)
        self.destroy()
