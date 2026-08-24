with open("ui/tabs/setup_tab.py", "w") as f:
    f.write('''import tkinter as tk
from tkinter import ttk, filedialog
from typing import TYPE_CHECKING, Optional

from lib.i18n import t as i18n_t, GLOBAL_NS as I18N_GLOBAL
from ui.helpers.tooltip import attach_i18n_tooltip

if TYPE_CHECKING:
    from app_gui import App


class SetupTab(tk.Frame):
    def __init__(self, parent: ttk.Notebook, app: "App", *args, **kwargs):
        super().__init__(parent, padx=12, pady=12, *args, **kwargs)
        self.parent = parent
        self.app = app
        self.lang = getattr(app, "lang", "vi")

        self._build_ui()
        self._update_setup_visibility()

    def _t(self, key: str, **kwargs) -> str:
        if hasattr(self.app, "_t"):
            return self.app._t(key, **kwargs)
        return i18n_t(key, ns=I18N_GLOBAL, lang=self.lang, **kwargs)

    def _build_ui(self):
        # Section 1: Configuration Mode
        mode_frame = tk.LabelFrame(self, text=self._t("setup_mode"), padx=12, pady=10)
        mode_frame.grid(row=0, column=0, columnspan=2, sticky="we", pady=(0, 12))

        mode_desc = tk.Label(
            mode_frame, text=self._t("setup_mode_desc"), fg="#666", font=("Arial", 9)
        )
        mode_desc.grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 8))

        current_mode = self.app.hunt_cfg.get("ui_mode", "beginner")
        self.app.setup_mode_var = tk.StringVar(value=current_mode)

        modes = [
            ("beginner", self._t("mode_beginner"), self._t("mode_beginner_desc")),
            ("intermediate", self._t("mode_intermediate"), self._t("mode_intermediate_desc")),
            ("advanced", self._t("mode_advanced"), self._t("mode_advanced_desc")),
        ]

        for idx, (mode_val, mode_label, mode_desc_text) in enumerate(modes):
            rb = tk.Radiobutton(
                mode_frame,
                text=mode_label,
                variable=self.app.setup_mode_var,
                value=mode_val,
                command=self._on_setup_mode_changed,
                font=("Arial", 9, "bold"),
            )
            rb.grid(row=idx + 1, column=0, sticky="w", pady=2)
            desc_label = tk.Label(
                mode_frame, text=f"  {mode_desc_text}", fg="#666", font=("Arial", 8)
            )
            desc_label.grid(row=idx + 1, column=1, sticky="w", padx=(4, 0), pady=2)

        # Section 2: Global Hotkeys
        hotkey_title = "Global Hotkeys" if self.lang == "en" else "Phím Tắt Toàn Cục"
        hotkey_frame = tk.LabelFrame(self, text=f"⌨️ {hotkey_title}", padx=12, pady=10)
        hotkey_frame.grid(row=1, column=0, columnspan=2, sticky="we", pady=(0, 12))

        hotkey_desc_text = (
            "Global hotkeys work even when app is minimized or not focused."
            if self.lang == "en"
            else "Phím tắt toàn cục hoạt động khi ứng dụng thu nhỏ hoặc không focus."
        )
        tk.Label(
            hotkey_frame,
            text=hotkey_desc_text,
            fg="#666",
            font=("Arial", 8),
            wraplength=500,
            justify="left",
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 8))

        hotkey_cfg = self.app.hunt_cfg.get("global_hotkeys", {})
        self.app.global_hotkey_enabled_var = tk.BooleanVar(
            value=hotkey_cfg.get("enabled", True)
        )

        enable_text = "Enable Global Hotkeys" if self.lang == "en" else "Bật phím tắt toàn cục"
        tk.Checkbutton(
            hotkey_frame,
            text=enable_text,
            variable=self.app.global_hotkey_enabled_var,
            font=("Arial", 9, "bold"),
            command=self._on_global_hotkey_toggle,
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 8))

        hotkey_options = [
            "ctrl+shift+r", "ctrl+shift+s", "ctrl+alt+r", "ctrl+alt+s",
            "f9", "f10", "f11", "f12",
        ]

        # Start / Stop Hotkeys
        tk.Label(hotkey_frame, text="Start Hunt:" if self.lang == "en" else "Bắt đầu Hunt:", font=("Arial", 9)).grid(
            row=2, column=0, sticky="e", padx=(0, 8), pady=4
        )
        self.app.global_hotkey_start_var = tk.StringVar(value=hotkey_cfg.get("start_key", "ctrl+shift+r"))
        ttk.Combobox(hotkey_frame, textvariable=self.app.global_hotkey_start_var, values=hotkey_options, width=15, state="readonly").grid(row=2, column=1, sticky="w", pady=4)

        tk.Label(hotkey_frame, text="Stop Hunt:" if self.lang == "en" else "Dừng Hunt:", font=("Arial", 9)).grid(
            row=3, column=0, sticky="e", padx=(0, 8), pady=4
        )
        self.app.global_hotkey_stop_var = tk.StringVar(value=hotkey_cfg.get("stop_key", "ctrl+shift+e"))
        ttk.Combobox(hotkey_frame, textvariable=self.app.global_hotkey_stop_var, values=hotkey_options, width=15, state="readonly").grid(row=3, column=1, sticky="w", pady=4)

        # Section 3: Advanced Hunt Settings
        self.adv_frame = tk.LabelFrame(self, text=self._t("setup_advanced"), padx=12, pady=10)
        self.adv_frame.grid(row=2, column=0, columnspan=2, sticky="we", pady=(0, 12))

        tk.Label(self.adv_frame, text=self._t("target_key")).grid(row=0, column=0, sticky="e", pady=4)
        self.app.setup_target_key_var = tk.StringVar(value=str(self.app.hunt_cfg.get("target_key", "TAB")))
        tk.Entry(self.adv_frame, textvariable=self.app.setup_target_key_var, width=8).grid(row=0, column=1, sticky="w", pady=4)

        tk.Label(self.adv_frame, text=self._t("press_ms")).grid(row=1, column=0, sticky="e", pady=4)
        self.app.setup_press_ms_var = tk.StringVar(value=str(self.app.hunt_cfg.get("attack_press_ms", 60)))
        tk.Entry(self.adv_frame, textvariable=self.app.setup_press_ms_var, width=8).grid(row=1, column=1, sticky="w", pady=4)

        tk.Label(self.adv_frame, text=self._t("target_cycle")).grid(row=1, column=2, sticky="e", padx=(16, 4), pady=4)
        self.app.setup_target_cycle_var = tk.StringVar(value=str(self.app.hunt_cfg.get("target_cycle_delay", 0.2)))
        tk.Entry(self.adv_frame, textvariable=self.app.setup_target_cycle_var, width=8).grid(row=1, column=3, sticky="w", pady=4)

        tk.Label(self.adv_frame, text=self._t("search_interval")).grid(row=2, column=0, sticky="e", pady=4)
        self.app.setup_search_interval_var = tk.StringVar(value=str(self.app.hunt_cfg.get("search_interval", 0.25)))
        tk.Entry(self.adv_frame, textvariable=self.app.setup_search_interval_var, width=8).grid(row=2, column=1, sticky="w", pady=4)

        tk.Label(self.adv_frame, text=self._t("attack_interval")).grid(row=2, column=2, sticky="e", padx=(16, 4), pady=4)
        self.app.setup_attack_interval_var = tk.StringVar(value=str(self.app.hunt_cfg.get("attack_interval", 0.15)))
        tk.Entry(self.adv_frame, textvariable=self.app.setup_attack_interval_var, width=8).grid(row=2, column=3, sticky="w", pady=4)

        tk.Label(self.adv_frame, text=self._t("lost_timeout")).grid(row=3, column=0, sticky="e", pady=4)
        self.app.setup_lost_timeout_var = tk.StringVar(value=str(self.app.hunt_cfg.get("lost_timeout_sec", 1.2)))
        tk.Entry(self.adv_frame, textvariable=self.app.setup_lost_timeout_var, width=8).grid(row=3, column=1, sticky="w", pady=4)

        tk.Label(self.adv_frame, text=self._t("attack_duration")).grid(row=3, column=2, sticky="e", padx=(16, 4), pady=4)
        self.app.setup_attack_duration_var = tk.StringVar(value=str(self.app.hunt_cfg.get("attack_min_duration_sec", 1.5)))
        tk.Entry(self.adv_frame, textvariable=self.app.setup_attack_duration_var, width=8).grid(row=3, column=3, sticky="w", pady=4)

        # Section 4: Window Settings
        self.window_frame = tk.LabelFrame(self, text=self._t("setup_window"), padx=12, pady=10)
        self.window_frame.grid(row=3, column=0, columnspan=2, sticky="we", pady=(0, 12))

        tk.Label(self.window_frame, text=self._t("template")).grid(row=0, column=0, sticky="e", pady=4)
        self.app.setup_template_var = tk.StringVar(value=str(self.app.hunt_cfg.get("template_path", "assets/images/target_frame.png")))
        tk.Entry(self.window_frame, textvariable=self.app.setup_template_var, width=40).grid(row=0, column=1, columnspan=2, sticky="w", pady=4)
        tk.Button(self.window_frame, text=self._t("browse"), command=self._browse_template).grid(row=0, column=3, padx=(4, 0), pady=4)

    def _browse_template(self):
        path = filedialog.askopenfilename(
            title="Select template image",
            filetypes=[("Images", "*.png;*.jpg;*.jpeg;*.bmp")],
        )
        if path:
            self.app.setup_template_var.set(path)

    def _on_setup_mode_changed(self):
        if hasattr(self.app, "_on_setup_mode_changed"):
            self.app._on_setup_mode_changed()
        self._update_setup_visibility()

    def _on_global_hotkey_toggle(self):
        if hasattr(self.app, "_on_global_hotkey_toggle"):
            self.app._on_global_hotkey_toggle()

    def _update_setup_visibility(self):
        mode = self.app.setup_mode_var.get() if hasattr(self.app, "setup_mode_var") else "beginner"
        if mode == "beginner":
            self.adv_frame.grid_remove()
            self.window_frame.grid_remove()
        elif mode == "intermediate":
            self.adv_frame.grid()
            self.window_frame.grid_remove()
        elif mode == "advanced":
            self.adv_frame.grid()
            self.window_frame.grid()
''')

with open("lib/system/instance_lock.py", "w") as f:
    f.write('''import os
import sys
import tempfile
from pathlib import Path


class SingleInstanceLock:
    def __init__(self, app_name: str = "CabalAutoHunt"):
        self.app_name = app_name
        self.mutex = None
        self.lock_file = None
        self.is_locked = False

        if sys.platform != "win32":
            lock_dir = Path(tempfile.gettempdir())
            self.lock_file_path = lock_dir / f"{app_name}.lock"

    def acquire(self) -> bool:
        try:
            if sys.platform == "win32":
                import ctypes
                kernel32 = ctypes.windll.kernel32
                mutex_name = f"Global\\{self.app_name}_SingleInstance"
                self.mutex = kernel32.CreateMutexW(None, False, mutex_name)

                last_error = kernel32.GetLastError()
                if last_error == 183:  # ERROR_ALREADY_EXISTS
                    kernel32.CloseHandle(self.mutex)
                    self.mutex = None
                    return False

                self.is_locked = True
                return True
            else:
                import fcntl
                try:
                    self.lock_file = open(self.lock_file_path, "w")
                    fcntl.flock(self.lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                    self.is_locked = True
                    self.lock_file.write(str(os.getpid()))
                    self.lock_file.flush()
                    return True
                except (OSError, IOError):
                    if self.lock_file:
                        self.lock_file.close()
                    return False
        except Exception as e:
            print(f"Error acquiring lock: {e}")
            return False

    def release(self):
        """Release the lock and clean up."""
        try:
            if sys.platform == "win32":
                if self.mutex and self.is_locked:
                    import ctypes
                    kernel32 = ctypes.windll.kernel32
                    kernel32.CloseHandle(self.mutex)
                    self.is_locked = False
            else:
                if self.lock_file and self.is_locked:
                    import fcntl
                    fcntl.flock(self.lock_file.fileno(), fcntl.LOCK_UN)
                    self.lock_file.close()
                    try:
                        os.unlink(self.lock_file_path)
                    except OSError:
                        pass
                    self.is_locked = False
        except Exception as e:
            print(f"Error releasing lock: {e}")
''')

with open("ui/windows/hotkey_diag_dialog.py", "w") as f:
    f.write('''import sys
import tkinter as tk
from tkinter import ttk, messagebox


def show_hotkey_diagnostics_modal(parent):
    """Show diagnostics modal for hotkeys (e.g. keyboard package missing)."""
    try:
        import keyboard  # noqa
        messagebox.showinfo(
            parent._t("diag_hotkeys_title"),
            parent._t("diag_hotkeys_ok"),
            parent=parent,
        )
        return
    except ImportError:
        pass

    modal = tk.Toplevel(parent)
    modal.title(parent._t("diag_hotkeys_title"))
    modal.geometry("500x350")
    modal.transient(parent)
    modal.grab_set()

    frm = ttk.Frame(modal, padding=20)
    frm.pack(fill="both", expand=True)

    ttk.Label(
        frm,
        text=parent._t("diag_hotkeys_issue_title"),
        font=("Segoe UI", 12, "bold"),
        foreground="#d32f2f",
    ).pack(anchor="w", pady=(0, 10))

    ttk.Label(
        frm,
        text=parent._t("diag_hotkeys_desc"),
        wraplength=450,
        justify="left",
    ).pack(anchor="w", pady=(0, 20))

    # Instructions
    inst_frm = ttk.LabelFrame(
        frm, text=parent._t("diag_hotkeys_fix_title"), padding=10
    )
    inst_frm.pack(fill="x", pady=(0, 20))

    ttk.Label(inst_frm, text=parent._t("diag_hotkeys_step1")).pack(
        anchor="w", pady=2
    )

    # Command entry (readonly)
    cmd = tk.StringVar(value="pip install keyboard")
    cmd_entry = ttk.Entry(
        inst_frm, textvariable=cmd, state="readonly", font=("Consolas", 10)
    )
    cmd_entry.pack(fill="x", pady=(5, 10))

    ttk.Label(inst_frm, text=parent._t("diag_hotkeys_step2")).pack(
        anchor="w", pady=2
    )

    btn_frm = ttk.Frame(frm)
    btn_frm.pack(fill="x", side="bottom")

    ttk.Button(btn_frm, text=parent._t("btn_close"), command=modal.destroy).pack(side="right")

    # Try to position modal center of parent
    parent.update_idletasks()
    x = parent.winfo_x() + (parent.winfo_width() - 500) // 2
    y = parent.winfo_y() + (parent.winfo_height() - 350) // 2
    modal.geometry(f"+{x}+{y}")
''')

with open("ui/windows/timing_calc_dialog.py", "w") as f:
    f.write('''import tkinter as tk
from tkinter import ttk


class TimingCalcDialog(tk.Toplevel):
    def __init__(self, parent, app, on_apply=None):
        super().__init__(parent)
        self.app = app
        self.on_apply = on_apply
        self.title(self.app._t("calc_title"))
        self.geometry("400x500")
        self.transient(parent)
        self.grab_set()
        self._build_ui()

    def _build_ui(self):
        frm = ttk.Frame(self, padding=20)
        frm.pack(fill="both", expand=True)

        ttk.Label(
            frm, text=self.app._t("calc_desc"), wraplength=350, justify="left"
        ).pack(fill="x", pady=(0, 15))

        # Input variables
        self.aps_var = tk.StringVar(value="2.0")
        self.ehp_var = tk.StringVar(value="1000")
        self.dps_var = tk.StringVar(value="500")

        # Input Frame
        input_frm = ttk.LabelFrame(frm, text=self.app._t("calc_input_title"), padding=10)
        input_frm.pack(fill="x", pady=(0, 15))

        # Pre-fill EHP if we have it
        if hasattr(self.app, 'monster_estimate_stats') and self.app.monster_estimate_stats:
            self.ehp_var.set(str(int(self.app.monster_estimate_stats.get("effective_hp", 1000))))
            self.dps_var.set(str(int(self.app.monster_estimate_stats.get("required_dps", 500))))
        else:
            # Fallback to reading the current form EHP if possible
            # Or just leave defaults
            pass

        ttk.Label(input_frm, text=self.app._t("calc_aps")).grid(
            row=0, column=0, sticky="w", pady=5
        )
        ttk.Entry(input_frm, textvariable=self.aps_var, width=15).grid(
            row=0, column=1, sticky="e", pady=5
        )

        ttk.Label(input_frm, text=self.app._t("calc_ehp")).grid(
            row=1, column=0, sticky="w", pady=5
        )
        ttk.Entry(input_frm, textvariable=self.ehp_var, width=15).grid(
            row=1, column=1, sticky="e", pady=5
        )

        ttk.Label(input_frm, text=self.app._t("calc_dps")).grid(
            row=2, column=0, sticky="w", pady=5
        )
        ttk.Entry(input_frm, textvariable=self.dps_var, width=15).grid(
            row=2, column=1, sticky="e", pady=5
        )

        # Output Frame
        output_frm = ttk.LabelFrame(
            frm, text=self.app._t("calc_output_title"), padding=10
        )
        output_frm.pack(fill="x", pady=(0, 15))

        self.res_label = ttk.Label(
            output_frm, text="", font=("Consolas", 10), justify="left", wraplength=330
        )
        self.res_label.pack(fill="both", expand=True)

        self.recommended_time = None

        def _do_calc():
            try:
                aps = float(self.aps_var.get())
                ehp = float(self.ehp_var.get())
                dps = float(self.dps_var.get())

                from lib.features.timing.calculator import calculate_timing
                res = calculate_timing(aps, ehp, dps)
                self.recommended_time = res["recommended_time"]

                # Format text
                text = (
                    f"EHP: {ehp:,.0f} | DPS: {dps:,.0f}\\n"
                    f"Time to kill: {res['time_to_kill']:.1f}s\\n"
                    f"Required Casts: {res['required_casts']:.1f}\\n"
                    f"Estimated Delay: {res['estimated_cast_time']:.1f}s\\n\\n"
                    f"Recommended Setting: {res['recommended_time']:.1f}s"
                )
                self.res_label.config(text=text, foreground="#333")
            except ValueError:
                self.res_label.config(text=self.app._t("calc_err_value"), foreground="#d32f2f")
            except Exception as e:
                import logging
                logging.getLogger("timing_calculator").error(f"Timing calculation error: {e}", exc_info=True)
                err_msg = (
                    "Calculation error. Please check your skill and monster inputs."
                    if getattr(self.app, "lang", "en") == "en"
                    else "Lỗi tính toán. Vui lòng kiểm tra lại thông số quái và kỹ năng."
                )
                self.res_label.config(text=f"⚠️ {err_msg}", foreground="#d32f2f")

        # Buttons
        btn_frm = ttk.Frame(frm)
        btn_frm.pack(fill="x")

        ttk.Button(btn_frm, text=self.app._t("calc_btn_calc"), command=_do_calc).pack(
            side="left", padx=5
        )

        def _apply():
            if self.recommended_time is not None and self.on_apply:
                self.on_apply(self.recommended_time)
                self.destroy()

        ttk.Button(btn_frm, text=self.app._t("calc_btn_apply"), command=_apply).pack(
            side="left", padx=5
        )
        ttk.Button(btn_frm, text=self.app._t("btn_close"), command=self.destroy).pack(
            side="right"
        )

        _do_calc()  # initial calc
''')
