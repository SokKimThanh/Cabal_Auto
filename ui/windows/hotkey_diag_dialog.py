import sys
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
