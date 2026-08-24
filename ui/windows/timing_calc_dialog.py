import tkinter as tk
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
                if aps <= 0:
                    raise ValueError('APS must be > 0')
                damage_per_hit = dps / aps
                rec = calculate_timing(monster_hp=ehp, damage_per_hit=damage_per_hit, attacks_per_second=aps)
                self.recommended_time = rec.estimated_kill_time_sec

                # Format text
                text = (
                    f"EHP: {ehp:,.0f} | DPS: {dps:,.0f}\n"
                    f"Time to kill: {rec.estimated_kill_time_sec:.1f}s\n"
                    f"Required Casts: {rec.hits_to_kill:.1f}\n"
                    f"Estimated Delay: {rec.attack_min_duration_sec:.1f}s\n\n"
                    f"Recommended Setting: {rec.estimated_kill_time_sec:.1f}s"
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
